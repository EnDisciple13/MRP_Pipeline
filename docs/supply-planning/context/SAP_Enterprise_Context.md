<!-- MIRROR: auto-synced from notes/projects/mrp/supply-planning/context/SAP_Enterprise_Context.md - do not edit directly. Edit the canonical file in the notes repo and run scripts/sync_project_docs.py -->

---
id: projects-mrp-supply-planning-context-SAP_Enterprise_Context
type: context
status: draft
dependencies:
  - projects/mrp/supply-planning/frameworks/Two_Dials_Framework.md
tags: []
invariants: []
---
# SAP Enterprise Context

Enterprise instantiation of [Two_Dials_Framework.md](../frameworks/Two_Dials_Framework.md) — SAP IBP/PP/MM as the global dictator in the peace/war closed loop. Reference mapping between enterprise modules and the local MRP simulator architecture.

## Related Notes

- [../architecture/MRP_State_Machine_Architecture.md](../architecture/MRP_State_Machine_Architecture.md) — local sequential MRP engine.
- [../frameworks/Two_Dials_Framework.md](../frameworks/Two_Dials_Framework.md) — canonical closed-loop framework (global SAP vs local Python).
- [../roadmaps/MRP_V2_Roadmap.md](../roadmaps/MRP_V2_Roadmap.md) — V2 feature gaps vs enterprise systems.

---

## **The Closed-Loop Enterprise Ecosystem**

In an enterprise environment like Stryker, **SAP IBP**, **SAP PP**, and **SAP MM** do not operate as independent software packages. They are structurally bound modules inside a single unified database. A single data entry or constraint mutation in one module automatically ripples through the entire stack.

To demonstrate mastery to a hiring manager, you must visualize this lifecycle as a continuous wheel: **Macro-Strategy (IBP) $\\rightarrow$ Algorithmic Parsing (PP) $\\rightarrow$ Physical Execution (MM) $\\rightarrow$ Analytical Feedback (IBP).**

## **1\. The Unified Data Architecture**

Before tracing operational chaos, we must map how the master tables relate to each other relational-style.

  \[ SAP IBP: Cloud Canvas \]  
     │  (Forecasts / Scenarios / S\&OP)  
     ▼  
   \[ SAP PP: Production Planning \]  
     │  (MRP Runs / BOM Explosions / Lead-Time Scheduling)  
     ▼  
   \[ SAP MM: Materials Management \]  
        (Purchase Info Records / Open POs / Warehouse Goods Movements)

| Operational Layer | Core Business Purpose | SAP Module | Your Simulator Parallel |
| :---- | :---- | :---- | :---- |
| **The Long-Term Forecast** | Establishes the 24-month horizon pull; handles "What-If" market scenarios. | **SAP IBP** (Demand & S\&OP) | DEMAND array payload & Phase 2 Chaos Scenarios. |
| **The Scheduling Logic** | Executes sequential chronological balancing and backward scheduling rules. | **SAP PP** (MRP / Net Requirements) | [SP_RM_Phase1](../../../../Notes/projects/mrp/blueprints/SP_RM_Phase1.md) — Sandbox MRP / sequential state machine. |
| **The Master Constraints** | Stores localized vendor capabilities, lead times, lot-sizing, and pricing tiers. | **SAP MM** (Material Master / Purchase Info Record) | dict\_master\_data schema. |
| **The Transaction Ledger** | Manages live warehouse on-hand stock and legally binding receipts on the water. | **SAP MM** (Inventory / Purchasing) | dict\_initial\_state & Lead-Time Fence arrays. |
| **The Exception Monitor** | Isolates variances, calculates financial risk, and rollups actions into campaigns. | **SAP IBP** (Control Tower) | [SP_RM_Phase3](../../../../Notes/projects/mrp/blueprints/SP_RM_Phase3.md) — Micro MILP comparative delta engine (Alpha/Beta/Delta architecture per [MRP_State_Machine_Architecture.md](../architecture/MRP_State_Machine_Architecture.md)). |

