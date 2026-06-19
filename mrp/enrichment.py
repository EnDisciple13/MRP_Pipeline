"""Baseline enrichment and inventory health metrics."""

import numpy as np
import pandas as pd


def enrich_baseline_matrix(df_raw, master_data):
    df = df_raw.copy()

    unit_cost_map = {sku: data["Unit_Cost"] for sku, data in master_data.items()}
    unit_rev_map = {sku: data["Unit_Revenue"] for sku, data in master_data.items()}
    ss_map = {sku: data["SS"] for sku, data in master_data.items()}
    lt_map = {sku: data["LT"] for sku, data in master_data.items()}
    max_cap_map = {sku: data["Max_Cap"] for sku, data in master_data.items()}

    df["Unit_Cost"] = df["SKU_ID"].map(unit_cost_map)
    df["Unit_Revenue"] = df["SKU_ID"].map(unit_rev_map)
    df["Target_SS"] = df["SKU_ID"].map(ss_map)
    df["Lead_Time"] = df["SKU_ID"].map(lt_map)
    df["Max_Cap"] = df["SKU_ID"].map(max_cap_map)
    df["Month_Index"] = df.groupby("SKU_ID").cumcount()

    conditions = [
        (df["Planned_Receipts"] == 0),
        (df["Planned_Receipts"] > 0) & ((df["Month_Index"] - df["Lead_Time"]) < 0),
        (df["Planned_Receipts"] > df["Max_Cap"]),
        (df["Planned_Receipts"] > 0) & ((df["Month_Index"] - df["Lead_Time"]) >= 0),
    ]
    choices = [
        "Stable",
        "🚨 MAGIC FIX (Past Due)",
        "⚠️ CAPACITY BREACH",
        "Normal Execution",
    ]
    df["Order_Type"] = np.select(conditions, choices, default="Unknown")

    df["Capital_Tied_Up"] = df["Locked_Inv"] * df["Unit_Cost"]
    df["Capital_Required"] = df["Planned_Receipts"] * df["Unit_Cost"]
    df["Safety_Stock_Cost"] = df["Target_SS"] * df["Unit_Cost"]
    df["Revenue_at_Risk"] = np.where(
        df["Order_Type"].isin(["🚨 MAGIC FIX (Past Due)", "⚠️ CAPACITY BREACH"]),
        df["Planned_Receipts"] * df["Unit_Revenue"],
        0,
    )

    return df.drop(columns=["Month_Index", "Target_SS", "Lead_Time", "Max_Cap"])


def calculate_inventory_health(df_enriched):
    """Dead stock vs active stock ratio using 6-month forward demand."""
    total_capital = df_enriched["Capital_Tied_Up"].sum()
    df_enriched["6M_Fwd_Demand"] = (
        df_enriched.groupby("SKU_ID")["Demand"]
        .shift(-6)
        .rolling(window=6, min_periods=1)
        .sum()
        .fillna(0)
    )
    df_enriched["Dead_Stock_Units"] = (
        df_enriched["Locked_Inv"] - df_enriched["6M_Fwd_Demand"]
    ).clip(lower=0)
    df_enriched["Dead_Stock_Value"] = df_enriched["Dead_Stock_Units"] * df_enriched["Unit_Cost"]
    total_dead_stock_value = df_enriched["Dead_Stock_Value"].sum()
    health_ratio = (
        ((total_capital - total_dead_stock_value) / total_capital) * 100
        if total_capital > 0
        else 100
    )
    df_enriched.drop(columns=["6M_Fwd_Demand", "Dead_Stock_Units", "Dead_Stock_Value"], inplace=True)
    return health_ratio, total_dead_stock_value


def calculate_alpha_health(df_alpha):
    """System health metrics for Alpha shadow ledger."""
    print(" -> Calculating Alpha System Health Metrics...")
    df = df_alpha.copy()
    
    df["Total_Order_Qty"] = df["Scheduled_Receipts"] + df["Planned_Releases"]
    total_capital_commitment = (df["Total_Order_Qty"] * df["Unit_Cost"]).sum()
    
    total_capital_tied_up = df["Capital_Tied_Up"].sum()
    df["6M_Fwd_Demand"] = (
        df.groupby("SKU_ID")["Demand"]
        .shift(-6)
        .rolling(window=6, min_periods=1)
        .sum()
        .fillna(0)
    )
    df["Dead_Stock_Units"] = (df["Locked_Inv"] - df["6M_Fwd_Demand"]).clip(lower=0)
    df["Dead_Stock_Value"] = df["Dead_Stock_Units"] * df["Unit_Cost"]
    total_dead_stock_value = df["Dead_Stock_Value"].sum()
    health_ratio = (
        (total_capital_tied_up - total_dead_stock_value) / total_capital_tied_up
        if total_capital_tied_up > 0
        else 1.0
    )
    return total_capital_commitment, health_ratio, total_dead_stock_value


def calculate_beta_health(df_beta):
    """System health metrics for Beta shadow ledger."""
    print(" -> Calculating Beta System Health Metrics...")
    df = df_beta.copy()
    
    df["Total_Order_Qty"] = df["Scheduled_Receipts"] + df["Planned_Releases"]
    total_capital_commitment = (df["Total_Order_Qty"] * df["Unit_Cost"]).sum()
    
    total_capital_tied_up = df["Capital_Tied_Up"].sum()
    df["6M_Fwd_Demand"] = (
        df.groupby("SKU_ID")["Demand"]
        .shift(-6)
        .rolling(window=6, min_periods=1)
        .sum()
        .fillna(0)
    )
    df["Dead_Stock_Units"] = (df["Locked_Inv"] - df["6M_Fwd_Demand"]).clip(lower=0)
    df["Dead_Stock_Value"] = df["Dead_Stock_Units"] * df["Unit_Cost"]
    total_dead_stock_value = df["Dead_Stock_Value"].sum()
    health_ratio = (
        (total_capital_tied_up - total_dead_stock_value) / total_capital_tied_up
        if total_capital_tied_up > 0
        else 1.0
    )
    return total_capital_commitment, health_ratio, total_dead_stock_value
