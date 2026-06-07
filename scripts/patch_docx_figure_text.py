from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.docx_figures import build_figure_inventory

DEFAULT_DOCX = Path(
    "resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx"
)
DEFAULT_SUMMARY = Path("src/SUMMARY.md")
DEFAULT_CHAPTERS_DIR = Path("src/chapters")

PARAGRAPH_RE = re.compile(r"(<w:p(?:\s[^>]*)?>.*?</w:p>)", re.DOTALL)
TEXT_NODE_RE = re.compile(
    r"(<(?P<tag>[A-Za-z0-9]+:(?:t|v))(?P<attrs>\s[^>]*)?>)(?P<text>.*?)(</(?P=tag)>)",
    re.DOTALL,
)


def _normalize_text(value: str) -> str:
    return value.replace("\xa0", " ").strip()


def _parse_replacements(items: list[str]) -> dict[str, str]:
    replacements: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"Replacement must use old=new syntax: {item}")
        old, new = item.split("=", 1)
        old = old.strip()
        if not old:
            raise ValueError(f"Replacement source cannot be empty: {item}")
        replacements[old] = new
    return replacements


def _load_mapping_file(path: Path) -> dict[int, dict[str, dict[str, str]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    mapping: dict[int, dict[str, dict[str, str]]] = {}
    for raw_figure, entry in data.items():
        figure_number = int(raw_figure)
        mapping[figure_number] = {
            "document": {str(k): str(v) for k, v in entry.get("document", {}).items()},
            "chart": {str(k): str(v) for k, v in entry.get("chart", {}).items()},
        }
    return mapping


def _patch_text_nodes(xml_text: str, replacements: dict[str, str]) -> tuple[str, dict[str, int]]:
    counts = {key: 0 for key in replacements}
    if not replacements:
        return xml_text, counts

    def replace_match(match: re.Match[str]) -> str:
        raw_text = match.group("text")
        normalized = _normalize_text(html.unescape(raw_text))
        if normalized not in replacements:
            return match.group(0)
        counts[normalized] += 1
        escaped_new = escape(replacements[normalized])
        return f"{match.group(1)}{escaped_new}{match.group(5)}"

    return TEXT_NODE_RE.sub(replace_match, xml_text), counts


def _patch_document_paragraph_range(
    document_xml: str,
    paragraph_start: int,
    paragraph_end: int,
    replacements: dict[str, str],
) -> tuple[str, dict[str, int]]:
    counts = {key: 0 for key in replacements}
    if not replacements:
        return document_xml, counts

    matches = list(PARAGRAPH_RE.finditer(document_xml))
    if paragraph_end >= len(matches):
        raise ValueError(
            f"Paragraph range {paragraph_start}-{paragraph_end} exceeds document paragraph count {len(matches)}"
        )

    pieces: list[str] = []
    cursor = 0
    for index, match in enumerate(matches):
        pieces.append(document_xml[cursor : match.start()])
        paragraph_xml = match.group(1)
        if paragraph_start <= index <= paragraph_end:
            patched_xml, local_counts = _patch_text_nodes(paragraph_xml, replacements)
            for key, value in local_counts.items():
                counts[key] += value
            pieces.append(patched_xml)
        else:
            pieces.append(paragraph_xml)
        cursor = match.end()
    pieces.append(document_xml[cursor:])
    return "".join(pieces), counts


def _local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    if ":" in tag:
        return tag.rsplit(":", 1)[1]
    return tag


def _patch_ooxml_paragraph_text(
    xml_text: str,
    replacements: dict[str, str],
) -> tuple[str, dict[str, int]]:
    counts = {key: 0 for key in replacements}
    if not replacements:
        return xml_text, counts

    root = ET.fromstring(xml_text)
    changed = False
    for container in root.iter():
        if _local_name(container.tag) not in {"txBody", "rich"}:
            continue
        for paragraph in container.iter():
            if _local_name(paragraph.tag) != "p":
                continue
            text_nodes = [node for node in paragraph.iter() if _local_name(node.tag) == "t"]
            if not text_nodes:
                continue
            joined = _normalize_text("".join((node.text or "") for node in text_nodes))
            if joined not in replacements:
                continue
            text_nodes[0].text = replacements[joined]
            for node in text_nodes[1:]:
                node.text = ""
            counts[joined] += 1
            changed = True

    if not changed:
        return xml_text, counts

    xml_declaration = ""
    if xml_text.startswith("<?xml"):
        xml_declaration = xml_text[: xml_text.index("?>") + 2]
    serialized = ET.tostring(root, encoding="unicode")
    if xml_declaration:
        return f"{xml_declaration}\n{serialized}", counts
    return serialized, counts


def _collect_document_replacements(
    mapping_by_figure: dict[int, dict[str, dict[str, str]]]
) -> dict[str, str]:
    merged: dict[str, str] = {}
    for figure_number in sorted(mapping_by_figure):
        for old, new in mapping_by_figure[figure_number]["document"].items():
            previous = merged.get(old)
            if previous is not None and previous != new:
                raise SystemExit(
                    f"Conflicting document replacements for {old!r}: {previous!r} vs {new!r}"
                )
            merged[old] = new
    return merged


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Patch figure text inside a DOCX file while preserving original XML packaging."
    )
    parser.add_argument("--docx", default=str(DEFAULT_DOCX))
    parser.add_argument("--summary", default=str(DEFAULT_SUMMARY))
    parser.add_argument("--chapters-dir", default=str(DEFAULT_CHAPTERS_DIR))
    parser.add_argument("--output-docx", required=True)
    parser.add_argument("--mapping-file", help="JSON mapping file keyed by figure number.")
    parser.add_argument("--figure", type=int, help="Single figure number for ad hoc replacement.")
    parser.add_argument(
        "--replace",
        action="append",
        default=[],
        help="Ad hoc document-XML replacement in old=new form. Requires --figure.",
    )
    parser.add_argument(
        "--chart-replace",
        action="append",
        default=[],
        help="Ad hoc chart/drawing XML replacement in old=new form. Requires --figure.",
    )
    return parser.parse_args()


def _build_mapping(args: argparse.Namespace) -> dict[int, dict[str, dict[str, str]]]:
    if args.mapping_file:
        return _load_mapping_file(Path(args.mapping_file))

    if args.figure is None:
        raise SystemExit("Either --mapping-file or --figure is required.")

    document_replacements = _parse_replacements(args.replace)
    chart_replacements = _parse_replacements(args.chart_replace)
    if not document_replacements and not chart_replacements:
        raise SystemExit("Provide at least one --replace or --chart-replace entry.")
    return {
        args.figure: {
            "document": document_replacements,
            "chart": chart_replacements,
        }
    }


def _write_zip(destination: Path, payloads: dict[str, bytes], source_zip: ZipFile) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, "w", compression=ZIP_DEFLATED) as out_zip:
        for info in source_zip.infolist():
            out_zip.writestr(info, payloads[info.filename])


