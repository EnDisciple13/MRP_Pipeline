<!-- MIRROR: auto-synced from notes/projects/mrp/supply-planning/MRP_V2_Roadmap.md - do not edit directly. Edit the canonical file in the notes repo and run scripts/sync_project_docs.py -->

# MRP V2 Roadmap

Project strategy for the next evolution of the MRP engine: from single-echelon deterministic baseline to stochastic, multi-echelon supply planning with cost optimization.

## Related Notes

- [MRP_State_Machine_Architecture.md](MRP_State_Machine_Architecture.md) — sequential state-machine foundation.
- [Two_Dials_Framework.md](Two_Dials_Framework.md) — macro/micro objective decoupling and peace/war workflow.
- [Supply_Planning_Tool_Roadmap.md](Supply_Planning_Tool_Roadmap.md) — phased Python tool build order.
- [../../../math/Math_Safety_Stock_Derivation.md](../../../Notes/math/Math_Safety_Stock_Derivation.md) — dynamic SS/ROP derivation (reference, do not duplicate).
- [../../../math/Math_Supply_Planning_OR_Lexicon.md](../../../Notes/math/Math_Supply_Planning_OR_Lexicon.md) — OR lexicon and MILP objective.

---

Here is the master reference architecture for the next evolution of your MRP engine.  
This document bridges the gap between your single-echelon, deterministic baseline and the stochastic, multi-echelon reality required by the Stryker Job Description. It is structured to act as your technical blueprint for building localized simulation tools.

### **The Global Mathematical Lexicon**

To ensure the engine remains cohesive, all formulas below utilize this unified notation:

* **$t$**: The current time period (month index).  
* **$D\_t$**: Independent Demand (Forecasted customer orders for Finished Goods).  
* **$D\_{dep, t}$**: Dependent Demand (Calculated requirement for raw materials/components).  
* **$I\_t$**: Locked On-Hand Inventory at the end of period $t$.  
* **$SR\_t$**: Scheduled Receipts (Legally binding, in-transit POs).  
* **$PR\_t$**: Planned Receipts (Units required to arrive at the dock in period $t$).  
* **$POR\_t$**: Planned Order Release (The exact period the human buyer must execute the order).  
* **$LT$**: Supplier Lead Time.

### **1\. Multi-Echelon Planning (The Bill of Materials)**

**JD Requirement:** *"Support the development of a Master Resource Plan... ensuring finished goods, raw materials, and components are planned out up to 24 months."*  
**The Missing Concept:** Your current engine calculates 7 isolated SKUs. In reality, SKUs are hierarchically linked. You must build an engine that calculates Finished Goods (Level 0), locks that timeline, and then passes the resulting required actions downward to the Raw Materials (Level 1).  
**The MRP Engine Math:**  
The demand for a raw material ($D\_{dep, t}$) is strictly dictated by the *Release Date* ($POR$) of its parent Finished Good (FG), multiplied by the Quantity Per Assembly ($Q\_c$).

1. **Calculate the FG Execution Date:**  
2. $$POR\_{FG, t-LT\_{FG}} \= PR\_{FG, t}$$  
3. **The Matrix Explosion (Gozinto Translation):** The execution date of the parent becomes the demand date for the child. If you must begin building the drill in Month 3, you need the battery in Month 3\.  
4. $$D\_{dep, t} \= POR\_{FG, t} \\times Q\_{c}$$

**The Interrelation:** This transforms your engine from a linear loop into a **recursive loop**. The engine cannot evaluate the constraints of the battery until the mathematical timeline of the surgical drill is absolutely locked. If a capacity bottleneck pushes the drill's $POR$ forward, the battery's $D\_{dep}$ must dynamically shift with it.

### **2\. Dynamic Target Inventory & Stochastic Variability**

**JD Requirement:** *"Work with the Supply Planning Manager to set appropriate inventory levels based on demand variability and lead times."*  
**The Missing Concept:** Your engine uses a static SS (Safety Stock) master rule. A true MRP engine calculates a dynamic Total Target Inventory ($TTI$) vector that expands and contracts based on historical volatility.  
**The MRP Engine Math:**  
You must calculate the standard deviation of historical demand ($\\sigma\_D$) and apply a Z-score ($Z$) representing the desired Service Level (e.g., 95% \= 1.645).

