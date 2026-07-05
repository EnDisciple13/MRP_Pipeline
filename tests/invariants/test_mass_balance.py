"""Stage 0: mass-balance — telescoped PAB recursion."""

from __future__ import annotations

from data.fixtures import CONSTRAINTS, DEMAND, INVENTORY
from mrp.calendar import generate_calendar_horizon
from mrp.simulation import execute_sku_simulation


def test_mass_balance_per_period():
    """Locked_Inv[t] == Locked_Inv[t-1] + SR[t] + PR[t] - Demand[t]."""
    calendar = generate_calendar_horizon(start_date="2026-06-01")
    sku = "SKU_001"
    df, _alerts = execute_sku_simulation(
        sku,
        CONSTRAINTS[sku],
        INVENTORY[sku],
        DEMAND[sku],
        calendar,
    )
    prev = INVENTORY[sku]["On_Hand"]
    for _idx, row in df.iterrows():
        receipts = row["Scheduled_Receipts"] + row["Planned_Receipts"]
        expected = prev + receipts - row["Demand"]
        assert row["Locked_Inv"] == expected, (
            f"mass-balance violation at {row['Date_Index']}: "
            f"got {row['Locked_Inv']}, expected {expected}"
        )
        prev = row["Locked_Inv"]
