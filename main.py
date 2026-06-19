#!/usr/bin/env python3
"""MRP Pipeline CLI entry point."""

import argparse
import sys

from mrp.calendar import generate_calendar_horizon
from pipeline.runner import run_alpha, run_beta, run_delta, run_full


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MRP Pipeline — Alpha / Beta / Delta simulation")
    parser.add_argument(
        "--phase",
        choices=["alpha", "beta", "delta", "full"],
        default="full",
        help="Pipeline phase to run (default: full)",
    )
    parser.add_argument(
        "--no-dashboards",
        action="store_true",
        help="Skip matplotlib dashboard generation",
    )
    parser.add_argument(
        "--fixtures",
        action="store_true",
        help="Generate enterprise Excel sandbox and test fixture workbooks",
    )
    parser.add_argument(
        "--semantic-test",
        action="store_true",
        help="Run semantic shadow test against test fixture (requires --fixtures first)",
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Verify calendar module only and exit",
    )
    args = parser.parse_args(argv)

    if args.smoke_test:
        cal = generate_calendar_horizon()
        assert len(cal) == 24, f"Expected 24 months, got {len(cal)}"
        print(f"✅ Smoke test passed. Calendar: {cal[0]} → {cal[-1]}")
        return 0

    dashboards = not args.no_dashboards

    if args.phase == "alpha":
        result = run_alpha(generate_dashboards=dashboards)
        print(f"Alpha complete: {len(result.df_raw)} rows")
        return 0

    if args.phase == "beta":
        alpha = run_alpha(generate_dashboards=dashboards)
        beta = run_beta(alpha, generate_dashboards=dashboards)
        print(f"Beta complete: {len(beta.df_raw)} rows")
        return 0

    if args.phase == "delta":
        alpha = run_alpha(generate_dashboards=dashboards)
        beta = run_beta(alpha, generate_dashboards=dashboards)
        delta = run_delta(alpha, beta, generate_dashboards=dashboards)
        print(f"Delta complete: {len(delta.df_joined)} joined rows")
        return 0

    alpha, beta, delta = run_full(
        generate_dashboards=dashboards,
        export_fixtures=args.fixtures,
        run_semantic_test=args.semantic_test,
    )
    print(
        f"Full pipeline complete: alpha={len(alpha.df_raw)} beta={len(beta.df_raw)} "
        f"delta_join={len(delta.df_joined)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
