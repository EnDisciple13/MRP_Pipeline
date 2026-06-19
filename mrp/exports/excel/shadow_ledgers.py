"""Alpha, Beta, and Delta system-of-record shadow ledgers."""

from datetime import datetime
from pathlib import Path

import pandas as pd

from mrp.delta import calculate_delta_math, compress_to_campaigns
from mrp.enrichment import calculate_alpha_health, calculate_beta_health
from mrp.exports.google_sheets_export import finalize_sor_google_exports
from mrp.exports.system_of_record_paths import sor_excel_path
from mrp.viz.dashboards import dashboard_path

def build_chaos_map(payload, calendar_array):
    """
    MODULE 1: The Chaos Router
    Scans the JSON payload and builds a fast-lookup map in RAM to identify
    exactly which SKU and Month indices were altered by a human.
    """
    print(" -> Building Chaos Routing Map in RAM...")
    chaos_map = set() # Stores tuples of (SKU_ID, Month_Index)

    for event in payload:
        sku = event["SKU_ID"]
        m_type = event["Mutation_Type"]
        target_date = event.get("Target_Date")

        if target_date and target_date in calendar_array:
            start_idx = calendar_array.index(target_date)

            # If Shock, only flag the single month
            if m_type == "Demand_Shock":
                chaos_map.add((sku, start_idx))

            # If Shift or Zombie, flag that month and ALL subsequent months
            elif m_type in ["Longitudinal_Demand_Shift", "Zombie"]:
                for i in range(start_idx, 24):
                    chaos_map.add((sku, i))

    return chaos_map


