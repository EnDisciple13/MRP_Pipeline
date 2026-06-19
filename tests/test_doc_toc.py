"""Verify Project_Documentation.md TOC links resolve to HTML anchor ids."""

import re
from pathlib import Path

DOC_PATH = Path(__file__).resolve().parents[1] / "Project_Documentation.md"


def test_toc_links_match_anchor_ids():
    text = DOC_PATH.read_text(encoding="utf-8")
    toc_section, _, _ = text.partition('<a id="project-outline"></a>')
    toc_links = set(re.findall(r"\]\(#([^)]+)\)", toc_section))
    anchors = set(re.findall(r'<a id="([^"]+)"></a>', text))

    missing = toc_links - anchors
    assert not missing, f"TOC links missing anchors: {sorted(missing)}"
    assert len(toc_links) >= 48
