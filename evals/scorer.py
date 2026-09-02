"""
Rule-based quality scorer for pipeline outputs.

Scores each section on a 0-3 scale, returns a dict:
  {analysis: int, recommendations: int, budget: int, total: int}
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
      +1 — text length >= 200 chars (indicates substance, not filler)
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


def score_result(result: dict, expense_data: list, expected_signals: list[str]) -> dict:
    """Score all three sections and return a combined score dict."""
    analysis_score = score_analysis(result.get("analysis", ""), expense_data, expected_signals)
    rec_score = score_recommendations(result.get("recommendations", ""), result.get("analysis", ""))
    budget_score = score_budget(result.get("budget", ""))

    return {
        "analysis":        analysis_score,
        "recommendations": rec_score,
        "budget":          budget_score,
        "total":           analysis_score + rec_score + budget_score,
        "max":             9,
    }
