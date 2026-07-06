# MRP mutation drill — property tests (2026-07-06)

Executor: Composer | Post-implementation anchor: Hypothesis property suite in `tests/invariants/` + `tests/lexicon/`

## Preconditions

- `py -X utf8 -m pytest tests/invariants/ tests/lexicon/ -q` → 19 passed, 1 xfailed (`zero-chaos-delta-zero` strict Δ≡0 — calendar seam implementation defect)
- Drill driver: `tests/mutation/run_property_drill.py`

## Kill matrix

| Mutant | Killed? | Killer |
|--------|---------|--------|
| M1 Drop Locked_Inv unit | **Y** | `mass-balance` |
| M2 Skip demand shift | **Y** | `inheritance-gluing` |
| M3 Reverse release_index | **N** | Spec defect — no transition-legality property; mass-balance unaffected on golden paths |
| M4 Double-count receipt | **Y** | `mass-balance` / lexicon |
| M5 Chaos leak to other SKU | **Y** | `chaos-support` |
| M6 Row-order flip | **Y** | `run-determinism` (via `df.equals`) |
| M7 Excel leading-zero coercion | **Y** | `export-round-trip` |

**Exit condition (SP §IV.2):** M1/M2 remain killed; chaos/determinism/export mutants killed. **SATISFIED** (M3 documented as spec gap).

## Spec defects noted

- **zero-chaos-delta-zero:** strict Δ≡0 xfail on headless pipeline (calendar seam).
- **M3:** surviving mutant → propose transition-legality property in future spec revision.

## Regression

Re-run after suite changes. Record in `tests/mutation/reports/`.
