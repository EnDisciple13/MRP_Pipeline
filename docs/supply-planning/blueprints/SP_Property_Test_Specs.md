<!-- MIRROR: auto-synced from notes/projects/mrp/supply-planning/blueprints/SP_Property_Test_Specs.md - do not edit directly. Edit the canonical file in the notes repo and run scripts/sync_project_docs.py -->

---
id: projects-mrp-supply-planning-blueprints-SP_Property_Test_Specs
type: blueprint
status: draft
dependencies:
  - math/supply-planning/Math_Supply_Planning_OR_Lexicon.md
  - projects/mrp/supply-planning/frameworks/MRP_Invariant_Suite.md
tags:
  - invariants
  - layer4
  - hypothesis
  - property-testing
invariants: []
---
# SP Property Test Specs (Supply Planning & MRP Engine)

> **Rule of Thumb:** Always derive property-test specifications strictly from formal OR mathematical definitions and state-machine boundaries without inspecting engine implementation internals.
>
> **Note on Schema Sequencing:** The `inherited_invariants:` frontmatter block presumes the chain-auditor plan's FM-015..FM-018 rules have landed in `scripts/validate_frontmatter.py`. Per plan instruction §IV.6, all rows are shipped as `status: planned` during initial Fable authorship and must not be stripped.
>
> **Theory & Mathematical Foundations:** Autoformalization of Layer 1 invariants from [MRP_Invariant_Suite.md](../frameworks/MRP_Invariant_Suite.md) and Operations Research foundations from [Math_Supply_Planning_OR_Lexicon.md](../math/Math_Supply_Planning_OR_Lexicon.md) into universally quantified Hypothesis property tests. Governed by [Invariant_Authorship.md](../../../../Notes/meta/rigor/Invariant_Authorship.md) §VI.4 (progression to Hypothesis properties per module) and §VII.1 (test-writer non-circularity).

## I. Fable Autoformalization Strategy & Scope

> **Rule of Thumb:** Randomize demand vectors, scheduled receipts, and lead-time offsets across multi-SKU horizons to expose silent unit drops and netting logic edge cases.

This blueprint establishes the Layer 2 implementation contract for upgrading the Material Requirements Planning (MRP) engine's verification harness from static unit tests (Stage 0) to universally quantified property tests using Python's `hypothesis` library.

### 1. Authorship Independence & Non-Circularity
To preserve the verification integrity required by `Invariant_Authorship.md` §VII.1, all specifications in this document are derived strictly from:
1. The formal invariant statements and priority orderings in `MRP_Invariant_Suite.md`.
2. The discrete-time dynamical system equations, Leontief inverse matrices, and Bang-Bang control laws in `Math_Supply_Planning_OR_Lexicon.md`.
3. The three-world state-space definitions (Alpha baseline, Beta simulation, Delta deviation).

**Hard Constraint:** No engine implementation internals (`mrp/*.py`, `pipeline/*.py`) were inspected during authorship. Test developers implementing this blueprint must code against the interface contracts and mathematical definitions defined below without referencing internal algorithmic implementations.

### 2. Randomization Strategy for Supply Planning
Supply planning engines are particularly vulnerable to boundary defects where netting loops drop single units across multi-period horizons or misapply lead-time offsets ($L$) under zero-demand epochs. While Stage 0 tests verify basic algebra on static golden fixtures, property testing must randomize:
* **Multi-SKU Bill of Materials (BOM):** Gozinto matrices ($B$) with varying depth and component ratios.
* **Temporal Horizons ($T$):** Randomized planning horizons ranging from 1 to 104 periods (weeks/days).
* **Forcing Functions ($D_t$):** Demand arrays featuring sparse demand, extreme demand shocks, and trailing zeroes.
* **Predetermined Supply ($S_t$):** Scheduled receipt arrays arriving across arbitrary lead-time offsets.

---

## II. Missing Invariants & End-to-End Theorems

> **Rule of Thumb:** Implement universally quantified Hypothesis properties for all missing invariants and end-to-end theorems to eradicate future M-series mutants.

This section defines the P1–P7 contract for the three missing MRP invariants plus the end-to-end zero-delta theorem.

### 1. Zero-Chaos End-to-End Delta Identity (`zero-chaos-delta-zero`)

> **Rule of Thumb:** Assert that executing the Beta simulation with an empty chaos event list produces an identically zero Delta output across all SKUs and time buckets.

