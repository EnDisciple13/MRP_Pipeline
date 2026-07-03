<!-- MIRROR: auto-synced from notes/projects/mrp/supply-planning/blueprints/SP_RM_Phase1.md - do not edit directly. Edit the canonical file in the notes repo and run scripts/sync_project_docs.py -->

# Technical Blueprint: Phase 1 - Sandbox Simulator (Local MRP Engine)

## I. Objective

**CS / English:** Build a standalone script that runs the deterministic netting loop ($I_t = PAB_{t-1} + S_t - D_t$) and applies lead-time offsets for a specific subset of parts. This is the foundation — you cannot optimize a cost function if netting math is wrong. Unlocks immediate offline scenario modeling (e.g., which hospitals stock out when a supplier is 7 days late).

**Mathematical Formalization:** See [MRP_State_Machine_Architecture.md](../architecture/MRP_State_Machine_Architecture.md) for sequential state-machine physics vs the vectorized trap. State/control vocabulary: [Math_Supply_Planning_OR_Lexicon.md](../../../../Notes/math/supply-planning/Math_Supply_Planning_OR_Lexicon.md).

**Prerequisites:** None. Read [MRP_State_Machine_Architecture.md](../architecture/MRP_State_Machine_Architecture.md) before implementing.

## II. Target Architecture

A standalone Python script that:

- Runs the deterministic netting loop for a subset of parts
- Applies lead-time offsets ($L$) to planned receipts
- Outputs PAB, gross requirements, net requirements, and planned orders offline
- Crashes with explicit assertions if Layer 4 invariants fail (see §III)

## III. Layer 4 Invariants

When you build this speedboat, write explicit `assert` statements at the end of the script. If an invariant fails, the script crashes before the planner sees the report.

**Conservation of Mass (Flow Balance):**

$$\sum_{t=1}^{T} S_t + I_0 = \sum_{t=1}^{T} D_t + I_T$$

*Why:* Catches time-shift leaks if the loop drops an array index or shifts a bucket incorrectly.

**Non-Negativity of Physics:**

$$I_t \ge 0 \quad \text{and} \quad PR_t \ge 0 \quad \text{for all } t$$

*Why:* You cannot hold negative physical inventory or order negative deliveries.

**Lead Time Offset Integrity:** If lead time ($L$) is 2 days and there are no open orders in transit, planned receipts for today and tomorrow must be zero.

- *Assertion:* If `sum(S[0:L]) == 0`, then `sum(PR[0:L]) == 0`.
- *Why:* The engine cannot receive material faster than $L$.

**Lot Size Modulo Check:** If MOQ is 50, every triggered POR must be a clean multiple of 50.

- *Assertion:* `POR_t % MOQ == 0` for all $t$.
- *Why:* Prevents floating-point rounding errors (e.g., POR = 49.99).

## IV. Related Notes

- [MRP_State_Machine_Architecture.md](../architecture/MRP_State_Machine_Architecture.md) — sequential MRP foundation
- [Supply_Planning_Tool_Roadmap.md](../roadmaps/Supply_Planning_Tool_Roadmap.md) — battleship vs speedboats narrative
- [SP_RM_Phase2.md](SP_RM_Phase2.md) — next phase (DAG tracer)
- [Math_Supply_Planning_OR_Lexicon.md](../../../../Notes/math/supply-planning/Math_Supply_Planning_OR_Lexicon.md) — OR vocabulary
