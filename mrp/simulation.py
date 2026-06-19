"""SKU simulation state machine (Alpha and Beta runs)."""

import math

import pandas as pd


def execute_sku_simulation(sku_id, master_data, initial_state, demand_array, calendar_array):
    """Runs the 4-step execution loop for a single SKU over the 24-month horizon."""
    locked_inv = []
    planned_receipts = []
    planned_releases = [0] * 24

    current_inv = initial_state["On_Hand"]
    ss = master_data["SS"]
    moq = master_data["MOQ"]
    lt = master_data["LT"]
    max_cap = master_data["Max_Cap"]

    scheduled_receipts = [0] * 24
    if initial_state["Open_PO"] > 0 and initial_state["PO_Month_Index"] < 24:
        scheduled_receipts[initial_state["PO_Month_Index"]] = initial_state["Open_PO"]

    for t in range(24):
        d_t = demand_array[t]
        sr_t = scheduled_receipts[t]
        raw_balance = current_inv + sr_t - d_t
        porcpt_t = 0

        if raw_balance < ss:
            deficit = ss - raw_balance
            porcpt_t = math.ceil(deficit / moq) * moq

        current_inv = raw_balance + porcpt_t
        locked_inv.append(current_inv)
        planned_receipts.append(porcpt_t)

    capacity_alerts = []
    for t in range(24):
        receipt_qty = planned_receipts[t]
        if receipt_qty > 0:
            release_index = t - lt
            if release_index >= 0:
                planned_releases[release_index] += receipt_qty
            else:
                planned_releases[0] += receipt_qty

            if receipt_qty > max_cap:
                capacity_alerts.append({
                    "Month": calendar_array[t],
                    "Required": receipt_qty,
                    "Limit": max_cap,
                })

    df_sku = pd.DataFrame({
        "SKU_ID": sku_id,
        "Date_Index": calendar_array,
        "Demand": demand_array,
        "Scheduled_Receipts": scheduled_receipts,
        "Planned_Receipts": planned_receipts,
        "Planned_Releases": planned_releases,
        "Locked_Inv": locked_inv,
    })

    return df_sku, capacity_alerts


def execute_beta_run(calendar_array, master_data, initial_state, demand_dict):
    """Reruns the path-dependent state machine on the Day X reality."""
    print("Initializing Beta Recalculation Engine...\n")
    all_sku_dfs = []
    beta_capacity_alerts = []

    for sku in master_data.keys():
        locked_inv = []
        planned_receipts = []
        planned_releases = [0] * 24

        current_inv = initial_state[sku]["On_Hand"]
        scheduled_receipts = initial_state[sku]["Firmed_Receipts_Array"]
        demand_array = demand_dict[sku]

        ss = master_data[sku]["SS"]
        moq = master_data[sku]["MOQ"]
        lt = master_data[sku]["LT"]
        max_cap = master_data[sku]["Max_Cap"]

        for t in range(24):
            d_t = demand_array[t]
            sr_t = scheduled_receipts[t]
            raw_balance = current_inv + sr_t - d_t
            porcpt_t = 0

            if raw_balance < ss:
                deficit = ss - raw_balance
                porcpt_t = math.ceil(deficit / moq) * moq

            current_inv = raw_balance + porcpt_t
            locked_inv.append(current_inv)
            planned_receipts.append(porcpt_t)

        for t in range(24):
            receipt_qty = planned_receipts[t]
            if receipt_qty > 0:
                release_index = t - lt
                if release_index >= 0:
                    planned_releases[release_index] += receipt_qty
                else:
                    planned_releases[0] += receipt_qty

                if receipt_qty > max_cap:
                    beta_capacity_alerts.append({
                        "SKU": sku,
                        "Month": calendar_array[t],
                        "Required": receipt_qty,
                        "Limit": max_cap,
                    })

        df_sku = pd.DataFrame({
            "SKU_ID": sku,
            "Date_Index": calendar_array,
            "Demand": demand_array,
            "Scheduled_Receipts": scheduled_receipts,
            "Planned_Receipts": planned_receipts,
            "Planned_Releases": planned_releases,
            "Locked_Inv": locked_inv,
        })
        all_sku_dfs.append(df_sku)

    df_beta_raw = pd.concat(all_sku_dfs, ignore_index=True)
    return df_beta_raw, beta_capacity_alerts
