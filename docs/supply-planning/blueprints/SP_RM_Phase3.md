<!-- MIRROR: auto-synced from notes/projects/mrp/supply-planning/blueprints/SP_RM_Phase3.md - do not edit directly. Edit the canonical file in the notes repo and run scripts/sync_project_docs.py -->

---
id: projects-mrp-supply-planning-blueprints-SP_RM_Phase3
type: blueprint
status: draft
dependencies:
  - math/supply-planning/Math_Advanced_OR_Addendum.md
  - math/supply-planning/Math_Supply_Planning_OR_Lexicon.md
  - projects/mrp/supply-planning/blueprints/SP_RM_Phase2.md
  - projects/mrp/supply-planning/frameworks/MRP_Invariant_Suite.md
tags: []
invariants:
  - id: milp-feasibility
    statement: "Micro MILP solution satisfies all inventory balance and capacity constraints"
  - id: horizon-bound
    statement: "Micro MILP horizon is bounded to 72-hour triage window"
inherited_invariants:
  - id: bellman-optimality
    from: math/supply-planning/Math_Advanced_OR_Addendum.md
    status: planned
    enforced_by: "tests/or/test_bellman_optimality.py::test_bellman_backup_holds"
  - id: disaggregation-conservation
    from: math/supply-planning/Math_Advanced_OR_Addendum.md
    status: planned
    enforced_by: "tests/or/test_disaggregation_conservation.py::test_family_totals_preserved"
  - id: inventory-balance
    from: math/supply-planning/Math_Supply_Planning_OR_Lexicon.md
    status: planned
    enforced_by: "tests/lexicon/test_inventory_balance.py::test_pab_recursion_matches_lexicon"
  - id: non-negative-controls
    from: math/supply-planning/Math_Supply_Planning_OR_Lexicon.md
    status: planned
    enforced_by: "tests/lexicon/test_non_negative_controls.py::test_inventory_and_receipts_non_negative"
  - id: bom-dag
    from: projects/mrp/supply-planning/blueprints/SP_RM_Phase2.md
    status: planned
    enforced_by: "tests/phase2/test_bom_dag.py::test_bom_is_acyclic"
  - id: quantity-per-conservation
    from: projects/mrp/supply-planning/blueprints/SP_RM_Phase2.md
    status: planned
    enforced_by: "tests/phase2/test_quantity_per_conservation.py::test_gozinto_factors_multiply"
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
# Technical Blueprint: Phase 3 - Micro-Optimizer (Local MILP, 72-Hour Triage)

## I. Objective

**CS / English:** Build a lightweight PuLP script that evaluates a severely amputated time horizon ($T=3$). Takes a localized capacity constraint (e.g., broken machine at 40%) and optimizes $u_t$ control variables to minimize shortage penalty for parts currently waiting. Controlled introduction to linear programming without the butterfly effect of long horizons.

**Mathematical Formalization:** Objective function, state/control variables, and MILP foundations in [Math_Supply_Planning_OR_Lexicon.md](../math/Math_Supply_Planning_OR_Lexicon.md).

**Prerequisites:** [SP_RM_Phase2.md](SP_RM_Phase2.md) complete.

## II. Target Architecture

A PuLP (or equivalent) script that:

- Limits horizon to $T \approx 3$ (72-hour triage window)
- Minimizes shortage penalty under a localized capacity constraint
- Outputs integer production/orders; crashes on invariant failure

## III. Layer 4 Invariants

**Strict Capacity Bound:** Multiply the final output vector ($U$) by run-time vector ($R$):

$$\sum (u_{i, t} \times R_i) \le Max\_Cap_t$$

*Why:* Do not trust `STATUS: OPTIMAL` alone — manually verify hours $\le$ 72.

**Integer Floor:**

$$u_{i, t} \in \mathbb{Z}^+$$

*Why:* Linear relaxations return fractional screws (45.7); factory needs integers.

**Baseline Greedy Override:**

$$Z_{MILP} \le Z_{MRP}$$

*Why:* If the solver costs more than dumb MRP, the objective or constraints are flawed.

**Complementary Slackness (Dual Feasibility):** If capacity used $<$ max capacity, shadow price must be zero.

- *Assertion:* If `Capacity_Used < Max_Cap`, then `Shadow_Price == 0`.
- *Why:* Unconstrained capacity should have zero marginal value.

## IV. Related Notes

- [SP_RM_Phase2.md](SP_RM_Phase2.md) — prerequisite DAG tracer
- [SP_RM_Phase4.md](SP_RM_Phase4.md) — next phase (horizon MILP)
- [Math_Supply_Planning_OR_Lexicon.md](../math/Math_Supply_Planning_OR_Lexicon.md) — MILP objective and constraints
