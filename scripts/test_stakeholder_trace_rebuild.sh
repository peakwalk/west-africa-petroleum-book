#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE_IMAGE="${1:-/var/folders/y7/ll1_jx7s583dgv6g95hpbx1m0000gn/T/codex-clipboard-c7f22ae1-9b12-486e-9851-0de308f10bbc.png}"
TMP_DIR="$(mktemp -d /tmp/stakeholder-trace-test.XXXXXX)"
OUTPUT_DIR="$TMP_DIR/package"
ZIP_PATH="$TMP_DIR/package.zip"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

python3 "$ROOT_DIR/scripts/build_stakeholder_icons_trace_rebuild.py" \
  --source "$SOURCE_IMAGE" \
  --output-dir "$OUTPUT_DIR" \
  --zip-path "$ZIP_PATH"

for required in \
  "$OUTPUT_DIR/source_reference/oil_drop_source.png" \
  "$OUTPUT_DIR/svg/oil_drop.svg" \
  "$OUTPUT_DIR/png/oil_drop_2048.png" \
  "$OUTPUT_DIR/preview/preview_compare_design.png" \
  "$OUTPUT_DIR/metadata.json" \
  "$OUTPUT_DIR/review_notes.md"
do
  test -f "$required"
done

python3 - "$OUTPUT_DIR/metadata.json" <<'PY'
import json
import sys
from pathlib import Path

metadata_path = Path(sys.argv[1])
payload = json.loads(metadata_path.read_text(encoding="utf-8"))
icons = payload.get("icons")
if not isinstance(icons, list) or len(icons) != 6:
    raise SystemExit("Expected 6 icons in metadata.json")

required_keys = {
    "name",
    "source_bbox",
    "svg_file",
    "png_sizes",
    "viewBox",
    "stroke_width",
    "fill_type",
    "whether_negative_space_used",
    "notes",
    "trace_source_file",
    "trace_method",
    "cleanup_actions",
}

for icon in icons:
    missing = sorted(required_keys.difference(icon))
    if missing:
        raise SystemExit(f"Missing metadata keys for {icon.get('name')}: {missing}")
    if not icon["trace_source_file"]:
        raise SystemExit(f"trace_source_file empty for {icon['name']}")
    if not icon["trace_method"]:
        raise SystemExit(f"trace_method empty for {icon['name']}")
    if not isinstance(icon["cleanup_actions"], list) or not icon["cleanup_actions"]:
        raise SystemExit(f"cleanup_actions missing for {icon['name']}")
PY

grep -qi 'trace' "$OUTPUT_DIR/review_notes.md"
grep -qi '自动描摹' "$OUTPUT_DIR/review_notes.md"
grep -q 'fill-rule="evenodd"' "$OUTPUT_DIR/svg/oil_drop.svg"
[[ "$(sips -g pixelWidth -g pixelHeight "$OUTPUT_DIR/png/global_2048.png")" == *2048* ]]
ZIP_LISTING="$(unzip -l "$ZIP_PATH")"
[[ "$ZIP_LISTING" == *'stakeholder_icons_trace_rebuild/svg/global.svg'* ]]
