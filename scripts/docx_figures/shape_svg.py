from __future__ import annotations

import html
import math
import re
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from scripts.docx_parity.normalize import normalize_visible_text

VML_NS = {
    "v": "urn:schemas-microsoft-com:vml",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}
STYLE_ITEM_RE = re.compile(r"\s*([^:]+):([^;]+)")
FIGURE_TEXT_RE = re.compile(r"^(Figure|Table)\s+\d+\s*:", re.IGNORECASE)


@dataclass(frozen=True)
class ShapeTextLine:
    text: str
    font_size_pt: float
    bold: bool
    color: str
    align: str


@dataclass(frozen=True)
class ShapeBox:
    x: float
    y: float
    width: float
    height: float
    fill: str
    stroke: str
    stroke_width_pt: float
    text_anchor: str
    vertical_anchor: str
    lines: list[ShapeTextLine]
    inset_left_pt: float = 2.88
    inset_top_pt: float = 1.44
    inset_right_pt: float = 2.88
    inset_bottom_pt: float = 1.44


@dataclass(frozen=True)
class ShapeGradientStop:
    offset: float
    color: str
    opacity: float


@dataclass(frozen=True)
class ShapePath:
    path_data: str
    fill: str
    fill_opacity: float
    stroke: str
    stroke_width_pt: float
    gradient_stops: tuple[ShapeGradientStop, ...]
    shadow_dy_pt: float
    shadow_color: str
    shadow_opacity: float


@dataclass(frozen=True)
class ShapeGroupSpec:
    width_pt: float
    height_pt: float
    coord_width: float
    coord_height: float
    boxes: list[ShapeBox]
    paths: tuple[ShapePath, ...] = ()
    origin_x_pt: float = 0.0
    origin_y_pt: float = 0.0


@dataclass(frozen=True)
class DocxTextDefaults:
    font_size_pt: float
    font_family: str


@dataclass(frozen=True)
class StandaloneOverlayRow:
    paragraph_index: int
    boxes: tuple[ShapeBox, ...]
    paths: tuple[ShapePath, ...]
    min_x: float
    min_y: float
    max_x: float
    max_y: float


def _read_xml(archive: ZipFile, member: str) -> ET.Element:
    return ET.fromstring(archive.read(member))


