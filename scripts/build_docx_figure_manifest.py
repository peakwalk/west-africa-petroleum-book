from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.edition_config import available_edition_locales, get_edition
from scripts.docx_figures import build_figure_inventory

DEFAULT_DOCX = Path(
    "resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx"
)
DEFAULT_SUMMARY = Path("src/SUMMARY.md")
DEFAULT_CHAPTERS_DIR = Path("src/chapters")
DEFAULT_OUTPUT = Path("src/images/figure-manifest.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a DOCX-derived figure inventory manifest."
    )
    parser.add_argument("--edition", choices=available_edition_locales())
    parser.add_argument("--docx")
    parser.add_argument("--summary")
    parser.add_argument("--chapters-dir")
    parser.add_argument("--output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    edition = get_edition(args.edition) if args.edition else None
    docx_path = Path(args.docx) if args.docx else edition.docx_path if edition else DEFAULT_DOCX
    summary_path = (
        Path(args.summary) if args.summary else edition.summary_path if edition else DEFAULT_SUMMARY
    )
    chapters_dir = (
        Path(args.chapters_dir)
        if args.chapters_dir
        else edition.chapter_root
        if edition
        else DEFAULT_CHAPTERS_DIR
    )
    output_path = (
        Path(args.output)
        if args.output
        else edition.figure_manifest_path
        if edition
        else DEFAULT_OUTPUT
    )
    inventory = build_figure_inventory(
        docx_path=docx_path,
        chapters_dir=chapters_dir,
        summary_path=summary_path,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps([asdict(record) for record in inventory], indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(inventory)} figure records to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
