"""AI payload serialization and supplier email drafting."""

import json


def generate_ai_payload(df_exceptions):
    """
    Compresses discrete monthly exceptions into continuous time-blocks
    and formats them into a structured JSON payload for the LLM Agent.
    """
    print("Executing Blueprint 10: Compressing timeline into AI JSON Payload...")

    ai_payload = {
        "system_status": "CRITICAL_VARIANCES_DETECTED",
        "total_sku_campaigns": 0,
        "skus": {},
    }

    for sku, group in df_exceptions.groupby("SKU_ID"):
        group = group.sort_values("Date_Index")
        compressed_events = []
        current_block = None

        for _, row in group.iterrows():
            date = row["Date_Index"]
            action_qty = row["Action_Delta"]
            capital = row["Capital_Variance"]
            action_type = "EXPEDITE_OR_BUY" if action_qty > 0 else "CANCEL_OR_DELAY"

            if current_block is None:
                current_block = {
                    "Action": action_type,
                    "Start_Date": date,
                    "End_Date": date,
                    "Duration_Months": 1,
                    "Total_Units_Impacted": action_qty,
                    "Total_Capital_Impact": capital,
                }
            elif current_block["Action"] == action_type:
                current_block["End_Date"] = date
                current_block["Duration_Months"] += 1
                current_block["Total_Units_Impacted"] += action_qty
                current_block["Total_Capital_Impact"] += capital
            else:
                compressed_events.append(current_block)
                current_block = {
                    "Action": action_type,
                    "Start_Date": date,
                    "End_Date": date,
                    "Duration_Months": 1,
                    "Total_Units_Impacted": action_qty,
                    "Total_Capital_Impact": capital,
                }

        if current_block:
            compressed_events.append(current_block)

        ai_payload["skus"][sku] = compressed_events
        ai_payload["total_sku_campaigns"] += len(compressed_events)

    return json.dumps(ai_payload, indent=4)


def draft_supplier_emails(json_payload_string, master_data):
    """Draft supplier communication from compressed AI JSON payload."""
    print("Executing Blueprint 10.2: Agentic Email Generation...")
    payload = json.loads(json_payload_string)

    if payload["total_sku_campaigns"] == 0:
        print("✅ No critical actions required. No emails drafted.")
        return {}

    emails_drafted = {}
    for sku, campaigns in payload["skus"].items():
        supplier_name = master_data[sku].get("Supplier", f"Supplier_for_{sku}")
        unit_cost = master_data[sku].get("Unit_Cost", 0)

        print(f"\n📩 DRAFTING EMAIL TO: {supplier_name} [Subject: Urgent Action Required - {sku}]")
        print("-" * 80)

        simulated_llm_response = f"""
Subject: Urgent PO Adjustment Required - {sku}

Hi {supplier_name} Team,

I am reaching out to request a critical adjustment to our purchasing plan for {sku} due to recent shifts in our downstream demand constraints.

Please review the following required adjustments to our open orders:

"""
        for camp in campaigns:
            action = "Increase/Expedite" if camp["Action"] == "EXPEDITE_OR_BUY" else "Cancel/Delay"
            simulated_llm_response += (
                f"- We need to {action} a net total of {abs(camp['Total_Units_Impacted'])} units "
                f"between {camp['Start_Date']} and {camp['End_Date']}.\n"
            )

        simulated_llm_response += """
Could you please review your production capacity and let me know by EOD tomorrow if you can support these adjustments? Once confirmed, I will route the formal PO updates through the ERP.

Thank you for your continued partnership.

Best regards,
[Your Name]
Senior Supply Chain Planner
        """

        print(simulated_llm_response.strip())
        print("-" * 80)
        emails_drafted[sku] = simulated_llm_response

    return emails_drafted