def _parse_style(style: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for item in (style or "").split(";"):
        if ":" not in item:
            continue
        key, value = item.split(":", 1)
        parsed[key.strip()] = value.strip()
    return parsed


def _parse_measure(value: str, default: float = 0.0) -> float:
    if not value:
        return default
    cleaned = value.strip().lower()
    if cleaned.endswith("pt"):
        cleaned = cleaned[:-2]
    try:
        return float(cleaned)
    except ValueError:
        return default


def _parse_coordsize(value: str) -> tuple[float, float]:
    if not value:
        return 1000.0, 1000.0
    width, height = (part.strip() for part in value.split(",", 1))
    return float(width), float(height)


def _build_shapetype_map(paragraphs: list[ET.Element]) -> dict[str, ET.Element]:
    shapetypes: dict[str, ET.Element] = {}
    for paragraph in paragraphs:
        for shapetype in paragraph.findall(".//v:shapetype", VML_NS):
            shape_id = shapetype.attrib.get("id")
            if shape_id and shape_id not in shapetypes:
                shapetypes[shape_id] = shapetype
    return shapetypes


def _parse_vml_fraction(value: str | None, default: float = 1.0) -> float:
    if not value:
        return default
    cleaned = value.strip().lower()
    if not cleaned:
        return default
    if re.fullmatch(r"[0-9a-f]+", cleaned):
        base = 0xFFFF if len(cleaned) <= 4 else 0xFFFFFF
        return max(0.0, min(1.0, int(cleaned, 16) / base))
    try:
        numeric = float(cleaned)
    except ValueError:
        return default
    if numeric > 1.0:
        numeric /= 100.0
    return max(0.0, min(1.0, numeric))


def _read_docx_text_defaults(archive: ZipFile) -> DocxTextDefaults:
    font_size_pt = 11.0
    font_family = "Calibri"

    try:
        styles_root = _read_xml(archive, "word/styles.xml")
        size_node = styles_root.find(
            ".//w:docDefaults/w:rPrDefault/w:rPr/w:sz",
            VML_NS,
        )
        if size_node is not None:
            font_size_pt = _parse_measure(
                size_node.attrib.get(f"{{{VML_NS['w']}}}val", ""),
                default=22.0,
            ) / 2.0
    except KeyError:
        pass

    try:
        theme_root = _read_xml(archive, "word/theme/theme1.xml")
        theme_ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
        latin_node = theme_root.find(
            ".//a:themeElements/a:fontScheme/a:minorFont/a:latin",
            theme_ns,
        )
        if latin_node is not None and latin_node.attrib.get("typeface"):
            font_family = latin_node.attrib["typeface"]
    except KeyError:
        pass

    return DocxTextDefaults(font_size_pt=font_size_pt, font_family=font_family)


def _sanitize_color(value: str | None, default: str) -> str:
    if not value:
        return default
    cleaned = value.split("[", 1)[0].strip().lower()
    named = {
        "red": "#ff0000",
        "yellow": "#ffff00",
        "white": "#ffffff",
        "black": "#000000",
        "blue": "#4472c4",
        "green": "#70ad47",
    }
    if cleaned in named:
        return named[cleaned]
    if re.fullmatch(r"#[0-9a-f]{6}", cleaned):
        return cleaned
    if re.fullmatch(r"[0-9a-f]{6}", cleaned):
        return "#" + cleaned
    return default


def _luminance(hex_color: str) -> float:
    color = hex_color.lstrip("#")
    if len(color) != 6:
        return 1.0
    r = int(color[0:2], 16) / 255.0
    g = int(color[2:4], 16) / 255.0
    b = int(color[4:6], 16) / 255.0
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _default_text_color(fill: str) -> str:
    return "#ffffff" if _luminance(fill) < 0.45 else "#111827"


def _extract_shape_lines(
    shape: ET.Element,
    fill: str,
    default_font_size_pt: float,
) -> list[ShapeTextLine]:
    textbox = shape.find("v:textbox", VML_NS)
    if textbox is None:
        return []

    lines: list[ShapeTextLine] = []
    for paragraph in textbox.findall(".//w:p", VML_NS):
        text = normalize_visible_text(
            "".join(node.text or "" for node in paragraph.findall(".//w:t", VML_NS))
        )
        if not text:
            continue
        align_node = paragraph.find("w:pPr/w:jc", VML_NS)
        align = align_node.attrib.get(f"{{{VML_NS['w']}}}val", "left") if align_node is not None else "left"
        runs = paragraph.findall("w:r", VML_NS)
        font_size_pt = default_font_size_pt
        bold = False
        color = _default_text_color(fill)
        for run in runs:
            size_node = run.find("w:rPr/w:sz", VML_NS)
            if size_node is not None:
                font_size_pt = max(
                    font_size_pt,
                    _parse_measure(size_node.attrib.get(f"{{{VML_NS['w']}}}val", ""), default=28.0) / 2.0,
                )
            if run.find("w:rPr/w:b", VML_NS) is not None:
                bold = True
            color_node = run.find("w:rPr/w:color", VML_NS)
            if color_node is not None:
                color = _sanitize_color(
                    color_node.attrib.get(f"{{{VML_NS['w']}}}val"),
                    color,
                )
        lines.append(
            ShapeTextLine(
                text=text,
                font_size_pt=font_size_pt,
                bold=bold,
                color=color,
                align=align,
            )
        )
    return lines


def _parse_textbox_inset_pt(shape: ET.Element) -> tuple[float, float, float, float]:
    textbox = shape.find("v:textbox", VML_NS)
    default_inset = (2.88, 1.44, 2.88, 1.44)
    if textbox is None:
        return default_inset

    raw_inset = textbox.attrib.get("inset")
    if not raw_inset:
        return default_inset

    values = [
        _parse_measure(part.strip(), default=default_inset[index])
        for index, part in enumerate(raw_inset.split(",")[:4])
    ]
    if len(values) != 4:
        return default_inset
    return values[0], values[1], values[2], values[3]


def _extract_group_spec(group: ET.Element, default_font_size_pt: float) -> ShapeGroupSpec:
    group_style = _parse_style(group.attrib.get("style", ""))
    origin_x_pt = _parse_measure(group_style.get("margin-left") or group_style.get("left"))
    origin_y_pt = _parse_measure(group_style.get("margin-top") or group_style.get("top"))
    width_pt = _parse_measure(group_style.get("width"), default=480.0)
    height_pt = _parse_measure(group_style.get("height"), default=640.0)
    coord_width, coord_height = _parse_coordsize(group.attrib.get("coordsize", ""))
    scale_x = coord_width / width_pt if width_pt else 1.0
    scale_y = coord_height / height_pt if height_pt else 1.0

    boxes: list[ShapeBox] = []
    for shape in list(group.findall("v:shape", VML_NS)) + list(group.findall("v:rect", VML_NS)):
        style = _parse_style(shape.attrib.get("style", ""))
        lines = _extract_shape_lines(shape, fill="#ffffff", default_font_size_pt=default_font_size_pt)
        joined_text = normalize_visible_text(" ".join(line.text for line in lines))
        if joined_text and FIGURE_TEXT_RE.match(joined_text):
            continue
        x = _parse_measure(style.get("left"))
        y = _parse_measure(style.get("top"))
        width = _parse_measure(style.get("width"))
        height = _parse_measure(style.get("height"))
        if width <= 0 or height <= 0:
            continue
        fill = _sanitize_color(shape.attrib.get("fillcolor"), "#ffffff")
        fill_node = shape.find("v:fill", VML_NS)
        if fill_node is not None:
            fill = _sanitize_color(fill_node.attrib.get("color"), fill)
        lines = _extract_shape_lines(shape, fill=fill, default_font_size_pt=default_font_size_pt)
        stroke = _sanitize_color(shape.attrib.get("strokecolor"), "#000000")
        stroke_node = shape.find("v:stroke", VML_NS)
        if stroke_node is not None:
            stroke = _sanitize_color(stroke_node.attrib.get("color"), stroke)
        stroke_width_pt = _parse_measure(shape.attrib.get("strokeweight"), default=0.75)
        v_anchor = style.get("v-text-anchor", "top")
        align = lines[0].align if lines else "left"
        text_anchor = "middle" if align == "center" else "start"
        inset_left_pt, inset_top_pt, inset_right_pt, inset_bottom_pt = _parse_textbox_inset_pt(shape)
        boxes.append(
            ShapeBox(
                x=x,
                y=y,
                width=width,
                height=height,
                fill=fill,
                stroke=stroke,
                stroke_width_pt=stroke_width_pt,
                text_anchor=text_anchor,
                vertical_anchor=v_anchor,
                lines=lines,
                inset_left_pt=inset_left_pt,
                inset_top_pt=inset_top_pt,
                inset_right_pt=inset_right_pt,
                inset_bottom_pt=inset_bottom_pt,
            )
        )

    return ShapeGroupSpec(
        width_pt=width_pt,
        height_pt=height_pt,
        coord_width=coord_width,
        coord_height=coord_height,
        boxes=boxes,
        origin_x_pt=origin_x_pt,
        origin_y_pt=origin_y_pt,
    )


def _parse_vml_path(path_value: str, x: float, y: float, width: float, height: float, coord_width: float, coord_height: float) -> str | None:
    if not path_value or coord_width <= 0 or coord_height <= 0:
        return None

    def to_svg_point(local_x: float, local_y: float) -> tuple[float, float]:
        return (
            x + (local_x / coord_width) * width,
            y + (local_y / coord_height) * height,
        )

    segments: list[str] = []
    current_point: tuple[float, float] | None = None
    for match in re.finditer(r"([a-z])([^a-z]*)", path_value, flags=re.IGNORECASE):
        command = match.group(1).lower()
        raw_args = match.group(2).strip()
        values = [
            float(token) if token.strip() else 0.0
            for token in raw_args.split(",")
            if token.strip() or token == ""
        ]
        pairs = [
            (values[index], values[index + 1])
            for index in range(0, len(values) - 1, 2)
        ]

        if command == "m":
            for index, (local_x, local_y) in enumerate(pairs):
                current_point = (local_x, local_y)
                svg_x, svg_y = to_svg_point(local_x, local_y)
                verb = "M" if index == 0 else "L"
                segments.append(f"{verb}{svg_x:.2f},{svg_y:.2f}")
        elif command == "l":
            for local_x, local_y in pairs:
                current_point = (local_x, local_y)
                svg_x, svg_y = to_svg_point(local_x, local_y)
                segments.append(f"L{svg_x:.2f},{svg_y:.2f}")
        elif command == "r":
            if current_point is None:
                continue
            for dx, dy in pairs:
                current_point = (current_point[0] + dx, current_point[1] + dy)
                svg_x, svg_y = to_svg_point(*current_point)
                segments.append(f"L{svg_x:.2f},{svg_y:.2f}")
        elif command == "x":
            segments.append("Z")
        elif command == "e":
            break

    return " ".join(segments) if segments else None


def _ellipse_polygon_path(
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    segments: int = 48,
) -> str:
    cx = x + width / 2.0
    cy = y + height / 2.0
    rx = width / 2.0
    ry = height / 2.0
    points: list[str] = []
    for index in range(segments):
        angle = (2.0 * math.pi * index) / segments
        px = cx + rx * math.cos(angle)
        py = cy + ry * math.sin(angle)
        verb = "M" if index == 0 else "L"
        points.append(f"{verb}{px:.2f},{py:.2f}")
    points.append("Z")
    return " ".join(points)


def _resolve_shape_path_definition(
    shape: ET.Element,
    shapetype_map: dict[str, ET.Element],
) -> tuple[str | None, str, str | None]:
    path_value = shape.attrib.get("path")
    coordsize_value = shape.attrib.get("coordsize", "")
    office_ns = "urn:schemas-microsoft-com:office:office"
    shape_spt = shape.attrib.get(f"{{{office_ns}}}spt")

    if path_value:
        return path_value, coordsize_value, shape_spt

    type_ref = shape.attrib.get("type", "").strip()
    if not type_ref.startswith("#"):
        return None, coordsize_value, shape_spt

    shapetype = shapetype_map.get(type_ref[1:])
    if shapetype is None:
        return None, coordsize_value, shape_spt

    if not coordsize_value:
        coordsize_value = shapetype.attrib.get("coordsize", "")
    if not shape_spt:
        shape_spt = shapetype.attrib.get(f"{{{office_ns}}}spt")
    return shapetype.attrib.get("path"), coordsize_value, shape_spt


def _extract_standalone_path(
    shape: ET.Element,
    default_font_size_pt: float,
    shapetype_map: dict[str, ET.Element],
) -> ShapePath | None:
    if _extract_shape_lines(shape, fill="#ffffff", default_font_size_pt=default_font_size_pt):
        return None
    path_value, coordsize_value, shape_spt = _resolve_shape_path_definition(shape, shapetype_map)
    if not path_value:
        return None

    style = _parse_style(shape.attrib.get("style", ""))
    x = _parse_measure(style.get("margin-left") or style.get("left"))
    y = _parse_measure(style.get("margin-top") or style.get("top"))
    width = _parse_measure(style.get("width"))
    height = _parse_measure(style.get("height"))
    if width <= 0 or height <= 0:
        return None

    coord_width, coord_height = _parse_coordsize(coordsize_value)
    is_ellipse_like = (
        (shape_spt or "").strip() == "120"
        or "qx" in path_value.lower()
        or "qy" in path_value.lower()
    )
    if is_ellipse_like:
        svg_path = _ellipse_polygon_path(x, y, width, height)
    else:
        svg_path = _parse_vml_path(path_value, x, y, width, height, coord_width, coord_height)
    if svg_path is None:
        return None

    stroke = "none" if shape.attrib.get("stroked", "").lower() == "f" else _sanitize_color(shape.attrib.get("strokecolor"), "#000000")
    stroke_width_pt = _parse_measure(shape.attrib.get("strokeweight"), default=0.75)
    fill = _sanitize_color(shape.attrib.get("fillcolor"), "#272727")
    fill_node = shape.find("v:fill", VML_NS)
    gradient_stops: tuple[ShapeGradientStop, ...] = ()
    fill_opacity = 0.85
    if fill_node is not None and fill_node.attrib.get("type") == "gradientRadial":
        center_color = _sanitize_color(fill_node.attrib.get("color2"), fill)
        colors_attr = fill_node.attrib.get("colors", "")
        colors_parts = [part.strip() for part in colors_attr.split(";") if part.strip()]
        mid_offset = 0.4
        mid_color = "#616161"
        if colors_parts:
            first_offset, _, first_color = colors_parts[0].partition(" ")
            parsed_offset = _parse_vml_fraction(first_offset, default=0.4)
            mid_offset = parsed_offset if 0.0 < parsed_offset < 1.0 else mid_offset
            if first_color:
                mid_color = _sanitize_color(first_color, mid_color)
        gradient_stops = (
            ShapeGradientStop(offset=0.0, color=center_color, opacity=_parse_vml_fraction(fill_node.attrib.get(f"{{urn:schemas-microsoft-com:office:office}}opacity2"), default=0.0)),
            ShapeGradientStop(offset=mid_offset, color=mid_color, opacity=0.62),
            ShapeGradientStop(offset=1.0, color=fill, opacity=0.9),
        )
    elif fill_node is not None and fill_node.attrib.get("type") == "gradient":
        fill_opacity = max(
            0.25,
            min(
                0.45,
                _parse_vml_fraction(
                    fill_node.attrib.get("{urn:schemas-microsoft-com:office:office}opacity2"),
                    default=0.16,
                )
                + 0.18,
            ),
        )

    shadow_dy_pt = 0.0
    shadow_color = "#000000"
    shadow_opacity = 0.0
    shadow_node = shape.find("v:shadow", VML_NS)
    if shadow_node is not None and shadow_node.attrib.get("on", "").lower() == "t":
        shadow_color = _sanitize_color(shadow_node.attrib.get("color"), "#000000")
        shadow_opacity = max(0.18, _parse_vml_fraction(shadow_node.attrib.get("opacity"), default=0.22))
        shadow_offset = shadow_node.attrib.get("offset", "")
        offset_y = shadow_offset.split(",", 1)[1] if "," in shadow_offset else shadow_offset
        shadow_dy_pt = _parse_measure(offset_y, default=1.5)

    return ShapePath(
        path_data=svg_path,
        fill=fill,
        fill_opacity=fill_opacity,
        stroke=stroke,
        stroke_width_pt=stroke_width_pt,
        gradient_stops=gradient_stops,
        shadow_dy_pt=shadow_dy_pt,
        shadow_color=shadow_color,
        shadow_opacity=shadow_opacity,
    )


def _extract_standalone_shape(shape: ET.Element, default_font_size_pt: float) -> ShapeBox | None:
    style = _parse_style(shape.attrib.get("style", ""))
    lines = _extract_shape_lines(shape, fill="#ffffff", default_font_size_pt=default_font_size_pt)
    joined_text = normalize_visible_text(" ".join(line.text for line in lines))
    if joined_text and FIGURE_TEXT_RE.match(joined_text):
        return None

    x = _parse_measure(style.get("margin-left") or style.get("left"))
    y = _parse_measure(style.get("margin-top") or style.get("top"))
    width = _parse_measure(style.get("width"))
    height = _parse_measure(style.get("height"))
    if width <= 0 or height <= 0:
        return None

    fill = _sanitize_color(shape.attrib.get("fillcolor"), "#ffffff")
    fill_node = shape.find("v:fill", VML_NS)
    if fill_node is not None:
        fill = _sanitize_color(fill_node.attrib.get("color"), fill)
    lines = _extract_shape_lines(shape, fill=fill, default_font_size_pt=default_font_size_pt)
    if not lines:
        return None

    stroke = _sanitize_color(shape.attrib.get("strokecolor"), "#000000")
    stroke_node = shape.find("v:stroke", VML_NS)
    if stroke_node is not None:
        stroke = _sanitize_color(stroke_node.attrib.get("color"), stroke)
    stroke_width_pt = _parse_measure(shape.attrib.get("strokeweight"), default=0.75)
    v_anchor = style.get("v-text-anchor", "top")
    align = lines[0].align if lines else "left"
    text_anchor = "middle" if align == "center" else "start"
    inset_left_pt, inset_top_pt, inset_right_pt, inset_bottom_pt = _parse_textbox_inset_pt(shape)
    return ShapeBox(
        x=x,
        y=y,
        width=width,
        height=height,
        fill=fill,
        stroke=stroke,
        stroke_width_pt=stroke_width_pt,
        text_anchor=text_anchor,
        vertical_anchor=v_anchor,
        lines=lines,
        inset_left_pt=inset_left_pt,
        inset_top_pt=inset_top_pt,
        inset_right_pt=inset_right_pt,
        inset_bottom_pt=inset_bottom_pt,
    )


def _extract_standalone_spec(
    paragraphs: list[ET.Element],
    default_font_size_pt: float,
) -> ShapeGroupSpec | None:
    row_gap = 20.0
    row_cursor = 0.0
    boxes: list[ShapeBox] = []

    for paragraph in paragraphs:
        paragraph_shapes = _paragraph_non_group_shapes(paragraph)
        row_shapes = [
            parsed
            for shape in paragraph_shapes
            if (parsed := _extract_standalone_shape(shape, default_font_size_pt)) is not None
        ]
        if not row_shapes:
            continue
        min_local_y = min(shape.y for shape in row_shapes)
        max_local_y = max(shape.y + shape.height for shape in row_shapes)
        row_base = row_cursor - min_local_y
        boxes.extend(
            ShapeBox(
                x=shape.x,
                y=shape.y + row_base,
                width=shape.width,
                height=shape.height,
                fill=shape.fill,
                stroke=shape.stroke,
                stroke_width_pt=shape.stroke_width_pt,
                text_anchor=shape.text_anchor,
                vertical_anchor=shape.vertical_anchor,
                lines=shape.lines,
                inset_left_pt=shape.inset_left_pt,
                inset_top_pt=shape.inset_top_pt,
                inset_right_pt=shape.inset_right_pt,
                inset_bottom_pt=shape.inset_bottom_pt,
            )
            for shape in row_shapes
        )
        row_cursor += (max_local_y - min_local_y) + row_gap

    if not boxes:
        return None

    min_x = min(box.x for box in boxes)
    min_y = min(box.y for box in boxes)
    max_x = max(box.x + box.width for box in boxes)
    max_y = max(box.y + box.height for box in boxes)
    padding = 18.0
    shifted_boxes = [
        ShapeBox(
            x=box.x - min_x + padding,
            y=box.y - min_y + padding,
            width=box.width,
            height=box.height,
            fill=box.fill,
            stroke=box.stroke,
            stroke_width_pt=box.stroke_width_pt,
            text_anchor=box.text_anchor,
            vertical_anchor=box.vertical_anchor,
            lines=box.lines,
            inset_left_pt=box.inset_left_pt,
            inset_top_pt=box.inset_top_pt,
            inset_right_pt=box.inset_right_pt,
            inset_bottom_pt=box.inset_bottom_pt,
        )
        for box in boxes
    ]
    width_pt = max_x - min_x + padding * 2
    height_pt = max_y - min_y + padding * 2
    return ShapeGroupSpec(
        width_pt=width_pt,
        height_pt=height_pt,
        coord_width=width_pt,
        coord_height=height_pt,
        boxes=shifted_boxes,
        origin_x_pt=0.0,
        origin_y_pt=0.0,
    )


def _collect_standalone_paths(
    paragraphs: list[ET.Element],
    default_font_size_pt: float,
) -> tuple[ShapePath, ...]:
    shapetype_map = _build_shapetype_map(paragraphs)
    paths: list[ShapePath] = []
    for paragraph in paragraphs:
        for shape in _paragraph_non_group_shapes(paragraph):
            if (parsed := _extract_standalone_path(shape, default_font_size_pt, shapetype_map)) is not None:
                paths.append(parsed)
    return tuple(paths)


def _paragraph_non_group_shapes(paragraph: ET.Element) -> list[ET.Element]:
    grouped_shapes = {
        shape
        for group in paragraph.findall(".//v:group", VML_NS)
        for shape in list(group.findall(".//v:shape", VML_NS)) + list(group.findall(".//v:rect", VML_NS))
    }
    shapes = list(paragraph.findall(".//v:shape", VML_NS)) + list(paragraph.findall(".//v:rect", VML_NS))
    return [shape for shape in shapes if shape not in grouped_shapes]


def _extract_standalone_overlay_rows(
    paragraphs: list[ET.Element],
    default_font_size_pt: float,
) -> tuple[StandaloneOverlayRow, ...]:
    shapetype_map = _build_shapetype_map(paragraphs)
    rows: list[StandaloneOverlayRow] = []
    pending_paths: list[ShapePath] = []
    pending_min_x = pending_min_y = pending_max_x = pending_max_y = 0.0
    pending_paragraph_index: int | None = None

    def path_bounds(path: ShapePath) -> tuple[float, float, float, float]:
        numbers = [float(value) for value in re.findall(r"-?\d+(?:\.\d+)?", path.path_data)]
        xs = numbers[0::2]
        ys = numbers[1::2]
        return min(xs), min(ys), max(xs), max(ys)

    for paragraph_index, paragraph in enumerate(paragraphs):
        paragraph_shapes = _paragraph_non_group_shapes(paragraph)
        boxes = [
            parsed
            for shape in paragraph_shapes
            if (parsed := _extract_standalone_shape(shape, default_font_size_pt)) is not None
        ]
        paths = [
            parsed
            for shape in paragraph_shapes
            if (parsed := _extract_standalone_path(shape, default_font_size_pt, shapetype_map)) is not None
        ]
        if not boxes and not paths:
            continue

        if not boxes and paths:
            bounds = [path_bounds(path) for path in paths]
            min_x = min(bound[0] for bound in bounds)
            min_y = min(bound[1] for bound in bounds)
            max_x = max(bound[2] for bound in bounds)
            max_y = max(bound[3] for bound in bounds)
            if not pending_paths:
                pending_min_x, pending_min_y, pending_max_x, pending_max_y = min_x, min_y, max_x, max_y
                pending_paragraph_index = paragraph_index
            else:
                pending_min_x = min(pending_min_x, min_x)
                pending_min_y = min(pending_min_y, min_y)
                pending_max_x = max(pending_max_x, max_x)
                pending_max_y = max(pending_max_y, max_y)
            pending_paths.extend(paths)
            continue

        min_x = min(box.x for box in boxes)
        min_y = min(box.y for box in boxes)
        max_x = max(box.x + box.width for box in boxes)
        max_y = max(box.y + box.height for box in boxes)
        if pending_paths:
            min_x = min(min_x, pending_min_x)
            min_y = min(min_y, pending_min_y)
            max_x = max(max_x, pending_max_x)
            max_y = max(max_y, pending_max_y)
        rows.append(
            StandaloneOverlayRow(
                paragraph_index=pending_paragraph_index if pending_paths and pending_paragraph_index is not None else paragraph_index,
                boxes=tuple(boxes),
                paths=tuple([*pending_paths, *paths]),
                min_x=min_x,
                min_y=min_y,
                max_x=max_x,
                max_y=max_y,
            )
        )
        pending_paths = []
        pending_paragraph_index = None

    if pending_paths:
        rows.append(
            StandaloneOverlayRow(
                paragraph_index=pending_paragraph_index or len(paragraphs),
                boxes=(),
                paths=tuple(pending_paths),
                min_x=pending_min_x,
                min_y=pending_min_y,
                max_x=pending_max_x,
                max_y=pending_max_y,
            )
        )
    return tuple(rows)


def _transform_path_data(
    path_data: str,
    transform,
) -> str:
    segments: list[str] = []
    for match in re.finditer(r"([MLZ])([^MLZ]*)", path_data):
        command = match.group(1)
        if command == "Z":
            segments.append("Z")
            continue
        coords = [
            float(value)
            for value in re.findall(r"-?\d+(?:\.\d+)?", match.group(2))
        ]
        pairs = [
            transform(coords[index], coords[index + 1])
            for index in range(0, len(coords), 2)
        ]
        if not pairs:
            continue
        formatted = " ".join(f"{x:.2f},{y:.2f}" for x, y in pairs)
        segments.append(f"{command}{formatted}")
    return " ".join(segments)


def _merge_overlay_rows_into_group(
    spec: ShapeGroupSpec,
    overlay_rows: tuple[StandaloneOverlayRow, ...],
) -> ShapeGroupSpec:
    if not overlay_rows:
        return spec

    scale_x = spec.coord_width / spec.width_pt if spec.width_pt else 1.0
    scale_y = spec.coord_height / spec.height_pt if spec.height_pt else 1.0
    content_boxes = [box for box in spec.boxes if box.height < spec.coord_height * 0.25]
    if not content_boxes:
        return spec

    sorted_boxes = sorted(content_boxes, key=lambda box: (box.y, box.x))
    row_bands: list[tuple[float, float]] = []
    tolerance = 300.0
    for box in sorted_boxes:
        top = box.y
        bottom = box.y + box.height
        if not row_bands or abs(top - row_bands[-1][0]) > tolerance:
            row_bands.append((top, bottom))
        else:
            row_bands[-1] = (
                min(row_bands[-1][0], top),
                max(row_bands[-1][1], bottom),
            )

    gaps: list[tuple[float, float]] = []
    for index in range(len(row_bands) - 1):
        gap_top = row_bands[index][1]
        gap_bottom = row_bands[index + 1][0]
        if gap_bottom - gap_top >= 3000.0 and gap_top >= 10000.0:
            gaps.append((gap_top, gap_bottom))

    merged_boxes = list(spec.boxes)
    merged_paths = list(spec.paths)
    group_left_pt = spec.origin_x_pt

    def row_anchor_range(row: StandaloneOverlayRow) -> tuple[float, float]:
        return (
            min((box.y for box in row.boxes), default=row.min_y),
            max((box.y + box.height for box in row.boxes), default=row.max_y),
        )

    def row_height_units(row: StandaloneOverlayRow) -> float:
        anchor_min_y, anchor_max_y = row_anchor_range(row)
        return (anchor_max_y - anchor_min_y) * scale_y

    def row_disjoint_horizontally(row: StandaloneOverlayRow, band_rows: list[StandaloneOverlayRow]) -> bool:
        for other in band_rows:
            if not (row.max_x <= other.min_x or row.min_x >= other.max_x):
                return False
        return True

    ordered_rows = sorted(overlay_rows, key=lambda item: item.paragraph_index)
    band_spacing = 900.0
    row_index = 0
    for gap_top, gap_bottom in gaps:
        if row_index >= len(ordered_rows):
            break

        gap_height = gap_bottom - gap_top
        bands: list[list[StandaloneOverlayRow]] = []
        band_heights: list[float] = []

        while row_index < len(ordered_rows):
            row = ordered_rows[row_index]
            height_units = row_height_units(row)
            if not bands:
                if height_units > gap_height:
                    break
                bands.append([row])
                band_heights.append(height_units)
                row_index += 1
                continue

            shared_height = max(band_heights[-1], height_units)
            shared_total = sum(band_heights[:-1]) + shared_height + band_spacing * (len(bands) - 1)
            if row_disjoint_horizontally(row, bands[-1]) and shared_total <= gap_height:
                bands[-1].append(row)
                band_heights[-1] = shared_height
                row_index += 1
                continue

            stacked_total = sum(band_heights) + height_units + band_spacing * len(bands)
            if stacked_total <= gap_height:
                bands.append([row])
                band_heights.append(height_units)
                row_index += 1
                continue
            break

        if not bands:
            continue

        content_height = sum(band_heights) + band_spacing * max(0, len(bands) - 1)
        band_top = gap_top + max(0.0, (gap_height - content_height) / 2.0)

        for band_rows, band_height in zip(bands, band_heights):
            for row in band_rows:
                anchor_min_y, anchor_max_y = row_anchor_range(row)
                row_height = (anchor_max_y - anchor_min_y) * scale_y
                row_top = band_top + max(0.0, (band_height - row_height) / 2.0)

                for box in row.boxes:
                    merged_boxes.append(
                        ShapeBox(
                            x=(box.x - group_left_pt) * scale_x,
                            y=row_top + (box.y - anchor_min_y) * scale_y,
                            width=box.width * scale_x,
                            height=box.height * scale_y,
                            fill=box.fill,
                            stroke=box.stroke,
                            stroke_width_pt=box.stroke_width_pt,
                            text_anchor=box.text_anchor,
                            vertical_anchor=box.vertical_anchor,
                            lines=box.lines,
                            inset_left_pt=box.inset_left_pt,
                            inset_top_pt=box.inset_top_pt,
                            inset_right_pt=box.inset_right_pt,
                            inset_bottom_pt=box.inset_bottom_pt,
                        )
                    )

                anchor_center_y = (anchor_min_y + anchor_max_y) / 2.0
                full_center_y = (row.min_y + row.max_y) / 2.0
                path_center_adjust = (anchor_center_y - full_center_y) * scale_y

                def transform(local_x: float, local_y: float) -> tuple[float, float]:
                    return (
                        (local_x - group_left_pt) * scale_x,
                        row_top + (local_y - anchor_min_y) * scale_y + path_center_adjust,
                    )

                for path in row.paths:
                    merged_paths.append(
                        ShapePath(
                            path_data=_transform_path_data(path.path_data, transform),
                            fill=path.fill,
                            fill_opacity=path.fill_opacity,
                            stroke=path.stroke,
                            stroke_width_pt=path.stroke_width_pt,
                            gradient_stops=path.gradient_stops,
                            shadow_dy_pt=path.shadow_dy_pt,
                            shadow_color=path.shadow_color,
                            shadow_opacity=path.shadow_opacity,
                        )
                    )

            band_top += band_height + band_spacing

    return ShapeGroupSpec(
        width_pt=spec.width_pt,
        height_pt=spec.height_pt,
        coord_width=spec.coord_width,
        coord_height=spec.coord_height,
        boxes=merged_boxes,
        paths=tuple(merged_paths),
        origin_x_pt=spec.origin_x_pt,
        origin_y_pt=spec.origin_y_pt,
    )


def _best_group(
    paragraphs: list[ET.Element],
    default_font_size_pt: float,
) -> ShapeGroupSpec:
    best_spec: ShapeGroupSpec | None = None
    for paragraph in paragraphs:
        for group in paragraph.findall(".//v:group", VML_NS):
            spec = _extract_group_spec(group, default_font_size_pt)
            if best_spec is None or len(spec.boxes) > len(best_spec.boxes):
                best_spec = spec
    if best_spec is None:
        best_spec = _extract_standalone_spec(paragraphs, default_font_size_pt)
    if best_spec is None:
        raise ValueError("No VML group or standalone shape set found in the requested paragraph range.")
    merged = ShapeGroupSpec(
        width_pt=best_spec.width_pt,
        height_pt=best_spec.height_pt,
        coord_width=best_spec.coord_width,
        coord_height=best_spec.coord_height,
        boxes=best_spec.boxes,
        paths=(),
        origin_x_pt=best_spec.origin_x_pt,
        origin_y_pt=best_spec.origin_y_pt,
    )
    overlay_rows = _extract_standalone_overlay_rows(paragraphs, default_font_size_pt)
    return _merge_overlay_rows_into_group(merged, overlay_rows)


def _css_font_stack(primary_family: str) -> str:
    families: list[str] = []
    for family in [primary_family, "Arial", "Helvetica", "sans-serif"]:
        if family and family not in families:
            families.append(family)
    quoted: list[str] = []
    for family in families:
        if family == "sans-serif":
            quoted.append(family)
        elif " " in family:
            quoted.append(f"'{family}'")
        else:
            quoted.append(family)
    return ",".join(quoted)


def _render_text_box_foreign_object(
    box: ShapeBox,
    scale_x: float,
    scale_y: float,
    font_family: str,
) -> str:
    if not box.lines:
        return ""

    line_heights = [line.font_size_pt * scale_y * 1.18 for line in box.lines]
    total_height = sum(line_heights)
    should_center_text = box.vertical_anchor == "middle" or box.height <= total_height * 2.4
    justify_content = "center" if should_center_text else "flex-start"
    inset_left = box.inset_left_pt * scale_x
    inset_top = box.inset_top_pt * scale_y
    inset_right = box.inset_right_pt * scale_x
    inset_bottom = box.inset_bottom_pt * scale_y
    text_align = "center" if box.text_anchor == "middle" else "left"
    align_items = "center" if box.text_anchor == "middle" else "stretch"
    container_style = "; ".join(
        [
            "width:100%",
            "height:100%",
            "display:flex",
            "flex-direction:column",
            f"justify-content:{justify_content}",
            f"align-items:{align_items}",
            "box-sizing:border-box",
            f"padding:{inset_top:.2f}px {inset_right:.2f}px {inset_bottom:.2f}px {inset_left:.2f}px",
            "overflow:hidden",
            f"font-family:{_css_font_stack(font_family)}",
        ]
    )

    paragraphs: list[str] = []
    for line in box.lines:
        paragraph_style = "; ".join(
            [
                "margin:0",
                f"font-size:{line.font_size_pt * scale_y:.2f}px",
                "line-height:1.18",
                f"font-weight:{700 if line.bold else 400}",
                f"color:{line.color}",
                f"text-align:{'center' if line.align == 'center' else text_align}",
                "white-space:normal",
                "overflow-wrap:break-word",
                "word-break:normal",
            ]
        )
        paragraphs.append(
            f'<p xmlns="http://www.w3.org/1999/xhtml" style="{paragraph_style}">{html.escape(line.text)}</p>'
        )

    return (
        f'<foreignObject x="{box.x:.2f}" y="{box.y:.2f}" width="{box.width:.2f}" height="{box.height:.2f}">'
        f'<div xmlns="http://www.w3.org/1999/xhtml" style="{container_style}">'
        + "".join(paragraphs)
        + "</div></foreignObject>"
    )


def render_shape_figure_svg(
    docx_path: Path,
    paragraph_start: int,
    paragraph_end: int,
    max_width_px: int = 1280,
) -> str:
    with ZipFile(docx_path) as archive:
        root = _read_xml(archive, "word/document.xml")
        text_defaults = _read_docx_text_defaults(archive)
    paragraphs = root.findall(".//w:body/w:p", VML_NS)[paragraph_start : paragraph_end + 1]
    spec = _best_group(paragraphs, default_font_size_pt=text_defaults.font_size_pt)

    width_px = max_width_px
    height_px = max(320, round(max_width_px * spec.height_pt / spec.width_pt))
    scale_x = spec.coord_width / spec.width_pt if spec.width_pt else 1.0
    scale_y = spec.coord_height / spec.height_pt if spec.height_pt else 1.0

    defs: list[str] = []
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width_px}" height="{height_px}" viewBox="0 0 {spec.coord_width:.0f} {spec.coord_height:.0f}" role="img" aria-label="Shape figure">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>',
        '.shape-box { rx: 120; ry: 120; }',
        '</style>',
    ]

    for index, path_shape in enumerate(spec.paths):
        if path_shape.gradient_stops:
            defs.append(f'<radialGradient id="shape-gradient-{index}" cx="50%" cy="50%" r="60%">')
            for stop in path_shape.gradient_stops:
                defs.append(
                    f'<stop offset="{stop.offset * 100:.2f}%" stop-color="{stop.color}" stop-opacity="{stop.opacity:.3f}" />'
                )
            defs.append("</radialGradient>")
        if path_shape.shadow_opacity > 0.0 and path_shape.shadow_dy_pt > 0.0:
            defs.append(
                f'<filter id="shape-shadow-{index}" x="-30%" y="-30%" width="160%" height="180%"><feDropShadow dx="0" dy="{path_shape.shadow_dy_pt * scale_y:.2f}" stdDeviation="{max(4.0, path_shape.shadow_dy_pt * scale_y * 0.8):.2f}" flood-color="{path_shape.shadow_color}" flood-opacity="{path_shape.shadow_opacity:.3f}" /></filter>'
            )

    if defs:
        parts.append("<defs>")
        parts.extend(defs)
        parts.append("</defs>")

    text_parts: list[str] = []
    for box in spec.boxes:
        stroke_width = max(0.5 * scale_x, box.stroke_width_pt * scale_x)
        parts.append(
            f'<rect x="{box.x:.2f}" y="{box.y:.2f}" width="{box.width:.2f}" height="{box.height:.2f}" fill="{box.fill}" stroke="{box.stroke}" stroke-width="{stroke_width:.2f}" />'
        )
        if not box.lines:
            continue
        text_parts.append(
            _render_text_box_foreign_object(
                box,
                scale_x=scale_x,
                scale_y=scale_y,
                font_family=text_defaults.font_family,
            )
        )

    for index, path_shape in enumerate(spec.paths):
        fill_value = f'url(#shape-gradient-{index})' if path_shape.gradient_stops else path_shape.fill
        filter_attr = f' filter="url(#shape-shadow-{index})"' if path_shape.shadow_opacity > 0.0 and path_shape.shadow_dy_pt > 0.0 else ""
        stroke_width = max(0.5 * scale_x, path_shape.stroke_width_pt * scale_x)
        parts.append(
            f'<path d="{path_shape.path_data}" fill="{fill_value}" fill-opacity="{path_shape.fill_opacity:.3f}" stroke="{path_shape.stroke}" stroke-width="{stroke_width:.2f}"{filter_attr} />'
        )

    parts.extend(text_parts)
    parts.append("</svg>")
    return "\n".join(parts) + "\n"