1. **Dynamic Safety Stock Vector:**  
2. $$SS\_t \= Z \\times \\sqrt{LT} \\times \\sigma\_D$$  
3. **Total Target Inventory (The New Floor):**  
4. The engine must hold enough stock to survive variability ($SS\_t$) PLUS the average units consumed between shipments (Cycle Stock, which is exactly $\\frac{MOQ}{2}$).  
5. $$TTI\_t \= SS\_t \+ \\frac{MOQ}{2}$$  
6. **The Unhealed Balance Recalculation:**  
7. Your original engine triggered an order when $I\_t \< SS$. The new engine calculates a continuous Net Requirement ($NR\_t$):  
8. $$NR\_t \= \\max(0, D\_t \+ TTI\_t \- I\_{t-1} \- SR\_t)$$

**The Interrelation:** This directly impacts your **Financial Scorecard**. Because $TTI\_t$ fluctuates, the amount of Working Capital tied up ($Cap\_{hold} \= I\_t \\times Unit\\\_Cost$) is no longer a flat line; it breathes with the market. High-volatility SKUs will automatically hoard more cash.

### **3\. Capacity Underutilization & Multi-Node Constraints**

**JD Requirement:** *"Support capacity planning to identify constraints, risks, and underutilization, and recommend actions to address gaps..."*  
**The Missing Concept:** Your engine beautifully captures $Max\\\_Cap$ (overutilization). You must add $Min\\\_Cap$ (supplier contractual minimums) and $Max\\\_Vol$ (Warehouse Cubic Capacity).  
**The MRP Engine Math:**  
If the baseline math dictates ordering zero units this month, but the supplier contract requires a 50-unit minimum run rate to keep the factory line open, the engine must execute a "Pull-Forward" override.

1. **Underutilization Trap:**  
2. If $PR\_t \< Min\\\_Cap$, the engine must artificially inflate the receipt to satisfy the supplier.  
3. $$PR\_{adjusted, t} \= \\max(PR\_t, \\: Min\\\_Cap)$$  
4. **Spatial Warehouse Constraint:**  
5. Every unit has a physical volume ($v$). The sum of all locked inventory across *all* SKUs in the portfolio cannot exceed the warehouse pallet limit ($W\_{max}$).  
6. $$\\sum\_{all\\\_SKUs} (I\_t \\times v) \\le W\_{max}$$

**The Interrelation:** Fixing underutilization creates a deliberate conflict with Target Inventory ($TTI\_t$). By ordering $Min\\\_Cap$ when you don't mathematically need it, your ending inventory ($I\_t$) will spike above the $TTI\_t$ ceiling. The engine must flag this as an "Underutilization Cost Penalty"—you are spending unplanned capital to keep the supplier happy.

### **4\. Cost Inefficiencies & Price Break Optimization**

**JD Requirement:** *"...recommend actions to address gaps or cost inefficiencies."*  
**The Missing Concept:** Planners don't just balance units; they optimize for price. If an MOQ is 100 units at $10, but the supplier offers 500 units at $7, the engine must decide if the discount outweighs the cost of storing the extra 400 units.  
**The MRP Engine Math:**  
The engine uses a modified Economic Order Quantity (EOQ) logic to evaluate the Total Cost ($TC$) at different step-function price tiers. Let $H$ be the holding cost percentage (e.g., 10% of unit cost) and $S$ be the fixed cost to place an order.

1. **Total Cost Evaluation:**  
2. $$TC \= (Demand \\times Price) \+ \\left(\\frac{Demand}{PR\_t} \\times S\\right) \+ \\left(\\frac{PR\_t}{2} \\times H \\times Price\\right)$$  
3. **The Optimizer Gate:**  
4. The engine calculates $TC$ for the required $PR\_t$, and recalculates it for the supplier's bulk discount tier. If $TC\_{bulk} \< TC\_{required}$, the engine overrides the standard lot-sizing and forces the bulk order.

