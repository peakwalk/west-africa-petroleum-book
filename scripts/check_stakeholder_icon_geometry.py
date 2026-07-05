from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
ICON_DIR = ROOT_DIR / "assets" / "icons" / "stakeholders"
EXPECTED_PIXEL_SIZE = (1024, 1024)

EXPECTED_BOUNDS = {
    "governments.png": {
        "width": (450, 454),
        "height": (532, 536),
        "offset_x": (280, 284),
        "offset_y": (243, 247),
    },
    "regulators.png": {
        "width": (526, 530),
        "height": (519, 523),
        "offset_x": (242, 246),
        "offset_y": (249, 253),
    },
    "national-oil-companies.png": {
        "width": (505, 509),
        "height": (526, 530),
        "offset_x": (257, 261),
        "offset_y": (243, 247),
    },
    "operators.png": {
        "width": (444, 448),
        "height": (535, 539),
        "offset_x": (290, 294),
        "offset_y": (241, 245),
    },
    "investors.png": {
        "width": (453, 457),
        "height": (534, 538),
        "offset_x": (285, 289),
        "offset_y": (242, 246),
    },
    "universities-researchers.png": {
        "width": (450, 454),
        "height": (524, 528),
        "offset_x": (284, 288),
        "offset_y": (244, 248),
    },
}

TRIM_PATTERN = re.compile(r"^(?P<width>\d+)x(?P<height>\d+)\+(?P<offset_x>-?\d+)\+(?P<offset_y>-?\d+)$")


def required_tools_available() -> bool:
    return bool(shutil.which("magick"))


def identify_pixel_size(icon_path: Path) -> tuple[int, int]:
    raw = subprocess.check_output(
        ["magick", "identify", "-format", "%wx%h", str(icon_path)],
        text=True,
    ).strip()
    width_text, height_text = raw.split("x", maxsplit=1)
    return int(width_text), int(height_text)


def identify_trimmed_bounds(icon_path: Path) -> tuple[int, int, int, int]:
    raw = subprocess.check_output(
        ["magick", str(icon_path), "-trim", "-format", "%wx%h+%X+%Y", "info:"],
        text=True,
    ).strip()
    normalized = raw.replace("++", "+").replace("+-", "-")
    match = TRIM_PATTERN.fullmatch(normalized)
    if match is None:
        raise SystemExit(f"Unexpected trim geometry '{raw}' for {icon_path.name}")

    return tuple(int(match.group(key)) for key in ("width", "height", "offset_x", "offset_y"))


def validate() -> list[str]:
    errors: list[str] = []
    for icon_name, expected in EXPECTED_BOUNDS.items():
        icon_path = ICON_DIR / icon_name
        if not icon_path.exists():
            errors.append(f"Missing expected icon asset {icon_path}")
            continue

        actual_pixel_size = identify_pixel_size(icon_path)
        if actual_pixel_size != EXPECTED_PIXEL_SIZE:
            errors.append(
                f"{icon_name}: expected pixel size {EXPECTED_PIXEL_SIZE[0]}x{EXPECTED_PIXEL_SIZE[1]} "
                f"but saw {actual_pixel_size[0]}x{actual_pixel_size[1]}"
            )

        width, height, offset_x, offset_y = identify_trimmed_bounds(icon_path)
        actual = {
            "width": width,
            "height": height,
            "offset_x": offset_x,
            "offset_y": offset_y,
        }
        for field, value in actual.items():
            low, high = expected[field]
            if value < low or value > high:
                errors.append(f"{icon_name}: expected {field} in [{low}, {high}] but saw {value}")

    return errors


def main() -> int:
    if not required_tools_available():
        print("Skipping stakeholder icon geometry check; requires magick.", file=sys.stderr)
        return 0

    errors = validate()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
