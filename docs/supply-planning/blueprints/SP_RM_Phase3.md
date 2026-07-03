<!-- MIRROR: auto-synced from notes/projects/mrp/supply-planning/blueprints/SP_RM_Phase3.md - do not edit directly. Edit the canonical file in the notes repo and run scripts/sync_project_docs.py -->

---
id: projects-mrp-supply-planning-blueprints-SP_RM_Phase3
type: blueprint
status: draft
dependencies:
tags: []
invariants: []
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
