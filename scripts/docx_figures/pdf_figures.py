from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .model import FigureRecord

PDF_RENDERABLE_KINDS = {"chart", "shape_group", "composite"}
DEFAULT_SIDE_MARGIN = 40.0
DEFAULT_TOP_MARGIN = 40.0
DEFAULT_CAPTION_GAP = 10.0
DEFAULT_INTER_FIGURE_GAP = 12.0
DEFAULT_CROP_PADDING = 8.0
DEFAULT_RENDER_SCALE = 6.0

ROOT_DIR = Path(__file__).resolve().parents[2]
SWIFT_RENDER_SCRIPT = ROOT_DIR / "scripts/docx_figures/render_pdf_figures.swift"


@dataclass(frozen=True)
class PdfCaptionBounds:
    x: float
    y: float
    width: float
    height: float
    page_width: float
    page_height: float

    @property
    def top(self) -> float:
        return self.y + self.height


@dataclass(frozen=True)
class PdfFigurePlacement:
    figure_number: int
    page_number: int
    caption_bounds: PdfCaptionBounds


@dataclass(frozen=True)
class PdfSearchWindow:
    figure_number: int
    page_number: int
    left: float
    right: float
    bottom: float
    top: float


def default_pdf_figure_numbers(records: list[FigureRecord]) -> list[int]:
    return [
        record.number
        for record in records
        if record.kind in PDF_RENDERABLE_KINDS
    ]


def build_search_windows(
    placements: list[PdfFigurePlacement],
    *,
    side_margin: float = DEFAULT_SIDE_MARGIN,
    top_margin: float = DEFAULT_TOP_MARGIN,
    caption_gap: float = DEFAULT_CAPTION_GAP,
    inter_figure_gap: float = DEFAULT_INTER_FIGURE_GAP,
) -> list[PdfSearchWindow]:
    grouped: dict[int, list[PdfFigurePlacement]] = {}
    for placement in placements:
        grouped.setdefault(placement.page_number, []).append(placement)

    windows: list[PdfSearchWindow] = []
    for page_number, page_placements in grouped.items():
        sorted_placements = sorted(page_placements, key=lambda item: item.caption_bounds.y)
        for index, placement in enumerate(sorted_placements):
            next_higher = (
                sorted_placements[index + 1]
                if index + 1 < len(sorted_placements)
                else None
            )
            bounds = placement.caption_bounds
            top = (
                next_higher.caption_bounds.y - inter_figure_gap
                if next_higher is not None
                else bounds.page_height - top_margin
            )
            bottom = bounds.top + caption_gap
            if top <= bottom:
                top = min(bounds.page_height - top_margin, bottom + 24.0)
            windows.append(
                PdfSearchWindow(
                    figure_number=placement.figure_number,
                    page_number=page_number,
                    left=side_margin,
                    right=bounds.page_width - side_margin,
                    bottom=bottom,
                    top=top,
                )
            )

    return sorted(windows, key=lambda item: item.figure_number)


def swift_render_env(base_env: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(base_env or os.environ)
    env.setdefault("SWIFT_MODULECACHE_PATH", "/tmp/swift-module-cache")
    env.setdefault("CLANG_MODULE_CACHE_PATH", "/tmp/clang-module-cache")
    return env


def render_pdf_figures(
    *,
    pdf_path: Path,
    output_dir: Path,
    figure_numbers: list[int],
    scale: float = DEFAULT_RENDER_SCALE,
    side_margin: float = DEFAULT_SIDE_MARGIN,
    top_margin: float = DEFAULT_TOP_MARGIN,
    caption_gap: float = DEFAULT_CAPTION_GAP,
    inter_figure_gap: float = DEFAULT_INTER_FIGURE_GAP,
    crop_padding: float = DEFAULT_CROP_PADDING,
) -> subprocess.CompletedProcess[str]:
    figure_arg = ",".join(str(number) for number in figure_numbers)
    command = [
        "swift",
        str(SWIFT_RENDER_SCRIPT),
        "--pdf",
        str(pdf_path),
        "--output-dir",
        str(output_dir),
        "--figures",
        figure_arg,
        "--scale",
        str(scale),
        "--side-margin",
        str(side_margin),
        "--top-margin",
        str(top_margin),
        "--caption-gap",
        str(caption_gap),
        "--inter-figure-gap",
        str(inter_figure_gap),
        "--crop-padding",
        str(crop_padding),
    ]
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        env=swift_render_env(),
    )