**The Interrelation:** This ties directly into the **Warehouse Constraint**. The engine might want to buy 500 units to save money, but it must pass the check: does the resulting volume ($\\sum I\_t \\times v$) breach $W\_{max}$? If yes, the engine rejects the discount.

### **5\. Plan Attainment & Root Cause Pegging**

**JD Requirement:** *"Monitor KPIs (plan attainment... back orders...) and identify root causes with recommendations for improvement."*  
**The Missing Concept:** The engine must measure physical execution against the mathematical theory, and trace failures backward through the supply chain hierarchy.  
**The MRP Engine Math:**

1. **Plan Attainment (The Reality Check):**  
2. $$PA\_t \= \\left( \\frac{Actual\\\_Receipts\_t}{PR\_{Alpha\\\_Baseline, t}} \\right) \\times 100$$  
3. **Root Cause Pegging (The Forensic Trace):**  
4. If $PA\_t \< 100\\%$ for a Finished Good, the engine does not stop there. It executes a programmatic search backward up the Gozinto Matrix.  
   * *Logic Check:* Look at $D\_{dep, t}$ for all Level 1 components linked to the FG.  
   * *Condition:* Find the specific component where $I\_t \< 0$ (a stockout).  
   * *Output:* The algorithm flags the specific raw material as the Root Cause of the Finished Good's failure.

**The Interrelation:** This completely closes the loop of the entire architecture. An exogenous shock (Blueprint 6 Chaos Injector) hits a raw material's lead time. The Multi-Echelon Matrix (Section 1\) mathematically forces the Finished Good to fail. The Plan Attainment metric (Section 5\) drops, and the Pegging Algorithm traces the financial Revenue at Risk exactly back to the delayed raw material, generating the JSON payload for the AI agent to write the supplier email.

# **Master Reference: The Supply Chain Optimization Engine**

## **1\. The Objective Function (What We Are Minimizing)**

In practice, addressing "cost inefficiencies" means writing an algorithm to find the lowest possible Total Cost ($Z$) across the entire 24-month horizon. The engine evaluates every decision by summing these five competing financial variables.

**The Master Equation:**

$$\\text{Minimize } Z \= \\sum\_{t=1}^{T} \\left\[ C\_{hold, t} \+ C\_{setup, t} \+ C\_{material, t} \+ C\_{shortage, t} \+ C\_{underutil, t} \\right\]$$

### **The Variable Breakdown & Math:**

**A. Holding Cost ($C\_{hold}$)**

* **What it is:** The cost of tying up capital in inventory, plus warehouse rent, insurance, and obsolescence risk.  
* **The Math:** $C\_{hold, t} \= I\_t \\times Unit\\\_Cost \\times h$  
  *(Where $I\_t$ is ending inventory and $h$ is the annual holding rate percentage, e.g., 0.15).*  
* **Engine Pressure:** Pushes the engine to order as little as possible, driving inventory toward zero.

**B. Setup / Ordering Cost ($C\_{setup}$)**

* **What it is:** The fixed financial penalty of executing a purchase order or forcing a factory to switch its assembly line.  
* **The Math:** $C\_{setup, t} \= S \\times Y\_t$  
  *(Where $S$ is the fixed setup cost, and $Y\_t$ is a binary variable \[0 or 1\] indicating if an order $PR\_t$ was placed).*  
* **Engine Pressure:** Pushes the engine to order massive, infrequent bulk batches to avoid paying the fixed fee multiple times.

**C. Material Cost & Price Breaks ($C\_{material}$)**

* **What it is:** The actual cost of the units, accounting for step-function volume discounts.  
* **The Math:** $C\_{material, t} \= PR\_t \\times P(PR\_t)$  
  *(Where $P(PR\_t)$ is a step-function returning a cheaper price if $PR\_t$ crosses a threshold).*  
* **Engine Pressure:** Pushes the engine to artificially inflate order quantities just enough to trigger the next price discount.

**D. Shortage & Risk Penalty ($C\_{shortage}$)**

* **What it is:** The financial cost of stocking out (Lost Revenue, expedited shipping fees, contractual penalties).  
* **The Math:** $C\_{shortage, t} \= \\max(0, \\: D\_t \- I\_t) \\times Penalty\\\_Rate$  
* **Engine Pressure:** Pushes the engine to hold high safety stock and order early to ensure zero missed sales.

