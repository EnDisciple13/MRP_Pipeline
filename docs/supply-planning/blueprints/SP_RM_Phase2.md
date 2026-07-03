<!-- MIRROR: auto-synced from notes/projects/mrp/supply-planning/blueprints/SP_RM_Phase2.md - do not edit directly. Edit the canonical file in the notes repo and run scripts/sync_project_docs.py -->

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
