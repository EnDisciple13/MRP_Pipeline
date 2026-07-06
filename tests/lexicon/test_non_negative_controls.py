"""Lexicon property: non-negative-controls — physical inventory and receipts ≥ 0."""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from data.fixtures import CONSTRAINTS
from mrp.calendar import generate_calendar_horizon
from mrp.simulation import execute_sku_simulation
from tests.invariants.helpers import non_negative_violations


@settings(max_examples=25, deadline=None)
@given(
    st.integers(min_value=0, max_value=100),
    st.lists(st.integers(min_value=1000, max_value=50_000), min_size=24, max_size=24),
)
def test_inventory_and_receipts_non_negative(initial_on_hand: int, demand_shock: list[int]):
    """Adversarial demand shocks must not produce negative inventory or receipts."""
    calendar = generate_calendar_horizon(start_date="2026-06-01")
    sku = "SKU_001"
    inventory = {"On_Hand": initial_on_hand, "Open_PO": 0, "PO_Month_Index": 0}
    df, _ = execute_sku_simulation(
        sku,
        CONSTRAINTS[sku],
        inventory,
        demand_shock,
        calendar,
    )
    violations = non_negative_violations(df)
    assert violations == [], violations
