"""Hypothesis property: export-round-trip — Excel values match source."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
from hypothesis import given, settings
from hypothesis import strategies as st

from tests.invariants.helpers import excel_round_trip_violations


@settings(max_examples=25, deadline=None)
@given(
    st.lists(
        st.tuples(
            st.from_regex(r"SKU_\d{3}", fullmatch=True),
            st.integers(min_value=0, max_value=10_000),
            st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        ),
        min_size=1,
        max_size=12,
    )
)
def test_excel_values_match_source(rows: list[tuple[str, int, float]]):
    """Round-trip dataframe through openpyxl preserves values."""
    source = pd.DataFrame(
        rows, columns=["SKU_ID", "Planned_Receipts", "Demand"]
    )
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "roundtrip.xlsx"
        source.to_excel(path, index=False, engine="openpyxl")
        round_tripped = pd.read_excel(path, engine="openpyxl", dtype={"SKU_ID": str})
    round_tripped["SKU_ID"] = round_tripped["SKU_ID"].astype(str)
    violations = excel_round_trip_violations(source, round_tripped)
    assert violations == [], violations
