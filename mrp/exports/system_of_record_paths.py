"""Path helpers for System of Record artifacts under output/system_of_record/."""

from pathlib import Path

SOR_ROOT = Path("output") / "system_of_record"

_PHASE_LABELS = {
    "alpha": "Alpha",
    "beta": "Beta",
    "delta": "Delta",
}


def sor_dir(phase: str) -> Path:
    """Return the output directory for a phase (alpha, beta, or delta), creating it if needed."""
    folder = SOR_ROOT / phase.lower()
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def sor_excel_path(phase: str) -> Path:
    """Full path for a phase System of Record workbook."""
    label = _PHASE_LABELS.get(phase.lower(), phase.title())
    return sor_dir(phase) / f"System_of_Record_{label}.xlsx"


def sor_sheets_dir(phase: str) -> Path:
    """Directory for Google Sheets-ready CSV tab exports."""
    folder = sor_dir(phase) / "google_sheets"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def sor_manifest_path(phase: str) -> Path:
    """Path for the Google Sheets API upload manifest JSON."""
    return sor_dir(phase) / "google_sheets_manifest.json"
