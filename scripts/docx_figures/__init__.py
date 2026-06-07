from .inventory import build_figure_inventory
from .model import FigureCoverageDiff, FigureObjectStats, FigureRecord
from .report import render_figure_coverage_json, render_figure_coverage_text

__all__ = [
    "build_figure_inventory",
    "FigureCoverageDiff",
    "FigureObjectStats",
    "FigureRecord",
    "render_figure_coverage_json",
    "render_figure_coverage_text",
]
