<!-- MIRROR: auto-synced from notes/projects/mrp/supply-planning/blueprints/SP_RM_Phase2.md - do not edit directly. Edit the canonical file in the notes repo and run scripts/sync_project_docs.py -->

---
id: projects-mrp-supply-planning-blueprints-SP_RM_Phase2
type: blueprint
status: draft
dependencies:
  - math/supply-planning/Math_Supply_Planning_OR_Lexicon.md
  - projects/mrp/supply-planning/blueprints/SP_RM_Phase1.md
  - projects/mrp/supply-planning/frameworks/MRP_Invariant_Suite.md
tags: []
invariants:
  - id: bom-dag
    statement: "Bill of Materials graph is a directed acyclic graph with no self-requiring assemblies"
  - id: quantity-per-conservation
    statement: "Gozinto quantity-per factors multiply correctly through BOM explosion"
inherited_invariants:
  - id: inventory-balance
    from: math/supply-planning/Math_Supply_Planning_OR_Lexicon.md
    status: planned
    enforced_by: "tests/lexicon/test_inventory_balance.py::test_pab_recursion_matches_lexicon"
  - id: non-negative-controls
    from: math/supply-planning/Math_Supply_Planning_OR_Lexicon.md
    status: planned
    enforced_by: "tests/lexicon/test_non_negative_controls.py::test_inventory_and_receipts_non_negative"
  - id: conservation-of-mass
    from: projects/mrp/supply-planning/blueprints/SP_RM_Phase1.md
    status: planned
    enforced_by: "tests/phase1/test_conservation_of_mass.py::test_supply_demand_balance"
  - id: non-negative-inventory
    from: projects/mrp/supply-planning/blueprints/SP_RM_Phase1.md
    status: planned
    enforced_by: "tests/phase1/test_non_negative_inventory.py::test_inventory_non_negative"
  - id: lead-time-offset
    from: projects/mrp/supply-planning/blueprints/SP_RM_Phase1.md
    status: planned
    enforced_by: "tests/phase1/test_lead_time_offset.py::test_zero_receipts_within_lead_time"
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
# Technical Blueprint: Phase 2 - Root-Cause Tracer (DAG Traversal)

## I. Objective

**CS / English:** Build a graph search algorithm that reads a messy list of SAP exception messages and traces them vertically through the BOM to find the originating constraint. Bridges single-node simulation (Phase 1) to multi-level factory reality. Reduces hours of manual Excel filtering to seconds.

**Mathematical Formalization:** BOM as DAG; Gozinto matrix and quantity-per conservation in [Math_Supply_Planning_OR_Lexicon.md](../math/Math_Supply_Planning_OR_Lexicon.md).

**Prerequisites:** [SP_RM_Phase1.md](SP_RM_Phase1.md) complete.

## II. Target Architecture

A Python script that:

- Ingests SAP exception messages (or simulated equivalents)
- Traverses the BOM DAG top-down or bottom-up to peg root-cause constraints
- Outputs the originating node (e.g., single failing screw vs 800 phantom alarms)

## III. Layer 4 Invariants

**Topological Acyclicity (No Infinite Loops):**

DAG depth must be strictly less than the total number of unique parts in the database.

*Why:* A cyclic BOM (kit requires screw, screw requires kit) causes infinite loops.

**Conservation of Quantity Per:**

If a parent kit requires exactly 4 screws ($Q=4$), the traced shortage of screws must be an exact modulo of parent demand:

$$Exceptions_{child} \equiv 0 \pmod Q$$

**Orphaned Demand Check:** Total dependent demand at the bottom of the graph must map back to parent gross requirements multiplied by edge weights.

- *Assertion:* $\sum \text{Child Req} = \sum (\text{Parent POR} \times \text{Quantity Per})$.
- *Why:* Proves no material requirements were lost in matrix explosion.

**Nilpotent Matrix Verification:** The adjacency matrix ($B$) of the BOM must be strictly nilpotent.

- *Assertion:* $B^k = 0$, where $k$ is the maximum BOM depth.
- *Why:* Rigorous pure-math check for cyclic loops ($B^k \neq 0$ implies a recursive loop).

## IV. Related Notes

- [SP_RM_Phase1.md](SP_RM_Phase1.md) — prerequisite sandbox MRP
- [SP_RM_Phase3.md](SP_RM_Phase3.md) — next phase (micro MILP)
- [Math_Supply_Planning_OR_Lexicon.md](../math/Math_Supply_Planning_OR_Lexicon.md) — DAG / Gozinto vocabulary
