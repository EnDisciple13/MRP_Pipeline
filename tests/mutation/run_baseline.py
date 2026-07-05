"""Run MRP mutation drill v0 baseline."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SIMULATION = REPO / "mrp" / "simulation.py"
RUNNER = REPO / "pipeline" / "runner.py"


def run_pytest(target: str) -> bool:
    result = subprocess.run(
        [sys.executable, "-X", "utf8", "-m", "pytest", target, "-q"],
        cwd=REPO,
        capture_output=True,
        text=True,
        env={**dict(**{"PYTHONIOENCODING": "utf-8"}), **__import__("os").environ},
    )
    return result.returncode == 0


def m1_drop_one_unit() -> bool:
    source = SIMULATION.read_text(encoding="utf-8")
    needle = "        current_inv = raw_balance + porcpt_t\n"
    mutant = needle.replace(
        "current_inv = raw_balance + porcpt_t",
        "current_inv = raw_balance + porcpt_t - 1",
        1,
    )
    if needle not in source:
        return False
    SIMULATION.write_text(source.replace(needle, mutant, 1), encoding="utf-8")
    try:
        return not run_pytest("tests/invariants/test_mass_balance.py")
    finally:
        SIMULATION.write_text(source, encoding="utf-8")


def m2_skip_inheritance_shift() -> bool:
    source = (REPO / "mrp" / "state.py").read_text(encoding="utf-8")
    needle = "        dict_beta_demand[sku] = current_demand[1:] + [current_demand[-1]]\n"
    mutant = "        dict_beta_demand[sku] = list(current_demand)\n"
    if needle not in source:
        return False
    path = REPO / "mrp" / "state.py"
    path.write_text(source.replace(needle, mutant, 1), encoding="utf-8")
    try:
        return not run_pytest("tests/invariants/test_inheritance_gluing.py::test_inheritance_gluing_demand_shift")
    finally:
        path.write_text(source, encoding="utf-8")


def main() -> int:
    print("Baseline:", run_pytest("tests/invariants/"))
    print("M1 killed mass-balance:", m1_drop_one_unit())
    print("M2 killed inheritance-gluing:", m2_skip_inheritance_shift())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