def build_alpha_shadow_ledger(df_alpha, skus, calendar_array, CONSTRAINTS, filename=None):
    if filename is None:
        filename = str(sor_excel_path("alpha"))
    excel_path = Path(filename)
    excel_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Executing Blueprint 17: Compiling Pure Python Shadow Ledger: {filename}")

    # Run the math in RAM
    agg_capital, health_grade, dead_stock = calculate_alpha_health(df_alpha)

    # Filter the 90-Day Action Plan in RAM
    df_action_plan = df_alpha[(df_alpha["Planned_Releases"] > 0) & (df_alpha.groupby("SKU_ID").cumcount() < 3)]

    # --- INITIALIZE EXCEL WRITER FIRST ---
    writer = pd.ExcelWriter(filename, engine='xlsxwriter', datetime_format='mmm-yy')
    workbook = writer.book

    # --- NOW INITIALIZE UI FORMATS ---
    header_fmt = workbook.add_format({'bold': True, 'bg_color': '#2C3E50', 'font_color': 'white', 'align': 'center'})
    date_fmt = workbook.add_format({'num_format': 'mmm-yy', 'bold': True, 'bg_color': '#34495E', 'font_color': 'white', 'align': 'center'})
    label_fmt = workbook.add_format({'bold': True, 'align': 'right', 'valign': 'vcenter'})
    money_fmt = workbook.add_format({'num_format': '$#,##0', 'align': 'left'})
    percent_fmt = workbook.add_format({'num_format': '0.0%', 'align': 'left'})
    num_fmt = workbook.add_format({'num_format': '#,##0', 'align': 'center'})

    # The Alert Formats
    format_red = workbook.add_format({'bg_color': '#E74C3C', 'font_color': 'white', 'bold': True, 'num_format': '#,##0', 'align': 'center'})
    format_orange = workbook.add_format({'bg_color': '#F39C12', 'font_color': 'black', 'bold': True, 'num_format': '#,##0', 'align': 'center'})

    # ========================================================
    # TAB 1: EXECUTIVE SUMMARY (The Static Front Page)
    # ========================================================
    ws_exec = workbook.add_worksheet("Executive_Summary")
    ws_exec.hide_gridlines(2)
    ws_exec.set_column('A:A', 35)
    ws_exec.set_column('B:B', 20)

    title_fmt = workbook.add_format({'bold': True, 'font_size': 16, 'font_color': '#2C3E50', 'bottom': 2})
    ws_exec.write("A1", "Alpha Brain: Day 0 System of Record", title_fmt)

    ws_exec.write("A3", "Aggregate Capital Commitment (PO Value):", label_fmt)
    ws_exec.write("B3", agg_capital, money_fmt)

    ws_exec.write("A4", "Inventory Health Grade (Active vs Dead):", label_fmt)
    ws_exec.write("B4", health_grade, percent_fmt)

    ws_exec.write("A5", "Total Dead Stock Risk Exposure:", label_fmt)
    ws_exec.write("B5", dead_stock, money_fmt)

    # ========================================================
    # TAB 2: THE HORIZONTAL PIVOT ENGINE (Shadow Sandbox)
    # ========================================================
    ws_matrix = workbook.add_worksheet("Alpha_Master_Plan")
    ws_matrix.set_column('A:A', 15)
    ws_matrix.set_column('B:B', 22, label_fmt)
    ws_matrix.set_column('C:Z', 12, num_fmt)
    ws_matrix.freeze_panes(1, 2)

    # Write Headers
    ws_matrix.write(0, 0, "SKU_ID", header_fmt)
    ws_matrix.write(0, 1, "Metric", header_fmt)

    # Convert String Array to Datetime on the fly
    for i, date_str in enumerate(calendar_array):
        dt_obj = datetime.strptime(date_str, "%Y-%m")
        ws_matrix.write_datetime(0, i + 2, dt_obj, date_fmt)

    # The Pivot Loop
    row_cursor = 1
    for sku in skus:
        df_sku = df_alpha[df_alpha['SKU_ID'] == sku].reset_index(drop=True)

        # Pull constraints for Python Logic Gate
        sku_lt = CONSTRAINTS[sku]['LT']
        sku_max_cap = CONSTRAINTS[sku]['Max_Cap']

        ws_matrix.write(row_cursor, 0, sku, workbook.add_format({'bold': True}))

        ws_matrix.write(row_cursor, 1, "Demand")
        ws_matrix.write(row_cursor + 1, 1, "Scheduled Receipts")
        ws_matrix.write(row_cursor + 2, 1, "Planned Releases (POs)")
        ws_matrix.write(row_cursor + 3, 1, "Ending Inventory")

        for index, row in df_sku.iterrows():
            col_idx = index + 2

            # Extract raw integers
            demand = row['Demand']
            planned_order = row['Planned_Releases']
            ending_inv = row['Locked_Inv']

            # THE PURE PYTHON ALERT ENGINE
            if planned_order > sku_max_cap:
                po_format = format_orange
            elif planned_order > 0 and (index + 1) <= sku_lt:
                po_format = format_red
            else:
                po_format = num_fmt

            # Write Dead Cells
            ws_matrix.write(row_cursor, col_idx, demand, num_fmt)
            ws_matrix.write(row_cursor + 1, col_idx, 0, num_fmt)
            ws_matrix.write(row_cursor + 2, col_idx, planned_order, po_format)
            ws_matrix.write(row_cursor + 3, col_idx, ending_inv, num_fmt)

        row_cursor += 5

    # ========================================================
    # TAB 3: 90-DAY ACTION PLAN (Vertical Database)
    # ========================================================
    action_cols = ["SKU_ID", "Date_Index", "Planned_Releases", "Capital_Required"]
    df_action_plan[action_cols].to_excel(writer, sheet_name="90-Day_Action_Plan", index=False)

    writer.close()
    print(f"✅ Absolute System of Record successfully saved.")
    finalize_sor_google_exports("alpha", excel_path)


