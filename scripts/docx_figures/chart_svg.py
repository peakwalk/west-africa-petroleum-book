from __future__ import annotations

import html
import math
import posixpath
from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from scripts.docx_parity.normalize import normalize_visible_text

CHART_NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
    "cdr": "http://schemas.openxmlformats.org/drawingml/2006/chartDrawing",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
}
SCHEME_COLOR_MAP = {
    "accent1": "#4472C4",
    "accent2": "#ED7D31",
    "accent3": "#A5A5A5",
    "accent4": "#FFC000",
    "accent5": "#5B9BD5",
    "accent6": "#70AD47",
    "tx1": "#404040",
    "tx2": "#666666",
}


@dataclass(frozen=True)
class ChartOverlayRect:
    x0: float
    y0: float
    x1: float
    y1: float
    fill: str
    text: str = ""


@dataclass(frozen=True)
class ChartSeries:
    title: str
    values: list[float | None]
    color: str


@dataclass(frozen=True)
class ChartSpec:
    chart_part: str
    chart_type: str
    title: str
    value_axis_title: str
    categories: list[str]
    series: list[ChartSeries]
    overlays: list[ChartOverlayRect] = field(default_factory=list)


def _read_xml(archive: ZipFile, member: str) -> ET.Element | None:
    try:
        return ET.fromstring(archive.read(member))
    except KeyError:
        return None


def _resolve_part_target(base_part: str, target: str) -> str:
    return posixpath.normpath(posixpath.join(posixpath.dirname(base_part), target))


def _build_relationship_map(archive: ZipFile, part_name: str) -> dict[str, str]:
    relationship_part = posixpath.normpath(
        posixpath.join(
            posixpath.dirname(part_name),
            "_rels",
            posixpath.basename(part_name) + ".rels",
        )
    )
    root = _read_xml(archive, relationship_part)
    if root is None:
        return {}
    relationships: dict[str, str] = {}
    for relationship in root.findall("pr:Relationship", CHART_NS):
        relationship_id = relationship.attrib.get("Id")
        target = relationship.attrib.get("Target")
        if not relationship_id or not target:
            continue
        relationships[relationship_id] = _resolve_part_target(part_name, target)
    return relationships


def _collect_descendant_text(node: ET.Element | None) -> str:
    if node is None:
        return ""
    allowed_tags = {
        f"{{{CHART_NS['a']}}}t",
        f"{{{CHART_NS['c']}}}v",
    }
    texts = [
        text.strip()
        for text in (
            descendant.text
            for descendant in node.iter()
            if descendant.tag in allowed_tags and descendant.text and descendant.text.strip()
        )
        if text
    ]
    return normalize_visible_text(" ".join(texts))


def _series_title(series_node: ET.Element) -> str:
    title = _collect_descendant_text(series_node.find("c:tx", CHART_NS))
    if title:
        return title
    label_parts: list[str] = []
    for label in series_node.findall(".//c:dLbl", CHART_NS):
        text = _collect_descendant_text(label.find("c:tx", CHART_NS))
        if text:
            label_parts.append(text)
    if label_parts:
        return normalize_visible_text(" ".join(label_parts))
    return "Series"


def _extract_color(series_node: ET.Element) -> str:
    solid = series_node.find(".//a:solidFill/a:srgbClr", CHART_NS)
    if solid is not None and solid.attrib.get("val"):
        return "#" + solid.attrib["val"].upper()
    scheme = series_node.find(".//a:solidFill/a:schemeClr", CHART_NS)
    if scheme is not None:
        return SCHEME_COLOR_MAP.get(scheme.attrib.get("val", ""), "#4472C4")
    grad_scheme = series_node.find(".//a:gradFill//a:schemeClr", CHART_NS)
    if grad_scheme is not None:
        return SCHEME_COLOR_MAP.get(grad_scheme.attrib.get("val", ""), "#4472C4")
    return "#4472C4"


def _extract_categories(series_node: ET.Element) -> list[str]:
    points = series_node.findall(".//c:cat//c:pt", CHART_NS)
    if points:
        indexed = {
            int(point.attrib.get("idx", "0")): normalize_visible_text(
                point.findtext("c:v", default="", namespaces=CHART_NS)
            )
            for point in points
        }
        if indexed:
            return [indexed.get(index, "") for index in range(max(indexed) + 1)]
    values = [
        normalize_visible_text(node.text or "")
        for node in series_node.findall(".//c:cat//c:v", CHART_NS)
    ]
    return [value for value in values if value]


