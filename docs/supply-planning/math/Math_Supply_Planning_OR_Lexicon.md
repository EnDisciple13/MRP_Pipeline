<!-- MIRROR: auto-synced from notes/math/supply-planning/Math_Supply_Planning_OR_Lexicon.md - do not edit directly. Edit the canonical file in the notes repo and run scripts/sync_project_docs.py -->

---
id: math-supply-planning-or-lexicon
type: math_domain
status: draft
dependencies:
  - math/supply-planning/Math_Safety_Stock_Derivation.md
tags: []
invariants:
  - id: inventory-balance
    statement: "Inventory balance I_t = I_{t-1} + R_t - D_t holds for all periods t"
  - id: non-negative-controls
    statement: "Control variables receipts R_t and planned orders must be non-negative"
---
# Supply Planning OR Lexicon

Formal OR foundations shared across supply-planning projects. Bridges Operations Research vocabulary and supply chain terminology.

## Related Notes

- [Math_Safety_Stock_Derivation.md](Math_Safety_Stock_Derivation.md) — probability model for safety stock.
- [../../projects/mrp/supply-planning/architecture/MRP_State_Machine_Architecture.md](../architecture/MRP_State_Machine_Architecture.md) — sequential MRP engine architecture.
- [../../meta/OR_AI_ASI.md](../../../../Notes/meta/OR_AI_ASI.md) — OR pillars and agent roles.

---

## **Part 1: The Lexicon (OR vs. Supply Chain)**

To architect or debug an Enterprise Resource Planning (ERP) system, you must fluidly translate between the mathematical reality and the corporate terminology.

### **System Dynamics & Topology**

| Operations Research Concept | Supply Chain Terminology | Definition |
| :---- | :---- | :---- |
| **Directed Acyclic Graph (DAG)** | Bill of Materials (BOM) | The structural hierarchy of how components assemble into finished goods. |
| **Edge Weight** | Quantity Per | The exact number of child components required to build one parent item. |
| **Adjacency Matrix** ($B$) | Gozinto Matrix | The algebraic representation of the BOM, transposed so columns equal recipes. |
| **Time Horizon** ($T$) | Planning Horizon | The finite discrete timeline (e.g., 24 months) divided into distinct buckets (days/weeks). |
| **Lag Operator** ($L$) | Lead Time Offset | The time-vector shift required to move an action backward to its necessary start date. |

### **The State-Space Engine**

| Operations Research Concept | Supply Chain Terminology | Definition |
| :---- | :---- | :---- |
| **State Variable** ($x\_t$ or $I\_t$) | Projected Available Balance (PAB) | The verified inventory sitting on the shelf at the end of time $t$. |
| **Forcing Function** ($d\_t$ or $D\_t$) | Gross Requirements (Demand) | Independent external inputs (sales) or dependent internal inputs driving the system. |
| **Predetermined Input** ($s\_t$ or $S\_t$) | Scheduled Receipts | In-transit inventory mathematically guaranteed to arrive at time $t$. |
| **Control Variable** ($u\_t$ or $PR\_t$) | Planned Receipt | The algorithmic intervention injected at time $t$ to prevent a system failure. |
| **Feedback Law** | Netting Logic / MRP Run | The logic loop that evaluates the state and calculates the exact control variable. |

### **Optimization & Boundaries**

| Operations Research Concept | Supply Chain Terminology | Definition |
| :---- | :---- | :---- |
| **State Constraint** | Safety Stock ($SS$) | The rigid lower bound the state variable ($I\_t$) is never allowed to cross. |
| **Control Constraint** | MOQ / EOQ / Max Capacity | Physical or legal limitations on the size or timing of the control variable ($u\_t$). |
| **Objective Function** ($Z$) | Total Cost / S\&OP Strategy | The global equation balancing holding, setup, and shortage costs across the enterprise. |

## **Part 2: The Spatial Architecture (Matrix Explosion)**

Before moving through time, the system must evaluate space. It must translate independent market demand into dependent factory requirements using linear algebra.

**1\. The Independent Demand Vector ($D$)**

A column vector representing external market orders for finished goods (e.g., a hospital ordering surgical kits).

**2\. The Gozinto Matrix ($B$)**

A strictly lower triangular (nilpotent) matrix where element $b\_{ij}$ represents the quantity of item $i$ required to build one unit of item $j$.

**3\. The Master Production Schedule ($R$)**

