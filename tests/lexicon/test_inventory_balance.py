"""Lexicon property: inventory-balance — PAB recursion matches OR lexicon."""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from data.fixtures import CONSTRAINTS, INVENTORY
from mrp.calendar import generate_calendar_horizon
from mrp.simulation import execute_sku_simulation
from tests.invariants.helpers import mass_balance_violations


@settings(max_examples=25, deadline=None)
@given(
    st.integers(min_value=0, max_value=20_000),
    st.lists(st.integers(min_value=0, max_value=500), min_size=24, max_size=24),
)
def test_pab_recursion_matches_lexicon(initial_on_hand: int, demand_series: list[int]):
    """I_t = I_{t-1} + R_t - D_t telescoped across 24-period horizon."""
    calendar = generate_calendar_horizon(start_date="2026-06-01")
    assert len(demand_series) == len(calendar)
    sku = "SKU_002"
    inventory = {**INVENTORY[sku], "On_Hand": initial_on_hand}
    df, _ = execute_sku_simulation(
        sku,
        CONSTRAINTS[sku],
        inventory,
        demand_series,
        calendar,
    )
    violations = mass_balance_violations(df, initial_on_hand, sku=sku)
    assert violations == [], violations
