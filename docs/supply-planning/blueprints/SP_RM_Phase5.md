<!-- MIRROR: auto-synced from notes/projects/mrp/supply-planning/blueprints/SP_RM_Phase5.md - do not edit directly. Edit the canonical file in the notes repo and run scripts/sync_project_docs.py -->

---
id: projects-mrp-supply-planning-blueprints-SP_RM_Phase5
type: blueprint
status: draft
dependencies:
  - math/supply-planning/Math_Advanced_OR_Addendum.md
  - projects/mrp/supply-planning/blueprints/SP_RM_Phase4.md
  - projects/mrp/supply-planning/frameworks/Two_Dials_Framework.md
  - projects/mrp/supply-planning/frameworks/MRP_Invariant_Suite.md
tags: []
invariants:
  - id: portfolio-conservation
    statement: "Portfolio MILP disaggregation preserves total resource allocation across product families"
inherited_invariants:
  - id: bellman-optimality
    from: math/supply-planning/Math_Advanced_OR_Addendum.md
    status: planned
    enforced_by: "tests/or/test_bellman_optimality.py::test_bellman_backup_holds"
  - id: disaggregation-conservation
    from: math/supply-planning/Math_Advanced_OR_Addendum.md
    status: planned
    enforced_by: "tests/or/test_disaggregation_conservation.py::test_family_totals_preserved"
  - id: cumulative-lead-time
    from: projects/mrp/supply-planning/blueprints/SP_RM_Phase4.md
    status: planned
    enforced_by: "tests/phase4/test_cumulative_lead_time.py::test_multi_echelon_lead_time_respected"
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
# Technical Blueprint: Phase 5 - Portfolio Optimizer (Jurisdictional Resource Disaggregation)

## I. Objective

**CS / English:** Flatten the vertical BOM and isolate a single horizontal slice (e.g., all Level 3 parts on one machine). Optimize the entire vector of sibling SKUs simultaneously against a strict capacity allocation (e.g., 40%), balancing setup costs ($C_{setup}$) against holding costs ($C_{hold}$). Mathematical resolution to the presheaf collision within one jurisdiction.

**Mathematical Formalization:** Sheaf/presheaf failure, resource disaggregation, and Dantzig-Wolfe in [Math_Advanced_OR_Addendum.md](../math/Math_Advanced_OR_Addendum.md).

**Prerequisites:** [SP_RM_Phase4.md](SP_RM_Phase4.md) complete.

## II. Target Architecture

Master portfolio MILP that:

- Optimizes a vector of sibling SKUs on one shared resource
- Uses binary setup switches ($Y \in \{0,1\}$) for changeover costs
- Enforces mutually exclusive machine use and setup cost matrix sanity

## III. Layer 4 Invariants

**Binary Big-M Lock:** If production $u_{i,t} > 0$, the binary switch must be 1:

$$u_{i,t} > 0 \implies Y_{i,t} = 1$$

*Why:* Poorly formatted Big-M lets the solver produce units while leaving $Y=0$ to avoid setup penalty.

**Mutually Exclusive State:** Parts sharing one CNC spindle cannot run simultaneously:

$$Y_{Cervical, t} + Y_{Trauma, t} \le 1$$

*Why:* Prevents the solver from stacking production when the $\le$ constraint is too loose.

**Setup Triangle Inequality:** Setup cost matrix must satisfy:

$$C(A,C) \le C(A,B) + C(B,C)$$

*Why:* Violations let the solver exploit fake micro-changeovers for cheaper transitions.

## IV. Related Notes

- [SP_RM_Phase4.md](SP_RM_Phase4.md) — prerequisite horizon MILP
- [Math_Advanced_OR_Addendum.md](../math/Math_Advanced_OR_Addendum.md) — presheaf / portfolio math
- [Two_Dials_Framework.md](../frameworks/Two_Dials_Framework.md) — macro/micro decoupling context