The total requirements vector representing every sub-component and raw material needed across the entire enterprise. It is calculated using the Leontief Inverse:

$$R \= (I \- B)^{-1} D$$  
**4\. The Internal Consumption Matrix**

To find exactly what the factory floor consumes internally (excluding what is shipped out to the market):

$$\\text{Internal Consumption} \= BR$$

## **Part 3: The Temporal Engine (State & Control)**

This is the core physics engine of the daily supply chain. It operates as a discrete-time dynamical system governed by a Feedback Control Policy (specifically, a Bang-Bang Controller).

### Receipt notation

When the distinction between predetermined and algorithmic supply matters, decompose total receipts:

- **$R_t$** — total receipts (aggregate inflow at period $t$)
- **$S_t$** — scheduled receipts (predetermined; in-transit POs, firm arrivals)
- **$u_t$** / **$PR_t$** — planned receipts (control variable; MRP intervention)

**Identity:** $R_t = S_t + u_t$ when scheduled and planned receipts are tracked separately.

**When to use which form:**

- **Aggregate:** $I_t = I_{t-1} + R_t - D_t$ — sufficient when only total inflow matters.
- **Decomposed:** $I_t = I_{t-1} + S_t + u_t - D_t$ — required when netting logic must separate predetermined from controllable supply.

**1\. The State Transition Function (The Physics Equation)**

This equation describes the unconstrained evolution of the physical warehouse. It calculates what the inventory ($I\_t$) will be at the end of the day, given yesterday's memory, today's forcing functions, and today's controls.

$$I\_t \= I\_{t-1} \+ S\_t \+ u\_t \- D\_t$$  
**2\. The Constraints (The Rigid Walls)**

The system must respect two sets of physical and business realities.

* **State Constraint:** The inventory must never breach the statistical buffer.  
  $$I\_t \\ge SS$$  
* **Control Constraints:** The factory cannot build negative units, and it must build in discrete batch multiples ($k$).  
  $$u\_t \\ge 0$$  
  $$u\_t \\equiv 0 \\pmod k$$

**3\. The Control Law (Net Requirements Formula)**

When the State Transition Function predicts a violation of the State Constraint ($I\_t \< SS$), the Bang-Bang Controller activates. It algebraically isolates the control variable ($u\_t$) to find the exact mathematical injection required to force the system back to the boundary limit.

$$u\_t \= \\max \\Big(0, (D\_t \+ SS) \- (I\_{t-1} \+ S\_t) \\Big)$$  
*Note: This generates the raw, unconstrained Net Requirement. The system then applies the modulo batch constraint ($k$) to round $u\_t$ up to the final Planned Receipt ($PR\_t$).*

**4\. The Time-Vector Shift (Planned Order Release)**

Once the system knows *what* control to inject ($u\_t$), it applies the lag operator ($L$) to tell the factory *when* to execute it.

$$\\text{Release Date} \= t \- L$$

## **Part 4: The Strategic Optimization (MILP Objective Function)**

While the daily MRP engine is a greedy heuristic that blindly enforces the Control Law to satisfy $SS$, the macro-level system (Advanced Planning and Scheduling) uses Mixed-Integer Linear Programming (MILP) to define the strategy over the long-term horizon ($T$).

The MILP solver evaluates the entire matrix simultaneously to minimize the global Total Cost ($Z$).

**The Master Objective Function:**

$$\\min Z \= \\sum\_{t=1}^{T} \\left\[ C\_{hold, t} \+ C\_{setup, t} \+ C\_{material, t} \+ C\_{shortage, t} \+ C\_{underutil, t} \\right\]$$  
**The Competing Variables:**

* **$C\_{hold, t}$ (Holding Cost):** Penalizes high inventory. Forces the system toward Just-In-Time delivery.  
* **$C\_{setup, t}$ (Setup Cost):** A fixed penalty for changing machine states. Forces the system to group orders into massive batches.  
* **$C\_{material, t}$ (Material Cost):** Driven by supplier step-functions. Forces the system to artificially inflate order sizes to trigger price breaks.  
* **$C\_{shortage, t}$ (Shortage Penalty):** In medical devices, this approaches infinity. It forces the system to disregard holding costs and artificially elevate the $SS$ constraint to protect the patient.  
* **$C\_{underutil, t}$ (Supplier Minimums):** Contractual penalties for not buying enough volume. Forces the system to inject inventory it mathematically does not need yet.
