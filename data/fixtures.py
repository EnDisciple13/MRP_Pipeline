"""Static master data, inventory, demand, and chaos scenario payloads."""

CONSTRAINTS = {
    "SKU_001": {"LT": 1, "SS": 20, "MOQ": 1,  "Max_Cap": 40,  "Unit_Cost": 50.00,  "Unit_Revenue": 200.00,  "Status": "Active"},
    "SKU_002": {"LT": 2, "SS": 10, "MOQ": 1,  "Max_Cap": 80,  "Unit_Cost": 120.00, "Unit_Revenue": 500.00,  "Status": "Active"},
    "SKU_003": {"LT": 1, "SS": 20, "MOQ": 10, "Max_Cap": 100, "Unit_Cost": 15.00,  "Unit_Revenue": 150.00,  "Status": "Active"},
    "SKU_004": {"LT": 1, "SS": 0,  "MOQ": 1,  "Max_Cap": 30,  "Unit_Cost": 10.00,  "Unit_Revenue": 50.00,   "Status": "Phasing_Out"},
    "SKU_005": {"LT": 1, "SS": 5,  "MOQ": 50, "Max_Cap": 150, "Unit_Cost": 5.00,   "Unit_Revenue": 35.00,   "Status": "Active"},
    "SKU_006": {"LT": 2, "SS": 20, "MOQ": 1,  "Max_Cap": 200, "Unit_Cost": 75.00,  "Unit_Revenue": 300.00,  "Status": "Phasing_In"},
    "SKU_007": {"LT": 1, "SS": 50, "MOQ": 1,  "Max_Cap": 300, "Unit_Cost": 200.00, "Unit_Revenue": 1200.00, "Status": "Active"},
}

INVENTORY = {
    "SKU_001": {"On_Hand": 100, "Open_PO": 0,  "PO_Month_Index": 0},
    "SKU_002": {"On_Hand": 10,  "Open_PO": 50, "PO_Month_Index": 3},
    "SKU_003": {"On_Hand": 50,  "Open_PO": 0,  "PO_Month_Index": 0},
    "SKU_004": {"On_Hand": 150, "Open_PO": 0,  "PO_Month_Index": 0},
    "SKU_005": {"On_Hand": 0,   "Open_PO": 0,  "PO_Month_Index": 0},
    "SKU_006": {"On_Hand": 0,   "Open_PO": 0,  "PO_Month_Index": 0},
    "SKU_007": {"On_Hand": 20,  "Open_PO": 0,  "PO_Month_Index": 0},
}

DEMAND = {
    "SKU_001": [10] * 24,
    "SKU_002": [20] * 24,
    "SKU_003": ([10] * 6) + [500] + ([10] * 17),
    "SKU_004": ([5] * 6) + [0] * 18,
    "SKU_005": [12] * 24,
    "SKU_006": ([0] * 3) + [50] * 21,
    "SKU_007": ([20] * 6) + [1000] + ([20] * 6) + [1000] + ([20] * 10),
}

CHAOS_PAYLOAD = [
    {"SKU_ID": "SKU_001", "Mutation_Type": "Longitudinal_Demand_Shift", "Target_Date": "2026-08", "Magnitude": -15},
    {"SKU_ID": "SKU_001", "Mutation_Type": "Longitudinal_Demand_Shift", "Target_Date": "2026-12", "Magnitude": 45},
    {"SKU_ID": "SKU_002", "Mutation_Type": "Longitudinal_Demand_Shift", "Target_Date": "2026-09", "Magnitude": 15},
    {"SKU_ID": "SKU_003", "Mutation_Type": "Demand_Shock", "Target_Date": "2026-10", "Magnitude": 500},
    {"SKU_ID": "SKU_003", "Mutation_Type": "Supply_Delay", "Target_Date": "2026-09", "Magnitude": 1},
    {"SKU_ID": "SKU_007", "Mutation_Type": "Constraint", "Target_Variable": "Max_Cap", "Magnitude": 150},
    {"SKU_ID": "SKU_007", "Mutation_Type": "Longitudinal_Demand_Shift", "Target_Date": "2026-07", "Magnitude": -20},
    {"SKU_ID": "SKU_007", "Mutation_Type": "Longitudinal_Demand_Shift", "Target_Date": "2027-07", "Magnitude": 50},
    {"SKU_ID": "SKU_006", "Mutation_Type": "Constraint", "Target_Variable": "LT", "Magnitude": 4},
    {"SKU_ID": "SKU_005", "Mutation_Type": "Zombie", "Target_Date": "2027-01"},
]
