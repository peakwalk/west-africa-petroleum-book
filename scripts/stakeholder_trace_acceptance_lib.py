from __future__ import annotations

import math
import shutil
import subprocess
import tempfile
from pathlib import Path


ICONS = ("oil_drop", "regulators", "governments", "operators", "shield_star", "global")
PNG_SIZES = (64, 128, 256, 512, 1024, 2048)
REQUIRED_DIRS = ("source_reference", "svg", "png", "preview")
ACCEPTANCE_PROFILES = ("baseline", "production")
PROFILE_SIMILARITY_THRESHOLDS = {
    "baseline": {
        "oil_drop": {"min_iou": 0.895, "min_dice": 0.945},
        "regulators": {"min_iou": 0.50, "min_dice": 0.67},
        "governments": {"min_iou": 0.54, "min_dice": 0.70},
        "operators": {"min_iou": 0.70, "min_dice": 0.82},
        "shield_star": {"min_iou": 0.45, "min_dice": 0.62},
        "global": {"min_iou": 0.52, "min_dice": 0.70},
    },
    "production": {
        "oil_drop": {"min_iou": 0.895, "min_dice": 0.945},
        "regulators": {"min_iou": 0.50, "min_dice": 0.67},
        "governments": {"min_iou": 0.54, "min_dice": 0.70},
        "operators": {"min_iou": 0.70, "min_dice": 0.82},
        "shield_star": {"min_iou": 0.45, "min_dice": 0.62},
        "global": {"min_iou": 0.52, "min_dice": 0.70},
    },
}
PROFILE_SVG_LENGTH_LIMITS = {
    "baseline": {
        "oil_drop": 4000,
        "operators": 5000,
        "shield_star": 2500,
    },
    "production": {
        "oil_drop": 1800,
        "regulators": 2200,
        "governments": 2500,
        "operators": 3000,
        "shield_star": 1400,
        "global": 2200,
    },
}
PRODUCTION_STROKE_DOMINANT_ICONS = frozenset({"regulators", "governments", "shield_star", "global"})


def ensure_tools() -> None:
    missing = [tool for tool in ("magick", "rsvg-convert") if shutil.which(tool) is None]
    if missing:
        raise SystemExit(f"Missing required tools: {', '.join(missing)}")


def parse_pbm(path: Path) -> list[list[int]]:
    data = path.read_bytes()
    if not data.startswith(b"P4"):
        raise SystemExit(f"Expected binary PBM P4: {path}")

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

    border = bits[0] + bits[-1]
    for row in bits[1:-1]:
        border.append(row[0])
        border.append(row[-1])
    background = 1 if sum(border) >= len(border) / 2 else 0
    filled = 0 if background == 1 else 1
    return [[1 if pixel == filled else 0 for pixel in row] for row in bits]


def build_mask(input_path: Path, output_path: Path) -> None:
    subprocess.run(
        [
            "magick",
            str(input_path),
            "-alpha",
            "extract",
            "-threshold",
            "10%",
            "-trim",
            "+repage",
            "-resize",
            "400x400",
            "-background",
            "black",
            "-gravity",
            "center",
            "-extent",
            "512x512",
            "PBM:" + str(output_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def compare_masks(source_png: Path, candidate_png: Path) -> tuple[float, float]:
    with tempfile.TemporaryDirectory(prefix="stakeholder-acceptance.") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        source_mask = temp_dir / "source.pbm"
        candidate_mask = temp_dir / "candidate.pbm"
        build_mask(source_png, source_mask)
        build_mask(candidate_png, candidate_mask)
        source = parse_pbm(source_mask)
        candidate = parse_pbm(candidate_mask)

        intersection = 0
        union = 0
        source_area = 0
        candidate_area = 0
        for y in range(len(source)):
            for x in range(len(source[0])):
                source_value = source[y][x]
                candidate_value = candidate[y][x]
                intersection += source_value & candidate_value
                union += 1 if source_value or candidate_value else 0
                source_area += source_value
                candidate_area += candidate_value

        iou = intersection / union if union else 1.0
        dice = (2 * intersection) / (source_area + candidate_area) if (source_area + candidate_area) else 1.0
        return iou, dice


def normalize_profile(profile: str) -> str:
    if profile not in ACCEPTANCE_PROFILES:
        raise ValueError(f"Unsupported acceptance profile: {profile}")
    return profile


def similarity_thresholds(profile: str) -> dict[str, dict[str, float]]:
    return PROFILE_SIMILARITY_THRESHOLDS[normalize_profile(profile)]


def similarity_passes(icon_name: str, iou: float, dice: float, profile: str = "baseline") -> bool:
    threshold = similarity_thresholds(profile)[icon_name]
    return iou >= threshold["min_iou"] and dice >= threshold["min_dice"]


def svg_length_limit(icon_name: str, profile: str = "baseline") -> int | None:
    return PROFILE_SVG_LENGTH_LIMITS[normalize_profile(profile)].get(icon_name)


def svg_length_passes(icon_name: str, svg_length: int, profile: str = "baseline") -> bool:
    limit = svg_length_limit(icon_name, profile)
    return limit is None or svg_length <= limit
