<!-- MIRROR: auto-synced from notes/projects/mrp/supply-planning/roadmaps/Supply_Planning_Tool_Roadmap.md - do not edit directly. Edit the canonical file in the notes repo and run scripts/sync_project_docs.py -->

# Supply Planning Tool Roadmap

Phased narrative for building standalone Python supply-planning tools (the Speedboat layer). Implementation specs and Layer 4 invariants live in [blueprints/](../../../../Notes/projects/mrp/supply-planning/roadmaps/blueprints).

## Related Notes

- [../architecture/MRP_State_Machine_Architecture.md](../architecture/MRP_State_Machine_Architecture.md) — Phase 1 foundation (sequential MRP).
- [MRP_V2_Roadmap.md](MRP_V2_Roadmap.md) — engine feature evolution in mrp_pipeline.
- [../frameworks/Two_Dials_Framework.md](../frameworks/Two_Dials_Framework.md) — architecture context (macro/micro, peace/war).
- [../../../../math/supply-planning/Math_Supply_Planning_OR_Lexicon.md](../../../../Notes/math/supply-planning/Math_Supply_Planning_OR_Lexicon.md) — formal OR foundations.
- [../../../../math/supply-planning/Math_Advanced_OR_Addendum.md](../../../../Notes/math/supply-planning/Math_Advanced_OR_Addendum.md) — sheaf theory, MPC, portfolio math.
- [../context/SAP_Enterprise_Context.md](../context/SAP_Enterprise_Context.md) — why offline tools are needed vs live ERP.

---

## Part I: The Global Picture (The ERP Battleship)

Enterprise Resource Planning (ERP) systems like SAP and Advanced Planning Systems (APS) represent the "Mother Battleship." They manage the macro-physics of the entire corporation. Three evolutionary tiers:

### 1. The Execution Engine (Standard MRP)

* **The Math:** A deterministic, discrete-time state machine using a Greedy Heuristic.
* **The Mechanism:** Topologically sorts the BOM as a DAG. Evaluates one part at a time, top-down. State transition $I_t = I_{t-1} + u_t - D_t$; triggers planned receipt the moment safety stock is violated.
* **The Flaw:** A **Presheaf** — optimizes parts in isolation, blind to shared constraints.

### 2. The Horizon Optimizer (Cumulative Lead Time)

* **The Math:** Dynamic Programming and Model Predictive Control.
* **The Mechanism:** Global cost function ($Z$) over cumulative lead time; balances holding vs setup over branching state-space trees.

### 3. The Portfolio Optimizer (Resource Disaggregation / The Sheaf)

* **The Math:** Multi-Item Knapsack via MILP.
* **The Mechanism:** S&OP severs shared topology with allocations (e.g., Cervical 40%). MILP optimizes SKUs within each silo.

## Part II: The Local Picture (The Need for Agile Speedboats)

If the ERP has massive MILP solvers, why build standalone tools? The battleship cannot handle **Injected Chaos** (port strike, broken machine, spiked order).

1. **The "Live Wire" Danger:** What-if scenarios in SAP overwrite master data and trigger global alarms.
2. **The Black Box Crisis:** Global MILP outputs untraceable schedule changes; planners lose trust.
3. **Computational Weight:** Factory floor needs triage in 10 minutes, not 12 hours.

Python/Excel scripts are **Speedboats** — offline digital twins that isolate chaos, prove solutions, and advise management before anyone touches the live ERP.

## Implementation Phases

Build in strict order. Canonical specs and Layer 4 invariants: [blueprints/](../../../../Notes/projects/mrp/supply-planning/roadmaps/blueprints).

| Phase | Blueprint | Summary |
|-------|-----------|---------|
| 1 | [SP_RM_Phase1.md](../blueprints/SP_RM_Phase1.md) | Sandbox MRP engine — deterministic netting loop |
| 2 | [SP_RM_Phase2.md](../blueprints/SP_RM_Phase2.md) | Root-cause tracer — BOM DAG traversal |
| 3 | [SP_RM_Phase3.md](../blueprints/SP_RM_Phase3.md) | Micro MILP — 72-hour triage |
| 4 | [SP_RM_Phase4.md](../blueprints/SP_RM_Phase4.md) | Horizon MILP — cumulative lead time |
| 5 | [SP_RM_Phase5.md](../blueprints/SP_RM_Phase5.md) | Portfolio MILP — resource disaggregation |

Epistemic verification: each speedboat script ends with explicit `assert` statements. If an invariant fails, the script crashes before the planner sees the report. See each blueprint §III for the canonical invariant list.
