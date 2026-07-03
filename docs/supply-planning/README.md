<!-- MIRROR: auto-synced from notes/projects/mrp/supply-planning/README.md - do not edit directly. Edit the canonical file in the notes repo and run scripts/sync_project_docs.py -->

---
id: projects-mrp-supply-planning-README
type: project_strategy
status: draft
dependencies:
tags: []
invariants: []
---
# Supply Planning Documentation

Canonical supply-planning strategy docs for the MRP Pipeline. Mirrors are auto-synced into
`mrp_pipeline/docs/supply-planning/` by `scripts/sync_project_docs.py`. Edit files here in the
Notes repo, then run `python scripts/sync_project_docs.py --write`
(Windows: `py scripts/sync_project_docs.py --write`).

## Strategy docs (canonical in Notes)

### Architecture

| Document | Local | GitHub |
|----------|-------|--------|
| State machine architecture | [architecture/MRP_State_Machine_Architecture.md](architecture/MRP_State_Machine_Architecture.md) | [MRP_State_Machine_Architecture.md](https://github.com/endisciple13/notes/blob/main/projects/mrp/supply-planning/architecture/MRP_State_Machine_Architecture.md) |

### Frameworks

| Document | Local | GitHub |
|----------|-------|--------|
| Two Dials framework | [frameworks/Two_Dials_Framework.md](frameworks/Two_Dials_Framework.md) | [Two_Dials_Framework.md](https://github.com/endisciple13/notes/blob/main/projects/mrp/supply-planning/frameworks/Two_Dials_Framework.md) |

### Roadmaps

| Document | Local | GitHub |
|----------|-------|--------|
| V2 engine roadmap | [roadmaps/MRP_V2_Roadmap.md](roadmaps/MRP_V2_Roadmap.md) | [MRP_V2_Roadmap.md](https://github.com/endisciple13/notes/blob/main/projects/mrp/supply-planning/roadmaps/MRP_V2_Roadmap.md) |
| Supply planning tool roadmap | [roadmaps/Supply_Planning_Tool_Roadmap.md](roadmaps/Supply_Planning_Tool_Roadmap.md) | [Supply_Planning_Tool_Roadmap.md](https://github.com/endisciple13/notes/blob/main/projects/mrp/supply-planning/roadmaps/Supply_Planning_Tool_Roadmap.md) |

### Context (optional)

| Document | Local | GitHub |
|----------|-------|--------|
| SAP enterprise context | [context/SAP_Enterprise_Context.md](context/SAP_Enterprise_Context.md) | [SAP_Enterprise_Context.md](https://github.com/endisciple13/notes/blob/main/projects/mrp/supply-planning/context/SAP_Enterprise_Context.md) |

### Blueprints (Speedboat phases)

| Phase | Local | GitHub |
|-------|-------|--------|
| Phase 1: Sandbox MRP | [blueprints/SP_RM_Phase1.md](blueprints/SP_RM_Phase1.md) | [SP_RM_Phase1.md](https://github.com/endisciple13/notes/blob/main/projects/mrp/supply-planning/blueprints/SP_RM_Phase1.md) |
| Phase 2: DAG tracer | [blueprints/SP_RM_Phase2.md](blueprints/SP_RM_Phase2.md) | [SP_RM_Phase2.md](https://github.com/endisciple13/notes/blob/main/projects/mrp/supply-planning/blueprints/SP_RM_Phase2.md) |
| Phase 3: Micro MILP | [blueprints/SP_RM_Phase3.md](blueprints/SP_RM_Phase3.md) | [SP_RM_Phase3.md](https://github.com/endisciple13/notes/blob/main/projects/mrp/supply-planning/blueprints/SP_RM_Phase3.md) |
| Phase 4: Horizon MILP | [blueprints/SP_RM_Phase4.md](blueprints/SP_RM_Phase4.md) | [SP_RM_Phase4.md](https://github.com/endisciple13/notes/blob/main/projects/mrp/supply-planning/blueprints/SP_RM_Phase4.md) |
| Phase 5: Portfolio MILP | [blueprints/SP_RM_Phase5.md](blueprints/SP_RM_Phase5.md) | [SP_RM_Phase5.md](https://github.com/endisciple13/notes/blob/main/projects/mrp/supply-planning/blueprints/SP_RM_Phase5.md) |

## Reading order

1. [architecture/MRP_State_Machine_Architecture.md](architecture/MRP_State_Machine_Architecture.md) — why the engine must be sequential (vectorized trap, healing loop)
2. [../../../math/supply-planning/Math_Supply_Planning_OR_Lexicon.md](math/Math_Supply_Planning_OR_Lexicon.md) — OR vocabulary and state/control equations
3. [roadmaps/MRP_V2_Roadmap.md](roadmaps/MRP_V2_Roadmap.md) — cost optimization and V2 feature gaps
4. [frameworks/Two_Dials_Framework.md](frameworks/Two_Dials_Framework.md) — macro/micro decoupling + peace/war closed loop
5. [roadmaps/Supply_Planning_Tool_Roadmap.md](roadmaps/Supply_Planning_Tool_Roadmap.md) — battleship vs speedboats narrative
6. [blueprints/SP_RM_Phase1.md](blueprints/SP_RM_Phase1.md) … [SP_RM_Phase5.md](blueprints/SP_RM_Phase5.md) — phased build specs + Layer 4 invariants
7. [context/SAP_Enterprise_Context.md](context/SAP_Enterprise_Context.md) — SAP IBP/PP/MM mapping (optional reference)

## Documentation map

Three overlapping phase schemes (Pipeline Phases 1–7, Speedboat Phases 1–5, MRP V2 features). Canonical explanation: [Documentation map](../../Project_Documentation.md#documentation-map) in `Project_Documentation.md`.

## Math (canonical in Notes, mirrored to mrp_pipeline)

Edit in **Notes** `math/supply-planning/`. Mirrors land in `mrp_pipeline/docs/supply-planning/math/`.

| Document | Canonical (Notes) | Mirror (mrp_pipeline) |
|----------|-------------------|----------------------|
| Math index | [math/README.md](../../../Notes/math/README.md) | — (Notes-only index) |
| [Math_Safety_Stock_Derivation.md](math/Math_Safety_Stock_Derivation.md) | [GitHub](https://github.com/endisciple13/notes/blob/main/math/supply-planning/Math_Safety_Stock_Derivation.md) | [math/Math_Safety_Stock_Derivation.md](https://github.com/endisciple13/mrp_pipeline/blob/main/docs/supply-planning/math/Math_Safety_Stock_Derivation.md) |
| [Math_Supply_Planning_OR_Lexicon.md](math/Math_Supply_Planning_OR_Lexicon.md) | [GitHub](https://github.com/endisciple13/notes/blob/main/math/supply-planning/Math_Supply_Planning_OR_Lexicon.md) | [math/Math_Supply_Planning_OR_Lexicon.md](https://github.com/endisciple13/mrp_pipeline/blob/main/docs/supply-planning/math/Math_Supply_Planning_OR_Lexicon.md) |
| [Math_Advanced_OR_Addendum.md](math/Math_Advanced_OR_Addendum.md) | [GitHub](https://github.com/endisciple13/notes/blob/main/math/supply-planning/Math_Advanced_OR_Addendum.md) | [math/Math_Advanced_OR_Addendum.md](https://github.com/endisciple13/mrp_pipeline/blob/main/docs/supply-planning/math/Math_Advanced_OR_Addendum.md) |

## Meta theory (notes-only, not mirrored)

| Document | GitHub |
|----------|--------|
| [Meta_Workflow.md](../../../Notes/meta/Meta_Workflow.md) | [Meta_Workflow.md](https://github.com/endisciple13/notes/blob/main/meta/Meta_Workflow.md) |
| [OR_AI_ASI.md](../../../Notes/meta/OR_AI_ASI.md) | [OR_AI_ASI.md](https://github.com/endisciple13/notes/blob/main/meta/OR_AI_ASI.md) |
| [AI_Deterministic_Delegation.md](../../../Notes/meta/AI_Deterministic_Delegation.md) | [AI_Deterministic_Delegation.md](https://github.com/endisciple13/notes/blob/main/meta/AI_Deterministic_Delegation.md) |
| [Layer4_TypeB_Auditing.md](../../../Notes/meta/Layer4_TypeB_Auditing.md) | [Layer4_TypeB_Auditing.md](https://github.com/endisciple13/notes/blob/main/meta/Layer4_TypeB_Auditing.md) |

## Layer 4 invariant summary (canonical in blueprints)

Canonical invariant definitions live in [blueprints/SP_RM_PhaseN.md](blueprints/SP_RM_Phase1.md). Summary for `mrp_pipeline` test/schema planning:

| Phase | Blueprint | Key invariants |
|-------|-----------|----------------|
| 1 — Sandbox MRP | [SP_RM_Phase1.md](blueprints/SP_RM_Phase1.md) | Conservation of mass; non-negativity; lead-time offset; MOQ modulo |
| 2 — DAG tracer | [SP_RM_Phase2.md](blueprints/SP_RM_Phase2.md) | Topological acyclicity; quantity-per conservation; nilpotent BOM matrix |
| 3 — Micro MILP | [SP_RM_Phase3.md](blueprints/SP_RM_Phase3.md) | Capacity bound audit; integer floor; $Z_{MILP} \le Z_{MRP}$; complementary slackness |
| 4 — Horizon MILP | [SP_RM_Phase4.md](blueprints/SP_RM_Phase4.md) | Terminal state $\ge SS$; frozen-zone POR lock |
| 5 — Portfolio MILP | [SP_RM_Phase5.md](blueprints/SP_RM_Phase5.md) | Mutually exclusive setup binaries; setup triangle inequality |

When dynamic safety stock lands, also enforce $ROP = E[DDLT] + SS$ per [Math_Safety_Stock_Derivation.md](math/Math_Safety_Stock_Derivation.md).

## Implementation docs (mrp_pipeline, not mirrored)

| Document | Purpose |
|----------|---------|
| [Project_Documentation.md](https://github.com/endisciple13/mrp_pipeline/blob/main/Project_Documentation.md) | Operational architecture reference (Alpha/Beta/Delta pipeline) |

## Keeping mirrors in sync

```bash
# from the Notes repo root
python scripts/sync_project_docs.py --check   # detect drift (used in CI / pre-commit)
python scripts/sync_project_docs.py --write   # regenerate mirror files in mrp_pipeline
```

Full project note index: [../README.md](../../../Notes/projects/mrp/README.md)
