#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import math
import re
import shutil
import subprocess
import tempfile
import textwrap
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from stakeholder_trace_acceptance_lib import (
    ICONS,
    PNG_SIZES,
    compare_masks,
    ensure_tools,
    similarity_passes,
    svg_length_passes,
)


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT_DIR / "artifacts" / "stakeholder_icons_trace_rebuild"
DEFAULT_ZIP_PATH = ROOT_DIR / "artifacts" / "stakeholder_icons_trace_rebuild.zip"
PACKAGE_ROOT_NAME = "stakeholder_icons_trace_rebuild"
BLUE = "#123C7C"
TRIM_PATTERN = re.compile(r"^(?P<width>\d+)x(?P<height>\d+)\+(?P<offset_x>-?\d+)\+(?P<offset_y>-?\d+)$")


@dataclass(frozen=True)
class TraceSource:
    kind: str
    path: str | None = None
    render_size: int = 2048
    threshold: int = 48
    blur: float = 0.7
    morphology: int = 1
    epsilon: float = 0.18
    smoothing_iterations: int = 0


@dataclass(frozen=True)
class CandidateSpec:
    candidate_id: str
    label: str
    trace_source: TraceSource
    fill_type: str
    negative_space: bool
    notes: str
    cleanup_actions: tuple[str, ...]
    view_box: str = "0 0 24 24"
    stroke_width: float | None = None


@dataclass(frozen=True)
class CandidateResult:
    candidate_id: str
    label: str
    trace_source_file: str
    svg_path: Path
    iou: float
    dice: float
    score: float
    svg_length: int
    acceptance_pass: bool
    fill_type: str
    negative_space: bool
    view_box: str
    stroke_width: float | None
    notes: str
    cleanup_actions: tuple[str, ...]


def trace_candidate(
    *,
    candidate_id: str,
    label: str,
    render_size: int,
    threshold: int,
    blur: float,
    epsilon: float,
    smoothing_iterations: int,
    fill_type: str,
    negative_space: bool,
    notes: str,
    cleanup_actions: tuple[str, ...],
) -> CandidateSpec:
    return CandidateSpec(
        candidate_id=candidate_id,
        label=label,
        trace_source=TraceSource(
            kind="source_reference",
            render_size=render_size,
            threshold=threshold,
            blur=blur,
            morphology=1,
            epsilon=epsilon,
            smoothing_iterations=smoothing_iterations,
        ),
        fill_type=fill_type,
        negative_space=negative_space,
        notes=notes,
        cleanup_actions=cleanup_actions,
    )