**E. Supplier Underutilization Penalty ($C\_{underutil}$)**

* **What it is:** The cost of breaking a contract with a supplier who requires a minimum monthly order volume to keep their factory open for you.  
* **The Math:** $C\_{underutil, t} \= \\max(0, \\: Min\\\_Cap \- PR\_t) \\times Underutil\\\_Penalty$  
* **Engine Pressure:** Pushes the engine to order inventory even when the demand forecast mathematically says you do not need it.

## **2\. The Hard Constraints (The Rules of Reality)**

The engine wants to drive $Z$ to zero, but it is bounded by the physical laws of the supply chain. If an optimization path violates any of these inequalities, the MILP solver rejects the path.

1. **Inventory Balance Law:** $I\_t \= I\_{t-1} \+ SR\_t \+ PR\_t \- D\_t$  
2. **Supplier Maximum Capacity:** $PR\_t \\le Max\\\_Cap\_t$  
3. **Warehouse Volume Capacity:** $\\sum\_{all} (I\_t \\times v) \\le W\_{max}$ *(Where $v$ is unit volume)*  
4. **Non-Negativity Constraint:** $I\_t \\ge 0$ and $PR\_t \\ge 0$

## **3\. The Interrelationships (The Trade-Offs)**

When analyzing data to recommend actions (per the Stryker JD), you are constantly managing the tension between the variables in the objective function. Pulling one lever inevitably breaks another.

* **Underutilization vs. Holding Cost (JD Bullet 2):** If you order extra units to satisfy a supplier's minimum capacity requirement ($C\_{underutil}$ drops), your ending inventory spikes, driving up your Holding Cost ($C\_{hold}$) and risking a breach of your warehouse capacity limit ($W\_{max}$).  
* **Target Inventory vs. Setup Costs (JD Bullet 4):** If you set your dynamic Target Inventory too lean to save on Holding Cost, the system will execute tiny orders every single week, causing your fixed Setup Costs ($C\_{setup}$) to explode.  
* **Price Breaks vs. Obsolescence:** If you order 1,000 units instead of 200 to trigger a 20% price discount ($C\_{material}$ drops), you tie up cash. If that product enters a Phase-Out cycle before you sell the 1,000 units, you incur a massive write-off penalty.

## **4\. The Theory Behind MILP (Mixed-Integer Linear Programming)**

When asked how you calculate an efficient path to resolve these competing variables, you must explain why standard calculus fails and how an MILP solver navigates the math.

**Why Not Calculus?**

Calculus (like Gradient Descent) requires a continuous, smooth mathematical surface so you can find the derivative and follow the slope to the bottom. Supply chains are **discrete** and **discontinuous**.

* You cannot order 2.7 pallets (Integer constraint).  
* Price breaks happen instantly at unit 500 (Discontinuous step-function).  
* Because the mathematical surface is full of jagged cliffs and dead ends, a standard gradient calculation becomes undefined or gets permanently trapped in a false local minimum.

**How MILP Solves It:**

Instead of brute-forcing millions of combinations, MILP uses geometric boundaries and tree logic:

1. **Continuous Relaxation (The Simplex Method):** The solver temporarily removes the integer rules (pretending you *can* order 2.7 pallets). This turns the problem into a smooth, multi-dimensional geometric shape called a convex polytope. The algorithm glides along the outer vertices of this shape to instantly find the mathematical minimum cost.  
   1. Note that this gliding cannot be done on a lattice of points, and hence we introduce edges.  
2. **Branch and Bound:** Once it finds the relaxed minimum (e.g., 2.7 pallets), it branches the universe into two physical realities: one where you order $\\le 2$ pallets, and one where you order $\\ge 3$ pallets.  
3. **Pruning the Tree:** It evaluates these branches. If the math proves that the $\\le 2$ branch immediately violates the Shortage Penalty, the algorithm "prunes" (deletes) that entire branch of the decision tree without testing the thousands of sub-combinations inside it. It zeroes in on the absolute lowest integer cost purely through the process of elimination.
