<!-- MIRROR: auto-synced from notes/math/supply-planning/Math_Advanced_OR_Addendum.md - do not edit directly. Edit the canonical file in the notes repo and run scripts/sync_project_docs.py -->

# Advanced OR Addendum (Supply Planning)

Formal operations-research theory for supply-planning architecture: sheaf-theoretic constraint topology, state-space trees, modern OR solution methods, and the category-theory ↔ linear-algebra equivalence.

## Related Notes

- [Math_Supply_Planning_OR_Lexicon.md](Math_Supply_Planning_OR_Lexicon.md) — OR vocabulary and state/control equations.
- [../../projects/mrp/supply-planning/frameworks/Two_Dials_Framework.md](../frameworks/Two_Dials_Framework.md) — macro/micro decoupling and peace/war closed loop.
- [../../projects/mrp/supply-planning/roadmaps/Supply_Planning_Tool_Roadmap.md](../roadmaps/Supply_Planning_Tool_Roadmap.md) — ERP battleship vs speedboats narrative.
- [../../projects/mrp/supply-planning/blueprints/SP_RM_Phase5.md](../blueprints/SP_RM_Phase5.md) — portfolio optimizer blueprint (presheaf resolution).

---

## Part 1: The Topology of Factory Constraints (Sheaf Theory & Operations)

Standard enterprise software struggles because it fundamentally misunderstands the topology of a shared factory floor. The mathematical failure of base-level supply planning can be rigorously defined using Sheaf Theory.

### The Setup: MRP as a Presheaf

Let the base space $X$ be the topological space of all physical resources in the factory (labor, warehouse space, machine hours).

* Let $U \subset X$ be the open set of resources required for the **Cervical Spine** portfolio.
* Let $V \subset X$ be the open set of resources required for the **Trauma Plate** portfolio.
* The intersection $U \cap V$ represents the shared constraints (e.g., the primary 5-axis CNC titanium cutting machine).

Let the functor $\mathcal{F}$ assign to every open set the space of *locally optimal feasible production schedules*.

* $s \in \mathcal{F}(U)$ is the greedy, locally optimal schedule for Cervical.
* $t \in \mathcal{F}(V)$ is the greedy, locally optimal schedule for Trauma.

### The Failure of the Gluing Axiom

For this system to be a true **Sheaf**, the Gluing Axiom must hold. It dictates that if $s$ and $t$ agree on their intersection, there exists a unique global schedule gluing them together seamlessly.

* **The Breakdown:** Because standard MRP optimizes locally, the Cervical schedule ($s$) assumes it has 100% of the CNC machine to minimize its own shortage penalties. The Trauma schedule ($t$) makes the exact same assumption.
* **The Math:** $s|_{U \cap V} \neq t|_{U \cap V}$
* **The Result:** The sections collide. The Gluing Axiom strictly fails. The system remains a **Presheaf**, and the factory floor devolves into chaos as two planners fight over the same machine.

### The Two Solutions

1. **The Global Sheaf (MILP):** The algorithm abandons the local sections entirely. It evaluates a massive objective function over the global space $\mathcal{F}(X)$, mathematically forcing a trade-off at the intersection.
2. **Resource Disaggregation (The S&OP Hack):** Management physically severs the topology. They declare that Cervical gets 40% of the machine and Trauma gets 60%. Mathematically, they redefine the base space such that $U \cap V = \emptyset$. Because the intersection is forced empty, local optimizations no longer collide, making local MILP computationally feasible.

## Part 2: The Geometry of Time & Decisions (State Space Trees)

When optimizing a supply chain, you are operating in the realm of **Optimal Control Theory**. You must strictly separate the physical condition of the system from the actions you take to alter it, while understanding how the cost function evaluates both.

### The Intertwining of State and Control

* **The State Space ($x_t$ or $I_t$):** The memory and physical reality of the system (e.g., Inventory).
* **The Control Space ($u_t$):** The independent actions available to you (e.g., Planned Receipts / Orders).

The Objective Function ($Z$) is not blind to either space. It evaluates the financial pain of *both* spaces simultaneously:

$$Z = \sum_{t=1}^{T} \Big[ \underbrace{C_{hold}(x_t) + C_{shortage}(x_t)}_{\text{State Penalties}} \Big] + \sum_{t=1}^{T} \Big[ \underbrace{C_{setup}(u_t) + C_{material}(u_t)}_{\text{Control Penalties}} \Big]$$

* *State Penalties* punish you for where you exist (holding too much inventory, or dropping below zero).
* *Control Penalties* punish you for taking action (paying a fixed $10,000 factory setup cost to switch the machine to a new part).

### Branching Worldlines (The State-Space Tree)

Every time you choose a control variable $u_t$, you do not just incur a penalty today; you permanently alter the feasible geometry of tomorrow.

By choosing $u_t$, the State Transition Function ($x_{t+1} = x_t + u_t - D_t$) collapses a branch of the decision tree, defining a brand new starting state for $t+1$. This creates a massive, branching fractal of possible realities ("worldlines") spanning the 24-month horizon.

### The Bellman Equation (Greedy vs. Global)

Standard MRP is **Greedy**. It minimizes the cost for exactly one time period ($t$), ignoring the rest of the tree.

True optimization relies on the **Bellman Equation** (Dynamic Programming):

$$V(x_t) = \min_{u_t} \Big[ C(x_t, u_t) + \gamma V(x_{t+1}) \Big]$$

