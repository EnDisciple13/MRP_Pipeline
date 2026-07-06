"""Shared MRP invariant oracles for property tests."""

from __future__ import annotations

import copy
from typing import Any

import pandas as pd


def mass_balance_violations(
    df: pd.DataFrame,
    initial_on_hand: float,
    sku: str | None = None,
) -> list[str]:
    """Per-period PAB recursion: I_t == I_{t-1} + SR + PR - D."""
    violations: list[str] = []
    work = df if sku is None else df[df["SKU_ID"] == sku]
    prev = initial_on_hand
    for _, row in work.iterrows():
        receipts = row["Scheduled_Receipts"] + row["Planned_Receipts"]
        expected = prev + receipts - row["Demand"]
        if row["Locked_Inv"] != expected:
            violations.append(
                f"{row.get('Date_Index')}: got {row['Locked_Inv']}, expected {expected}"
            )
        prev = row["Locked_Inv"]
    return violations


def chaos_support_violations(
    pre: pd.DataFrame,
    post: pd.DataFrame,
    target_skus: set[str],
    target_periods: set[str] | None = None,
) -> list[str]:
    """Frame rule: diff support must stay within declared chaos targets."""
    violations: list[str] = []
    numeric_cols = [
        "Demand",
        "Locked_Inv",
        "Scheduled_Receipts",
        "Planned_Receipts",
        "Planned_Releases",
    ]
    for sku in pre["SKU_ID"].unique():
        pre_sku = pre[pre["SKU_ID"] == sku].set_index("Date_Index")
        post_sku = post[post["SKU_ID"] == sku].set_index("Date_Index")
        for period in pre_sku.index:
            if sku in target_skus and (
                target_periods is None or period in target_periods
            ):
                continue
            for col in numeric_cols:
                if col not in pre_sku.columns:
                    continue
                if pre_sku.at[period, col] != post_sku.at[period, col]:
                    violations.append(f"leak {sku}/{period}/{col}")
    return violations


def delta_zero_violations(delta_df: pd.DataFrame, col: str = "Action_Delta") -> list[str]:
    if col not in delta_df.columns:
        return [f"missing column {col}"]
    if delta_df[col].abs().max() != 0:
        return [f"non-zero delta max={delta_df[col].abs().max()}"]
    return []


def non_negative_violations(df: pd.DataFrame) -> list[str]:
    violations: list[str] = []
    for col in ("Locked_Inv", "Planned_Receipts", "Scheduled_Receipts"):
        if col in df.columns and (df[col] < 0).any():
            violations.append(f"negative values in {col}")
    return violations


def excel_round_trip_violations(source: pd.DataFrame, round_tripped: pd.DataFrame) -> list[str]:
    violations: list[str] = []
    if list(source.columns) != list(round_tripped.columns):
        violations.append("column mismatch")
    for col in source.columns:
        for a, b in zip(source[col].tolist(), round_tripped[col].tolist()):
            if isinstance(a, str) or isinstance(b, str):
                if str(a) != str(b):
                    violations.append(f"string mismatch in {col}: {a!r} vs {b!r}")
            else:
                if abs(float(a) - float(b)) > 1e-9:
                    violations.append(f"numeric mismatch in {col}: {a} vs {b}")
    return violations