def main() -> int:
    args = parse_args()
    mapping_by_figure = _build_mapping(args)

    docx_path = Path(args.docx)
    output_docx = Path(args.output_docx)

    inventory = {
        record.number: record
        for record in build_figure_inventory(
            docx_path=docx_path,
            chapters_dir=Path(args.chapters_dir),
            summary_path=Path(args.summary),
        )
    }

    missing_figures = sorted(set(mapping_by_figure).difference(inventory))
    if missing_figures:
        raise SystemExit(f"Figures not found in inventory: {missing_figures}")

    with ZipFile(docx_path) as src_zip:
        payloads = {info.filename: src_zip.read(info.filename) for info in src_zip.infolist()}
        document_xml = payloads["word/document.xml"].decode("utf-8")

        replacement_report: list[str] = []

        global_document_replacements = _collect_document_replacements(mapping_by_figure)
        if global_document_replacements:
            document_xml, document_counts = _patch_text_nodes(
                document_xml, global_document_replacements
            )
            if any(count == 0 for count in document_counts.values()):
                missing = [key for key, count in document_counts.items() if count == 0]
                raise SystemExit(f"Missing document replacements {missing}")
            replacement_report.append(f"Document replacements {document_counts}")

        for figure_number in sorted(mapping_by_figure):
            record = inventory[figure_number]
            config = mapping_by_figure[figure_number]

            if config["chart"]:
                related_parts = list(dict.fromkeys(record.objects.chart_targets + record.objects.drawing_targets))
                if not related_parts:
                    raise SystemExit(
                        f"Figure {figure_number}: requested chart replacements but no chart/drawing parts were found."
                    )
                aggregate_counts = {key: 0 for key in config["chart"]}
                for part_name in related_parts:
                    xml_text = payloads[part_name].decode("utf-8")
                    patched_text, local_counts = _patch_text_nodes(xml_text, config["chart"])
                    missing_after_node_patch = {
                        key: value for key, value in config["chart"].items() if local_counts[key] == 0
                    }
                    if missing_after_node_patch:
                        patched_text, paragraph_counts = _patch_ooxml_paragraph_text(
                            patched_text, missing_after_node_patch
                        )
                        for key, value in paragraph_counts.items():
                            local_counts[key] += value
                    payloads[part_name] = patched_text.encode("utf-8")
                    for key, value in local_counts.items():
                        aggregate_counts[key] += value
                if any(count == 0 for count in aggregate_counts.values()):
                    missing = [key for key, count in aggregate_counts.items() if count == 0]
                    raise SystemExit(
                        f"Figure {figure_number}: missing chart replacements {missing}"
                    )
                replacement_report.append(f"Figure {figure_number} chart {aggregate_counts}")

        payloads["word/document.xml"] = document_xml.encode("utf-8")

        if output_docx.resolve() == docx_path.resolve():
            with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as handle:
                temp_path = Path(handle.name)
            try:
                _write_zip(temp_path, payloads, src_zip)
                shutil.move(temp_path, output_docx)
            finally:
                if temp_path.exists():
                    temp_path.unlink()
        else:
            _write_zip(output_docx, payloads, src_zip)

    for line in replacement_report:
        print(line)
    print(f"Patched {len(mapping_by_figure)} figure mapping(s) into {output_docx}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
