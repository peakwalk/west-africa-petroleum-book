from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FigureObjectStats:
    blip_targets: list[str] = field(default_factory=list)
    chart_targets: list[str] = field(default_factory=list)
    drawing_targets: list[str] = field(default_factory=list)
    anchor_count: int = 0
    inline_count: int = 0
    vshape_count: int = 0
    wps_shape_count: int = 0

    def has_objects(self) -> bool:
        return bool(
            self.blip_targets
            or self.chart_targets
            or self.drawing_targets
            or self.anchor_count
            or self.inline_count
            or self.vshape_count
            or self.wps_shape_count
        )

    def score(self) -> int:
        return (
            len(self.blip_targets) * 5
            + len(self.chart_targets) * 7
            + len(self.drawing_targets) * 3
            + self.anchor_count
            + self.inline_count
            + self.vshape_count
            + self.wps_shape_count
        )


@dataclass(frozen=True)
class FigureRecord:
    number: int
    caption: str
    chapter_title: str
    chapter_path: str
    caption_paragraph_index: int
    object_paragraph_start: int
    object_paragraph_end: int
    kind: str
    objects: FigureObjectStats
    published_assets: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class FigureCoverageDiff:
    figure_number: int | None
    chapter_path: str
    diff_type: str
    detail: str
