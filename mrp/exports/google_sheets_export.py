"""Google Sheets-ready CSV exports and optional live spreadsheet upload."""

import csv
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from mrp.exports.system_of_record_paths import sor_manifest_path, sor_sheets_dir
from mrp.viz.dashboards import dashboard_path

_VISUAL_DASHBOARDS_SHEET = "4_Visual_Dashboards"


def _sanitize_sheet_filename(sheet_name: str) -> str:
    """Convert an Excel sheet name into a safe CSV filename stem."""
    stem = re.sub(r"[^\w\-]+", "_", sheet_name.replace("&", "_and_"))
    stem = re.sub(r"_+", "_", stem).strip("_")
    return stem or "sheet"


def _build_visual_dashboards_csv(skus: list) -> pd.DataFrame:
    rows = []
    for sku in skus:
        img_path = dashboard_path("delta", sku)
        if img_path.exists():
            rows.append(
                {
                    "SKU_ID": sku,
                    "dashboard_image_path": str(img_path),
                    "status": "available",
                }
            )
        else:
            rows.append(
                {
                    "SKU_ID": sku,
                    "dashboard_image_path": "",
                    "status": "missing — run dashboard generation first",
                }
            )
    return pd.DataFrame(rows)


def export_sor_csv_tabs(
    excel_path: Path,
    csv_dir: Path,
    *,
    phase: str | None = None,
    skus: list | None = None,
) -> list[Path]:
    """Export each Excel workbook tab as a CSV file for Google Sheets import."""
    csv_dir.mkdir(parents=True, exist_ok=True)
    sheets = pd.read_excel(excel_path, sheet_name=None, engine="openpyxl")
    written: list[Path] = []

    for sheet_name, df in sheets.items():
        if (
            sheet_name == _VISUAL_DASHBOARDS_SHEET
            and phase == "delta"
            and skus is not None
        ):
            df = _build_visual_dashboards_csv(skus)

        out_path = csv_dir / f"{_sanitize_sheet_filename(sheet_name)}.csv"
        df.to_csv(out_path, index=False)
        written.append(out_path)

    print(f" -> Exported {len(written)} CSV tab(s) to {csv_dir}")
    return written


def _credentials_path() -> Path | None:
    raw = os.environ.get("GOOGLE_SHEETS_CREDENTIALS", "").strip()
    if not raw:
        return None
    path = Path(raw)
    return path if path.is_file() else None


def _read_csv_rows(csv_path: Path) -> list[list[str]]:
    with csv_path.open(newline="", encoding="utf-8") as handle:
        return list(csv.reader(handle))


def upload_sor_to_google_sheets(phase: str, csv_dir: Path, title: str) -> dict | None:
    """Upload CSV tabs to a new Google Spreadsheet when credentials are configured."""
    creds_file = _credentials_path()
    if creds_file is None:
        print(
            " -> Google Sheets upload skipped (set GOOGLE_SHEETS_CREDENTIALS to a service-account JSON path)."
        )
        return None

    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        print(" -> Google Sheets upload skipped (install gspread and google-auth).")
        return None

    csv_files = sorted(csv_dir.glob("*.csv"))
    if not csv_files:
        print(f" -> Google Sheets upload skipped (no CSV files in {csv_dir}).")
        return None

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = Credentials.from_service_account_file(str(creds_file), scopes=scopes)
    client = gspread.authorize(credentials)

    spreadsheet = client.create(title)
    folder_id = os.environ.get("GOOGLE_SHEETS_FOLDER_ID", "").strip()
    if folder_id:
        try:
            spreadsheet.move_to_folder(folder_id)
        except Exception as exc:
            print(f" -> Warning: could not move spreadsheet to folder {folder_id}: {exc}")

    worksheets_meta: list[dict] = []
    for index, csv_path in enumerate(csv_files):
        tab_name = csv_path.stem[:100]
        rows = _read_csv_rows(csv_path)
        if not rows:
            continue

        if index == 0:
            worksheet = spreadsheet.sheet1
            worksheet.update_title(tab_name)
        else:
            worksheet = spreadsheet.add_worksheet(
                title=tab_name,
                rows=max(len(rows), 1),
                cols=max(len(rows[0]), 1),
            )

        worksheet.update(rows, "A1")
        worksheets_meta.append({"tab": tab_name, "csv_file": csv_path.name})

    manifest = {
        "phase": phase.lower(),
        "spreadsheet_id": spreadsheet.id,
        "url": spreadsheet.url,
        "worksheets": worksheets_meta,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    manifest_path = sor_manifest_path(phase)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f" -> Google Spreadsheet uploaded: {spreadsheet.url}")
    print(f" -> Manifest saved to {manifest_path}")
    return manifest


def finalize_sor_google_exports(
    phase: str,
    excel_path: Path,
    *,
    skus: list | None = None,
) -> None:
    """Export CSV tabs and optionally upload to Google Sheets."""
    csv_dir = sor_sheets_dir(phase)
    export_sor_csv_tabs(excel_path, csv_dir, phase=phase.lower(), skus=skus)

    label = phase.title()
    title = f"MRP System of Record - {label} - {datetime.now().strftime('%Y-%m-%d')}"
    upload_sor_to_google_sheets(phase.lower(), csv_dir, title)