def _extract_values(series_node: ET.Element, category_count: int) -> list[float | None]:
    points = series_node.findall(".//c:val//c:pt", CHART_NS)
    indexed: dict[int, float] = {}
    for point in points:
        raw_value = normalize_visible_text(
            point.findtext("c:v", default="", namespaces=CHART_NS)
        )
        if not raw_value:
            continue
        indexed[int(point.attrib.get("idx", "0"))] = float(raw_value)
    if not indexed:
        return [None] * category_count
    length = max(category_count, max(indexed) + 1)
    values: list[float | None] = [None] * length
    for index, value in indexed.items():
        values[index] = value
    return values


def _extract_overlays(archive: ZipFile, chart_part: str) -> list[ChartOverlayRect]:
    relationships = _build_relationship_map(archive, chart_part)
    drawing_targets = [
        target
        for target in relationships.values()
        if target.endswith(".xml") and "/drawings/" in target
    ]
    overlays: list[ChartOverlayRect] = []
    for drawing_target in drawing_targets:
        drawing_root = _read_xml(archive, drawing_target)
        if drawing_root is None:
            continue
        for anchor in drawing_root.findall(".//cdr:relSizeAnchor", CHART_NS):
            start = anchor.find("cdr:from", CHART_NS)
            end = anchor.find("cdr:to", CHART_NS)
            shape = anchor.find("cdr:sp", CHART_NS)
            if start is None or end is None or shape is None:
                continue
            fill_node = shape.find(".//a:solidFill/a:srgbClr", CHART_NS)
            fill = "#70AD47"
            if fill_node is not None and fill_node.attrib.get("val"):
                fill = "#" + fill_node.attrib["val"].upper()
            overlays.append(
                ChartOverlayRect(
                    x0=float(start.findtext("cdr:x", default="0", namespaces=CHART_NS)),
                    y0=float(start.findtext("cdr:y", default="0", namespaces=CHART_NS)),
                    x1=float(end.findtext("cdr:x", default="0", namespaces=CHART_NS)),
                    y1=float(end.findtext("cdr:y", default="0", namespaces=CHART_NS)),
                    fill=fill,
                    text=_collect_descendant_text(shape.find("cdr:txBody", CHART_NS)),
                )
            )
    return overlays


def parse_chart_part(docx_path: Path, chart_part: str) -> ChartSpec:
    with ZipFile(docx_path) as archive:
        root = _read_xml(archive, chart_part)
        if root is None:
            raise FileNotFoundError(f"Missing chart part: {chart_part}")

        chart_node = None
        chart_type = ""
        for candidate in ("barChart", "bar3DChart", "lineChart"):
            chart_node = root.find(f".//c:{candidate}", CHART_NS)
            if chart_node is not None:
                chart_type = candidate
                break
        if chart_node is None:
            raise ValueError(f"Unsupported chart type in {chart_part}")

        series_nodes = chart_node.findall("c:ser", CHART_NS)
        if not series_nodes:
            raise ValueError(f"No series data found in {chart_part}")

        categories = _extract_categories(series_nodes[0])
        category_count = len(categories)
        series = [
            ChartSeries(
                title=_series_title(series_node),
                values=_extract_values(series_node, category_count),
                color=_extract_color(series_node),
            )
            for series_node in series_nodes
        ]
        return ChartSpec(
            chart_part=chart_part,
            chart_type=chart_type,
            title=_collect_descendant_text(root.find(".//c:chart/c:title", CHART_NS)),
            value_axis_title=_collect_descendant_text(root.find(".//c:valAx/c:title", CHART_NS)),
            categories=categories,
            series=series,
            overlays=_extract_overlays(archive, chart_part),
        )


def _format_number(value: float) -> str:
    rounded = f"{value:.2f}"
    if "." in rounded:
        rounded = rounded.rstrip("0").rstrip(".")
    return rounded


