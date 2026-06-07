from __future__ import annotations

import json
from dataclasses import asdict

from .model import FigureCoverageDiff


def render_figure_coverage_text(diffs: list[FigureCoverageDiff]) -> str:
    lines = ["DOCX figure coverage check failed:"]
    for diff in diffs:
        label = (
            f"Figure {diff.figure_number}"
            if diff.figure_number is not None
            else "General"
        )
        lines.extend(
            [
                f"- {label} [{diff.diff_type}]",
                f"  chapter: {diff.chapter_path}",
                f"  detail: {diff.detail}",
            ]
        )
    return "\n".join(lines)


def render_figure_coverage_json(diffs: list[FigureCoverageDiff]) -> str:
    return json.dumps([asdict(diff) for diff in diffs], indent=2, ensure_ascii=False)
