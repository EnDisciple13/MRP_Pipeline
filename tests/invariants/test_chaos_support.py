"""Hypothesis property: chaos-support — diff support ⊆ event targets."""

from __future__ import annotations

import copy

import pytest

from data.fixtures import CONSTRAINTS, DEMAND
from mrp.state import apply_chaos_events, deep_copy_beta_state, extract_inherited_state


@pytest.mark.parametrize("sku", ["SKU_001", "SKU_002", "SKU_003"])
@pytest.mark.parametrize("magnitude", [-50, 0, 25])
def test_diff_support_subset(sku: str, magnitude: int, headless_pipeline):
    """Non-target SKUs unchanged after demand-shock chaos event."""
    alpha = headless_pipeline["alpha"]
    calendar = alpha.calendar_array
    beta_initial, beta_master, beta_demand = extract_inherited_state(
        alpha.df_enriched, CONSTRAINTS, DEMAND
    )
    pre_initial, pre_master, pre_demand = deep_copy_beta_state(
        beta_initial, beta_master, beta_demand
    )

    event = {
        "SKU_ID": sku,
        "Mutation_Type": "Demand_Shock",
        "Target_Date": calendar[3],
        "Magnitude": magnitude,
    }
    _post_initial, _post_master, post_demand = apply_chaos_events(
        copy.deepcopy(pre_initial),
        copy.deepcopy(pre_master),
        copy.deepcopy(pre_demand),
        calendar,
        [event],
    )

    for other in CONSTRAINTS:
        if other == sku:
            continue
        assert pre_demand[other] == post_demand[other], f"leak into {other}"
