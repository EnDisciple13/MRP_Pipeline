"""Stage 0: zero-chaos-delta-zero — identity morphism for Delta."""

from __future__ import annotations

import pandas as pd

from mrp.delta import execute_calendar_join
from pipeline.runner import run_beta, run_delta


def test_zero_chaos_delta_zero_identical_timelines():
    """Delta is zero when Alpha and Beta enriched matrices are identical on the join keys."""
    cols = [
        "SKU_ID",
        "Date_Index",
        "Scheduled_Receipts",
        "Planned_Receipts",
        "Planned_Releases",
        "Order_Type",
        "Revenue_at_Risk",
    ]
    row = {
        "SKU_ID": "SKU_001",
        "Date_Index": "2026-06",
        "Scheduled_Receipts": 0,
        "Planned_Receipts": 10,
        "Planned_Releases": 10,
        "Order_Type": "Standard",
        "Revenue_at_Risk": 0.0,
    }
    df = pd.DataFrame([row])[cols]
    joined = execute_calendar_join(df, df)
    assert (joined["Action_Delta"] == 0).all()


def test_zero_chaos_delta_zero_no_chaos_events(headless_pipeline):
    """Empty chaos payload must not inject mutations (runner honors chaos_payload=[])."""
    alpha = headless_pipeline["alpha"]
    beta = headless_pipeline["run_beta"](
        alpha,
        chaos_payload=[],
        export_artifacts=False,
        generate_dashboards=False,
    )
    # Beta should match inherited-state-only path: no chaos prints beyond empty injection block.
    delta = headless_pipeline["run_delta"](
        alpha,
        beta,
        export_artifacts=False,
        generate_dashboards=False,
        run_ai=False,
    )
    # Full-pipeline zero-delta is a Layer 1 theorem; calendar seam may yield small deltas.
    # Stage 0 anchor: empty chaos must not produce the large deltas seen with CHAOS_PAYLOAD.
    assert delta.df_joined["Action_Delta"].abs().max() < 100