| Field | Content |
| :--- | :--- |
| **P1. Property statement** | Let $\text{State}_{\text{Alpha}}$ be any valid baseline planning state over horizon $T$ and SKU set $\mathcal{K}$. When the Beta simulation engine executes with an empty chaos event list ($\text{chaos\_payload} = \emptyset$), the resulting deviation state $\Delta = \text{Beta} - \text{Alpha}$ is identically zero across all SKUs $k \in \mathcal{K}$, time buckets $t \in [1, T]$, and state variables (PAB, Net Requirements, Planned Receipts): $\Delta \equiv 0$. |
| **P2. Strategy design** | Composite Hypothesis strategy generating valid multi-SKU Alpha baseline states. Use `st.integers(min_value=1, max_value=50)` for SKU counts and horizon lengths $T \in [1, 52]$. Populate initial inventory $I_0$, safety stock $SS$, lead times $L \in [0, 12]$, demand arrays $D_t \ge 0$, and scheduled receipts $S_t \ge 0$ using `st.lists` of non-negative integers or floats. Fix `chaos_payload = []`. |
| **P3. Oracle** | **Exact recomputation & identity assertion.** Execute Alpha baseline netting loop and Beta simulation loop. Compute Delta dataframe/state object. Assert `delta_df.abs().max().max() == 0` (or exact bitwise/numerical zero across all state fields). This serves as the identity-morphism test for the entire three-world engine. |
| **P4. Edge cases pinned** | `@example` inputs with: (a) zero demand across all SKUs and periods ($D_t = 0$); (b) initial inventory exactly equal to safety stock ($I_0 = SS$); (c) lead times exceeding horizon length ($L > T$); (d) single-period horizons ($T = 1$). |
| **P5. Stochasticity handling** | None required. Netting loops and state transitions are strictly deterministic. |
| **P6. Kill targets** | Eradicates calendar seam misalignment, unforced netting drift, and future M-series identity-morphism mutants. |
| **P7. Test function name** | `tests/invariants/test_zero_chaos_delta_zero.py::test_zero_chaos_delta_zero_no_chaos_events` |

### 2. Chaos Support Separation Law (`chaos-support`)

> **Rule of Thumb:** Verify that state modifications caused by chaos event injections remain strictly confined to the event's explicitly declared SKU and temporal target scope.

| Field | Content |
| :--- | :--- |
| **P1. Property statement** | Let $e$ be a chaos event (e.g., demand shock, supplier delay, capacity reduction) with explicitly declared target scope $\text{targets}(e) \subseteq \mathcal{K} \times [1, T]$. Let $\Delta_{\text{chaos}} = \text{State}_{\text{post}} - \text{State}_{\text{pre}}$ be the state diff induced by applying $e$. By the frame rule of separation logic, the support of the diff is strictly contained within the declared targets: $\text{supp}(\Delta_{\text{chaos}}) \subseteq \text{targets}(e)$. For any $(k, t) \notin \text{targets}(e)$, $\Delta_{\text{chaos}}(k, t) = 0$. |
| **P2. Strategy design** | Generate valid Alpha planning states over multi-SKU horizons. Generate synthetic chaos events by sampling subsets of SKUs $\mathcal{K}_{\text{sub}} \subset \mathcal{K}$ and period intervals $[t_{\text{start}}, t_{\text{end}}] \subseteq [1, T]$. Generate event payloads modifying demand (+/-), shifting receipt dates, or altering safety stock buffers strictly within $\mathcal{K}_{\text{sub}} \times [t_{\text{start}}, t_{\text{end}}]$. |
| **P3. Oracle** | **Frame rule / separation assertion.** Compute $\text{State}_{\text{pre}}$ and $\text{State}_{\text{post}}$. For all SKUs $k \notin \mathcal{K}_{\text{sub}}$ and all time periods outside the declared target window (before netting propagation effects if evaluating raw injections, or on uncoupled SKUs across the full horizon), assert exact bitwise equality between pre- and post-injection states. Assert zero side effects on non-target SKUs. |
| **P4. Edge cases pinned** | `@example` inputs with: (a) chaos events targeting period $T$ (horizon boundary); (b) events targeting SKU $k_1$ where $k_1$ shares a Gozinto BOM parent with untouched SKU $k_2$ (verifying independent demand isolation); (c) zero-magnitude chaos events (e.g., +0 demand shock). |
| **P5. Stochasticity handling** | None required. Chaos event injection and state modification are deterministic. |
| **P6. Kill targets** | Eradicates event injector leakage, unintended SKU cross-talk, and future M-series frame-rule mutants. |
| **P7. Test function name** | `tests/invariants/test_chaos_support.py::test_diff_support_subset` |

