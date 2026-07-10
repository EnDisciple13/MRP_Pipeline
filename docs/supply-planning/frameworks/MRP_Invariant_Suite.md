<!-- MIRROR: auto-synced from notes/projects/mrp/supply-planning/frameworks/MRP_Invariant_Suite.md - do not edit directly. Edit the canonical file in the notes repo and run scripts/sync_project_docs.py -->

---
id: projects-mrp-supply-planning-frameworks-MRP_Invariant_Suite
type: framework
status: verified
dependencies:
  - math/supply-planning/Math_Supply_Planning_OR_Lexicon.md
  - meta/rigor/Invariant_Authorship.md
  - meta/verification/Layer4_TypeB_Auditing.md
  - projects/mrp/supply-planning/architecture/MRP_State_Machine_Architecture.md
tags:
  - invariants
  - layer4
invariants:
  - id: zero-chaos-delta-zero
    statement: "A Beta run with an empty chaos event list yields a Delta output that is identically zero"
  - id: mass-balance
    statement: "For every SKU and horizon: ending_PAB == starting_PAB + sum(receipts) - sum(demand)"
  - id: inheritance-gluing
    statement: "Beta initial state equals Alpha final state at the cut date, field by field"
  - id: chaos-support
    statement: "The state diff produced by chaos injection has support contained in the event's declared targets"
  - id: run-determinism
    statement: "Identical seed and inputs produce byte-identical pipeline outputs"
  - id: export-round-trip
    statement: "Values read back from generated Excel deliverables equal the source dataframe values"
---
# MRP Invariant Suite (Layer 4 Validation Targets)

> Applied inventory of Layer 4 invariants for the MRP engine's **already-implemented** phases. Theory and taxonomy: [Invariant_Authorship.md](../../../../Notes/meta/rigor/Invariant_Authorship.md). Audit mechanisms and ROI tiers: [Layer4_TypeB_Auditing.md](../../../../Notes/meta/verification/Layer4_TypeB_Auditing.md). State-space definitions (Alpha/Beta/Delta): [MRP_State_Machine_Architecture.md](../architecture/MRP_State_Machine_Architecture.md).

## Enforcement status (as of 2026-07-06)

**Hypothesis property suite implemented** in `tests/invariants/` and `tests/lexicon/` (pytest + hypothesis). **Named tests:** `zero-chaos-delta-zero`, `mass-balance`, `inheritance-gluing`, `chaos-support`, `run-determinism`, `export-round-trip`, `inventory-balance`, `non-negative-controls`. **Mutation drill 2026-07-06:** M1/M2/M4/M5/M6/M7 killed; M3 survivor documented as transition-legality spec gap. **xfail:** strict Δ≡0 on headless pipeline (calendar seam).

**Existing (unchanged):** Dashboard audit and smoke/path tests.

## The suite (priority order)

| # | Invariant id | Class | Statement | Target modules |
|---|--------------|-------|-----------|----------------|
| 1 | `zero-chaos-delta-zero` | Functional law (identity) | Beta run with empty chaos list ⇒ Delta ≡ 0 | `mrp/state.py` → `mrp/simulation.py` → `mrp/delta.py` |
| 2 | `mass-balance` | Conservation | `ending_PAB == starting_PAB + Σ receipts − Σ demand` per SKU/horizon (telescoped PAB recursion) | `mrp/simulation.py` |
| 3 | `inheritance-gluing` | Inductive / gluing | Beta initial state == Alpha final state at cut date, field by field | `mrp/state.py::extract_inherited_state` |
| 4 | `chaos-support` | Frame rule | Pre/post-injection state diff has support ⊆ event's declared targets | `mrp/state.py::apply_chaos_events` |
| 5 | `run-determinism` | Functional law | Same seed + inputs ⇒ byte-identical outputs, run twice | `pipeline/runner.py` |
| 6 | `export-round-trip` | Round-trip | Excel values read back == source dataframe values | `mrp/exports/excel/` |

### Notes per invariant

1. **Zero-chaos ⇒ Delta ≡ 0** is a theorem of the Layer 1 spec (Delta measures deviation from baseline; no perturbation ⇒ no deviation). It exercises the full Alpha→Beta→Delta path end to end, needs no ground truth, and is ~20 lines. **Implement first** — it is the identity-morphism test for the whole engine.
2. **Mass balance** is the telescoped form of the per-day PAB recursion $I_{t+1} = I_t + R_t - D_t$, where PAB (projected available balance) is the OR lexicon's inventory state $I_t$ — see [Math_Supply_Planning_OR_Lexicon.md](../math/Math_Supply_Planning_OR_Lexicon.md). Randomize demand arrays with Hypothesis. Catches the classic silent failure: an allocation refactor that drops one unit in an edge case.
3. **Inheritance gluing** is a cocycle condition on the seam between timelines — precisely where silent drift enters path-dependent systems.
4. **Chaos support** is the frame rule of separation logic: what the event did not declare, it must not touch. A demand-shock event may change demand rows; anything else changing means the injector leaks.
5. **Determinism** is a prerequisite for the Phase 7 Excel↔Python isomorphism test (a full bisimulation), which will be flaky unless this holds first.
6. **Export round-trip:** presentation layers are where correct numbers go to die.

## First rep

**Done (2026-07-06):** Hypothesis property suite per [SP_Property_Test_Specs.md](../blueprints/SP_Property_Test_Specs.md); mutation drill 2026-07-06 (M1/M2/M4/M5/M6/M7 killed).

**Next:** transition-legality property for M3 survivor; strict zero-chaos Δ≡0 calendar seam fix.

## Related Notes

- [Invariant_Authorship.md](../../../../Notes/meta/rigor/Invariant_Authorship.md) — theory, taxonomy, authorship split.
- [MRP_State_Machine_Architecture.md](../architecture/MRP_State_Machine_Architecture.md) — Alpha/Beta/Delta state space these invariants defend.
- [MRP_V2_Roadmap.md](../roadmaps/MRP_V2_Roadmap.md) — engine evolution; V2 features inherit this suite.
- [SP_RM_Phase1.md](../blueprints/SP_RM_Phase1.md) — phased blueprints; blueprints should map inherited invariant ids to named tests.
