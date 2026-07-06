"""Run MRP mutation drill M1-M4 + new property mutants (2026-07-06)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _pytest() -> int:
    result = subprocess.run(
        [sys.executable, "-X", "utf8", "-m", "pytest", "tests/invariants/", "tests/lexicon/", "-q", "--tb=no"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    print(result.stdout + result.stderr)
    return result.returncode


def main() -> int:
    if _pytest() != 0:
        print("Baseline not green")
        return 1

    results: list[tuple[str, bool]] = []

    sim = REPO / "mrp" / "simulation.py"
    orig = sim.read_text(encoding="utf-8")

    m1 = orig.replace(
        "locked_inv.append(current_inv)",
        "locked_inv.append(current_inv - 1)",
        1,
    )
    sim.write_text(m1, encoding="utf-8")
    results.append(("M1 mass-balance", _pytest() != 0))
    sim.write_text(orig, encoding="utf-8")

    state = REPO / "mrp" / "state.py"
    s_orig = state.read_text(encoding="utf-8")
    m2 = s_orig.replace(
        "dict_beta_demand[sku] = current_demand[1:] + [current_demand[-1]]",
        "dict_beta_demand[sku] = list(current_demand)",
        1,
    )
    state.write_text(m2, encoding="utf-8")
    results.append(("M2 inheritance-gluing", _pytest() != 0))
    state.write_text(s_orig, encoding="utf-8")

    m3 = orig.replace("if release_index >= 0:", "if release_index <= 0:", 1)
    sim.write_text(m3, encoding="utf-8")
    results.append(("M3 transition/mass-balance", _pytest() != 0))
    sim.write_text(orig, encoding="utf-8")

    m4 = orig.replace(
        "current_inv = raw_balance + porcpt_t",
        "current_inv = raw_balance + porcpt_t + sr_t",
        1,
    )
    sim.write_text(m4, encoding="utf-8")
    results.append(("M4 mass-balance edge", _pytest() != 0))
    sim.write_text(orig, encoding="utf-8")

    m5 = s_orig.replace(
        "beta_demand[sku][idx] += mag",
        "beta_demand[sku][idx] += mag\n                for leak_sku in beta_demand:\n                    if leak_sku != sku:\n                        beta_demand[leak_sku][idx] += 1",
        1,
    )
    state.write_text(m5, encoding="utf-8")
    results.append(("M5 chaos-support leak", _pytest() != 0))
    state.write_text(s_orig, encoding="utf-8")

    m6 = orig.replace(
        "return df_sku, capacity_alerts",
        "df_sku = df_sku.iloc[::-1].reset_index(drop=True)\n    return df_sku, capacity_alerts",
        1,
    )
    sim.write_text(m6, encoding="utf-8")
    results.append(("M6 run-determinism", _pytest() != 0))
    sim.write_text(orig, encoding="utf-8")

    export_test = REPO / "tests" / "invariants" / "test_export_round_trip.py"
    e_orig = export_test.read_text(encoding="utf-8")
    e_mut = e_orig.replace(
        'st.from_regex(r"SKU_\\d{3}", fullmatch=True),',
        'st.just("00456"),',
        1,
    ).replace(
        'round_tripped["SKU_ID"] = round_tripped["SKU_ID"].astype(str)',
        'round_tripped["SKU_ID"] = round_tripped["SKU_ID"].astype(float).astype(int).astype(str)',
        1,
    )
    export_test.write_text(e_mut, encoding="utf-8")
    results.append(("M7 export-round-trip", _pytest() != 0))
    export_test.write_text(e_orig, encoding="utf-8")

    print("\n=== Kill matrix ===")
    for name, killed in results:
        print(f"{name}: {'KILLED' if killed else 'SURVIVED'}")

    survivors = [n for n, k in results if not k]
    return 1 if survivors else 0


if __name__ == "__main__":
    raise SystemExit(main())
