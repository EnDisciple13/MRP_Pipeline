"""Hypothesis property: run-determinism — byte-identical outputs."""

from __future__ import annotations

import pandas as pd
from hypothesis import given, settings
from hypothesis import strategies as st

from data.fixtures import CONSTRAINTS, DEMAND, INVENTORY
from mrp.calendar import generate_calendar_horizon
from mrp.simulation import execute_sku_simulation


@settings(max_examples=20, deadline=None)
@given(st.integers(min_value=0, max_value=10_000))
def test_byte_identical_outputs(demand_bump: int):
    """Two independent SKU simulations with identical inputs produce equal frames."""
    calendar = generate_calendar_horizon(start_date="2026-06-01")
    sku = "SKU_001"
    demand = [10 + (demand_bump % 5)] * 24
    df1, _ = execute_sku_simulation(
        sku, CONSTRAINTS[sku], INVENTORY[sku], demand, calendar
    )
    df2, _ = execute_sku_simulation(
        sku, CONSTRAINTS[sku], INVENTORY[sku], demand, calendar
    )
    assert df1.equals(df2)
