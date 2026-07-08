#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from stakeholder_trace_acceptance_lib import (
    ACCEPTANCE_PROFILES,
    ICONS,
    PNG_SIZES,
    PRODUCTION_STROKE_DOMINANT_ICONS,
    REQUIRED_DIRS,
    compare_masks,
    ensure_tools,
    similarity_passes,
    svg_length_limit,
    svg_length_passes,
)


CURRENT_COLOR_RE = re.compile(r"currentColor")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check stakeholder trace rebuild package acceptance.")
    parser.add_argument("--package-dir", required=True, type=Path)
    parser.add_argument("--profile", choices=ACCEPTANCE_PROFILES, default="baseline")
    return parser.parse_args()


def require(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def check_package_structure(package_dir: Path, errors: list[str]) -> None:
    require(package_dir.exists(), errors, f"Missing package dir: {package_dir}")
    for name in REQUIRED_DIRS:
        require((package_dir / name).is_dir(), errors, f"Missing required dir: {name}")
    for name in ("metadata.json", "review_notes.md"):
        require((package_dir / name).is_file(), errors, f"Missing required file: {name}")


def check_svg_semantics(package_dir: Path, profile: str, errors: list[str]) -> None:
    for icon in ICONS:
        svg_path = package_dir / "svg" / f"{icon}.svg"
        require(svg_path.is_file(), errors, f"Missing SVG: {svg_path.name}")
        if not svg_path.is_file():
            continue

        text = svg_path.read_text(encoding="utf-8")
        require("base64" not in text.lower(), errors, f"{icon}: SVG embeds raster data")
        require(CURRENT_COLOR_RE.search(text) is not None, errors, f"{icon}: SVG does not use currentColor")
        if icon == "oil_drop":
            require(
                'fill-rule="evenodd"' in text or "<mask" in text or "<clipPath" in text,
                errors,
                "oil_drop: missing negative-space implementation",
            )
        if profile == "production" and icon in PRODUCTION_STROKE_DOMINANT_ICONS:
            require('stroke="currentColor"' in text, errors, f"{icon}: production profile requires stroke=currentColor")
            require('stroke-linecap="round"' in text, errors, f"{icon}: production profile requires round line caps")
            require('stroke-linejoin="round"' in text, errors, f"{icon}: production profile requires round line joins")
            require(
                'vector-effect="non-scaling-stroke"' in text,
                errors,
                f"{icon}: production profile requires non-scaling stroke delivery",
            )
            require('fill-rule="evenodd"' not in text, errors, f"{icon}: production profile rejects evenodd-filled trace silhouettes")
        if not svg_length_passes(icon, len(text), profile):
            limit = svg_length_limit(icon, profile)
            errors.append(f"{icon}: SVG path markup too large for {profile} profile ({len(text)} > {limit})")


def check_png_exports(package_dir: Path, errors: list[str]) -> None:
    for icon in ICONS:
        source_path = package_dir / "source_reference" / f"{icon}_source.png"
        require(source_path.is_file(), errors, f"Missing source reference: {source_path.name}")
        for size in PNG_SIZES:
            png_path = package_dir / "png" / f"{icon}_{size}.png"
            require(png_path.is_file(), errors, f"Missing PNG export: {png_path.name}")


def check_similarity(package_dir: Path, profile: str, errors: list[str]) -> None:
    for icon in ICONS:
        source_png = package_dir / "source_reference" / f"{icon}_source.png"
        candidate_png = package_dir / "png" / f"{icon}_512.png"
        if not source_png.is_file() or not candidate_png.is_file():
            continue

        iou, dice = compare_masks(source_png, candidate_png)
        if not similarity_passes(icon, iou, dice, profile):
            errors.append(f"{icon}: IoU {iou:.4f}, Dice {dice:.4f} below {profile} acceptance threshold")


def main() -> int:
    args = parse_args()
    ensure_tools()

    errors: list[str] = []
    check_package_structure(args.package_dir, errors)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    check_svg_semantics(args.package_dir, args.profile, errors)
    check_png_exports(args.package_dir, errors)
    check_similarity(args.package_dir, args.profile, errors)

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
