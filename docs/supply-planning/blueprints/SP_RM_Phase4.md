<!-- MIRROR: auto-synced from notes/projects/mrp/supply-planning/blueprints/SP_RM_Phase4.md - do not edit directly. Edit the canonical file in the notes repo and run scripts/sync_project_docs.py -->

---
id: projects-mrp-supply-planning-blueprints-SP_RM_Phase4
type: blueprint
status: draft
dependencies:
  - math/supply-planning/Math_Advanced_OR_Addendum.md
  - projects/mrp/supply-planning/blueprints/SP_RM_Phase3.md
  - projects/mrp/supply-planning/frameworks/MRP_Invariant_Suite.md
tags: []
invariants:
  - id: cumulative-lead-time
    statement: "Horizon MILP respects cumulative lead time across multi-echelon BOM paths"
inherited_invariants:
  - id: bellman-optimality
    from: math/supply-planning/Math_Advanced_OR_Addendum.md
    status: planned
    enforced_by: "tests/or/test_bellman_optimality.py::test_bellman_backup_holds"
  - id: disaggregation-conservation
    from: math/supply-planning/Math_Advanced_OR_Addendum.md
    status: planned
    enforced_by: "tests/or/test_disaggregation_conservation.py::test_family_totals_preserved"
  - id: milp-feasibility
    from: projects/mrp/supply-planning/blueprints/SP_RM_Phase3.md
    status: planned
    enforced_by: "tests/phase3/test_milp_feasibility.py::test_solution_satisfies_constraints"
  - id: horizon-bound
    from: projects/mrp/supply-planning/blueprints/SP_RM_Phase3.md
    status: planned
    enforced_by: "tests/phase3/test_horizon_bound.py::test_horizon_within_72h"
  - id: zero-chaos-delta-zero
    from: projects/mrp/supply-planning/frameworks/MRP_Invariant_Suite.md
    status: planned
    enforced_by: "tests/invariants/test_zero_chaos_delta_zero.py::test_zero_chaos_delta_zero_no_chaos_events"
  - id: mass-balance
    from: projects/mrp/supply-planning/frameworks/MRP_Invariant_Suite.md
    status: planned
    enforced_by: "tests/invariants/test_mass_balance.py::test_mass_balance_per_period"
  - id: inheritance-gluing
    from: projects/mrp/supply-planning/frameworks/MRP_Invariant_Suite.md
    status: planned
    enforced_by: "tests/invariants/test_inheritance_gluing.py::test_inheritance_gluing_on_hand"
  - id: chaos-support
    from: projects/mrp/supply-planning/frameworks/MRP_Invariant_Suite.md
    status: planned
    enforced_by: "tests/invariants/test_chaos_support.py::test_diff_support_subset"
  - id: run-determinism
    from: projects/mrp/supply-planning/frameworks/MRP_Invariant_Suite.md
    status: planned
    enforced_by: "tests/invariants/test_run_determinism.py::test_byte_identical_outputs"
  - id: export-round-trip
    from: projects/mrp/supply-planning/frameworks/MRP_Invariant_Suite.md
    status: planned
    enforced_by: "tests/invariants/test_export_round_trip.py::test_excel_values_match_source"
---
# Technical Blueprint: Phase 4 - Horizon Optimizer (Cumulative Lead Time)

## I. Objective

**CS / English:** Expand Phase 3 MILP by extending $T$ to the product line's full cumulative lead time (e.g., 180 days). Graduate to dynamic programming — evaluate the long-term cost integral and understand how Month 1 decisions force state-space collapse in Month 6. Run offline to identify where SAP is about to make a fatal long-term error.

**Mathematical Formalization:** State-space trees, Bellman equation, and MPC in [Math_Advanced_OR_Addendum.md](../math/Math_Advanced_OR_Addendum.md).

**Prerequisites:** [SP_RM_Phase3.md](SP_RM_Phase3.md) complete.

## II. Target Architecture

Phase 3 MILP extended to full cumulative lead time horizon:

- Long-horizon cost integral (holding + setup + shortage)
- Lead-time offset between POR and PR
- Terminal-state and frozen-zone boundary conditions enforced

## III. Layer 4 Invariants

**Temporal Offset Law:** For every planned receipt ($PR$) at time $t$, a matching POR exists at $t - L$:

$$\sum_{t=L}^{T} PR_t = \sum_{t=0}^{T-L} POR_t$$

*Why:* Solvers sometimes "teleport" material to avoid shortage penalties.

**Terminal State Validity (End-of-World Check):**

$$I_T \ge SS_{target}$$

*Why:* Solvers drain inventory to exactly 0 on day $T$ to avoid holding cost unless boundary conditions are enforced.

**Frozen Zone Lock:** Inside immediate cumulative lead time, reality cannot change.

- *Assertion:* $POR_t$ for $t \le L$ must equal 0 (or match locked historical execution).
- *Why:* Solver must not rewrite orders placed yesterday to fix next month's shortage.

## IV. Related Notes

- [SP_RM_Phase3.md](SP_RM_Phase3.md) — prerequisite micro MILP
- [SP_RM_Phase5.md](SP_RM_Phase5.md) — next phase (portfolio optimizer)
- [Math_Advanced_OR_Addendum.md](../math/Math_Advanced_OR_Addendum.md) — dynamic programming / MPC theory
