"""Stage 0 + Hypothesis: inheritance-gluing — Beta initial equals Alpha seam."""

from __future__ import annotations

import pytest

from mrp.state import extract_inherited_state


@pytest.mark.parametrize("sku", ["SKU_001", "SKU_002", "SKU_003"])
def test_inheritance_gluing_on_hand(sku: str, headless_pipeline):
    """Beta On_Hand equals Alpha month-0 Locked_Inv per SKU."""
    alpha = headless_pipeline["alpha"]
    constraints = headless_pipeline["constraints"]
    demand = headless_pipeline["demand"]

    beta_initial, _master, _beta_demand = extract_inherited_state(
        alpha.df_enriched, constraints, demand
    )

    alpha_row0 = alpha.df_enriched[alpha.df_enriched["SKU_ID"] == sku].iloc[0]
    assert beta_initial[sku]["On_Hand"] == alpha_row0["Locked_Inv"]


def test_inheritance_gluing_demand_shift(headless_pipeline):
    """Beta demand is Alpha demand shifted by one period (last value padded)."""
    alpha = headless_pipeline["alpha"]
    constraints = headless_pipeline["constraints"]
    demand = headless_pipeline["demand"]

    _beta_initial, _master, beta_demand = extract_inherited_state(
        alpha.df_enriched, constraints, demand
    )

    for sku in constraints:
        alpha_d = demand[sku]
        expected = alpha_d[1:] + [alpha_d[-1]]
        assert beta_demand[sku] == expected
