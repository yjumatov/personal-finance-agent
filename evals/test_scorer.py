"""
Unit tests for evals/scorer.py, focused on score_grounding.

These run offline against hand-written fake analysis strings — no Claude API
calls, no network. Run with:

    python -m unittest evals.test_scorer
"""

import unittest

from evals.scorer import score_grounding


EXPENSES = [
    {"date": "2024-01-01", "description": "Grocery Store", "amount": 100.00, "category": "Food"},
    {"date": "2024-01-02", "description": "Restaurant",    "amount": 50.00,  "category": "Food"},
    {"date": "2024-01-03", "description": "Bus Pass",      "amount": 25.00,  "category": "Transport"},
]
# expected_total = 175.00, category_totals = {Food: 150.00, Transport: 25.00}


class ScoreGroundingTests(unittest.TestCase):

    def test_correct_total_and_categories_scores_full_marks(self):
        text = "Total spending: $175.00. Food: $150.00. Transport: $25.00."
        result = score_grounding(text, EXPENSES)
        self.assertEqual(result["score"], 3)
        self.assertTrue(result["total_found"])
        self.assertEqual(result["categories_matched"], 2)
        self.assertEqual(result["categories_total"], 2)
        self.assertEqual(result["hallucinated_amounts"], [])

    def test_total_correct_but_no_category_subtotals_loses_a_point(self):
        text = "Total spending: $175.00. You spent a lot on food and transport."
        result = score_grounding(text, EXPENSES)
        self.assertEqual(result["score"], 2)
        self.assertTrue(result["total_found"])
        self.assertEqual(result["categories_matched"], 0)

    def test_hallucinated_figure_loses_a_point_and_is_reported(self):
        text = "Total: $175.00. Food: $150.00. Transport: $25.00. Misc fees: $412.50."
        result = score_grounding(text, EXPENSES)
        self.assertEqual(result["score"], 2)
        self.assertEqual(result["hallucinated_amounts"], [412.50])

    def test_no_dollar_amounts_scores_zero_without_crashing(self):
        text = "You spent roughly forty percent of your budget on food this month."
        result = score_grounding(text, EXPENSES)
        self.assertEqual(result["score"], 0)
        self.assertTrue(result["no_amounts_found"])

    def test_individual_expense_amount_is_not_a_hallucination(self):
        # $100.00 is a real line-item amount, not a subtotal or the total —
        # citing it should not be flagged as an invented figure.
        text = "One notable purchase was $100.00 for groceries. Total: $175.00."
        result = score_grounding(text, EXPENSES)
        self.assertTrue(result["total_found"])
        self.assertEqual(result["hallucinated_amounts"], [])

    def test_wrong_total_is_flagged_as_hallucination(self):
        text = "Total: $999.00."
        result = score_grounding(text, EXPENSES)
        self.assertFalse(result["total_found"])
        self.assertEqual(result["hallucinated_amounts"], [999.00])

    def test_tolerance_boundary_within_one_cent_matches(self):
        expenses = [{"amount": 305.98}]
        result = score_grounding("Total: $305.99.", expenses)
        self.assertTrue(result["total_found"])

    def test_tolerance_boundary_beyond_one_cent_does_not_match(self):
        expenses = [{"amount": 305.98}]
        result = score_grounding("Total: $306.00.", expenses)
        self.assertFalse(result["total_found"])
        self.assertEqual(result["hallucinated_amounts"], [306.00])

    def test_no_categories_in_input_counts_the_category_check_as_satisfied(self):
        expenses = [{"amount": 50.00}, {"amount": 50.00}]
        result = score_grounding("Total: $100.00.", expenses)
        self.assertEqual(result["categories_total"], 0)
        self.assertEqual(result["score"], 3)

    def test_more_than_half_of_categories_required(self):
        # Distinct amounts per category so each mention can only match one.
        expenses = [
            {"amount": 10.00, "category": "A"},
            {"amount": 20.00, "category": "B"},
            {"amount": 30.00, "category": "C"},
        ]
        # Only 1 of 3 category subtotals mentioned — below half, no point.
        one_of_three = score_grounding("Total: $60.00. A: $10.00.", expenses)
        self.assertEqual(one_of_three["categories_matched"], 1)
        # 2 of 3 mentioned — meets half, point awarded.
        two_of_three = score_grounding("Total: $60.00. A: $10.00. B: $20.00.", expenses)
        self.assertEqual(two_of_three["categories_matched"], 2)
        self.assertEqual(two_of_three["score"] - one_of_three["score"], 1)

    def test_handles_commas_in_large_figures(self):
        expenses = [{"amount": 1850.00, "category": "Housing"}]
        result = score_grounding("Rent: $1,850.00. Total: $1,850.00.", expenses)
        self.assertTrue(result["total_found"])
        self.assertEqual(result["categories_matched"], 1)


if __name__ == "__main__":
    unittest.main()