## **2\. The Multi-Tier Ripple Effect (Operational Scenarios)**

To understand how these modules link, let’s follow two real-world supply chain crises from start to finish.

### **Scenario A: The Macro Demand Surge (The SKU\_003 / SKU\_007 Blast)**

Imagine Stryker's sales team signs a major hospital network contract, introducing a sudden **500-unit demand spike in Month 7**.

\[IBP Demand Revision\] ──► \[PP Net Requirements Run\] ──► \[MM Capacity & Lot Validation\] ──► \[IBP Control Tower Escalation\]

1. **Initiation (SAP IBP):** The forecast change is entered in the cloud. IBP updates the **Planned Independent Requirements (PIR)** for Month 7\. This acts exactly like your Phase 2 Chaos Injector overwriting the demand vector.  
2. **Algorithmic Parsing (SAP PP):** The overnight batch job triggers a **Net Requirements Calculation**. The engine processes time linearly, tracking the unconstrained inventory position via the standard state formula:  
    $$B\_t \= I\_{t-1} \+ SR\_t \- D\_t$$  
    When it hits Month 7, the 500-unit demand shock causes $B\_t$ to breach the Safety Stock ($SS$) floor.  
3. **Lot Sizing & Scheduling (SAP PP $\\rightarrow$ SAP MM):** To heal the breach, the PP engine queries the **SAP MM Purchase Info Record** to find the procurement rules. It reads the supplier's **Minimum Order Quantity (MOQ)** and applies integer step-function logic to round up the required receipt ($PR\_t$):  
    $$PR\_t \= \\left\\lceil \\frac{SS \- B\_t}{MOQ} \\right\\rceil \\times MOQ$$  
    The PP engine then subtracts the Lead Time (LT) from Month 7 to calculate the exact month the purchase order must be cut (**Backward Scheduling**).  
4. **The Constraint Collision (SAP MM $\\rightarrow$ SAP PP):** The calculated order volume hits a wall. The PP engine checks the volume against the **Maximum Supplier Capacity** stored in MM. If the required order is 600 units but the vendor's maximum monthly capacity is hard-capped at 300, the unconstrained plan violates physical reality.  
5. **Executive Rollup (SAP IBP Control Tower):** Because PP cannot solve a capacity breach automatically, it leaves the inventory deficit in the matrix, locks the unhealed state, and routes an **Intelligent Alert** up to the **IBP Control Tower**.  
   * Your **Phase 3 Comparative Delta Engine** mirrors this perfectly. It uses a relational inner join to drop the balanced noise, maps the unit shortage back to the master data, and outputs a strict dollar-valued **Revenue at Risk** metric for executive review.

### **Scenario B: The Supply Chain Bottleneck (The Boat is Late)**

A cargo ship carrying raw titanium components is delayed at sea, pushing an expected **Month 2 arrival out to Month 3**.

\[MM Warehouse Event\] ──► \[PP Time Fence Reconciliation\] ──► \[PP Core Matrix Re-Run\] ──► \[MM PR Generation / Human Action\]

1. **Transaction Event (SAP MM):** The supplier transmits an updated shipping notification. The delivery date on the **Open Purchase Order** is updated in MM.  
2. **Time Fence Reconciliation (SAP PP):** When the MRP engine runs, it evaluates the modified timeline against the **Lead Time Fence**. Because this PO falls inside the physical lead-time boundary, it is treated as an immutable **Firmed Scheduled Receipt**. The system recognizes that it cannot magically generate a brand-new replacement order to arrive tomorrow, because time travel is impossible.  
3. **The Deficit Ripple (SAP PP):** The engine re-runs the 4-step execution loop using the shifted data. Because the inventory arrival vanished from Month 2, the ending inventory position drops below the Safety Stock floor, creating an immediate stockout risk in Month 2\.  
4. **The Exception Generation (SAP PP $\\rightarrow$ SAP MM):** Because the engine cannot reverse the delay, its backward scheduling logic looks at the Month 2 shortage, subtracts the lead time, and realizes the order should have been placed a month ago.  
   * In SAP, this triggers an **Exception Message 10 (Bring process forward / Expedite)**.  
   * In your engine, this is tracked as a **"Magic Fix (Past Due)"** alert. The state machine logs the impossible date index, calculates the **Unplanned Capital Flow** required to resolve it, and drops the record into a targeted **90-Day Action Plan** tab for human expediting protocol.

