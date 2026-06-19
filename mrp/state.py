"""State inheritance and chaos injection for Beta timeline."""

import copy

import pandas as pd


def extract_inherited_state(df_alpha_enriched, master_data, alpha_demand):
    """
    Baseline lock and pipeline reconciliation with lead-time fence.
    """
    print("Executing Baseline Lock: Inheriting Day 0 State (Time Fence Enabled)...")

    dict_beta_initial_state = {}
    dict_beta_master_data = {}
    dict_beta_demand = {}

    sku_list = df_alpha_enriched["SKU_ID"].unique()

    for sku in sku_list:
        df_sku = df_alpha_enriched[df_alpha_enriched["SKU_ID"] == sku].reset_index(drop=True)

        lt = master_data[sku]["LT"]
        dict_beta_master_data[sku] = {
            "LT": lt,
            "SS": master_data[sku]["SS"],
            "MOQ": master_data[sku]["MOQ"],
            "Max_Cap": master_data[sku]["Max_Cap"],
            "Unit_Cost": master_data[sku]["Unit_Cost"],
            "Unit_Revenue": master_data[sku]["Unit_Revenue"],
            "Status": master_data[sku]["Status"],
            "Lifecycle_Status": "Active",
        }

        locked_inv_month_1 = df_sku.loc[0, "Locked_Inv"]
        alpha_planned_receipts = df_sku["Planned_Receipts"].tolist()
        shifted_planned = alpha_planned_receipts[1:] + [0]

        beta_firmed_receipts = []
        for i in range(24):
            if i < lt:
                beta_firmed_receipts.append(shifted_planned[i])
            else:
                beta_firmed_receipts.append(0)

        dict_beta_initial_state[sku] = {
            "On_Hand": locked_inv_month_1,
            "Firmed_Receipts_Array": beta_firmed_receipts,
        }

        current_demand = alpha_demand[sku]
        dict_beta_demand[sku] = current_demand[1:] + [current_demand[-1]]

    return dict_beta_initial_state, dict_beta_master_data, dict_beta_demand


def apply_chaos_events(beta_initial_state, beta_master_data, beta_demand, beta_calendar, payload):
    print("Executing Blueprint 6: Injecting Chaos Payload into Day X Timeline...\n")

    for event in payload:
        sku = event["SKU_ID"]
        m_type = event["Mutation_Type"]

        if sku not in beta_master_data:
            continue

        print(f"🚨 INJECTING [{m_type}] into {sku}...")

        if m_type == "Demand_Shock":
            target_date = event["Target_Date"]
            mag = event["Magnitude"]
            if target_date in beta_calendar:
                idx = beta_calendar.index(target_date)
                beta_demand[sku][idx] += mag
                print(f"   -> Demand at {target_date} altered by {mag} units.")

        elif m_type == "Longitudinal_Demand_Shift":
            target_date = event["Target_Date"]
            mag = event["Magnitude"]
            if target_date in beta_calendar:
                idx = beta_calendar.index(target_date)
                for i in range(idx, 24):
                    beta_demand[sku][i] = max(0, beta_demand[sku][i] + mag)
                print(f"   -> Structural Market Shift: Demand adjusted by {mag} from {target_date} to end of horizon.")

        elif m_type == "Supply_Delay":
            target_date = event["Target_Date"]
            delay_months = event["Magnitude"]
            if target_date in beta_calendar:
                idx = beta_calendar.index(target_date)
                firmed_array = beta_initial_state[sku]["Firmed_Receipts_Array"]
                if firmed_array[idx] > 0:
                    delayed_qty = firmed_array[idx]
                    firmed_array[idx] = 0
                    new_arrival_idx = idx + delay_months
                    if new_arrival_idx < 24:
                        firmed_array[new_arrival_idx] += delayed_qty
                        print(f"   -> Boat Delayed! {delayed_qty} units pushed from {target_date} to {beta_calendar[new_arrival_idx]}.")
                    else:
                        print(f"   -> CRITICAL: {delayed_qty} units delayed past the 24-month planning horizon. Inventory lost.")

        elif m_type == "Constraint":
            var = event["Target_Variable"]
            new_val = event["Magnitude"]
            old_val = beta_master_data[sku][var]
            beta_master_data[sku][var] = new_val
            print(f"   -> Supplier parameter [{var}] mutated from {old_val} to {new_val}.")

        elif m_type == "Zombie":
            target_date = event["Target_Date"]
            beta_master_data[sku]["Lifecycle_Status"] = "Zombie"
            if target_date in beta_calendar:
                idx = beta_calendar.index(target_date)
                for i in range(idx, 24):
                    beta_demand[sku][i] = 0
            print(f"   -> Product flagged for retirement. Demand zeroed out from {target_date} onward.")

    return beta_initial_state, beta_master_data, beta_demand


def deep_copy_beta_state(initial_state, master_data, demand):
    """Return deep copies of beta state dicts for safe chaos mutation."""
    return (
        copy.deepcopy(initial_state),
        copy.deepcopy(master_data),
        copy.deepcopy(demand),
    )