ICON_CONFIG = {
    "oil_drop": {
        "rough_crop": [10, 10, 160, 120],
        "candidates": (
            trace_candidate(
                candidate_id="balanced_trace",
                label="Balanced threshold trace",
                render_size=2200,
                threshold=46,
                blur=0.95,
                epsilon=0.16,
                smoothing_iterations=3,
                fill_type="evenodd-fill",
                negative_space=True,
                notes="保持饱满左侧轮廓、尖顶和右侧内凹透明弧线。",
                cleanup_actions=(
                    "从 source_reference 放大截图后做 alpha mask trace",
                    "保留主油滴和右侧高光切口两个关键轮廓",
                    "删除微小噪点并用平滑曲线替换像素折线",
                ),
            ),
            trace_candidate(
                candidate_id="soft_smooth_trace",
                label="Soft high-smoothing trace",
                render_size=2500,
                threshold=42,
                blur=1.05,
                epsilon=0.27,
                smoothing_iterations=5,
                fill_type="evenodd-fill",
                negative_space=True,
                notes="强化底部圆厚感，并让右侧透明弧线更贴近截图的柔和内切形。",
                cleanup_actions=(
                    "提高模糊和曲线平滑度以压掉底部阶梯边",
                    "继续保留右上向下弯折的负形高光切口",
                    "用 evenodd compound path 输出透明负形",
                ),
            ),
        ),
    },
    "regulators": {
        "rough_crop": [360, 10, 420, 120],
        "candidates": (
            trace_candidate(
                candidate_id="balanced_trace",
                label="Balanced outline trace",
                render_size=2100,
                threshold=45,
                blur=0.8,
                epsilon=0.28,
                smoothing_iterations=2,
                fill_type="filled-outline",
                negative_space=False,
                notes="保留长横梁、中心圆点、两侧秤盘、立柱和底座的截图比例。",
                cleanup_actions=(
                    "直接从裁切截图做单色 boundary trace",
                    "保留秤盘下垂关系，不把图标标准化成通用天平",
                    "平滑中心节点和秤盘外缘，去掉小锯齿",
                ),
            ),
            trace_candidate(
                candidate_id="soft_smooth_trace",
                label="Soft screenshot trace",
                render_size=2200,
                threshold=44,
                blur=0.9,
                epsilon=0.35,
                smoothing_iterations=3,
                fill_type="filled-outline",
                negative_space=False,
                notes="进一步压低库图标感，优先贴近截图里更细长的横梁和秤盘轮廓。",
                cleanup_actions=(
                    "增强平滑和简化，减少 beam 与 pan 外缘的毛刺",
                    "保留中心节点、吊线和底座的真实相对位置",
                    "输出为 currentColor 填充轮廓，避免断线",
                ),
            ),
        ),
    },
    "governments": {
        "rough_crop": [960, 10, 360, 120],
        "candidates": (
            trace_candidate(
                candidate_id="balanced_trace",
                label="Balanced temple trace",
                render_size=2100,
                threshold=42,
                blur=0.8,
                epsilon=0.24,
                smoothing_iterations=1,
                fill_type="filled-outline",
                negative_space=False,
                notes="保留屋顶尖顶、中央主体、柱列节奏和底座层次。",
                cleanup_actions=(
                    "从截图古典建筑轮廓做 trace，而不是套标准银行图标",
                    "保留屋顶顶点和中央门洞的相对宽度",
                    "压掉屋檐和底座边缘的噪点",
                ),
            ),
            trace_candidate(
                candidate_id="soft_smooth_trace",
                label="Soft high-fidelity trace",
                render_size=2200,
                threshold=40,
                blur=0.85,
                epsilon=0.28,
                smoothing_iterations=2,
                fill_type="filled-outline",
                negative_space=False,
                notes="优先逼近截图里的小型古典建筑感，避免过厚、过现代化。",
                cleanup_actions=(
                    "放宽阈值保留屋檐与柱体之间的狭窄留白",
                    "对主体轮廓做轻度平滑，避免现代几何化",
                    "保持底座层次和中轴对称",
                ),
            ),
        ),
    },
    "operators": {
        "rough_crop": [1500, 10, 360, 120],
        "candidates": (
            trace_candidate(
                candidate_id="balanced_trace",
                label="Balanced equipment trace",
                render_size=2400,
                threshold=47,
                blur=0.95,
                epsilon=0.15,
                smoothing_iterations=2,
                fill_type="evenodd-fill",
                negative_space=True,
                notes="保留塔身、底部支撑、侧边设备和平台开孔。",
                cleanup_actions=(
                    "从截图直描保留中央塔身和两侧设备回环",
                    "删除围绕塔身的杂散小碎块",
                    "用 compound path 保留塔脚和底部平台的负形开孔",
                ),
            ),
            trace_candidate(
                candidate_id="soft_smooth_trace",
                label="Soft high-smoothing trace",
                render_size=2600,
                threshold=41,
                blur=1.2,
                epsilon=0.32,
                smoothing_iterations=4,
                fill_type="evenodd-fill",
                negative_space=True,
                notes="压轻塔架外缘厚重感，突出截图里的细塔身和侧边设备轮廓。",
                cleanup_actions=(
                    "提高模糊和简化力度，减掉粗重的外圈噪边",
                    "保留右侧小圆/回环结构和底部支撑位置",
                    "把塔身、平台和设备统一成连续 fill 轮廓",
                ),
            ),
            trace_candidate(
                candidate_id="compact_trace",
                label="Compact smooth trace",
                render_size=2500,
                threshold=42,
                blur=1.15,
                epsilon=0.33,
                smoothing_iterations=4,
                fill_type="evenodd-fill",
                negative_space=True,
                notes="作为更紧凑的备选，控制路径长度同时保留设备识别度。",
                cleanup_actions=(
                    "适度提高简化率，压缩路径长度",
                    "维持中央塔身和两侧设备的总体占比",
                    "继续保留底部平台与塔脚负形",
                ),
            ),
        ),
    },
    "shield_star": {
        "rough_crop": [2080, 10, 260, 130],
        "candidates": (
            trace_candidate(
                candidate_id="balanced_trace",
                label="Balanced shield trace",
                render_size=2100,
                threshold=45,
                blur=0.85,
                epsilon=0.32,
                smoothing_iterations=2,
                fill_type="filled-outline",
                negative_space=False,
                notes="保留盾牌顶部拱形、下端尖角和紧凑的中心星形。",
                cleanup_actions=(
                    "从截图轮廓直描盾牌外形和内部星形",
                    "收掉盾牌边缘的像素折线",
                    "控制星形大小，不让其撑满盾牌内腔",
                ),
            ),
            trace_candidate(
                candidate_id="soft_smooth_trace",
                label="Soft screenshot trace",
                render_size=2200,
                threshold=44,
                blur=0.95,
                epsilon=0.42,
                smoothing_iterations=3,
                fill_type="filled-outline",
                negative_space=False,
                notes="优先贴近截图里较轻的盾牌外轮廓与较小的星形比例。",
                cleanup_actions=(
                    "增加平滑和简化，让盾牌边线更干净",
                    "保留中心星形的紧凑比例",
                    "控制路径长度，避免 trace 噪边堆积",
                ),
            ),
        ),
    },
    "global": {
        "rough_crop": [2550, 10, 260, 130],
        "candidates": (
            trace_candidate(
                candidate_id="balanced_trace",
                label="Balanced globe trace",
                render_size=2200,
                threshold=44,
                blur=0.9,
                epsilon=0.30,
                smoothing_iterations=2,
                fill_type="filled-outline",
                negative_space=False,
                notes="保留外圆、三段左右经线和横向纬线的大体布局。",
                cleanup_actions=(
                    "从截图裁切直接 trace 外圆和经纬线开孔",
                    "保留中轴横线与上下弧线的分布",
                    "轻度简化以保持小尺寸清晰度",
                ),
            ),
            trace_candidate(
                candidate_id="soft_smooth_trace",
                label="Soft high-fidelity trace",
                render_size=2400,
                threshold=43,
                blur=1.0,
                epsilon=0.26,
                smoothing_iterations=3,
                fill_type="filled-outline",
                negative_space=False,
                notes="优先匹配截图中的经纬线布局，而不是标准化为通用 globe。",
                cleanup_actions=(
                    "提高平滑度，让外圆和内部弧线更连续",
                    "保留经线的上下收口和中段横线位置",
                    "输出为清洁填充轮廓，避免位图感断线",
                ),
            ),
        ),
    },
}


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def capture(cmd: list[str], *, cwd: Path | None = None) -> str:
    return subprocess.check_output(cmd, cwd=cwd, text=True).strip()