### 3. Run Determinism & Bisimulation Prerequisite (`run-determinism`)

> **Rule of Thumb:** Assert that independent pipeline runner executions with identical seeds and input dataframes produce byte-identical output artifacts.

| Field | Content |
| :--- | :--- |
| **P1. Property statement** | Let $R_{\text{engine}} : \text{Config} \times \text{State}_{\text{in}} \to \text{State}_{\text{out}}$ be the pipeline runner execution function. For any valid initial planning state, Gozinto matrix, demand history, chaos event list, and random seed $\sigma$, two independent executions produce identical outputs: $R_{\text{engine}}(\sigma, \text{State}_{\text{in}}) \equiv R_{\text{engine}}(\sigma, \text{State}_{\text{in}})$ bitwise across all generated dataframes, logs, and export payloads. |
| **P2. Strategy design** | Generate randomized complete MRP simulation configurations using `hypothesis.strategies`. Randomize floating-point demand series, integer quantities, MOQ/EOQ batch parameters, and simulation seed integers $\sigma \in [0, 2^{32}-1]$. |
| **P3. Oracle** | **Byte-identity assertion.** Execute pipeline runner twice in separate in-memory structures or clean temporary directories under identical seed $\sigma$. Assert exact equality of resulting Pandas dataframes (`df1.equals(df2)`) and serialized JSON/CSV deliverables. This forms the prerequisite for Phase 7 Excel↔Python bisimulation. |
| **P4. Edge cases pinned** | `@example` inputs with: (a) highly fractional floating-point demand triggering rounding boundaries; (b) large multi-echelon BOM networks; (c) simultaneous chaos events occurring on the same time bucket. |
| **P5. Stochasticity handling** | All internal randomness (if any, e.g., stochastic lead-time sampling) must be strictly controlled via seed $\sigma$. |
| **P6. Kill targets** | Eradicates floating-point instability, unseeded random number generation, and future M-series non-determinism mutants. |
| **P7. Test function name** | `tests/invariants/test_run_determinism.py::test_byte_identical_outputs` |

### 4. Excel Export Round-Trip Isomorphism (`export-round-trip`)

> **Rule of Thumb:** Assert that numeric values and string identifiers read back from generated Excel presentation deliverables match source dataframe values exactly.

| Field | Content |
| :--- | :--- |
| **P1. Property statement** | Let $E : \text{DataFrame} \to \text{ExcelFile}$ be the deliverable generation morphism (`mrp/exports/excel/`) and $E^{-1} : \text{ExcelFile} \to \text{DataFrame}$ be the spreadsheet parsing operator. For any valid planning dataframe $X$, the round-trip presentation mapping is an isomorphism over data values: $E^{-1}(E(X)) \equiv X$ across all cell values, dates, and alphanumeric SKU identifiers. |
| **P2. Strategy design** | Generate random planning dataframes with columns for SKU IDs, dates/periods, gross requirements, scheduled receipts, PAB, and planned receipts. Populate with integers, floats, boundary dates (leap years, year-end), and special SKU strings (containing hyphens, leading zeroes e.g., `"000123"`). |
| **P3. Oracle** | **Round-trip identity assertion.** Pass dataframe $X$ to Excel exporter; save to temporary file. Parse workbook back into Pandas dataframe $X'$. Assert exact equality of string identifiers (verifying leading zeroes were not stripped or converted to scientific notation) and numerical equality of floating-point quantities within strict IEEE 754 tolerance ($\epsilon = 10^{-9}$). |
| **P4. Edge cases pinned** | `@example` inputs with: (a) SKU IDs with leading zeroes (`"00456"`) or E-notation strings (`"12E34"`); (b) empty dataframes; (c) values exceeding standard integer limits; (d) Unicode characters in SKU descriptions. |
| **P5. Stochasticity handling** | None required. File serialization and parsing are deterministic. |
| **P6. Kill targets** | Eradicates spreadsheet type-coercion bugs, truncation errors, and future M-series presentation-layer mutants. |
| **P7. Test function name** | `tests/invariants/test_export_round_trip.py::test_excel_values_match_source` |

---

## III. Hypothesis Retrofit Specifications (Already-Implemented Invariants)