def build_beta_shadow_ledger(df_beta, skus, calendar_array, mutated_constraints, payload, filename=None):
    if filename is None:
        filename = str(sor_excel_path("beta"))
    excel_path = Path(filename)
    excel_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Executing Blueprint 18: Compiling Pure Python Beta Shadow Ledger: {filename}")

    # 1. Execute Pre-Processors
    agg_capital, health_grade, dead_stock = calculate_beta_health(df_beta)
    chaos_map = build_chaos_map(payload, calendar_array)
    df_action_plan = df_beta[(df_beta["Planned_Releases"] > 0) & (df_beta.groupby("SKU_ID").cumcount() < 3)]

    # 2. Initialize Excel Writer
    writer = pd.ExcelWriter(filename, engine='xlsxwriter', datetime_format='mmm-yy')
    workbook = writer.book

    # 3. UI Formats
    header_fmt = workbook.add_format({'bold': True, 'bg_color': '#2C3E50', 'font_color': 'white', 'align': 'center'})
    date_fmt = workbook.add_format({'num_format': 'mmm-yy', 'bold': True, 'bg_color': '#34495E', 'font_color': 'white', 'align': 'center'})
    label_fmt = workbook.add_format({'bold': True, 'align': 'right', 'valign': 'vcenter'})
    money_fmt = workbook.add_format({'num_format': '$#,##0', 'align': 'left'})
    percent_fmt = workbook.add_format({'num_format': '0.0%', 'align': 'left'})
    num_fmt = workbook.add_format({'num_format': '#,##0', 'align': 'center'})

    # THE TRI-COLOR PALETTE
    format_red = workbook.add_format({'bg_color': '#E74C3C', 'font_color': 'white', 'bold': True, 'num_format': '#,##0', 'align': 'center'})
    format_orange = workbook.add_format({'bg_color': '#F39C12', 'font_color': 'black', 'bold': True, 'num_format': '#,##0', 'align': 'center'})
    format_blue = workbook.add_format({'bg_color': '#87CEEB', 'font_color': 'black', 'bold': True, 'num_format': '#,##0', 'align': 'center'})

    # ========================================================
    # TAB 1: EXECUTIVE SUMMARY (The Static Front Page)
    # ========================================================
    ws_exec = workbook.add_worksheet("Executive_Summary")
    ws_exec.hide_gridlines(2)
    ws_exec.set_column('A:A', 35)
    ws_exec.set_column('B:B', 20)

    title_fmt = workbook.add_format({'bold': True, 'font_size': 16, 'font_color': '#2C3E50', 'bottom': 2})
    ws_exec.write("A1", "Beta Brain: Day X System of Record (Mutated)", title_fmt)

    ws_exec.write("A3", "Aggregate Capital Commitment (PO Value):", label_fmt)
    ws_exec.write("B3", agg_capital, money_fmt)
    ws_exec.write("A4", "Inventory Health Grade (Active vs Dead):", label_fmt)
    ws_exec.write("B4", health_grade, percent_fmt)
    ws_exec.write("A5", "Total Dead Stock Risk Exposure:", label_fmt)
    ws_exec.write("B5", dead_stock, money_fmt)

    # ========================================================
    # TAB 2: THE HORIZONTAL PIVOT ENGINE
    # ========================================================
    ws_matrix = workbook.add_worksheet("Beta_Reality")
    ws_matrix.set_column('A:A', 15)
    ws_matrix.set_column('B:B', 22, label_fmt)
    ws_matrix.set_column('C:Z', 12, num_fmt)
    ws_matrix.freeze_panes(1, 2)

    ws_matrix.write(0, 0, "SKU_ID", header_fmt)
    ws_matrix.write(0, 1, "Metric", header_fmt)

    for i, date_str in enumerate(calendar_array):
        dt_obj = datetime.strptime(date_str, "%Y-%m")
        ws_matrix.write_datetime(0, i + 2, dt_obj, date_fmt)

    # The Pivot Loop
    row_cursor = 1
    for sku in skus:
        df_sku = df_beta[df_beta['SKU_ID'] == sku].reset_index(drop=True)

        # Pull MUTATED constraints
        sku_lt = mutated_constraints[sku]['LT']
        sku_max_cap = mutated_constraints[sku]['Max_Cap']

        ws_matrix.write(row_cursor, 0, sku, workbook.add_format({'bold': True}))
        ws_matrix.write(row_cursor, 1, "Demand")
        ws_matrix.write(row_cursor + 1, 1, "Scheduled Receipts")
        ws_matrix.write(row_cursor + 2, 1, "Planned Releases (POs)")
        ws_matrix.write(row_cursor + 3, 1, "Ending Inventory")

        for index, row in df_sku.iterrows():
            col_idx = index + 2
            demand = row['Demand']
            planned_order = row['Planned_Releases']
            ending_inv = row['Locked_Inv']

            # MODULE 3: THE TRI-COLOR LOGIC GATE (Evaluated strictly in Python RAM)

            # Check 1: Human Override (Demand Shift)
            if (sku, index) in chaos_map:
                dem_format = format_blue
            else:
                dem_format = num_fmt

            # Check 2 & 3: System Physics Breaches (POs)
            if planned_order > sku_max_cap:
                po_format = format_orange
            elif planned_order > 0 and (index + 1) <= sku_lt:
                po_format = format_red
            else:
                po_format = num_fmt

            # Write the Dead Cells with dynamically chosen formats
            ws_matrix.write(row_cursor, col_idx, demand, dem_format)          # Sky Blue if Mutated
            ws_matrix.write(row_cursor + 1, col_idx, 0, num_fmt)
            ws_matrix.write(row_cursor + 2, col_idx, planned_order, po_format)# Red/Orange if Breached
            ws_matrix.write(row_cursor + 3, col_idx, ending_inv, num_fmt)

        row_cursor += 5

    # ========================================================
    # TAB 3: 90-DAY ACTION PLAN (The Beta Hit List)
    # ========================================================
    action_cols = ["SKU_ID", "Date_Index", "Planned_Releases", "Capital_Required"]
    df_action_plan[action_cols].to_excel(writer, sheet_name="90-Day_Action_Plan", index=False)

    writer.close()
    print(f"✅ Beta System of Record successfully saved.")
    finalize_sor_google_exports("beta", excel_path)


