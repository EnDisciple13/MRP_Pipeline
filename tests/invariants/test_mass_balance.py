"""Stage 0 + Hypothesis: mass-balance — telescoped PAB recursion."""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from data.fixtures import CONSTRAINTS, INVENTORY
from mrp.calendar import generate_calendar_horizon
from mrp.simulation import execute_sku_simulation
from tests.invariants.helpers import mass_balance_violations


@settings(max_examples=30, deadline=None)
@given(
    st.integers(min_value=0, max_value=5000),
    st.lists(st.integers(min_value=0, max_value=1000), min_size=24, max_size=24),
)
def test_mass_balance_per_period(initial_on_hand: int, demand_series: list[int]):
    """Locked_Inv[t] == Locked_Inv[t-1] + SR[t] + PR[t] - Demand[t]."""
    calendar = generate_calendar_horizon(start_date="2026-06-01")
    sku = "SKU_001"
    inventory = {**INVENTORY[sku], "On_Hand": initial_on_hand}
    df, _alerts = execute_sku_simulation(
        sku,
        CONSTRAINTS[sku],
        inventory,
        demand_series,
        calendar,
    )
    violations = mass_balance_violations(df, initial_on_hand, sku=sku)
    assert violations == [], violations
