# MRP Pipeline — agent entry point

Supply-planning MRP engine. Registry id `mrp_pipeline` in the sibling Notes repo (`../Notes/registry.yaml`). This repo is **proof space** (implementation); strategy and roadmap truth is proposition space in Notes.

## Read order

1. [Project_Documentation.md](Project_Documentation.md) — application + implementation doc (single layered doc)
2. `docs/supply-planning/` — strategy mirrors, generated from Notes

## Critical rules

- **Never edit files under `docs/supply-planning/`** — they carry a `MIRROR:` banner and are overwritten on sync. Canonical files live in `../Notes/projects/mrp/supply-planning/`; edit there, then run `py scripts/sync_project_docs.py --write` from the Notes repo root, and commit the regenerated mirrors here separately.
- Roadmap/planning status is canonical in Notes; as-built truth is canonical here (`Project_Documentation.md`).
- Cross-repo conventions: `../Notes/AGENTS.md`. Agent config channels: `../Notes/Agent_Routing.md`.
- Windows: use `py`, not `python`, for scripts.
