#!/usr/bin/env python3
"""
CLI entry point for the eval + token-usage report.

Usage:
  python run_evals.py           # run all 5 scenarios → eval_report.html
  python run_evals.py --fast    # run 1 scenario (quick smoke test)
  python run_evals.py --output report.html  # custom output path
"""

import argparse
import sys

from evals.eval_runner import run_all
from evals.report_generator import generate_report


def main():
    parser = argparse.ArgumentParser(description="Run evals for the personal finance agent.")
    parser.add_argument("--fast",   action="store_true", help="Run only the first scenario.")
    parser.add_argument("--output", default="eval_report.html", help="Output HTML file path.")
    args = parser.parse_args()

    print("Personal Finance Agent — Eval Runner")
    print("=" * 50)

    results = run_all(fast=args.fast)

    ok = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "error"]

    print("\n" + "=" * 50)
    print(f"Finished: {len(ok)} succeeded, {len(failed)} failed")

    if ok:
        avg_score = sum(r["scores"]["total"] for r in ok) / len(ok)
        avg_tokens_in  = sum((r.get("usage") or {}).get("total_input_tokens",  0) for r in ok) / len(ok)
        avg_tokens_out = sum((r.get("usage") or {}).get("total_output_tokens", 0) for r in ok) / len(ok)
        print(f"Avg score:        {avg_score:.1f}/9")
        print(f"Avg input tokens: {avg_tokens_in:,.0f}")
        print(f"Avg output tokens:{avg_tokens_out:,.0f}")

    output_path = generate_report(results, output_path=args.output)
    print(f"\nReport written to: {output_path}")
    print("Open it in any browser to share with your friend.")

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