def build_delta_shadow_ledger(df_alpha, df_beta, skus, calendar_array, master_data, filename=None):
    """
    MODULE 3: The Deliverable Architecture
    Compiles the 5-Tab Master Audit File.
    """
    if filename is None:
        filename = str(sor_excel_path("delta"))
    excel_path = Path(filename)
    excel_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"\nExecuting Blueprint 19: Compiling Delta Shadow Ledger: {filename}")

    # 1. Run Pre-Processors
    df_join, df_exceptions, alpha_spend, beta_spend, net_impact = calculate_delta_math(df_alpha, df_beta, master_data)
    df_campaigns = compress_to_campaigns(df_exceptions)

    # 2. Initialize Excel Writer
    writer = pd.ExcelWriter(filename, engine='xlsxwriter', datetime_format='mmm-yy')
    workbook = writer.book

    # 3. UI Formats
    header_fmt = workbook.add_format({'bold': True, 'bg_color': '#2C3E50', 'font_color': 'white', 'align': 'center'})
    date_fmt = workbook.add_format({'num_format': 'mmm-yy', 'bold': True, 'bg_color': '#34495E', 'font_color': 'white', 'align': 'center'})
    label_fmt = workbook.add_format({'bold': True, 'align': 'right', 'valign': 'vcenter'})
    metric_fmt = workbook.add_format({'bold': True, 'align': 'right'})
    money_fmt = workbook.add_format({'num_format': '$#,##0', 'align': 'left'})
    num_fmt = workbook.add_format({'num_format': '#,##0', 'align': 'center'})
    money_center_fmt = workbook.add_format({'num_format': '$#,##0', 'align': 'center'})

    # Strict Python Formatting (Red/Green Logic)
    format_red_num = workbook.add_format({'bg_color': '#FADBD8', 'font_color': '#900C3F', 'bold': True, 'num_format': '#,##0', 'align': 'center'})
    format_green_num = workbook.add_format({'bg_color': '#D5F5E3', 'font_color': '#1E8449', 'bold': True, 'num_format': '#,##0', 'align': 'center'})
    format_red_money = workbook.add_format({'bg_color': '#FADBD8', 'font_color': '#900C3F', 'bold': True, 'num_format': '$#,##0', 'align': 'center'})
    format_green_money = workbook.add_format({'bg_color': '#D5F5E3', 'font_color': '#1E8449', 'bold': True, 'num_format': '$#,##0', 'align': 'center'})

    # ========================================================
    # TAB 1: EXECUTIVE SUMMARY
    # ========================================================
    ws_exec = workbook.add_worksheet("1_Executive_Summary")
    ws_exec.hide_gridlines(2)
    ws_exec.set_column('A:A', 30)
    ws_exec.set_column('B:B', 20)

    title_fmt = workbook.add_format({'bold': True, 'font_size': 16, 'font_color': '#2C3E50', 'bottom': 2})
    ws_exec.write("A1", "Delta Brain: System-Wide Financial Audit", title_fmt)

    ws_exec.write("A3", "Total Baseline Spend (Day 0):", label_fmt)
    ws_exec.write("B3", alpha_spend, money_fmt)
    ws_exec.write("A4", "Total Mutated Spend (Day X):", label_fmt)
    ws_exec.write("B4", beta_spend, money_fmt)

    # Color-coded impact
    impact_fmt = format_red_money if net_impact > 0 else format_green_money
    if net_impact == 0: impact_fmt = money_fmt
    ws_exec.write("A5", "NET CAPITAL IMPACT:", workbook.add_format({'bold': True, 'align': 'right'}))
    ws_exec.write("B5", net_impact, impact_fmt)

    # ========================================================
    # TAB 2: S&OP VARIANCE GRID (The Horizontal Pivot)
    # ========================================================
    ws_matrix = workbook.add_worksheet("2_S&OP_Variance_Grid")
    ws_matrix.set_column('A:A', 15)
    ws_matrix.set_column('B:B', 22, label_fmt)
    ws_matrix.set_column('C:Z', 12)
    ws_matrix.freeze_panes(1, 2)

    ws_matrix.write(0, 0, "SKU_ID", header_fmt)
    ws_matrix.write(0, 1, "Metric", header_fmt)

    for i, date_str in enumerate(calendar_array):
        dt_obj = datetime.strptime(date_str, "%Y-%m")
        ws_matrix.write_datetime(0, i + 2, dt_obj, date_fmt)

    row_cursor = 1
    for sku in skus:
        df_sku = df_join[df_join['SKU_ID'] == sku].reset_index(drop=True)
        unit_cost = master_data[sku]["Unit_Cost"]

        ws_matrix.write(row_cursor, 0, sku, workbook.add_format({'bold': True}))

        # Block Labels
        labels = [
            "Alpha Orders (Day 0)", "Beta Orders (Day X)", "ACTION DELTA",
            "Alpha Ending Inv.", "Beta Ending Inv.", "UNIT VARIANCE",
            "Alpha Spend ($)", "Beta Spend ($)", "NET CAPITAL IMPACT"
        ]
        for idx, label in enumerate(labels):
            ws_matrix.write(row_cursor + idx, 1, label, metric_fmt)

        # Unspool the Dead Cells
        for index, row in df_sku.iterrows():
            col_idx = index + 2

            # 1. Orders
            a_ord = row['Planned_Releases_Alpha']
            b_ord = row['Planned_Releases_Beta']
            act_delta = row['Action_Delta']

            act_fmt = format_red_num if act_delta > 0 else format_green_num if act_delta < 0 else num_fmt

            ws_matrix.write(row_cursor, col_idx, a_ord, num_fmt)
            ws_matrix.write(row_cursor + 1, col_idx, b_ord, num_fmt)
            ws_matrix.write(row_cursor + 2, col_idx, act_delta, act_fmt) # Colored via Python

            # 2. Physics (Inventory)
            a_inv = row['Locked_Inv_Alpha']
            b_inv = row['Locked_Inv_Beta']
            inv_var = row['Inventory_Variance']

            ws_matrix.write(row_cursor + 3, col_idx, a_inv, num_fmt)
            ws_matrix.write(row_cursor + 4, col_idx, b_inv, num_fmt)
            ws_matrix.write(row_cursor + 5, col_idx, inv_var, num_fmt)

            # 3. Finance
            ws_matrix.write(row_cursor + 6, col_idx, a_ord * unit_cost, money_center_fmt)
            ws_matrix.write(row_cursor + 7, col_idx, b_ord * unit_cost, money_center_fmt)

            cap_var = act_delta * unit_cost
            cap_fmt = format_red_money if cap_var > 0 else format_green_money if cap_var < 0 else money_center_fmt
            ws_matrix.write(row_cursor + 8, col_idx, cap_var, cap_fmt) # Colored via Python

        row_cursor += 10 # Spacer between SKUs

    # ========================================================
    # TAB 3: ACTION CAMPAIGNS (The Hit List)
    # ========================================================
    if not df_campaigns.empty:
        df_campaigns.to_excel(writer, sheet_name='3_Action_Campaigns', index=False)
        ws_camp = writer.sheets['3_Action_Campaigns']
        ws_camp.set_column('A:H', 18)
        ws_camp.set_column('G:G', 18, money_fmt) # Format Capital column

    # ========================================================
    # TAB 4: VISUAL DASHBOARDS (Presentation Images)
    # ========================================================
    ws_dash = workbook.add_worksheet("4_Visual_Dashboards")
    ws_dash.hide_gridlines(2)
    ws_dash.write("A1", "Delta Variance Visualizations", title_fmt)

    image_row = 2
    for sku in skus:
        img_path = dashboard_path("delta", sku)
        if img_path.exists():
            ws_dash.write(image_row, 0, f"System Physics Map: {sku}", workbook.add_format({'bold': True, 'font_size': 14}))
            ws_dash.insert_image(image_row + 1, 0, str(img_path), {'x_scale': 0.7, 'y_scale': 0.7})
            image_row += 45 # Space images out so they don't overlap
        else:
            ws_dash.write(image_row, 0, f"(Run Blueprint 11.2 first to generate PNG for {sku})")
            image_row += 2

    # ========================================================
    # TAB 5: ERP MASTER DATA (The Mutated Foundation)
    # ========================================================
    df_master = pd.DataFrame.from_dict(master_data, orient='index').reset_index().rename(columns={'index': 'SKU_ID'})
    df_master.to_excel(writer, sheet_name='5_ERP_Master_Data', index=False)

    writer.close()
    print(f"✅ Absolute Delta System of Record successfully saved.")
    finalize_sor_google_exports("delta", excel_path, skus=skus)

