"""
Orchestrates eval runs: calls the pipeline for each test case,
scores the output, and returns structured results.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.crew import analyze_finances
from evals.scorer import score_result
from evals.test_cases import TEST_CASES


def run_single(test_case: dict) -> dict:
    """Run one test case through the pipeline and score it."""
    print(f"\n{'='*60}")
    print(f"Running: {test_case['name']}")
    print(f"{'='*60}")

    result = analyze_finances(test_case["expenses"])

    if result.get("status") == "error":
        return {
            "name": test_case["name"],
            "description": test_case["description"],
            "status": "error",
            "error": result.get("error"),
            "scores": None,
            "usage": None,
            "outputs": None,
        }

    scores = score_result(result, test_case["expenses"], test_case["expected_signals"])
    usage = result.get("usage", {})

    print(f"  Score: {scores['total']}/{scores['max']}  "
          f"(analysis={scores['analysis']} rec={scores['recommendations']} budget={scores['budget']})")
    if usage:
        print(f"  Tokens: {usage.get('total_input_tokens', 0)} in / "
              f"{usage.get('total_output_tokens', 0)} out")

    return {
        "name":        test_case["name"],
        "description": test_case["description"],
        "status":      "success",
        "expenses":    test_case["expenses"],
        "outputs": {
            "analysis":        result.get("analysis", ""),
            "recommendations": result.get("recommendations", ""),
            "budget":          result.get("budget", ""),
        },
        "scores": scores,
        "usage":  usage,
    }


def run_all(fast: bool = False) -> list[dict]:
    """Run evals for all (or just the first) test case(s)."""
    cases = TEST_CASES[:1] if fast else TEST_CASES
    return [run_single(tc) for tc in cases]