## **3\. The Core Translation Guide**

When discussing system capabilities in an interview, use this matrix to seamlessly translate your codebase terminology into enterprise SAP standard vernacular.

### **💡 Technical Appendix: System Architecture Mapping**

* **Independent Demand Vectors** $\\longrightarrow$ **Planned Independent Requirements (PIR):** The forward-looking unconstrained market forecast driving the long-term horizon.  
* **dict\_initial\_state Table** $\\longrightarrow$ **MD04 Stock/Requirements List:** The canonical, live transactional ledger showing beginning stock, incoming supplier shipments, and outgoing requirements.  
* **Lot-Sizing Functions** $\\longrightarrow$ **Rounding Profiles & Lot Sizes:** The hard coded parameter constraints (like MOQ) that force fractional raw deficits into full pallet increments.  
* **Time Fence Matrix** $\\longrightarrow$ **Firming Logic / Planning Time Fence:** The physical boundary inside of which system automation is blinded, locking open PRs into static, contractually binding PO receipts.  
* **Heuristic Active Variance Filtering** $\\longrightarrow$ **IBP Control Tower Exception Aggregation:** The process of executing data-pruning inner joins to suppress routine balancing stock lines, exposing only the bleeding edges of capital exposure.

## **4\. Advanced Insights for System Growth (Your Slide 5 Arsenal)**

To cement your image as an elite analytical candidate during the technical gauntlet, be prepared to critique your own model. This proves you know exactly what an enterprise system requires to scale.

### **The Material Explosion (The BOM Extension)**

Your V1.0 pipeline treats every SKU as an independent finished item. In a true manufacturing plant like Stryker Flower Mound, demand for a finished orthopedic implant must trigger sub-assembly requirements.

* *The System Link:* To bridge this, a V2.0 engine must map an **SAP PP Bill of Materials (BOM)**. When independent demand hits a finished good, the engine runs a **BOM Explosion**, multiplying the finished requirement vector by the component breakdown scalars to dynamically populate the dependent demand arrays for raw materials.

### **Dynamic Variability (From Static Floors to Statistical Rails)**

Your current safety stock parameters are hardcoded static integers. In enterprise planning, a static floor fails if market volatility shifts.

* *The System Link:* To elevate capital efficiency, the engine should implement an **SAP IBP Inventory Optimization** model. This replaces static variables with dynamic statistical safety rails that recalculate every month based on the standard deviation of historical forecast errors and supplier lead-time variances:  
  $$SS \= Z \\times \\sqrt{(LT \\times \\sigma\_D^2) \+ (D^2 \\times \\sigma\_{LT}^2)}$$  
  *(Where $Z$ is the service level factor, $\\sigma\_D$ is demand variance, and $\\sigma\_{LT}$ is lead-time variance).*

### **The Live Sandbox (Live Formulas vs. Hardcoded Records)**

Your pipeline utilizes a dual-engine layout: an unalterable Python matrix for data compliance and an interactive Excel sheet with embedded active calculations.

* *The System Link:* This mirrors the divide between **Systems of Record (S/4HANA)** and **Planning Sandboxes (IBP Excel Add-in)**. True planners leverage active formulas (XLOOKUP, CEILING, OFFSET) to execute instantaneous local adjustments without threatening the immutable historical ledger stored in production RAM.