def _nice_axis_max(value: float) -> float:
    if value <= 0:
        return 1.0
    magnitude = 10 ** math.floor(math.log10(value))
    fraction = value / magnitude
    if fraction <= 1:
        nice_fraction = 1
    elif fraction <= 2:
        nice_fraction = 2
    elif fraction <= 5:
        nice_fraction = 5
    else:
        nice_fraction = 10
    return nice_fraction * magnitude


def _wrap_label(label: str, max_line_length: int = 12) -> list[str]:
    words = label.split()
    if not words:
        return [label]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if len(candidate) <= max_line_length:
            current = candidate
            continue
        lines.append(current)
        current = word
    lines.append(current)
    return lines


def render_chart_svg(chart: ChartSpec, width: int = 1280, height: int = 820) -> str:
    if not chart.categories:
        raise ValueError("Chart has no categories to render.")

    left_margin = 128
    right_margin = 64
    top_margin = 120 if chart.title else 88
    bottom_margin = 140
    chart_width = width - left_margin - right_margin
    chart_height = height - top_margin - bottom_margin

    all_values = [
        value
        for series in chart.series
        for value in series.values
        if value is not None
    ]
    max_value = max(all_values) if all_values else 1.0
    axis_max = _nice_axis_max(max_value)
    tick_count = 5
    tick_values = [axis_max * index / tick_count for index in range(tick_count + 1)]

    category_count = len(chart.categories)
    group_width = chart_width / max(category_count, 1)
    inner_gap = group_width * 0.12
    series_count = max(len(chart.series), 1)
    bar_width = max((group_width - inner_gap * 2) / series_count, 12)
    label_step = max(1, math.ceil(category_count / 12))

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(chart.title or "Chart")}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>',
        '.chart-title { font: 700 30px Georgia, "Times New Roman", serif; fill: #1f2937; }',
        '.axis-label { font: 600 18px "Helvetica Neue", Arial, sans-serif; fill: #334155; }',
        '.tick-label { font: 500 16px "Helvetica Neue", Arial, sans-serif; fill: #475569; }',
        '.value-label { font: 600 14px "Helvetica Neue", Arial, sans-serif; fill: #0f172a; }',
        '.legend-label { font: 600 16px "Helvetica Neue", Arial, sans-serif; fill: #0f172a; }',
        '.grid-line { stroke: #d7dde5; stroke-width: 1; }',
        '.axis-line { stroke: #94a3b8; stroke-width: 1.5; }',
        "</style>",
    ]

    if chart.title:
        parts.append(
            f'<text x="{width / 2:.1f}" y="52" text-anchor="middle" class="chart-title">{html.escape(chart.title)}</text>'
        )

    legend_x = left_margin
    legend_y = 80 if chart.title else 48
    for index, series in enumerate(chart.series):
        swatch_x = legend_x + index * 220
        parts.append(
            f'<rect x="{swatch_x}" y="{legend_y - 14}" width="18" height="18" rx="3" fill="{series.color}"/>'
        )
        parts.append(
            f'<text x="{swatch_x + 28}" y="{legend_y}" class="legend-label">{html.escape(series.title)}</text>'
        )

    plot_top = top_margin
    plot_bottom = top_margin + chart_height
    plot_left = left_margin
    plot_right = left_margin + chart_width

    for tick_value in tick_values:
        y = plot_bottom - (tick_value / axis_max) * chart_height
        parts.append(
            f'<line x1="{plot_left}" y1="{y:.2f}" x2="{plot_right}" y2="{y:.2f}" class="grid-line"/>'
        )
        parts.append(
            f'<text x="{plot_left - 14}" y="{y + 6:.2f}" text-anchor="end" class="tick-label">{html.escape(_format_number(tick_value))}</text>'
        )

    parts.append(
        f'<line x1="{plot_left}" y1="{plot_top}" x2="{plot_left}" y2="{plot_bottom}" class="axis-line"/>'
    )
    parts.append(
        f'<line x1="{plot_left}" y1="{plot_bottom}" x2="{plot_right}" y2="{plot_bottom}" class="axis-line"/>'
    )

    if chart.value_axis_title:
        axis_label_x = 40
        axis_label_y = top_margin + chart_height / 2
        parts.append(
            f'<text x="{axis_label_x}" y="{axis_label_y:.2f}" text-anchor="middle" class="axis-label" transform="rotate(-90 {axis_label_x} {axis_label_y:.2f})">{html.escape(chart.value_axis_title)}</text>'
        )

    if chart.chart_type in {"barChart", "bar3DChart"}:
        for category_index, category in enumerate(chart.categories):
            group_x = plot_left + category_index * group_width + inner_gap
            for series_index, series in enumerate(chart.series):
                value = (
                    series.values[category_index]
                    if category_index < len(series.values)
                    else None
                )
                if value is None:
                    continue
                bar_height = (value / axis_max) * chart_height
                bar_x = group_x + series_index * bar_width
                bar_y = plot_bottom - bar_height
                parts.append(
                    f'<rect x="{bar_x:.2f}" y="{bar_y:.2f}" width="{bar_width - 8:.2f}" height="{bar_height:.2f}" rx="6" fill="{series.color}" opacity="0.95"/>'
                )
                parts.append(
                    f'<text x="{bar_x + (bar_width - 8) / 2:.2f}" y="{bar_y - 8:.2f}" text-anchor="middle" class="value-label">{html.escape(_format_number(value))}</text>'
                )
    elif chart.chart_type == "lineChart":
        x_step = chart_width / max(category_count - 1, 1)
        for series in chart.series:
            points: list[tuple[float, float, float]] = []
            for category_index, value in enumerate(series.values):
                if category_index >= category_count or value is None:
                    continue
                x = plot_left + category_index * x_step
                y = plot_bottom - (value / axis_max) * chart_height
                points.append((x, y, value))
            if len(points) < 2:
                continue
            point_string = " ".join(f"{x:.2f},{y:.2f}" for x, y, _ in points)
            parts.append(
                f'<polyline fill="none" stroke="{series.color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" points="{point_string}"/>'
            )
            for x, y, value in points:
                parts.append(
                    f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5.5" fill="{series.color}" stroke="#ffffff" stroke-width="2"/>'
                )
            last_x, last_y, last_value = points[-1]
            parts.append(
                f'<text x="{last_x + 10:.2f}" y="{last_y - 10:.2f}" class="value-label">{html.escape(_format_number(last_value))}</text>'
            )
    else:
        raise ValueError(f"Unsupported chart type for rendering: {chart.chart_type}")

    for category_index, category in enumerate(chart.categories):
        if (
            category_count > 12
            and category_index % label_step != 0
            and category_index != category_count - 1
        ):
            continue
        label_x = (
            plot_left + category_index * group_width + group_width / 2
            if chart.chart_type in {"barChart", "bar3DChart"}
            else plot_left + category_index * (chart_width / max(category_count - 1, 1))
        )
        label_lines = _wrap_label(category)
        label_y = plot_bottom + 28
        parts.append(
            f'<text x="{label_x:.2f}" y="{label_y:.2f}" text-anchor="middle" class="tick-label">'
        )
        for line_index, line in enumerate(label_lines):
            dy = 0 if line_index == 0 else 20
            parts.append(
                f'<tspan x="{label_x:.2f}" dy="{dy}">{html.escape(line)}</tspan>'
            )
        parts.append("</text>")

    overlay_frame_x = plot_left
    overlay_frame_y = top_margin - 12
    overlay_frame_width = chart_width
    overlay_frame_height = chart_height + 48
    for overlay in chart.overlays:
        rect_x = overlay_frame_x + overlay.x0 * overlay_frame_width
        rect_y = overlay_frame_y + overlay.y0 * overlay_frame_height
        rect_width = (overlay.x1 - overlay.x0) * overlay_frame_width
        rect_height = (overlay.y1 - overlay.y0) * overlay_frame_height
        parts.append(
            f'<rect x="{rect_x:.2f}" y="{rect_y:.2f}" width="{rect_width:.2f}" height="{rect_height:.2f}" fill="{overlay.fill}" opacity="0.65"/>'
        )
        if overlay.text:
            parts.append(
                f'<text x="{rect_x + rect_width / 2:.2f}" y="{rect_y + rect_height / 2:.2f}" text-anchor="middle" dominant-baseline="middle" class="tick-label">{html.escape(overlay.text)}</text>'
            )

    parts.append("</svg>")
    return "\n".join(parts) + "\n"