* **The Purpose:** This equation proves that the optimal decision today ($u_t$) must minimize today's localized cost $C(x_t, u_t)$ **plus** the total, global future cost of the specific worldline you just committed the factory to $V(x_{t+1})$.
* **The Example:** A greedy MRP sees a demand of 10 screws in Month 1 and 100 screws in Month 2. It orders 10 screws today to save on Holding Cost (State Penalty). But in doing so, it forces the factory to pay the massive $10,000 Setup Cost (Control Penalty) *twice* (once in Month 1, once in Month 2). The Bellman Equation looks down the worldline, absorbs the slight Holding Cost penalty of ordering 110 screws today, and mathematically avoids the second Setup Cost, finding the true global minimum.

## Part 3: Modern Operations Research Solutions

The industry has developed highly specific algorithms to bypass the computational limits of evaluating massive topological spaces and infinitely branching trees.

### A. The Capacitated Lot-Sizing Problem (CLSP)

* **The Problem:** Solving the Presheaf collision.
* **The Solution:** A specific MILP formulation that introduces a binary indicator variable ($Y_{i,t} \in \{0, 1\}$). It forces the algorithm to mathematically balance the Setup Costs of switching product families against the global capacity constraint of the machine. It packs the matrix perfectly, ensuring the sum of all setup times and run times strictly respects the physical $\le$ boundary of the CNC machine.

### B. Shadow Pricing (Dual Variables)

* **The Problem:** The "Black Box" explainability crisis. When a global solver makes a 24-month decision, humans do not trust it.
* **The Solution:** By analyzing the dual formulation of the linear program, the solver outputs a **Shadow Price** for every constraint. This represents the exact first derivative of the objective function with respect to the constraint boundary.
* **The Example:** If the CNC machine capacity is binding, the Shadow Price might be $\$5,000$. You can mathematically prove to the Director: *"If we authorize 1 hour of overtime for the machinist this Saturday, the algorithm guarantees it will reduce our total 24-month supply chain cost by exactly $5,000."*

### C. Model Predictive Control (MPC) / Receding Horizon

* **The Problem:** Injected chaos. Optimizing a 24-month tree is useless if a titanium shipment is delayed in Month 2, instantly invalidating Months 3 through 24.
* **The Solution:** The algorithm calculates the true global optimum for the entire 24-month Cumulative Lead Time, ensuring the factory respects the long-term physics. **However, it only executes the control variable ($u_t$) for the current time step (Month 1).** Once Month 1 concludes, the system absorbs the injected chaos, updates the true starting state $x_t$, and recalculates a brand new 24-month horizon. It constantly looks to the global horizon, but only ever steps one local period at a time.

## Notes: Sheaf Theory vs Practice

Sheaf theory is a rigorous lens for understanding the *structural failure* of local optimization. Operations Research (OR) does not use topological spaces, restriction maps, or gluing axioms — it lives in **Linear Algebra**, **Convex Geometry**, and **Graph Theory**.

### 1. The Factory Floor: Network Flows and Bipartite Graphs

In OR, the physical layout of the factory is modeled as a **Network Flow Problem**, specifically utilizing **Bipartite Graphs**.

* **The Framework:** A bipartite graph is a set of graph vertices decomposed into two disjoint sets where edges only connect Set 1 to Set 2.
* **The Supply Planning Translation:** Set 1 contains the *Operations*. Set 2 contains the *Resources*. The edges connecting them represent the capacity allocation.
* **The Goal:** The algorithm solves for the optimal flow of material through this graph over discrete time steps without exceeding the capacity of any specific node in Set 2.

### 2. The Core Engine: The Constraint Matrix (Polyhedral Geometry)

OR stacks every rule of the factory into a Polytope, defined by a **Constraint Matrix**:

$$Ax \le b$$

* **The Columns ($x$):** Every column represents a decision variable.
* **The Rows ($b$):** Every row represents a physical rule or constraint.
* **The Intersection:** The shared CNC machine is simply a horizontal row in the matrix.

### 3. The Native "Gluing" Mechanism: Dantzig-Wolfe Decomposition

**Dantzig-Wolfe Decomposition** or **Lagrangian Relaxation** operates like local-to-global gluing but uses economics instead of topology.

* **The Subproblems:** Independent blocks optimize locally.
* **The Master Problem:** A central algorithm watches shared resources.
* **The "Glue" (Shadow Pricing):** The Master Problem uses **Lagrange Multipliers** (prices) to raise the internal cost of overbooked resources until local solutions fit together.

### 4. The Applied Discipline: Job-Shop Scheduling (JSSP)

When packaged into software, this is formally categorized as **Job-Shop Scheduling (JSSP)** or **Resource-Constrained Project Scheduling (RCPSP)**.

## Mathematical Equivalence

Category Theory and Linear Algebra are looking at the exact same physical reality from two different altitudes of abstraction.

### 1. Are they "Mathematically Equivalent"?

Yes — **Applied Category Theory (ACT)** proves that OR graphs, matrices, and cost functions translate into the language of categories.

* A resource is an **Object**.
* A manufacturing process is a **Morphism**.
* The factory floor is a **Symmetric Monoidal Category**.

### 2. The Big Picture vs. The Mechanism

* **The Sheaf (Category Theory)** tells you *why* the factory is failing.
* **The Matrix (Linear Algebra)** tells you *how* to fix it.

### 3. The Point of Category Theory (The Universal Framework)

Category Theory looks for **Universal Properties**. A topological intersection, a database JOIN, and a factory constraint are all the same mathematical object (a **Pullback**).