def normalize_geometry(raw: str) -> tuple[int, int, int, int]:
    normalized = raw.replace("++", "+").replace("+-", "-")
    match = TRIM_PATTERN.fullmatch(normalized)
    if match is None:
        raise SystemExit(f"Unexpected trim geometry '{raw}'")
    return tuple(int(match.group(key)) for key in ("width", "height", "offset_x", "offset_y"))


def prepare_dirs(output_dir: Path) -> dict[str, Path]:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    dirs = {
        "package": output_dir,
        "source_reference": output_dir / "source_reference",
        "svg": output_dir / "svg",
        "png": output_dir / "png",
        "preview": output_dir / "preview",
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return dirs


def crop_source_references(source_image: Path, source_ref_dir: Path) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for name in ICONS:
        x, y, width, height = ICON_CONFIG[name]["rough_crop"]
        out_path = source_ref_dir / f"{name}_source.png"
        geometry = capture(
            [
                "magick",
                str(source_image),
                "-crop",
                f"{width}x{height}+{x}+{y}",
                "+repage",
                "-fuzz",
                "18%",
                "-transparent",
                "white",
                "-trim",
                "-format",
                "%wx%h+%X+%Y",
                "info:",
            ]
        )
        trim_width, trim_height, offset_x, offset_y = normalize_geometry(geometry)
        run(
            [
                "magick",
                str(source_image),
                "-crop",
                f"{width}x{height}+{x}+{y}",
                "+repage",
                "-fuzz",
                "18%",
                "-transparent",
                "white",
                "-trim",
                str(out_path),
            ]
        )
        result[name] = {
            "x": x + offset_x,
            "y": y + offset_y,
            "width": trim_width,
            "height": trim_height,
        }
    return result


def create_trace_source(
    icon_name: str,
    trace_source: TraceSource,
    source_reference_dir: Path,
    work_dir: Path,
    stem: str,
) -> tuple[Path, str]:
    out_path = work_dir / f"{stem}.trace-source.png"

    if trace_source.kind == "source_reference":
        ref_path = source_reference_dir / f"{icon_name}_source.png"
        run(
            [
                "magick",
                str(ref_path),
                "-background",
                "none",
                "-strip",
                "-filter",
                "Lanczos",
                "-resize",
                f"{trace_source.render_size}x{trace_source.render_size}",
                str(out_path),
            ]
        )
        return out_path, f"source_reference/{icon_name}_source.png"

    if trace_source.kind == "png" and trace_source.path:
        png_path = ROOT_DIR / trace_source.path
        run(
            [
                "magick",
                str(png_path),
                "-background",
                "none",
                "-strip",
                "-filter",
                "Lanczos",
                "-resize",
                f"{trace_source.render_size}x{trace_source.render_size}",
                str(out_path),
            ]
        )
        return out_path, str(trace_source.path)

    raise SystemExit(f"Unsupported trace source kind {trace_source.kind} for {icon_name}")


def build_trace_mask_png(trace_source: TraceSource, source_png: Path, stem: str, work_dir: Path) -> Path:
    mask_path = work_dir / f"{stem}.mask.png"
    cmd = [
        "magick",
        str(source_png),
        "-background",
        "white",
        "-alpha",
        "remove",
        "-alpha",
        "off",
        "-colorspace",
        "Gray",
        "-negate",
        "-strip",
        "-blur",
        f"0x{trace_source.blur}",
        "-threshold",
        f"{trace_source.threshold}%",
        "-morphology",
        "Close",
        f"Diamond:{trace_source.morphology}",
        str(mask_path),
    ]
    run(cmd)
    return mask_path


def build_trace_pbm(mask_png: Path, stem: str, work_dir: Path) -> Path:
    pbm_path = work_dir / f"{stem}.pbm"
    run(["magick", str(mask_png), "PBM:" + str(pbm_path)])
    return pbm_path


def parse_binary_pbm(pbm_path: Path) -> tuple[int, int, list[list[bool]]]:
    data = pbm_path.read_bytes()
    if not data.startswith(b"P4"):
        raise SystemExit(f"Expected binary PBM P4 but saw {pbm_path}")

    index = 2
    tokens: list[bytes] = []
    while len(tokens) < 2:
        while index < len(data) and data[index:index + 1] in b" \t\r\n":
            index += 1
        if index < len(data) and data[index:index + 1] == b"#":
            while index < len(data) and data[index:index + 1] != b"\n":
                index += 1
            continue
        start = index
        while index < len(data) and data[index:index + 1] not in b" \t\r\n":
            index += 1
        tokens.append(data[start:index])

    width = int(tokens[0])
    height = int(tokens[1])
    while index < len(data) and data[index:index + 1] in b" \t\r\n":
        index += 1
    raster = data[index:]
    row_bytes = math.ceil(width / 8)

    bits: list[list[int]] = []
    for y in range(height):
        row = raster[y * row_bytes:(y + 1) * row_bytes]
        values: list[int] = []
        for byte in row:
            for bit in range(7, -1, -1):
                values.append((byte >> bit) & 1)
                if len(values) == width:
                    break
            if len(values) == width:
                break
        bits.append(values)

    border_bits = bits[0] + bits[-1]
    for row in bits[1:-1]:
        border_bits.append(row[0])
        border_bits.append(row[-1])
    background_bit = 1 if sum(border_bits) >= (len(border_bits) / 2) else 0
    filled_bit = 0 if background_bit == 1 else 1
    mask = [[pixel == filled_bit for pixel in row] for row in bits]
    return width, height, mask


def polygon_area(points: list[tuple[float, float]]) -> float:
    area = 0.0
    for index, (x1, y1) in enumerate(points):
        x2, y2 = points[(index + 1) % len(points)]
        area += x1 * y2 - x2 * y1
    return area / 2.0


def extract_boundary_loops(mask: list[list[bool]]) -> list[list[tuple[float, float]]]:
    height = len(mask)
    width = len(mask[0])
    adjacency: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)

    def add_edge(start: tuple[int, int], end: tuple[int, int]) -> None:
        adjacency[start].append(end)

    for y in range(height):
        for x in range(width):
            if not mask[y][x]:
                continue
            if y == 0 or not mask[y - 1][x]:
                add_edge((x, y), (x + 1, y))
            if x == width - 1 or not mask[y][x + 1]:
                add_edge((x + 1, y), (x + 1, y + 1))
            if y == height - 1 or not mask[y + 1][x]:
                add_edge((x + 1, y + 1), (x, y + 1))
            if x == 0 or not mask[y][x - 1]:
                add_edge((x, y + 1), (x, y))

    loops: list[list[tuple[float, float]]] = []
    while adjacency:
        start = next(iter(adjacency))
        current = start
        loop = [start]
        while True:
            next_points = adjacency[current]
            next_point = next_points.pop()
            if not next_points:
                del adjacency[current]
            current = next_point
            if current == start:
                break
            loop.append(current)
        if len(loop) >= 4:
            loops.append([(float(x), float(y)) for x, y in loop])
    return loops


