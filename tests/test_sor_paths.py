"""Tests for System of Record output path helpers."""

from mrp.exports.system_of_record_paths import (
    SOR_ROOT,
    sor_dir,
    sor_excel_path,
    sor_manifest_path,
    sor_sheets_dir,
)


def test_sor_excel_path_alpha():
    path = sor_excel_path("alpha")
    assert path == SOR_ROOT / "alpha" / "System_of_Record_Alpha.xlsx"


def test_sor_excel_path_delta_case_insensitive():
    path = sor_excel_path("DELTA")
    assert path == SOR_ROOT / "delta" / "System_of_Record_Delta.xlsx"


def test_sor_sheets_dir_under_phase():
    path = sor_sheets_dir("delta")
    assert path == SOR_ROOT / "delta" / "google_sheets"


def test_sor_manifest_path():
    path = sor_manifest_path("beta")
    assert path == SOR_ROOT / "beta" / "google_sheets_manifest.json"


def test_sor_dir_creates_folder(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "mrp.exports.system_of_record_paths.SOR_ROOT",
        tmp_path / "system_of_record",
    )
    folder = sor_dir("alpha")
    assert folder.is_dir()
