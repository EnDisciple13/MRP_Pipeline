# Mutation drill harness (v0 — agent-driven runbook)

Runtime counterpart of the Notes trap-fixture harnesses: inject a deliberate, subtle Type B bug; the invariant suite must go red. Every **surviving mutant names a missing invariant** — a work item by construction, and a priority input to `/invariant-propose`.

Theory: Notes `meta/Invariant_Authorship.md` §VI.2 (drills, kill rate) and §VIII (mechanical anchor role). Plan: Notes `inbox/2026-07-04-invariant-loop-plan.md` §II.2.

**Precondition (Stage 0):** priority invariant tests in `tests/invariants/` (2026-07-05): `zero-chaos-delta-zero`, `mass-balance`, `inheritance-gluing`.

## Protocol (per drill)

1. Clean baseline: `py -X utf8 -m pytest tests/invariants/ -q` green; `git status` clean.
2. Apply ONE mutation from the canned list (single-site, minimal diff).
3. Run the invariant suite.
4. Record in the kill matrix: which invariant(s) went red. **All green = surviving mutant** → open a work item naming the missing invariant.
5. `git checkout -- .` (revert). Verify clean baseline before the next drill.

Design rule: **subtle, single-site, Type B** — plausible output, wrong content; something code review would miss.

## Canned mutation list (v0 — 2026-07-05)

| # | Mutation | Target | Should be killed by |
|---|----------|--------|---------------------|
| M1 | Drop one unit from `Locked_Inv` in one allocation branch | `mrp/simulation.py` | `mass-balance` |
| M2 | Skip `extract_inherited_state` — reuse Alpha demand without shift | `pipeline/runner.py` `run_beta` | `inheritance-gluing` |
| M3 | Reverse time comparison in one branch (`release_index >= 0` → `<= 0`) | `mrp/simulation.py` | `mass-balance` or new transition-legality invariant |
| M4 | Double-count one receipt under rare calendar edge (duplicate `sr_t` add) | `mrp/simulation.py` | `mass-balance` |

Expected initial survivors: mutations targeting chaos-support, run-determinism, export-round-trip (not yet in Stage 0 suite).

## Kill matrix (copy per run into `reports/YYYY-MM-DD-<label>.md`)

| Mutant | Applied cleanly? | Invariants red | Killed? | Surviving-mutant work item |
|--------|------------------|----------------|---------|----------------------------|
| M1 | | | | |
| ... | | | | |

## Reports

| Date | Report | Model/agent | Kill rate | Survivors |
|------|--------|-------------|-----------|-----------|
| 2026-07-05 | [2026-07-05-baseline.md](reports/2026-07-05-baseline.md) | Composer 2.5 | M1/M2 killed; M3/M4 partial | chaos-support, determinism (not in Stage 0) |
| 2026-07-06 | [2026-07-06-property-tests.md](reports/2026-07-06-property-tests.md) | Composer | M1/M2/M4/M5/M6/M7 killed; M3 survivor (spec gap) | M3 transition-legality |

Re-run after new invariant tests or model change. Each re-run should add ≥1 new mutation matching current failure sophistication.

## Rules

- One mutation at a time; always revert before the next.
- Never commit a mutation.
- v1 (scripted mutations, CI-schedulable) waits until this list stabilizes across two full runs.
