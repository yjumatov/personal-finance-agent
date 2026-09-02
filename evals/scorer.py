"""
Rule-based quality scorer for pipeline outputs.

Scores each of four dimensions on a 0-3 scale, returns a dict:
  {analysis: int, recommendations: int, budget: int, grounding: int, total: int, max: int}

Three of the four dimensions (analysis, recommendations, budget) check the
SHAPE of the output — keyword presence, dollar/percent signs, text length.
They cannot tell a correct analysis from a confidently wrong one. The fourth,
grounding, is the one dimension that checks correctness: it recomputes the
real numbers from the input data and verifies the model's figures against
them, catching fabricated totals that would otherwise sail through the
shape-only checks above.
"""

import re


def _has_keywords(text: str, keywords: list[str]) -> int:
    """Count how many of the given keywords appear in text (case-insensitive)."""
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw.lower() in text_lower)


def _count_percent_mentions(text: str) -> int:
    return len(re.findall(r"\d+\s*%", text))


def _count_dollar_amounts(text: str) -> int:
    return len(re.findall(r"\$[\d,]+(?:\.\d+)?", text))


def _extract_dollar_amounts(text: str) -> list[float]:
    """Pull every dollar figure out of text as a float, e.g. '$1,850.00' -> 1850.0."""
    raw = re.findall(r"\$\s?([\d,]+(?:\.\d+)?)", text)
    return [float(amount.replace(",", "")) for amount in raw]


def _to_amount(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _amount_matches(value: float, target: float, tolerance: float = 0.01) -> bool:
    return abs(value - target) <= tolerance


def score_analysis(analysis_text: str, expense_data: list, expected_signals: list[str]) -> int:
    """
    Rubric (0-3):
      +1 — at least 2 expected signals appear in the text
      +1 — dollar amounts or totals are present (shows numeric grounding)
      +1 — mentions 3 or more distinct categories from the input data
    """
    score = 0

    if _has_keywords(analysis_text, expected_signals) >= 2:
        score += 1

    if _count_dollar_amounts(analysis_text) >= 2:
        score += 1

    input_categories = {e.get("category", "").lower() for e in expense_data if e.get("category")}
    mentioned = sum(1 for cat in input_categories if cat in analysis_text.lower())
    if mentioned >= 3:
        score += 1

    return score


def score_recommendations(recommendations_text: str, analysis_text: str) -> int:
    """
    Rubric (0-3):
      +1 — at least 3 numbered or bulleted suggestions present
      +1 — at least one category from the analysis is referenced
      +1 — text length >= 200 chars (crude minimum-effort check only — length
           says nothing about whether the content is actually substantive)
    """
    score = 0

    numbered = re.findall(r"(?:^|\n)\s*[\d\-\*\•]\s+\S", recommendations_text)
    if len(numbered) >= 3:
        score += 1

    analysis_words = set(re.findall(r"\b[a-zA-Z]{4,}\b", analysis_text.lower()))
    rec_words = set(re.findall(r"\b[a-zA-Z]{4,}\b", recommendations_text.lower()))
    overlap = len(analysis_words & rec_words)
    if overlap >= 5:
        score += 1

    if len(recommendations_text.strip()) >= 200:
        score += 1

    return score


def score_budget(budget_text: str) -> int:
    """
    Rubric (0-3):
      +1 — percentage figures present (e.g., "30%")
      +1 — dollar amounts present
      +1 — mentions emergency fund or savings
    """
    score = 0

    if _count_percent_mentions(budget_text) >= 2:
        score += 1

    if _count_dollar_amounts(budget_text) >= 2:
        score += 1

    if any(kw in budget_text.lower() for kw in ["emergency", "savings", "save"]):
        score += 1

    return score


def score_grounding(analysis_text: str, expense_data: list) -> dict:
    """
    Checks the Expense Analyzer's numbers against ground truth computed from
    expense_data itself, rather than just checking that numbers are present.
    Every dollar figure in expense_data (the total, per-category subtotals, and
    each individual expense amount) is fair game — the model is free to cite
    any of them, and anything it cites that matches none of them is treated as
    a hallucination.

    Rubric (0-3):
      +1 — the correct overall total appears in the analysis (within $0.01)
      +1 — at least half of the per-category subtotals appear (within $0.01)
      +1 — no hallucinated figures: every dollar amount found in the analysis
           matches a real subtotal, the real total, or an individual expense
           amount from the input (within $0.01)

    Returns a dict with the score plus the evidence used to compute it, so a
    report can show exactly what matched and what didn't.
    """
    expected_total = round(sum(_to_amount(e.get("amount", 0)) for e in expense_data), 2)

    category_totals: dict[str, float] = {}
    for e in expense_data:
        category = e.get("category")
        if not category:
            continue
        category_totals[category] = category_totals.get(category, 0.0) + _to_amount(e.get("amount", 0))
    category_totals = {c: round(v, 2) for c, v in category_totals.items()}

    individual_amounts = [round(_to_amount(e.get("amount", 0)), 2) for e in expense_data]

    found_amounts = _extract_dollar_amounts(analysis_text)

    if not found_amounts:
        return {
            "score": 0,
            "expected_total": expected_total,
            "total_found": False,
            "categories_matched": 0,
            "categories_total": len(category_totals),
            "hallucinated_amounts": [],
            "no_amounts_found": True,
        }

    total_found = any(_amount_matches(a, expected_total) for a in found_amounts)

    categories_total = len(category_totals)
    categories_matched = sum(
        1 for target in category_totals.values()
        if any(_amount_matches(a, target) for a in found_amounts)
    )

    known_amounts = [expected_total, *category_totals.values(), *individual_amounts]
    hallucinated_amounts = list(dict.fromkeys(
        a for a in found_amounts
        if not any(_amount_matches(a, known) for known in known_amounts)
    ))

    score = 0
    if total_found:
        score += 1
    # No categories to check against (e.g. uncategorized input) counts as satisfied.
    if categories_total == 0 or categories_matched >= categories_total / 2:
        score += 1
    if not hallucinated_amounts:
        score += 1

    return {
        "score": score,
        "expected_total": expected_total,
        "total_found": total_found,
        "categories_matched": categories_matched,
        "categories_total": categories_total,
        "hallucinated_amounts": hallucinated_amounts,
    }


def score_result(result: dict, expense_data: list, expected_signals: list[str]) -> dict:
    """Score all four dimensions and return a combined score dict."""
    analysis_score = score_analysis(result.get("analysis", ""), expense_data, expected_signals)
    rec_score = score_recommendations(result.get("recommendations", ""), result.get("analysis", ""))
    budget_score = score_budget(result.get("budget", ""))
    grounding = score_grounding(result.get("analysis", ""), expense_data)

    return {
        "analysis":          analysis_score,
        "recommendations":   rec_score,
        "budget":            budget_score,
        "grounding":         grounding["score"],
        "grounding_evidence": grounding,
        "total":             analysis_score + rec_score + budget_score + grounding["score"],
        "max":               12,
    }