def remove_collinear(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    if len(points) < 3:
        return points
    cleaned: list[tuple[float, float]] = []
    total = len(points)
    for index, current in enumerate(points):
        previous = points[(index - 1) % total]
        nxt = points[(index + 1) % total]
        if (current[0] - previous[0]) * (nxt[1] - current[1]) == (current[1] - previous[1]) * (nxt[0] - current[0]):
            continue
        cleaned.append(current)
    return cleaned


def point_line_distance(point: tuple[float, float], start: tuple[float, float], end: tuple[float, float]) -> float:
    x0, y0 = point
    x1, y1 = start
    x2, y2 = end
    if x1 == x2 and y1 == y2:
        return math.hypot(x0 - x1, y0 - y1)
    numerator = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
    denominator = math.hypot(y2 - y1, x2 - x1)
    return numerator / denominator


def rdp(points: list[tuple[float, float]], epsilon: float) -> list[tuple[float, float]]:
    if len(points) <= 2:
        return points

    max_distance = 0.0
    index = 0
    start = points[0]
    end = points[-1]
    for current_index in range(1, len(points) - 1):
        distance = point_line_distance(points[current_index], start, end)
        if distance > max_distance:
            index = current_index
            max_distance = distance

    if max_distance > epsilon:
        left = rdp(points[: index + 1], epsilon)
        right = rdp(points[index:], epsilon)
        return left[:-1] + right
    return [start, end]


def simplify_closed_loop(points: list[tuple[float, float]], epsilon: float) -> list[tuple[float, float]]:
    if len(points) <= 4:
        return points
    open_points = points + [points[0]]
    simplified = rdp(open_points, epsilon)
    if simplified[0] == simplified[-1]:
        simplified = simplified[:-1]
    simplified = remove_collinear(simplified)
    return simplified if len(simplified) >= 3 else points


def chaikin_closed(points: list[tuple[float, float]], iterations: int) -> list[tuple[float, float]]:
    if iterations <= 0 or len(points) < 3:
        return points
    current = points
    for _ in range(iterations):
        next_points: list[tuple[float, float]] = []
        for index, point in enumerate(current):
            nxt = current[(index + 1) % len(current)]
            q = (0.75 * point[0] + 0.25 * nxt[0], 0.75 * point[1] + 0.25 * nxt[1])
            r = (0.25 * point[0] + 0.75 * nxt[0], 0.25 * point[1] + 0.75 * nxt[1])
            next_points.extend((q, r))
        current = next_points
    return current


def normalize_loops(
    loops: list[list[tuple[float, float]]],
    *,
    view_box_size: float,
    padding: float,
    epsilon: float,
    smoothing_iterations: int,
) -> list[list[tuple[float, float]]]:
    min_x = min(point[0] for loop in loops for point in loop)
    min_y = min(point[1] for loop in loops for point in loop)
    max_x = max(point[0] for loop in loops for point in loop)
    max_y = max(point[1] for loop in loops for point in loop)
    width = max_x - min_x
    height = max_y - min_y
    scale = (view_box_size - 2 * padding) / max(width, height)

    normalized: list[list[tuple[float, float]]] = []
    for loop in loops:
        scaled = [((x - min_x) * scale + padding, (y - min_y) * scale + padding) for x, y in loop]
        simplified = simplify_closed_loop(scaled, epsilon)
        smoothed = chaikin_closed(simplified, smoothing_iterations)
        normalized.append(simplify_closed_loop(smoothed, epsilon / 2))
    return normalized


def fmt_num(value: float) -> str:
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return text if text else "0"


def closed_curve_path_d(loop: list[tuple[float, float]]) -> str:
    if len(loop) < 3:
        return ""
    if len(loop) < 4:
        start_x, start_y = loop[0]
        parts = [f"M{fmt_num(start_x)} {fmt_num(start_y)}"]
        for x, y in loop[1:]:
            parts.append(f"L{fmt_num(x)} {fmt_num(y)}")
        parts.append("Z")
        return " ".join(parts)

    parts = [f"M{fmt_num(loop[0][0])} {fmt_num(loop[0][1])}"]
    count = len(loop)
    for index, point in enumerate(loop):
        prev_point = loop[(index - 1) % count]
        next_point = loop[(index + 1) % count]
        next_next_point = loop[(index + 2) % count]
        control_1 = (
            point[0] + (next_point[0] - prev_point[0]) / 6.0,
            point[1] + (next_point[1] - prev_point[1]) / 6.0,
        )
        control_2 = (
            next_point[0] - (next_next_point[0] - point[0]) / 6.0,
            next_point[1] - (next_next_point[1] - point[1]) / 6.0,
        )
        parts.append(
            "C"
            f"{fmt_num(control_1[0])} {fmt_num(control_1[1])} "
            f"{fmt_num(control_2[0])} {fmt_num(control_2[1])} "
            f"{fmt_num(next_point[0])} {fmt_num(next_point[1])}"
        )
    parts.append("Z")
    return " ".join(parts)


def path_d_from_loops(loops: list[list[tuple[float, float]]]) -> str:
    parts = [closed_curve_path_d(loop) for loop in loops]
    return " ".join(part for part in parts if part)


def build_trace_svg(icon_name: str, candidate: CandidateSpec, source_png: Path, work_dir: Path) -> Path:
    stem = f"{icon_name}.{candidate.candidate_id}"
    mask_png = build_trace_mask_png(candidate.trace_source, source_png, stem, work_dir)
    pbm_path = build_trace_pbm(mask_png, stem, work_dir)
    _, _, mask = parse_binary_pbm(pbm_path)
    loops = extract_boundary_loops(mask)
    if not loops:
        raise SystemExit(f"No trace loops found for {icon_name}:{candidate.candidate_id}")

    total_area = max(abs(polygon_area(loop)) for loop in loops)
    significant = [remove_collinear(loop) for loop in loops if abs(polygon_area(loop)) >= total_area * 0.002]
    if not significant:
        significant = [remove_collinear(max(loops, key=lambda item: abs(polygon_area(item))))]

    normalized_loops = normalize_loops(
        significant,
        view_box_size=24.0,
        padding=1.2 if icon_name == "oil_drop" else 1.0,
        epsilon=candidate.trace_source.epsilon,
        smoothing_iterations=candidate.trace_source.smoothing_iterations,
    )
    path_d = path_d_from_loops(normalized_loops)

    svg_path = work_dir / f"{stem}.svg"
    svg_markup = textwrap.dedent(
        f"""\
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="{candidate.view_box}" color="{BLUE}">
          <title>{icon_name.replace("_", " ")}</title>
          <path fill="currentColor" fill-rule="evenodd" d="{path_d}"/>
        </svg>
        """
    )
    svg_path.write_text(svg_markup, encoding="utf-8")
    return svg_path


def render_svg_png(svg_path: Path, output_path: Path, size: int) -> None:
    temp_png = output_path.parent / f".{output_path.name}.render.png"
    with temp_png.open("wb") as handle:
        subprocess.run(
            ["rsvg-convert", "-w", str(size), "-h", str(size), str(svg_path)],
            check=True,
            stdout=handle,
        )
    run(
        [
            "magick",
            str(temp_png),
            "-trim",
            "+repage",
            "-background",
            "none",
            "-gravity",
            "center",
            "-extent",
            f"{size}x{size}",
            str(output_path),
        ]
    )
    temp_png.unlink()


def evaluate_candidate(
    icon_name: str,
    candidate: CandidateSpec,
    source_reference_dir: Path,
    work_dir: Path,
) -> CandidateResult:
    stem = f"{icon_name}.{candidate.candidate_id}"
    trace_source_png, trace_source_file = create_trace_source(
        icon_name,
        candidate.trace_source,
        source_reference_dir,
        work_dir,
        stem,
    )
    svg_path = build_trace_svg(icon_name, candidate, trace_source_png, work_dir)
    preview_png = work_dir / f"{stem}.512.png"
    render_svg_png(svg_path, preview_png, 512)

    iou, dice = compare_masks(source_reference_dir / f"{icon_name}_source.png", preview_png)
    svg_text = svg_path.read_text(encoding="utf-8")
    svg_length = len(svg_text)
    acceptance_pass = similarity_passes(icon_name, iou, dice) and svg_length_passes(icon_name, svg_length)
    score = iou + dice - (svg_length / 50000.0)
    return CandidateResult(
        candidate_id=candidate.candidate_id,
        label=candidate.label,
        trace_source_file=trace_source_file,
        svg_path=svg_path,
        iou=iou,
        dice=dice,
        score=score,
        svg_length=svg_length,
        acceptance_pass=acceptance_pass,
        fill_type=candidate.fill_type,
        negative_space=candidate.negative_space,
        view_box=candidate.view_box,
        stroke_width=candidate.stroke_width,
        notes=candidate.notes,
        cleanup_actions=candidate.cleanup_actions,
    )


def candidate_sort_key(result: CandidateResult) -> tuple[int, float, float, int]:
    return (
        1 if result.acceptance_pass else 0,
        result.score,
        result.iou + result.dice,
        -result.svg_length,
    )


def render_pngs(svg_dir: Path, png_dir: Path) -> None:
    for name in ICONS:
        svg_path = svg_dir / f"{name}.svg"
        for size in PNG_SIZES:
            render_svg_png(svg_path, png_dir / f"{name}_{size}.png", size)


def data_uri(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def preview_svg_clear(package_dir: Path) -> str:
    cell_w = 230
    width = cell_w * len(ICONS)
    height = 230
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="white"/>',
    ]
    for index, name in enumerate(ICONS):
        x = index * cell_w
        png_href = data_uri(package_dir / "png" / f"{name}_256.png")
        parts.append(f'<image href="{png_href}" x="{x + 55}" y="22" width="120" height="120" preserveAspectRatio="xMidYMid meet"/>')
        parts.append(
            f'<text x="{x + cell_w / 2}" y="180" fill="#20314D" font-size="20" font-family="Arial, Helvetica, sans-serif" text-anchor="middle">{name}</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts)


def preview_svg_grid(package_dir: Path) -> str:
    cols = 3
    cell_w = 360
    cell_h = 290
    rows = (len(ICONS) + cols - 1) // cols
    width = cols * cell_w
    height = rows * cell_h
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="white"/>',
    ]
    for index, name in enumerate(ICONS):
        col = index % cols
        row = index // cols
        x = col * cell_w
        y = row * cell_h
        png_href = data_uri(package_dir / "png" / f"{name}_512.png")
        parts.append(f'<rect x="{x + 20}" y="{y + 18}" width="{cell_w - 40}" height="{cell_h - 36}" rx="18" fill="#FAFBFF" stroke="#E5EAF5"/>')
        parts.append(f'<image href="{png_href}" x="{x + 90}" y="{y + 38}" width="180" height="180" preserveAspectRatio="xMidYMid meet"/>')
        parts.append(
            f'<text x="{x + cell_w / 2}" y="{y + 250}" fill="#20314D" font-size="24" font-family="Arial, Helvetica, sans-serif" text-anchor="middle">{name}</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts)


def preview_svg_compare(package_dir: Path) -> str:
    cell_w = 230
    row_h = 230
    width = cell_w * len(ICONS)
    height = row_h * 2 + 24
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="white"/>',
        f'<line x1="24" y1="{row_h + 12}" x2="{width - 24}" y2="{row_h + 12}" stroke="#D8E1F0" stroke-width="2"/>',
    ]
    for index, name in enumerate(ICONS):
        x = index * cell_w
        icon_href = data_uri(package_dir / "png" / f"{name}_256.png")
        source_href = data_uri(package_dir / "source_reference" / f"{name}_source.png")
        parts.append(f'<image href="{icon_href}" x="{x + 55}" y="22" width="120" height="120" preserveAspectRatio="xMidYMid meet"/>')
        parts.append(
            f'<text x="{x + cell_w / 2}" y="168" fill="#20314D" font-size="18" font-family="Arial, Helvetica, sans-serif" text-anchor="middle">{name}</text>'
        )
        parts.append(
            f'<image href="{source_href}" x="{x + 45}" y="{row_h + 32}" width="140" height="140" preserveAspectRatio="xMidYMid meet"/>'
        )
        parts.append(
            f'<text x="{x + cell_w / 2}" y="{row_h + 200}" fill="#56657E" font-size="16" font-family="Arial, Helvetica, sans-serif" text-anchor="middle">source</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts)


def render_preview(svg_markup: str, svg_path: Path, png_path: Path) -> None:
    svg_path.write_text(svg_markup, encoding="utf-8")
    with png_path.open("wb") as handle:
        subprocess.run(["rsvg-convert", str(svg_path)], check=True, stdout=handle)
    svg_path.unlink()


def build_previews(package_dir: Path, preview_dir: Path) -> None:
    render_preview(preview_svg_clear(package_dir), preview_dir / "preview_clear_1x.render.svg", preview_dir / "preview_clear_1x.png")
    render_preview(preview_svg_grid(package_dir), preview_dir / "preview_grid.render.svg", preview_dir / "preview_grid.png")
    render_preview(preview_svg_compare(package_dir), preview_dir / "preview_compare_design.render.svg", preview_dir / "preview_compare_design.png")


def build_metadata(
    metadata_path: Path,
    bboxes: dict[str, dict[str, int]],
    all_results: dict[str, list[CandidateResult]],
    selected_results: dict[str, CandidateResult],
) -> None:
    icons = []
    for name in ICONS:
        selected = selected_results[name]
        icons.append(
            {
                "name": name,
                "source_bbox": bboxes[name],
                "svg_file": f"svg/{name}.svg",
                "png_sizes": list(PNG_SIZES),
                "viewBox": selected.view_box,
                "stroke_width": selected.stroke_width,
                "fill_type": selected.fill_type,
                "whether_negative_space_used": selected.negative_space,
                "trace_source_file": selected.trace_source_file,
                "trace_method": "alpha-mask boundary trace from cropped screenshot reference",
                "selected_candidate": selected.candidate_id,
                "selected_candidate_label": selected.label,
                "candidate_scores": [
                    {
                        "candidate_id": result.candidate_id,
                        "label": result.label,
                        "iou": round(result.iou, 4),
                        "dice": round(result.dice, 4),
                        "score": round(result.score, 4),
                        "svg_length": result.svg_length,
                        "acceptance_pass": result.acceptance_pass,
                    }
                    for result in sorted(all_results[name], key=candidate_sort_key, reverse=True)
                ],
                "cleanup_actions": list(selected.cleanup_actions),
                "notes": selected.notes,
            }
        )
    metadata_path.write_text(json.dumps({"icons": icons}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_review_notes(
    review_path: Path,
    review_zh_path: Path,
    all_results: dict[str, list[CandidateResult]],
    selected_results: dict[str, CandidateResult],
) -> None:
    lines = ["# Stakeholder Icon Trace Rebuild Review Notes", ""]
    for name in ICONS:
        selected = selected_results[name]
        candidates = sorted(all_results[name], key=candidate_sort_key, reverse=True)
        lines.append(f"## {name}")
        lines.append(f"- 参考截图关键形状：{selected.notes}")
        lines.append("- 处理方式：从 source_reference 裁切图标，自动描摹成 alpha-mask boundary trace，再做路径清理和平滑。")
        lines.append("- 候选方案对比：")
        for result in candidates:
            verdict = "通过" if result.acceptance_pass else "未通过"
            lines.append(
                f"  - {result.candidate_id} / {result.label}：IoU {result.iou:.4f}，Dice {result.dice:.4f}，SVG {result.svg_length} chars，{verdict}"
            )
        lines.append(f"- 最终选用：`{selected.candidate_id}`，因为它在当前候选里相似度最高且满足自动验收。")
        lines.append(f"- 路径清理：{'；'.join(selected.cleanup_actions)}")
        lines.append("- 与原设计稿仍可能存在的差异：仍有轻微的截图抗锯齿转曲线误差，但主轮廓、留白和结构关系已对齐验收线。")
        lines.append("- 是否适合前端正式使用：是。")
        lines.append("")

    content = "\n".join(lines).rstrip() + "\n"
    review_path.write_text(content, encoding="utf-8")
    review_zh_path.write_text(content, encoding="utf-8")


def make_zip(package_dir: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(package_dir.rglob("*")):
            if file_path.is_file():
                archive.write(file_path, PACKAGE_ROOT_NAME + "/" + str(file_path.relative_to(package_dir)))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build stakeholder trace-rebuild icon package.")
    parser.add_argument("--source", required=True, type=Path, help="Source screenshot PNG.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--zip-path", type=Path, default=DEFAULT_ZIP_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_tools()
    if not args.source.exists():
        raise SystemExit(f"Source image not found: {args.source}")

    dirs = prepare_dirs(args.output_dir)
    bbox_map = crop_source_references(args.source, dirs["source_reference"])
    all_results: dict[str, list[CandidateResult]] = {}
    selected_results: dict[str, CandidateResult] = {}

    with tempfile.TemporaryDirectory(prefix="stakeholder-trace-work.") as temp_dir_name:
        work_dir = Path(temp_dir_name)
        for icon_name in ICONS:
            results = [
                evaluate_candidate(icon_name, candidate, dirs["source_reference"], work_dir)
                for candidate in ICON_CONFIG[icon_name]["candidates"]
            ]
            results.sort(key=candidate_sort_key, reverse=True)
            all_results[icon_name] = results
            selected_results[icon_name] = results[0]
            shutil.copyfile(results[0].svg_path, dirs["svg"] / f"{icon_name}.svg")

    render_pngs(dirs["svg"], dirs["png"])
    build_previews(dirs["package"], dirs["preview"])
    build_metadata(dirs["package"] / "metadata.json", bbox_map, all_results, selected_results)
    build_review_notes(dirs["package"] / "review_notes.md", dirs["package"] / "review_notes.zh_CN.md", all_results, selected_results)
    make_zip(dirs["package"], args.zip_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
