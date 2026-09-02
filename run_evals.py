#!/usr/bin/env python3
"""
CLI entry point for the eval + token-usage report.

Usage:
  python run_evals.py                    # run all 5 scenarios → eval_report.html
  python run_evals.py --fast             # run 1 scenario (quick smoke test)
  python run_evals.py --output report.html   # custom output path
  python run_evals.py --threshold 0.8    # require 80% of max score to pass
  python run_evals.py --strict           # any single scenario below threshold fails the run
  python run_evals.py --save-baseline    # record this run's scores as the new regression baseline
"""

import argparse
import json
import os
import sys

from evals.eval_runner import run_all
from evals.report_generator import generate_report

BASELINE_PATH = os.path.join(os.path.dirname(__file__), "evals", "baseline.json")


def load_baseline() -> dict:
    if not os.path.exists(BASELINE_PATH):
        return {}
    with open(BASELINE_PATH, "r", encoding="utf-8") as f:
        return json.load(f).get("scenarios", {})


def save_baseline(results: list[dict]) -> None:
    scenarios = {
        r["name"]: r["scores"]
        for r in results
        if r["status"] == "success"
    }
    with open(BASELINE_PATH, "w", encoding="utf-8") as f:
        json.dump({"scenarios": scenarios}, f, indent=2)
    print(f"Baseline saved to {BASELINE_PATH}")


def print_scenario_summary(results: list[dict], threshold: float, baseline: dict) -> bool:
    """
    Print a PASS/FAIL line per scenario (plus a baseline delta, if one exists)
    and return whether every scenario passed.

    A scenario passes only if its score meets the threshold AND its grounding
    dimension is non-zero — a pipeline that invents numbers is broken even if
    it reads well, so zero grounding fails the scenario regardless of score.
    """
    print("\n" + "-" * 50)
    print("Scenario results")
    print("-" * 50)

    all_passed = True

    for r in results:
        name = r["name"]

        if r["status"] == "error":
            print(f"  [FAIL] {name}: pipeline error — {r.get('error')}")
            all_passed = False
            continue

        scores = r["scores"]
        pct = scores["total"] / scores["max"]
        zero_grounding = scores["grounding"] == 0
        passed = pct >= threshold and not zero_grounding
        all_passed = all_passed and passed

        status = "PASS" if passed else "FAIL"
        line = f"  [{status}] {name}: {scores['total']}/{scores['max']} ({pct:.0%})"
        if zero_grounding:
            line += "  ⚠ grounding=0 (numbers don't match the input data)"
        print(line)

        baseline_scores = baseline.get(name)
        if baseline_scores:
            delta = scores["total"] - baseline_scores["total"]
            regression = delta <= -2
            arrow = f"{delta:+d}"
            tag = "  ⚠ REGRESSION" if regression else ""
            print(f"         baseline: was {baseline_scores['total']}/{baseline_scores['max']} ({arrow}){tag}")

    return all_passed


def main():
    parser = argparse.ArgumentParser(description="Run evals for the personal finance agent.")
    parser.add_argument("--fast",   action="store_true", help="Run only the first scenario.")
    parser.add_argument("--output", default="eval_report.html", help="Output HTML file path.")
    parser.add_argument("--threshold", type=float, default=0.7,
                         help="Minimum fraction of max score for a scenario to pass (default 0.7).")
    parser.add_argument("--strict", action="store_true",
                         help="Fail the run if any single scenario is below threshold "
                              "(default: only the aggregate average is checked).")
    parser.add_argument("--save-baseline", action="store_true",
                         help="Write this run's scores to evals/baseline.json for future regression checks.")
    args = parser.parse_args()

    print("Personal Finance Agent — Eval Runner")
    print("=" * 50)

    baseline = load_baseline()
    results = run_all(fast=args.fast)

    ok = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "error"]

    print("\n" + "=" * 50)
    print(f"Finished: {len(ok)} succeeded, {len(failed)} failed")

    if ok:
        avg_score = sum(r["scores"]["total"] for r in ok) / len(ok)
        avg_max = sum(r["scores"]["max"] for r in ok) / len(ok)
        avg_tokens_in  = sum((r.get("usage") or {}).get("total_input_tokens",  0) for r in ok) / len(ok)
        avg_tokens_out = sum((r.get("usage") or {}).get("total_output_tokens", 0) for r in ok) / len(ok)
        print(f"Avg score:        {avg_score:.1f}/{avg_max:.0f}")
        print(f"Avg input tokens: {avg_tokens_in:,.0f}")
        print(f"Avg output tokens:{avg_tokens_out:,.0f}")

    output_path = generate_report(results, output_path=args.output)
    print(f"\nReport written to: {output_path}")
    print("Open it in any browser to share with your friend.")

    all_scenarios_passed = print_scenario_summary(results, args.threshold, baseline)

    if args.save_baseline:
        save_baseline(results)

    # Aggregate check: average score across scenarios must clear the threshold.
    avg_pct = (sum(r["scores"]["total"] / r["scores"]["max"] for r in ok) / len(ok)) if ok else 0.0
    any_zero_grounding = any(r["scores"]["grounding"] == 0 for r in ok)

    overall_pass = bool(ok) and not failed and avg_pct >= args.threshold and not any_zero_grounding
    if args.strict and not all_scenarios_passed:
        overall_pass = False

    print("\n" + "=" * 50)
    verdict = "PASS" if overall_pass else "FAIL"
    print(f"Overall: {verdict}  (avg {avg_pct:.0%}, threshold {args.threshold:.0%}"
          f"{', strict mode' if args.strict else ''})")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