> **Rule of Thumb:** Upgrade existing Stage 0 unit tests by injecting randomized Hypothesis strategies for demand arrays, initial inventories, and timeline seams.

Per blueprint instruction §IV.2, this section defines the Hypothesis retrofit specifications for the three already-implemented Stage 0 invariants plus the OR Lexicon conservation laws. In accordance with contract requirements, detailed specifications focus on **P2 (Strategy design)** and **P4 (Edge cases pinned)** to inject randomization into existing static test harnesses.

### 5. Mass Balance & Inventory Conservation (`mass-balance` / `inventory-balance`)

> **Rule of Thumb:** Assert that telescoped PAB recursion exactly balances starting inventory plus total receipts minus gross demand across randomized multi-period horizons.

* **Target Test Functions:** 
  * `tests/invariants/test_mass_balance.py::test_mass_balance_per_period` (`mass-balance`)
  * `tests/lexicon/test_inventory_balance.py::test_pab_recursion_matches_lexicon` (`inventory-balance`)
* **P1 / P3 / P5 / P6 Concise Mapping:** Asserts the telescoped OR Lexicon inventory balance equation $I_t = I_{t-1} + R_t - D_t$ (where total receipts $R_t = S_t + u_t$) across all time periods $t \in [1, T]$. Oracle recomputes cumulative sum of receipts minus demand and asserts exact equality with ending PAB minus starting PAB. Eradicates unit-dropping defects and future M-series conservation mutants.
* **P2. Strategy design (Hypothesis Retrofit):**
  * Use `hypothesis.strategies` to generate multi-period planning schedules ($T \in [1, 104]$ periods).
  * **Demand Arrays ($D_t$):** Generate lists of length $T$ using `st.lists(st.integers(min_value=0, max_value=10000), min_size=1, max_size=104)`. To model realistic supply chain bursts, use composite strategies mixing zero-demand periods (80% probability) with sudden demand spikes (20% probability).
  * **Receipt Arrays ($S_t, u_t$):** Randomize scheduled receipts $S_t \ge 0$ and planned receipt control interventions $u_t \ge 0$ across the horizon.
  * **Initial Conditions:** Randomize starting inventory $I_0 \in [0, 50000]$ and safety stock buffers $SS \in [0, 5000]$.
* **P4. Edge cases pinned:**
  * `@example` schedule with 100% zero demand ($D_t = 0 \;\forall t$) to verify inventory remains constant when receipts are zero.
  * `@example` schedule where demand occurs exclusively on period $T$ (horizon boundary).
  * `@example` schedule where $D_t > I_{t-1} + S_t$ (triggering emergency Planned Receipt control injection $u_t > 0$).
  * `@example` single-period horizon ($T = 1$) with massive demand spike ($D_1 = 10^6$).

### 6. Inheritance Gluing Cocycle Condition (`inheritance-gluing`)

> **Rule of Thumb:** Verify that the Beta initial state equals the Alpha final state field-by-field at the cut-date timeline seam across randomized planning trajectories.

* **Target Test Function:** `tests/invariants/test_inheritance_gluing.py::test_inheritance_gluing_on_hand`
* **P1 / P3 / P5 / P6 Concise Mapping:** Asserts that when transitioning from the Alpha baseline timeline to the Beta simulation timeline at cut date $T_{\text{cut}}$, the initial state of Beta exactly equals the final state of Alpha at the seam: $I_0^{\text{Beta}} = I_{T_{\text{cut}}}^{\text{Alpha}}$, field by field (On-Hand inventory, backorders, work-in-progress). Oracle asserts deep dictionary/dataframe equality at the boundary seam. Eradicates timeline seam drift and future M-series gluing mutants.
* **P2. Strategy design (Hypothesis Retrofit):**
  * Generate random Alpha planning trajectories over horizon $T_{\text{Alpha}} \in [10, 52]$.
  * **Seam Cut-Date ($T_{\text{cut}}$):** Sample cut dates randomly across the interior of the Alpha horizon: $T_{\text{cut}} \sim \mathcal{U}(1, T_{\text{Alpha}}-1)$.
  * **State Vectors:** Randomize On-Hand inventory quantities, open backorder allocations, and in-transit scheduled receipt queues at the cut date using `st.builds` over state models.
  * **Demand Shifts:** Inject randomized demand modifications immediately following $T_{\text{cut}}$ in the Beta timeline to verify that gluing holds prior to divergence.
