"""Delta join, exception rollup, and campaign compression."""

import pandas as pd


def execute_calendar_join(df_alpha, df_beta):
    """Merges Day 0 and Day X timelines using an inner join on pipeline volume."""
    print("Executing Blueprint 8: Calendar Join Engine (Pipeline Volume Patch)...")

    cols_to_keep = [
        "SKU_ID",
        "Date_Index",
        "Scheduled_Receipts",
        "Planned_Receipts",
        "Planned_Releases",
        "Order_Type",
        "Revenue_at_Risk",
    ]

    df_alpha_subset = df_alpha[cols_to_keep].copy()
    df_beta_subset = df_beta[cols_to_keep].copy()

    df_joined = pd.merge(
        df_alpha_subset,
        df_beta_subset,
        on=["SKU_ID", "Date_Index"],
        how="inner",
        suffixes=("_Alpha", "_Beta"),
    )

    df_joined["Action_Delta"] = df_joined["Planned_Releases_Beta"] - df_joined["Planned_Releases_Alpha"]

    total_months = len(df_joined["Date_Index"].unique())
    print(f"✅ Timelines Merged successfully over a strictly aligned {total_months}-month horizon.")
    return df_joined


def generate_executive_alerts(df_joined, master_data):
    """Filters comparative baseline and rolls up header-level executive alerts."""
    print("Executing Blueprint 9: Executive Exception Rollup...")

    df_exceptions = df_joined[df_joined["Action_Delta"] != 0].copy()
    if df_exceptions.empty:
        print("✅ Zero exceptions found. Pipeline is perfectly balanced.")
        return pd.DataFrame(), pd.DataFrame()

    df_exceptions["Unit_Cost"] = df_exceptions["SKU_ID"].map(lambda x: master_data[x]["Unit_Cost"])
    df_exceptions["Capital_Variance"] = df_exceptions["Action_Delta"] * df_exceptions["Unit_Cost"]
    df_exceptions["Rev_Risk_Variance"] = (
        df_exceptions["Revenue_at_Risk_Beta"] - df_exceptions["Revenue_at_Risk_Alpha"]
    )

    rollup = df_exceptions.groupby("SKU_ID").agg(
        Months_Affected=("Date_Index", "count"),
        Start_Date=("Date_Index", "min"),
        End_Date=("Date_Index", "max"),
        Net_Action_Units=("Action_Delta", "sum"),
        Total_Capital_Impact=("Capital_Variance", "sum"),
        Peak_Rev_Risk=("Rev_Risk_Variance", "max"),
    ).reset_index()

    print(f"✅ Filtered {len(df_exceptions)} monthly anomalies into {len(rollup)} Executive Alerts.\n")
    print("=" * 85)
    print(" 🚨 PHASE III: EXECUTIVE EXCEPTION MONITOR (HEADER LEVEL) 🚨 ")
    print("=" * 85)

    for _, row in rollup.iterrows():
        risk = row["Peak_Rev_Risk"]
        risk_str = f"${risk:,.0f}" if risk > 0 else "---"
        if risk < 0:
            risk_str = f"Save: ${abs(risk):,.0f}"
        print(
            f"[{row['SKU_ID']}] | Horizon: {row['Start_Date']} to {row['End_Date']} "
            f"({row['Months_Affected']} mos) | Net Action: {row['Net_Action_Units']:+,.0f} units"
        )
        print(
            f"          -> Net Cap Flow: ${row['Total_Capital_Impact']:+,.0f} | Peak Rev Risk: {risk_str}"
        )
        print("-" * 85)

    return rollup, df_exceptions


def calculate_delta_math(df_alpha, df_beta, master_data):
    """Inner join in RAM to calculate exact mathematical variance."""
    print(" -> Executing Mathematical Inner Join (Alpha vs. Beta)...")
    df_join = pd.merge(df_alpha, df_beta, on=["SKU_ID", "Date_Index"], suffixes=("_Alpha", "_Beta"))
    df_join["Unit_Cost"] = df_join["SKU_ID"].map(lambda x: master_data[x]["Unit_Cost"])
    df_join["Action_Delta"] = df_join["Planned_Releases_Beta"] - df_join["Planned_Releases_Alpha"]
    df_join["Capital_Variance"] = df_join["Action_Delta"] * df_join["Unit_Cost"]
    df_join["Inventory_Variance"] = df_join["Locked_Inv_Beta"] - df_join["Locked_Inv_Alpha"]

    total_alpha_spend = (df_join["Planned_Releases_Alpha"] * df_join["Unit_Cost"]).sum()
    total_beta_spend = (df_join["Planned_Releases_Beta"] * df_join["Unit_Cost"]).sum()
    net_capital_impact = total_beta_spend - total_alpha_spend
    df_exceptions = df_join[df_join["Action_Delta"] != 0].copy()

    return df_join, df_exceptions, total_alpha_spend, total_beta_spend, net_capital_impact


def compress_to_campaigns(df_exceptions):
    """Translates monthly anomalies into continuous action time-blocks."""
    print(" -> Compressing Anomalies into Action Campaigns...")
    campaigns = []

    for sku, group in df_exceptions.groupby("SKU_ID"):
        group = group.sort_values("Date_Index")
        current_block = None

        for _, row in group.iterrows():
            date = row["Date_Index"]
            action_qty = row["Action_Delta"]
            capital = row["Capital_Variance"]
            action_type = "BUY / EXPEDITE" if action_qty > 0 else "CANCEL / DELAY"

            if current_block is None:
                current_block = {
                    "SKU_ID": sku,
                    "Action": action_type,
                    "Start_Date": date,
                    "End_Date": date,
                    "Duration_Months": 1,
                    "Net_Units": action_qty,
                    "Net_Capital": capital,
                }
            elif current_block["Action"] == action_type:
                current_block["End_Date"] = date
                current_block["Duration_Months"] += 1
                current_block["Net_Units"] += action_qty
                current_block["Net_Capital"] += capital
            else:
                campaigns.append(current_block)
                current_block = {
                    "SKU_ID": sku,
                    "Action": action_type,
                    "Start_Date": date,
                    "End_Date": date,
                    "Duration_Months": 1,
                    "Net_Units": action_qty,
                    "Net_Capital": capital,
                }
        if current_block:
            campaigns.append(current_block)

    return pd.DataFrame(campaigns)
