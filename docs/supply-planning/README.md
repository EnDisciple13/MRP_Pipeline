<!-- MIRROR: auto-synced from notes/projects/mrp/supply-planning/README.md - do not edit directly. Edit the canonical file in the notes repo and run scripts/sync_project_docs.py -->

# Supply Planning Documentation

Canonical supply-planning strategy docs for the MRP Pipeline. Mirrors are auto-synced into
`mrp_pipeline/docs/supply-planning/` by `scripts/sync_project_docs.py`. Edit files here in the
Notes repo, then run `python scripts/sync_project_docs.py --write`
(Windows: `py scripts/sync_project_docs.py --write`).

## Strategy docs (canonical in Notes)

| Document | Local | GitHub |
|----------|-------|--------|
| State machine architecture | [MRP_State_Machine_Architecture.md](MRP_State_Machine_Architecture.md) | [MRP_State_Machine_Architecture.md](https://github.com/endisciple13/notes/blob/main/projects/mrp/supply-planning/MRP_State_Machine_Architecture.md) |
| V2 engine roadmap | [MRP_V2_Roadmap.md](MRP_V2_Roadmap.md) | [MRP_V2_Roadmap.md](https://github.com/endisciple13/notes/blob/main/projects/mrp/supply-planning/MRP_V2_Roadmap.md) |
| Two Dials framework | [Two_Dials_Framework.md](Two_Dials_Framework.md) | [Two_Dials_Framework.md](https://github.com/endisciple13/notes/blob/main/projects/mrp/supply-planning/Two_Dials_Framework.md) |
| Supply planning tool roadmap | [Supply_Planning_Tool_Roadmap.md](Supply_Planning_Tool_Roadmap.md) | [Supply_Planning_Tool_Roadmap.md](https://github.com/endisciple13/notes/blob/main/projects/mrp/supply-planning/Supply_Planning_Tool_Roadmap.md) |
| SAP enterprise context | [SAP_Enterprise_Context.md](SAP_Enterprise_Context.md) | [SAP_Enterprise_Context.md](https://github.com/endisciple13/notes/blob/main/projects/mrp/supply-planning/SAP_Enterprise_Context.md) |

## Reading order

1. [MRP_State_Machine_Architecture.md](MRP_State_Machine_Architecture.md) — why the engine must be sequential (vectorized trap, healing loop)
2. [../../../math/Math_Supply_Planning_OR_Lexicon.md](../../../Notes/math/Math_Supply_Planning_OR_Lexicon.md) — OR vocabulary and state/control equations
3. [MRP_V2_Roadmap.md](MRP_V2_Roadmap.md) — cost optimization and V2 feature gaps
4. [Two_Dials_Framework.md](Two_Dials_Framework.md) — macro/micro decoupling + peace/war closed loop
5. [Supply_Planning_Tool_Roadmap.md](Supply_Planning_Tool_Roadmap.md) — phased Python Speedboat build with Layer 4 invariants
6. [SAP_Enterprise_Context.md](SAP_Enterprise_Context.md) — SAP IBP/PP/MM mapping (optional reference)

## Documentation map

Three overlapping phase schemes (Pipeline Phases 1–7, Speedboat Phases 1–5, MRP V2 features). Canonical explanation: [Documentation map](../../Project_Documentation.md#documentation-map) in `Project_Documentation.md`.

## Reusable theory (notes-only, not mirrored)

| Document | GitHub |
|----------|--------|
| [Math_Safety_Stock_Derivation.md](../../../Notes/math/Math_Safety_Stock_Derivation.md) | [Math_Safety_Stock_Derivation.md](https://github.com/endisciple13/notes/blob/main/math/Math_Safety_Stock_Derivation.md) |
| [Math_Supply_Planning_OR_Lexicon.md](../../../Notes/math/Math_Supply_Planning_OR_Lexicon.md) | [Math_Supply_Planning_OR_Lexicon.md](https://github.com/endisciple13/notes/blob/main/math/Math_Supply_Planning_OR_Lexicon.md) |
| [Meta_Workflow.md](../../../Notes/meta/Meta_Workflow.md) | [Meta_Workflow.md](https://github.com/endisciple13/notes/blob/main/meta/Meta_Workflow.md) |
| [OR_AI_ASI.md](../../../Notes/meta/OR_AI_ASI.md) | [OR_AI_ASI.md](https://github.com/endisciple13/notes/blob/main/meta/OR_AI_ASI.md) |
| [AI_Deterministic_Delegation.md](../../../Notes/meta/AI_Deterministic_Delegation.md) | [AI_Deterministic_Delegation.md](https://github.com/endisciple13/notes/blob/main/meta/AI_Deterministic_Delegation.md) |
| [Layer4_TypeB_Auditing.md](../../../Notes/meta/Layer4_TypeB_Auditing.md) | [Layer4_TypeB_Auditing.md](https://github.com/endisciple13/notes/blob/main/meta/Layer4_TypeB_Auditing.md) |

## Layer 4 invariant flags (from Supply Planning Tool Roadmap)

| Phase | Invariants to enforce in `mrp_pipeline` tests/schemas |
|-------|------------------------------------------------------|
| 1 — Sandbox MRP | Conservation of mass; non-negativity; lead-time offset; MOQ modulo |
| 2 — DAG tracer | Topological acyclicity; quantity-per conservation; nilpotent BOM matrix |
| 3 — Micro MILP | Capacity bound audit; integer floor; $Z_{MILP} \le Z_{MRP}$; complementary slackness |
| 4 — Horizon MILP | Terminal state $\ge SS$; frozen-zone POR lock |
| 5 — Portfolio MILP | Mutually exclusive setup binaries; setup triangle inequality |

When dynamic safety stock lands, also enforce $ROP = E[DDLT] + SS$ per [Math_Safety_Stock_Derivation.md](../../../Notes/math/Math_Safety_Stock_Derivation.md).

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