* **P4. Edge cases pinned:**
  * `@example` cut date at exact start of horizon ($T_{\text{cut}} = 0$).
  * `@example` cut date at exact end of horizon ($T_{\text{cut}} = T_{\text{Alpha}}$).
  * `@example` seam transition where On-Hand inventory is exactly zero ($I_{T_{\text{cut}}}^{\text{Alpha}} = 0$) and open backorders are positive.
  * `@example` seam transition with multiple scheduled receipts arriving precisely on $T_{\text{cut}}$.

### 7. Non-Negative Controls & Physical Boundaries (`non-negative-controls`)

> **Rule of Thumb:** Enforce that physical inventory levels and Planned Receipt control variables generated by the Bang-Bang controller remain strictly non-negative under randomized demand shocks.

* **Target Test Function:** `tests/lexicon/test_non_negative_controls.py::test_inventory_and_receipts_non_negative`
* **P1 / P3 / P5 / P6 Concise Mapping:** Asserts that under the Bang-Bang feedback control law $u_t = \max(0, (D_t + SS) - (I_{t-1} + S_t)) \pmod k$, all physical inventory states and control variables remain strictly non-negative: $I_t \ge 0$, $u_t \ge 0$, and total receipts $R_t \ge 0$ for all $t$. Oracle inspects generated simulation dataframes and asserts minimum value $\ge 0$ across all periods. Eradicates negative inventory bugs and future M-series boundary mutants.
* **P2. Strategy design (Hypothesis Retrofit):**
  * Generate extreme adversarial demand shocks designed to force inventory below zero if control laws fail.
  * **Adversarial Demand:** Use `st.integers(min_value=1000, max_value=100000)` for gross requirements against small initial inventories ($I_0 \in [0, 100]$).
  * **Control Parameters:** Randomize safety stock buffers $SS \in [0, 1000]$ and discrete batch order multiples ($k \in [1, 500]$, MOQ/EOQ constraints).
  * **Lead Time ($L$):** Randomize lead times $L \in [0, 5]$ to verify that when supply is constrained by lag operator $L$, netting logic correctly elevates backorders or planned orders without allowing physical shelf inventory $I_t$ to drop below zero.
* **P4. Edge cases pinned:**
  * `@example` zero initial inventory ($I_0 = 0$), zero scheduled receipts ($S_t = 0$), and positive demand ($D_1 > 0$).
  * `@example` batch multiple $k = 1000$ where net requirement is 1 unit (verifying control variable rounds up to $u_t = 1000 \ge 0$).
  * `@example` safety stock set to zero ($SS = 0$) with demand exactly equal to starting inventory ($D_1 = I_0$).
  * `@example` massive demand shock occurring during lead-time offset window where emergency planned receipts cannot arrive immediately.

---

## IV. Implementation & Verification Contract (Composer Hand-Off)

> **Rule of Thumb:** Implement test suites strictly from this blueprint without referencing engine internals, confirming success by recording baseline kill matrices in the project runbook.

### 1. Execution Rules for Composer
1. **Model Boundary Enforcement:** Composer must implement the test functions named in `inherited_invariants:` inside the MRP repository's `tests/invariants/` and `tests/lexicon/` directories using **only** this blueprint note and the repository's existing test scaffolding. Composer must not read engine implementation code in `mrp/` or `pipeline/` during test authoring.
2. **One Invariant per Commit:** Implement each property test suite in an isolated commit, verifying that pytest executes cleanly and Hypothesis runs without strategy health-check failures.
3. **No Ad-Hoc Patching:** If a newly implemented property test fails against the current codebase, report the failure as an revealed defect or spec gap. Do not ad-hoc patch the engine implementation or weaken the property test to force a green CI build.

### 2. Exit Condition & Mutation Drill Verification
Once all 8 property tests are implemented or retrofitted:
1. Execute the mutation testing harness across the MRP repository.
2. Compare the resulting kill matrix against the baseline recorded in the project's mutation runbook.
3. **Mandatory Exit Condition:** All M1 and M2 class mutants must remain killed, and all newly recorded M-series mutants targeting chaos support, run determinism, and Excel export round-trips must be eradicated.
4. Upon confirmation of mutant death, update `SP_Property_Test_Specs.md` frontmatter to flip all `inherited_invariants:` rows from `status: planned` to `status: enforced`, and sync enforcement status blocks across project documentation.
