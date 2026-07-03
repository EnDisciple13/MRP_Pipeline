<!-- MIRROR: auto-synced from notes/projects/mrp/supply-planning/Supply_Planning_Tool_Roadmap.md - do not edit directly. Edit the canonical file in the notes repo and run scripts/sync_project_docs.py -->

# Supply Planning Tool Roadmap

Phased implementation roadmap for building standalone Python supply-planning tools (the Speedboat layer). Includes Layer 4 epistemic invariants per phase.

## Related Notes

- [MRP_State_Machine_Architecture.md](MRP_State_Machine_Architecture.md) — Phase 1 foundation (sequential MRP).
- [MRP_V2_Roadmap.md](MRP_V2_Roadmap.md) — engine feature evolution in mrp_pipeline.
- [Two_Dials_Framework.md](Two_Dials_Framework.md) — architecture context (macro/micro, peace/war).
- [../../../math/Math_Supply_Planning_OR_Lexicon.md](../../../Notes/math/Math_Supply_Planning_OR_Lexicon.md) — formal OR foundations.
- [SAP_Enterprise_Context.md](SAP_Enterprise_Context.md) — why offline tools are needed vs live ERP.

---

# 

[Master Reference: Supply Planning Architecture & Implementation Roadmap](#master-reference:-supply-planning-architecture-&-implementation-roadmap)

[Part I: The Global Picture (The ERP Battleship)](#part-i:-the-global-picture-\(the-erp-battleship\))

[1\. The Execution Engine (Standard MRP)](#1.-the-execution-engine-\(standard-mrp\))

[2\. The Horizon Optimizer (Cumulative Lead Time)](#2.-the-horizon-optimizer-\(cumulative-lead-time\))

[3\. The Portfolio Optimizer (Resource Disaggregation / The Sheaf)](#3.-the-portfolio-optimizer-\(resource-disaggregation-/-the-sheaf\))

[Part II: The Local Picture (The Need for Agile Speedboats)](#part-ii:-the-local-picture-\(the-need-for-agile-speedboats\))

[Part III: The Implementation Roadmap (Optimal Build Order)](#part-iii:-the-implementation-roadmap-\(optimal-build-order\))

[Phase 1: The Sandbox Simulator (Local MRP Engine)](#phase-1:-the-sandbox-simulator-\(local-mrp-engine\))

[Phase 2: The Root-Cause Tracer (DAG Traversal)](#phase-2:-the-root-cause-tracer-\(dag-traversal\))

[Phase 3: The Micro-Optimizer (Local MILP \- 72 Hour Triage)](#phase-3:-the-micro-optimizer-\(local-milp---72-hour-triage\))

[Phase 4: The Horizon Optimizer (Cumulative Lead Time)](#phase-4:-the-horizon-optimizer-\(cumulative-lead-time\))

[Phase 5: The Portfolio Optimizer (Jurisdictional Resource Disaggregation)](#phase-5:-the-portfolio-optimizer-\(jurisdictional-resource-disaggregation\))

[Part IV: The Pure Math Addendum (Operations Research Theory)](#part-iv:-the-pure-math-addendum-\(operations-research-theory\))

[1\. The Topology of Factory Constraints (Sheaf Theory & Operations)](#1.-the-topology-of-factory-constraints-\(sheaf-theory-&-operations\))

[The Setup: MRP as a Presheaf](#the-setup:-mrp-as-a-presheaf)

[The Failure of the Gluing Axiom](#the-failure-of-the-gluing-axiom)

[The Two Solutions](#the-two-solutions)

[2\. The Geometry of Time & Decisions (State Space Trees)](#2.-the-geometry-of-time-&-decisions-\(state-space-trees\))

[The Intertwining of State and Control](#the-intertwining-of-state-and-control)

[Branching Worldlines (The State-Space Tree)](#branching-worldlines-\(the-state-space-tree\))

[The Bellman Equation (Greedy vs. Global)](#the-bellman-equation-\(greedy-vs.-global\))

[3\. Modern Operations Research Solutions](#3.-modern-operations-research-solutions)

[A. The Capacitated Lot-Sizing Problem (CLSP)](#a.-the-capacitated-lot-sizing-problem-\(clsp\))

[B. Shadow Pricing (Dual Variables)](#b.-shadow-pricing-\(dual-variables\))

[C. Model Predictive Control (MPC) / Receding Horizon](#c.-model-predictive-control-\(mpc\)-/-receding-horizon)

[Note Sheaf Theory Vs Practice](#notes-sheaf-theory-vs-practice)

[1\. The Factory Floor: Network Flows and Bipartite Graphs](#1.-the-factory-floor:-network-flows-and-bipartite-graphs)

[2\. The Core Engine: The Constraint Matrix (Polyhedral Geometry)](#2.-the-core-engine:-the-constraint-matrix-\(polyhedral-geometry\))

[3\. The Native "Gluing" Mechanism: Dantzig-Wolfe Decomposition](#3.-the-native-"gluing"-mechanism:-dantzig-wolfe-decomposition)

[4\. The Applied Discipline: Job-Shop Scheduling (JSSP)](#4.-the-applied-discipline:-job-shop-scheduling-\(jssp\))

[Mathematical Equivalence](#mathematical-equivalence)

[1\. Are they "Mathematically Equivalent"?](#1.-are-they-"mathematically-equivalent"?)

[2\. The Big Picture vs. The Mechanism](#2.-the-big-picture-vs.-the-mechanism)

[3\. The Point of Category Theory (The Universal Framework)](#3.-the-point-of-category-theory-\(the-universal-framework\))

# 

# **Master Reference: Supply Planning Architecture & Implementation Roadmap** {#master-reference:-supply-planning-architecture-&-implementation-roadmap}

This document serves as your architectural blueprint. It maps the structural tension between global enterprise software and local operations, explicitly detailing the mathematical evolution of the systems and the exact optimal order for building your standalone Python/Excel toolset.

## **Part I: The Global Picture (The ERP Battleship)** {#part-i:-the-global-picture-(the-erp-battleship)}

Enterprise Resource Planning (ERP) systems like SAP and Advanced Planning Systems (APS) represent the "Mother Battleship." They are designed to manage the macro-physics of the entire corporation. To build effective local tools, you must understand the three evolutionary tiers of how this battleship processes mathematics.

### **1\. The Execution Engine (Standard MRP)** {#1.-the-execution-engine-(standard-mrp)}

* **The Math:** A deterministic, discrete-time state machine using a Greedy Heuristic.  
* **The Mechanism:** It topologically sorts the Bill of Materials (BOM) as a Directed Acyclic Graph (DAG). It evaluates one part at a time, moving strictly top-down. It calculates the State Transition Function ($I\_t \= I\_{t-1} \+ u\_t \- D\_t$) and violently triggers a Planned Receipt the exact moment the Safety Stock constraint is violated.  
* **The Flaw:** It is a **Presheaf**. Because it optimizes parts in isolation, it is completely blind to shared constraints. It will mathematically command two different product lines to use 100% of the same CNC machine on the exact same day.

### **2\. The Horizon Optimizer (Cumulative Lead Time)** {#2.-the-horizon-optimizer-(cumulative-lead-time)}

* **The Math:** Dynamic Programming and Model Predictive Control.  
* **The Mechanism:** To prevent the greedy MRP from walking the factory into a fatal trap 6 months from now, the system introduces a global Cost Function ($Z$). It expands the time horizon ($T$) out to the Cumulative Lead Time of the product family. It evaluates the integral of the cost function across branching state-space trees, calculating the mathematically optimal path to balance Holding Costs against Setup Costs over the long term.

### **3\. The Portfolio Optimizer (Resource Disaggregation / The Sheaf)** {#3.-the-portfolio-optimizer-(resource-disaggregation-/-the-sheaf)}

* **The Math:** Multi-Item Knapsack Problem via Mixed-Integer Linear Programming (MILP).  
* **The Mechanism:** To fix the "Presheaf" collision problem, management intervenes via Sales and Operations Planning (S\&OP). They artificially sever the shared topology. Instead of letting all products fight for the global machine, they enforce strict allocations (e.g., "Cervical gets 40%"). The MILP solver is then deployed to optimize the vector of SKUs *within* that specific silo, perfectly packing the production schedule into the allocated constraint without collisions.

## **Part II: The Local Picture (The Need for Agile Speedboats)** {#part-ii:-the-local-picture-(the-need-for-agile-speedboats)}

If the ERP possesses these massive MILP solvers, why do Supply Planning Analysts need to build standalone tools? Because the battleship is entirely unequipped to handle **Injected Chaos** (e.g., a port strike, a broken machine, a spiked hospital order).

1. **The "Live Wire" Danger:** You cannot run "What-If" scenarios in a live ERP. If you test a 3-week delay in SAP, you overwrite the master data and trigger global stockout alarms across the company.  
2. **The Black Box Crisis:** When global MILP solvers react to chaos, they output wildly different schedules. Standard planners cannot trace *why* the algorithm changed its mind, leading to a total loss of trust in the system.  
3. **Computational Weight:** SAP’s global solver is too heavy to run daily. When a machine breaks on a Tuesday, the factory floor needs a triage schedule in 10 minutes, not 12 hours.

As an analyst, you use AI as a force multiplier to rapidly write Python/Excel scripts. These scripts are your "Speedboats"—agile, offline Digital Twins that allow you to mathematically isolate chaos, prove the solution, and advise management before anyone touches the live ERP.

## **Part III: The Implementation Roadmap (Optimal Build Order)** {#part-iii:-the-implementation-roadmap-(optimal-build-order)}

This is the exact sequence to build your toolset. It is structured progressively: you must master the fundamental deterministic physics before you attempt to tame the discrete topology.

### **Phase 1: The Sandbox Simulator (Local MRP Engine)** {#phase-1:-the-sandbox-simulator-(local-mrp-engine)}

* **What it is:** A standalone script that runs the deterministic netting loop ($I\_t \= PAB\_{t-1} \+ S\_t \- D\_t$) and applies Lead Time offsets for a specific subset of parts.  
* **Why build it first:** This is your foundation. You cannot optimize a cost function if your netting math is wrong. It forces you to completely internalize APICS vocabulary (PAB, Gross Reqs, Net Reqs) and the discrete time-shift mechanics.  
* **The Business Value:** Unlocks immediate offline scenario modeling. You can safely calculate exactly which hospitals will stock out when a supplier is 7 days late.

### **Phase 2: The Root-Cause Tracer (DAG Traversal)** {#phase-2:-the-root-cause-tracer-(dag-traversal)}

* **What it is:** A graph search algorithm that reads a messy list of SAP exception messages and traces them vertically through the BOM to find the originating constraint.  
* **Why build it second:** Once you can simulate a single node (Phase 1), you must connect them spatially. This tool bridges your local simulation to the multi-level reality of the factory.  
* **The Business Value:** Reduces hours of manual Excel filtering into seconds of computation. Allows you to direct the expediting team to the single failing screw rather than chasing 800 phantom alarms.

### **Phase 3: The Micro-Optimizer (Local MILP \- 72 Hour Triage)** {#phase-3:-the-micro-optimizer-(local-milp---72-hour-triage)}

* **What it is:** A lightweight PuLP script that evaluates a severely amputated time horizon ($T=3$). It takes a localized capacity constraint (e.g., a broken machine operating at 40%) and optimizes the $u\_t$ control variables to minimize the Shortage Penalty for the parts currently waiting.  
* **Why build it third:** This is your controlled introduction to Linear Programming. By limiting $T$, you eliminate the "butterfly effect." You learn how to write the Objective Function and define Feasible Regions without melting your computer's RAM.  
* **The Business Value:** Provides mathematically optimal, rapid-response schedules for the factory floor during acute crises.

### **Phase 4: The Horizon Optimizer (Cumulative Lead Time)** {#phase-4:-the-horizon-optimizer-(cumulative-lead-time)}

* **What it is:** You expand your Phase 3 MILP by extending $T$ to match the product line's full Cumulative Lead Time (e.g., 180 days).  
* **Why build it fourth:** You are now graduating to Dynamic Programming. You are learning to evaluate the long-term cost integral. You must understand how a decision made in Month 1 mathematically forces a state-space collapse in Month 6\.  
* **The Business Value:** Allows you to outsmart the greedy ERP. You can run the Horizon offline, identify where SAP is about to make a fatal long-term error, and manually override the system today.

### **Phase 5: The Portfolio Optimizer (Jurisdictional Resource Disaggregation)** {#phase-5:-the-portfolio-optimizer-(jurisdictional-resource-disaggregation)}

* **What it is:** The master architecture. You flatten the vertical BOM and isolate a single horizontal slice (e.g., all Level 3 parts on one machine). You optimize the entire vector of sibling SKUs simultaneously against your strict 40% capacity allocation, balancing Setup Costs ($C\_{setup}$) against Holding Costs ($C\_{hold}$).  
* **Why build it last:** This requires absolute mastery of spatial constraints, matrix packing, and cost dynamics. It is the exact mathematical resolution to the "presheaf" problem within your specific jurisdiction.  
* **The Business Value:** Squeezes maximum financial margin out of rigid physical assets. This is the tool that elevates you from Analyst to Principal Architect.

### **Part 2: Epistemic Verification for Your Speedboats**

When you build your Python tools, you do not let a human check the output. You write explicit assert statements at the very end of your script. If the invariant fails, the script intentionally crashes and throws a fatal error before the planner ever sees the Excel report.

Here are the strict invariants (the walls of the polytope) for each of your 5 Phases.

#### **Phase 1: The Sandbox (Local MRP Engine)**

In Phase 1, you are dealing with the physical movement of inventory.

* **Invariant 1: The Conservation of Mass (Flow Balance)**  
  The absolute sum of all starting inventory plus all incoming supply must perfectly equal the sum of all demand plus the final ending inventory.  
  $$\\sum\_{t=1}^{T} S\_t \+ I\_0 \= \\sum\_{t=1}^{T} D\_t \+ I\_T$$  
  *Why it matters:* If your AI-written loop drops an array index or shifts a time-bucket incorrectly, inventory will vanish into the ether or appear out of nowhere. This invariant catches time-shift leaks.  
* **Invariant 2: The Non-Negativity of Physics**  
  $$I\_t \\ge 0 \\quad \\text{and} \\quad PR\_t \\ge 0 \\quad \\text{for all } t$$  
  *Why it matters:* You cannot hold negative physical screws, and you cannot order a negative delivery to magically erase inventory.

#### **Phase 2: The Root-Cause Tracer (DAG Traversal)**

In Phase 2, you are traversing the Bill of Materials.

* **Invariant 1: Topological Acyclicity (No Infinite Loops)**  
  *Why it matters:* In medical devices, data-entry errors happen. A junior engineer might accidentally code the BOM so that a Cervical Kit requires a Screw, but the Screw's BOM requires the Cervical Kit. If your script hits a cycle, it will infinite-loop forever. Your invariant must assert that the DAG depth is strictly less than the total number of unique parts in the database.  
* **Invariant 2: Conservation of "Quantity Per"**  
  If a parent kit requires exactly 4 screws ($Q=4$), the traced shortage of screws must be an exact modulo of the parent demand.  
  $$Exceptions\_{child} \\equiv 0 \\pmod Q$$

#### **Phase 3: The Micro-Optimizer (Local MILP 72-Hour)**

In Phase 3, you introduce a mathematical solver. Solvers are notorious for finding "loopholes" in poorly written constraints.

* **Invariant 1: The Strict Capacity Bound**  
  You take the AI's final output vector ($U$) and mathematically multiply it by the run-time vector ($R$).  
  $$\\sum (u\_{i, t} \\times R\_i) \\le Max\\\_Cap\_t$$  
  *Why it matters:* You do not trust the solver's STATUS: OPTIMAL flag. You take the literal output, manually calculate the hours, and assert that it is $\\le 72$. If the solver hallucinated extra capacity, the script crashes.  
* **Invariant 2: The Integer Floor**  
  $$u\_{i, t} \\in \\mathbb{Z}^+$$  
  *Why it matters:* Linear relaxations will try to tell the factory to build 45.7 titanium screws to perfectly hit a capacity limit. You must audit that the final output vector contains only pure integers.

#### **Phase 4: The Horizon Optimizer (Cumulative Lead Time)**

In Phase 4, you stretch the time dimension ($T$), introducing offset delays.

* **Invariant 1: The Temporal Offset Law**  
  For every Planned Receipt ($PR$) arriving at time $t$, there must exist a matching Planned Order Release ($POR$) at time $t \- L$.  
  $$\\sum\_{t=L}^{T} PR\_t \= \\sum\_{t=0}^{T-L} POR\_t$$  
  *Why it matters:* Solvers sometimes "teleport" material to avoid shortage penalties. This invariant audits the time dimension, proving that nothing arrived without first paying the time-delay penalty.

#### **Phase 5: The Portfolio Optimizer (Resource Disaggregation)**

In Phase 5, you introduce Binary Switches ($Y \\in \\{0, 1\\}$) to model Setup Costs ($C\_{setup}$).

* **Invariant 1: The Binary "Big-M" Lock**  
  If the solver outputs a production run ($u\_{i, t} \> 0$), you must mathematically assert that the binary switch for that part was flipped to exactly $1$.  
  $$u\_{i,t} \> 0 \\implies Y\_{i,t} \= 1$$  
  *Why it matters:* If the "Big-M" constraint in your MILP is poorly formatted, the solver will cheat. It will produce 10,000 screws ($u \> 0$) but leave the binary switch at $0$ to illegally avoid paying the $C\_{setup}$ penalty in the objective function. This invariant catches algorithmic cheating.

#### **Phase 1: The Sandbox (Deterministic Engine)**

You already have the Conservation of Mass and Non-Negativity. Now we lock down the time-vector physics.

* **The Lead Time Offset Integrity:** If Lead Time ($L$) is 2 days, and there are no open orders currently in transit, the Planned Receipts for today and tomorrow must mathematically be zero.  
  * *Assertion:* If sum(S\[0:L\]) \== 0, then sum(PR\[0:L\]) \== 0.  
  * *Why:* The engine cannot physically receive material faster than $L$. This catches offset indexing errors in your code.  
* **The Lot Size Modulo Check:** If your Minimum Order Quantity (MOQ) is 50, every single triggered Planned Order Release ($POR$) must be a clean multiple of 50\.  
  * *Assertion:* POR\_t % MOQ \== 0 for all $t$.  
  * *Why:* AI coding agents frequently struggle with rounding logic, returning POR \= 49.99 due to floating-point math. This guarantees valid integer execution for the purchasing team.

#### **Phase 2: The Root-Cause Tracer (DAG Traversal)**

You have Topological Acyclicity. Now we lock down the relational geometry.

* **The "Orphaned Demand" Check:** The total sum of dependent demand at the bottom of the graph (Level 3\) must perfectly map back to the parent Gross Requirements at Level 0, multiplied by the edge weights.  
  * *Assertion:* $\\sum \\text{Child Req} \= \\sum (\\text{Parent POR} \\times \\text{Quantity Per})$.  
  * *Why:* If the DAG traversal drops a node or severs an edge by accident, demand becomes "orphaned." This proves no material requirements were lost in the matrix explosion.  
* **The Nilpotent Matrix Verification:** The Adjacency Matrix ($B$) of the Bill of Materials must be strictly nilpotent.  
  * *Assertion:* $B^k \= 0$, where $k$ is the maximum depth of the BOM.  
  * *Why:* This is the rigorous pure math check for a cyclic loop. If $B^k \\neq 0$, a recursive loop exists in the master data, and your tracer will run forever.

#### **Phase 3: The Micro-Optimizer (Local MILP 72-Hour)**

You have the Capacity Bound and the Integer Floor. Now we audit the solver's logic.

* **The Baseline Greedy Override:** An optimization solver must *always* beat or equal a dumb heuristic.  
  * *Assertion:* The total cost output of the MILP ($Z\_{MILP}$) must be $\\le$ the total cost of standard MRP logic ($Z\_{MRP}$).  
  * *Why:* If the solver returns a higher penalty cost than just running standard MRP, your objective function is mathematically flawed or your constraints are choking the feasible region.  
* **Complementary Slackness (Dual Feasibility):** If the CNC machine has 4 hours of unused capacity remaining, its "Shadow Price" must be mathematically zero.  
  * *Assertion:* If Capacity\_Used \< Max\_Cap, then Shadow\_Price \== 0.  
  * *Why:* If the machine isn't maxed out, gaining one extra hour of capacity has zero value. If the solver assigns a financial value to an unconstrained resource, the internal dual-variable math has broken down.

#### **Phase 4: The Horizon Optimizer (Cumulative Lead Time)**

You have the Temporal Offset Law. Now we protect the boundaries of time.

* **The Terminal State Validity (End-of-World Check):** Solvers love to cheat at the edge of the horizon ($T$). Knowing they don't have to survive Day $T+1$, the solver will artificially drain your inventory to exactly $0$ on Day $T$ to avoid paying Holding Costs.  
  * *Assertion:* $I\_T \\ge SS\_{target}$.  
  * *Why:* You must enforce a boundary condition on the terminal state, ensuring the solver leaves the factory in a safe, mathematically viable position for the next planning horizon.  
* **The "Frozen Zone" Lock:** Inside the immediate cumulative lead time, the system is physically unable to change reality.  
  * *Assertion:* The $POR\_t$ vector for $t \\le L$ must equal exactly $0$ (or match the historical locked execution).  
  * *Why:* The solver might try to change an order you placed yesterday to optimize a shortage next month. This asserts that the solver respects the arrow of time.

#### **Phase 5: The Portfolio Optimizer (Resource Disaggregation)**

You have the "Big-M" Lock. Now we protect the physical constraints of the machine itself.

* **The Mutually Exclusive State:** If two parts (Cervical Screws and Trauma Plates) require the exact same CNC spindle, they cannot run simultaneously.  
  * *Assertion:* $Y\_{Cervical, t} \+ Y\_{Trauma, t} \\le 1$.  
  * *Why:* Solvers will attempt to stack production if the $\\le$ constraint is too loose. This strictly enforces that the binary switches are mutually exclusive per machine.  
* **The Setup Triangle Inequality:** If tooling changeover A $\\to$ B costs $100, B $\\to$ C costs $100, and A $\\to$ C costs $500.  
  * *Assertion:* The setup cost matrix must satisfy $C(A,C) \\le C(A,B) \+ C(B,C)$.  
  * *Why:* If your master data violates the triangle inequality, the MILP solver will exploit it. It will tell the factory to physically switch the machine to Part B for one microsecond just to get a cheaper changeover to Part C. This checks the sanity of the financial input data before the solver touches it.

## **Part IV: The Pure Math Addendum (Operations Research Theory)** {#part-iv:-the-pure-math-addendum-(operations-research-theory)}

### **1\. The Topology of Factory Constraints (Sheaf Theory & Operations)** {#1.-the-topology-of-factory-constraints-(sheaf-theory-&-operations)}

Standard enterprise software struggles because it fundamentally misunderstands the topology of a shared factory floor. The mathematical failure of base-level supply planning can be rigorously defined using Sheaf Theory.

#### **The Setup: MRP as a Presheaf** {#the-setup:-mrp-as-a-presheaf}

Let the base space $X$ be the topological space of all physical resources in the factory (labor, warehouse space, machine hours).

* Let $U \\subset X$ be the open set of resources required for the **Cervical Spine** portfolio.  
* Let $V \\subset X$ be the open set of resources required for the **Trauma Plate** portfolio.  
* The intersection $U \\cap V$ represents the shared constraints (e.g., the primary 5-axis CNC titanium cutting machine).

Let the functor $\\mathcal{F}$ assign to every open set the space of *locally optimal feasible production schedules*.

* $s \\in \\mathcal{F}(U)$ is the greedy, locally optimal schedule for Cervical.  
* $t \\in \\mathcal{F}(V)$ is the greedy, locally optimal schedule for Trauma.

#### **The Failure of the Gluing Axiom** {#the-failure-of-the-gluing-axiom}

For this system to be a true **Sheaf**, the Gluing Axiom must hold. It dictates that if $s$ and $t$ agree on their intersection, there exists a unique global schedule gluing them together seamlessly.

* **The Breakdown:** Because standard MRP optimizes locally, the Cervical schedule ($s$) assumes it has 100% of the CNC machine to minimize its own shortage penalties. The Trauma schedule ($t$) makes the exact same assumption.  
* **The Math:** $s|\_{U \\cap V} \\neq t|\_{U \\cap V}$  
* **The Result:** The sections collide. The Gluing Axiom strictly fails. The system remains a **Presheaf**, and the factory floor devolves into chaos as two planners fight over the same machine.

#### **The Two Solutions** {#the-two-solutions}

1. **The Global Sheaf (MILP):** The algorithm abandons the local sections entirely. It evaluates a massive objective function over the global space $\\mathcal{F}(X)$, mathematically forcing a trade-off at the intersection.  
2. **Resource Disaggregation (The S\&OP Hack):** Management physically severs the topology. They declare that Cervical gets 40% of the machine and Trauma gets 60%. Mathematically, they redefine the base space such that $U \\cap V \= \\emptyset$. Because the intersection is forced empty, local optimizations no longer collide, making local MILP computationally feasible.

### **2\. The Geometry of Time & Decisions (State Space Trees)** {#2.-the-geometry-of-time-&-decisions-(state-space-trees)}

When optimizing a supply chain, you are operating in the realm of **Optimal Control Theory**. You must strictly separate the physical condition of the system from the actions you take to alter it, while understanding how the cost function evaluates both.

#### **The Intertwining of State and Control** {#the-intertwining-of-state-and-control}

* **The State Space ($x\_t$ or $I\_t$):** The memory and physical reality of the system (e.g., Inventory).  
* **The Control Space ($u\_t$):** The independent actions available to you (e.g., Planned Receipts / Orders).

The Objective Function ($Z$) is not blind to either space. It evaluates the financial pain of *both* spaces simultaneously:

$$Z \= \\sum\_{t=1}^{T} \\Big\[ \\underbrace{C\_{hold}(x\_t) \+ C\_{shortage}(x\_t)}\_{\\text{State Penalties}} \\Big\] \+ \\sum\_{t=1}^{T} \\Big\[ \\underbrace{C\_{setup}(u\_t) \+ C\_{material}(u\_t)}\_{\\text{Control Penalties}} \\Big\]$$

* *State Penalties* punish you for where you exist (holding too much inventory, or dropping below zero).  
* *Control Penalties* punish you for taking action (paying a fixed $10,000 factory setup cost to switch the machine to a new part).

#### **Branching Worldlines (The State-Space Tree)** {#branching-worldlines-(the-state-space-tree)}

Every time you choose a control variable $u\_t$, you do not just incur a penalty today; you permanently alter the feasible geometry of tomorrow.

By choosing $u\_t$, the State Transition Function ($x\_{t+1} \= x\_t \+ u\_t \- D\_t$) collapses a branch of the decision tree, defining a brand new starting state for $t+1$. This creates a massive, branching fractal of possible realities ("worldlines") spanning the 24-month horizon.

#### **The Bellman Equation (Greedy vs. Global)** {#the-bellman-equation-(greedy-vs.-global)}

Standard MRP is **Greedy**. It minimizes the cost for exactly one time period ($t$), ignoring the rest of the tree.

True optimization relies on the **Bellman Equation** (Dynamic Programming):

$$V(x\_t) \= \\min\_{u\_t} \\Big\[ C(x\_t, u\_t) \+ \\gamma V(x\_{t+1}) \\Big\]$$

* **The Purpose:** This equation proves that the optimal decision today ($u\_t$) must minimize today's localized cost $C(x\_t, u\_t)$ **plus** the total, global future cost of the specific worldline you just committed the factory to $V(x\_{t+1})$.  
* **The Example:** A greedy MRP sees a demand of 10 screws in Month 1 and 100 screws in Month 2\. It orders 10 screws today to save on Holding Cost (State Penalty). But in doing so, it forces the factory to pay the massive $10,000 Setup Cost (Control Penalty) *twice* (once in Month 1, once in Month 2). The Bellman Equation looks down the worldline, absorbs the slight Holding Cost penalty of ordering 110 screws today, and mathematically avoids the second Setup Cost, finding the true global minimum.

### **3\. Modern Operations Research Solutions** {#3.-modern-operations-research-solutions}

The industry has developed highly specific algorithms to bypass the computational limits of evaluating massive topological spaces and infinitely branching trees.

#### **A. The Capacitated Lot-Sizing Problem (CLSP)** {#a.-the-capacitated-lot-sizing-problem-(clsp)}

* **The Problem:** Solving the Presheaf collision.  
* **The Solution:** A specific MILP formulation that introduces a binary indicator variable ($Y\_{i,t} \\in \\{0, 1\\}$). It forces the algorithm to mathematically balance the Setup Costs of switching product families against the global capacity constraint of the machine. It packs the matrix perfectly, ensuring the sum of all setup times and run times strictly respects the physical $\\le$ boundary of the CNC machine.

#### **B. Shadow Pricing (Dual Variables)** {#b.-shadow-pricing-(dual-variables)}

* **The Problem:** The "Black Box" explainability crisis. When a global solver makes a 24-month decision, humans do not trust it.  
* **The Solution:** By analyzing the dual formulation of the linear program, the solver outputs a **Shadow Price** for every constraint. This represents the exact first derivative of the objective function with respect to the constraint boundary.  
* **The Example:** If the CNC machine capacity is binding, the Shadow Price might be $\\$5,000$. You can mathematically prove to the Director: *"If we authorize 1 hour of overtime for the machinist this Saturday, the algorithm guarantees it will reduce our total 24-month supply chain cost by exactly $5,000."*

#### **C. Model Predictive Control (MPC) / Receding Horizon** {#c.-model-predictive-control-(mpc)-/-receding-horizon}

* **The Problem:** Injected chaos. Optimizing a 24-month tree is useless if a titanium shipment is delayed in Month 2, instantly invalidating Months 3 through 24\.  
* **The Solution:** The algorithm calculates the true global optimum for the entire 24-month Cumulative Lead Time, ensuring the factory respects the long-term physics. **However, it only executes the control variable ($u\_t$) for the current time step (Month 1).** Once Month 1 concludes, the system absorbs the injected chaos, updates the true starting state $x\_t$, and recalculates a brand new 24-month horizon. It constantly looks to the global horizon, but only ever steps one local period at a time.

## **Notes Sheaf Theory Vs Practice** {#notes-sheaf-theory-vs-practice}

You caught exactly what happened. Sheaf theory is a beautiful, rigorous lens for understanding the *structural failure* of local optimization, but you are right to ask for the native language of the discipline. Operations Research (OR) does not use topological spaces, restriction maps, or gluing axioms.

OR lives almost entirely in the realms of **Linear Algebra**, **Convex Geometry**, and **Graph Theory**.

When a supply planning architect looks at the "topology" of factory constraints—how different medical device product lines intersect at shared CNC machines—they use a highly specific mathematical framework to map and solve it. Here is the native OR translation of the concepts we discussed.

### **1\. The Factory Floor: Network Flows and Bipartite Graphs**  {#1.-the-factory-floor:-network-flows-and-bipartite-graphs}

In OR, the physical layout of the factory isn't modeled as overlapping open sets. It is modeled as a **Network Flow Problem**, specifically utilizing **Bipartite Graphs**.

* **The Framework:** A bipartite graph is a set of graph vertices decomposed into two disjoint sets where edges only connect Set 1 to Set 2\.  
* **The Supply Planning Translation:** Set 1 contains the *Operations* (e.g., routing step 10 for a cervical plate, routing step 20 for a trauma screw). Set 2 contains the *Resources* (e.g., Machine A, Machine B). The edges connecting them represent the capacity allocation.  
* **The Goal:** The algorithm solves for the optimal flow of material through this graph over discrete time steps without exceeding the capacity (weight limit) of any specific node in Set 2\.

### **2\. The Core Engine: The Constraint Matrix (Polyhedral Geometry)** {#2.-the-core-engine:-the-constraint-matrix-(polyhedral-geometry)}

OR does not attempt to mathematically "glue" local solutions together. Instead, it stacks every single rule of the factory into a massive multidimensional geometric shape called a Polytope, defined by a **Constraint Matrix**.

Instead of a topological space, the framework is the linear system:

$$Ax \\le b$$

* **The Columns ($x$):** Every column in matrix $A$ represents a decision variable (e.g., how many 10mm screws to build today).  
* **The Rows ($b$):** Every row in matrix $A$ represents a physical rule or constraint.  
* **The Intersection (The Native "Presheaf" Collision):** The shared CNC machine is simply a horizontal row in the matrix. If the 10mm screws and the 12mm screws both need that machine, their respective columns will both have non-zero coefficients in that specific row. The algorithm is geometrically bound by the vector $b$ (the absolute limit of machine hours).

### **3\. The Native "Gluing" Mechanism: Dantzig-Wolfe Decomposition** {#3.-the-native-"gluing"-mechanism:-dantzig-wolfe-decomposition}

This is the crown jewel of your intuition. You noticed that running a massive global optimization is computationally explosive, and asked how OR manages the local-to-global relationship if they don't use sheaves.

The native OR framework for this is called **Decomposition Techniques**—most famously **Dantzig-Wolfe Decomposition** or **Lagrangian Relaxation**. It operates exactly like the local-to-global gluing concept, but it uses economics instead of topology.

* **The Subproblems (The Local Presheaves):** The algorithm artificially severs the global constraint matrix into smaller, independent blocks (e.g., isolating the Cervical desk from the Trauma desk). These subproblems optimize locally, which is computationally cheap.  
* **The Master Problem (The Global Coordinator):** A central algorithm watches the shared resources. When the local subproblems inevitably collide on the shared CNC machine, the Master Problem intervenes.  
* **The "Glue" (Shadow Pricing):** Instead of topological gluing, the Master Problem uses **Lagrange Multipliers** (prices). It looks at the overbooked CNC machine and artificially raises the internal mathematical "cost" of using it. It broadcasts this new penalty price down to the local subproblems. The subproblems recalculate their local math, realize the machine is now too expensive to monopolize, and naturally shift their schedules to use less of it. They iterate this pricing loop until the local solutions perfectly fit together without violating the global limit.

### **4\. The Applied Discipline: Job-Shop Scheduling (JSSP)** {#4.-the-applied-discipline:-job-shop-scheduling-(jssp)}

When this pure math is packaged into software to run a factory floor, it is formally categorized as the **Job-Shop Scheduling Problem (JSSP)** or the **Resource-Constrained Project Scheduling Problem (RCPSP)**.

If you read OR literature, JSSP is the framework dedicated to answering: *"I have $N$ jobs, $M$ machines, and strict routing sequences. What is the exact sequence of operations that minimizes the total span of time (makespan) without double-booking a machine?"*

## **Mathematical Equivalence** {#mathematical-equivalence}

Category Theory and Linear Algebra are looking at the exact same physical reality, just from two different altitudes of abstraction.

Here is the breakdown of why your intuition is spot on, and how mathematicians bridge that gap.

### **1\. Are they "Mathematically Equivalent"?** {#1.-are-they-"mathematically-equivalent"?}

Yes, in modern mathematics, there is an entire rapidly growing field called **Applied Category Theory (ACT)** (led by mathematicians like Brendan Fong and David Spivak) that proves exactly what you just hypothesized.

They have rigorously proven that you can take the graphs, matrices, and cost functions of Operations Research and translate them perfectly into the language of categories.

* A resource (like a CNC machine or titanium) is an **Object**.  
* A manufacturing process (turning titanium into a screw) is a **Morphism**.  
* The factory floor is a **Symmetric Monoidal Category**, where you can compose processes sequentially (series) or run them side-by-side (parallel).

So yes, the topological sheaf you visualized and the $Ax \\le b$ constraint matrix I showed you are mathematically equivalent. They encode the exact same data.

### **2\. The Big Picture vs. The Mechanism** {#2.-the-big-picture-vs.-the-mechanism}

Your theme is flawless: *"Category theory gives the picture, OR gives the mechanism."*

In mathematics, Category Theory is often jokingly called "generalized abstract nonsense." It doesn't care about the numbers. It zooms out so far that it erases the details to look strictly at the **structure** and the **relationships**.

* **The Sheaf (Category Theory)** tells you *why* the factory is failing: "Your local sections do not agree on the intersection."  
* **The Matrix (Linear Algebra)** tells you *how* to fix it: "Pivot this exact matrix coefficient to shift 4 hours of capacity to the 10mm screw."

When you are architecting a supply chain strategy, you use your Category Theory brain. When you open Python and write a PuLP script, you use your Linear Algebra brain.

### **3\. The Point of Category Theory (The Universal Framework)** {#3.-the-point-of-category-theory-(the-universal-framework)}

You asked if the point of Category Theory is to see patterns and leverage overarching frameworks. **That is its exact, defining purpose.**

Category Theory looks for **Universal Properties**. Once you realize that a concept fits a universal property, you can steal theorems from wildly different fields of math and apply them to your current problem.

Because you looked at supply chain through this lens, you realized that:

* A topological intersection (two open sets overlapping)  
* A database JOIN (two tables sharing a foreign key)  
* A factory constraint (two product lines needing the same machine)

...are all the exact same mathematical object (specifically, what Category Theory calls a **Pullback**).

By realizing this, you didn't have to learn supply chain theory from scratch. You just took what you already knew about how local spaces fail to glue globally, applied it to a CNC machine, and instantly understood why a multi-million dollar SAP system crashes. That is the ultimate power of category theory.
