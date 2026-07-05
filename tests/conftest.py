"""Shared helpers and headless pipeline fixture."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from data.fixtures import CONSTRAINTS, DEMAND, INVENTORY


@pytest.fixture
def headless_pipeline(tmp_path, monkeypatch):
    """Run Alpha/Beta/Delta without filesystem exports or dashboards."""
    audit_dir = tmp_path / "dashboards"
    audit_dir.mkdir(parents=True, exist_ok=True)
    sor_dir = tmp_path / "sor"
    sor_dir.mkdir(parents=True, exist_ok=True)

    def _noop(*_args, **_kwargs):
        return None

    patches = [
        patch("pipeline.runner.export_sku_dashboard_audit", _noop),
        patch("pipeline.runner.export_delta_dashboard_audit", _noop),
        patch("pipeline.runner.build_beta_shadow_ledger", _noop),
        patch("pipeline.runner.build_delta_shadow_ledger", _noop),
        patch("pipeline.runner.cleanup_legacy_root_artifacts", lambda: []),
    ]
    for item in patches:
        item.start()

    from pipeline.runner import run_alpha, run_beta, run_delta

    alpha = run_alpha(
        constraints=CONSTRAINTS,
        inventory=INVENTORY,
        demand=DEMAND,
        export_csv=False,
        export_excel=False,
        generate_dashboards=False,
    )
    yield {
        "alpha": alpha,
        "run_beta": run_beta,
        "run_delta": run_delta,
        "constraints": CONSTRAINTS,
        "demand": DEMAND,
    }
    for item in patches:
        item.stop()
