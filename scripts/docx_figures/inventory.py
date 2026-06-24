from __future__ import annotations

import posixpath
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from scripts.docx_parity.normalize import normalize_visible_text

from .model import FigureObjectStats, FigureRecord

W_NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "v": "urn:schemas-microsoft-com:vml",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
}
PACKAGE_REL_NS = {"pr": "http://schemas.openxmlformats.org/package/2006/relationships"}
SUMMARY_LINK_RE = re.compile(r"^\s*-\s+\[(?P<title>.+?)\]\((?P<path>.+?)\)\s*$")
CHAPTER_MARKER_RE = re.compile(
    r"^(?:Chapter|Chapitre)\s+(?P<number>\d+)(?:\s*:?\s*(?P<title>.*))?$",
    re.IGNORECASE,
)
FIGURE_CAPTION_RE = re.compile(r"Figure\s+(?P<number>\d+)\s*:?\s*(?P<tail>.+)", re.IGNORECASE)
FIGURE_INDEX_RE = re.compile(
    r'href="(?P<html>[^"#]+)#figure-(?P<number>\d+)">(?P<caption>Figure\s+\d+:\s*[^<]+)</a>',
    re.IGNORECASE,
)
SECTION_HEADING_RE = re.compile(r"^\d+(?:\.\d+)*(?:\s*-\s*|[.-]).+")


@dataclass(frozen=True)
class ParagraphScan:
    index: int
    text: str
    chapter_title: str
    chapter_path: str
    style_id: str
    is_heading: bool
    caption_number: int | None
    caption_text: str | None
    objects: FigureObjectStats


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
    for relationship in root.findall("pr:Relationship", PACKAGE_REL_NS):
        target = relationship.attrib.get("Target")
        relationship_id = relationship.attrib.get("Id")
        if not target or not relationship_id:
            continue
        relationships[relationship_id] = _resolve_part_target(part_name, target)
    return relationships


def _build_chart_drawing_map(archive: ZipFile, chart_parts: list[str]) -> dict[str, list[str]]:
    chart_drawing_map: dict[str, list[str]] = {}
    for chart_part in chart_parts:
        relationships = _build_relationship_map(archive, chart_part)
        drawing_targets = sorted(
            {
                target
                for target in relationships.values()
                if "/drawings/" in target or target.endswith("/drawing1.xml")
            }
        )
        if drawing_targets:
            chart_drawing_map[chart_part] = drawing_targets
    return chart_drawing_map


def _chapter_map(summary_path: Path) -> tuple[dict[str, str], dict[int, str], dict[int, str]]:
    by_title: dict[str, str] = {}
    by_number: dict[int, str] = {}
    by_number_title: dict[int, str] = {}
    for raw_line in summary_path.read_text(encoding="utf-8").splitlines():
        match = SUMMARY_LINK_RE.match(raw_line)
        if not match:
            continue
        relative_path = Path(match.group("path"))
        chapter_path = (summary_path.parent / relative_path).resolve()
        if not chapter_path.name.startswith("chapter-"):
            continue
        title = normalize_visible_text(match.group("title"))
        by_title[_title_key(title)] = str(chapter_path)
        chapter_match = CHAPTER_MARKER_RE.match(title)
        if chapter_match is not None:
            chapter_number = int(chapter_match.group("number"))
            plain_title = normalize_visible_text(chapter_match.group("title") or "")
            if plain_title:
                by_title[_title_key(plain_title)] = str(chapter_path)
            by_number[chapter_number] = str(chapter_path)
            by_number_title[chapter_number] = title
    return by_title, by_number, by_number_title


def _markdown_heading_title(chapter_path: Path) -> str:
    for raw_line in chapter_path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("# "):
            return normalize_visible_text(stripped[2:])
    return chapter_path.stem


def _plain_chapter_title(title: str) -> str:
    chapter_match = CHAPTER_MARKER_RE.match(title)
    if chapter_match is None:
        return normalize_visible_text(title)
    return normalize_visible_text(chapter_match.group("title") or "")


def _title_key(title: str) -> str:
    normalized = normalize_visible_text(title)
    decomposed = unicodedata.normalize("NFKD", normalized)
    stripped = "".join(char for char in decomposed if not unicodedata.combining(char))
    return stripped.casefold()


def _resolve_chapter_marker(
    chapter_match: re.Match[str],
    *,
    normalized_text: str,
    title_to_path: dict[str, str],
    chapter_number_to_path: dict[int, str],
    chapter_number_to_title: dict[int, str],
) -> tuple[str, str] | None:
    chapter_number = int(chapter_match.group("number"))
    expected_title = chapter_number_to_title.get(chapter_number, "")
    expected_plain_title = _plain_chapter_title(expected_title)
    observed_plain_title = normalize_visible_text(chapter_match.group("title") or "")

    if normalized_text != expected_title and observed_plain_title != expected_plain_title:
        return None

    chapter_path = title_to_path.get(_title_key(normalized_text), "")
    if not chapter_path:
        chapter_path = chapter_number_to_path.get(chapter_number, "")
    if not chapter_path:
        return None

    chapter_title = expected_title or normalized_text
    return chapter_title, chapter_path


def _resolve_pending_chapter_title(
    pending_chapter_number: int | None,
    *,
    normalized_text: str,
    chapter_number_to_path: dict[int, str],
    chapter_number_to_title: dict[int, str],
) -> tuple[str, str] | None:
    if pending_chapter_number is None:
        return None

    expected_title = chapter_number_to_title.get(pending_chapter_number, "")
    expected_plain_title = _plain_chapter_title(expected_title)
    if not expected_plain_title:
        return None
    if _title_key(normalized_text) != _title_key(expected_plain_title):
        return None

    chapter_path = chapter_number_to_path.get(pending_chapter_number, "")
    if not chapter_path:
        return None
    return expected_title or normalized_text, chapter_path


def _figure_index_map(
    chapters_dir: Path,
) -> tuple[dict[int, str], dict[int, str], dict[str, str]]:
    figure_index_path = chapters_dir / "list-of-figures.md"
    chapter_title_map: dict[str, str] = {}
    if not figure_index_path.exists():
        return {}, {}, chapter_title_map

    by_number_path: dict[int, str] = {}
    by_number_caption: dict[int, str] = {}
    content = figure_index_path.read_text(encoding="utf-8")
    for match in FIGURE_INDEX_RE.finditer(content):
        number = int(match.group("number"))
        chapter_html = Path(match.group("html")).name
        chapter_md_path = (chapters_dir / chapter_html.replace(".html", ".md")).resolve()
        by_number_path[number] = str(chapter_md_path)
        by_number_caption[number] = normalize_visible_text(match.group("caption"))
        if str(chapter_md_path) not in chapter_title_map and chapter_md_path.exists():
            chapter_title_map[str(chapter_md_path)] = _markdown_heading_title(chapter_md_path)

    return by_number_path, by_number_caption, chapter_title_map


def _paragraph_text(paragraph: ET.Element) -> str:
    parts = [node.text for node in paragraph.findall(".//w:t", W_NS) if node.text]
    return normalize_visible_text("".join(parts))


def _paragraph_style(paragraph: ET.Element) -> str:
    style_node = paragraph.find("w:pPr/w:pStyle", W_NS)
    if style_node is None:
        return ""
    return style_node.attrib.get(f"{{{W_NS['w']}}}val", "")


def _is_heading_paragraph(style_id: str, text: str) -> bool:
    lowered_style = style_id.lower()
    if lowered_style.startswith("heading"):
        return True
    return bool(SECTION_HEADING_RE.match(text))


def _dedupe_exact_double(text: str) -> str:
    normalized = normalize_visible_text(text)
    if len(normalized) % 2 == 0:
        midpoint = len(normalized) // 2
        if normalized[:midpoint] == normalized[midpoint:]:
            return normalized[:midpoint]
    words = normalized.split()
    if words and len(words) % 2 == 0:
        midpoint = len(words) // 2
        if words[:midpoint] == words[midpoint:]:
            return " ".join(words[:midpoint])
    return normalized


def _extract_caption(text: str) -> tuple[int, str] | None:
    normalized = _dedupe_exact_double(text)
    matches = list(FIGURE_CAPTION_RE.finditer(normalized))
    if not matches:
        return None
    start = matches[0].start()
    end = matches[1].start() if len(matches) > 1 else len(normalized)
    caption = normalize_visible_text(normalized[start:end])
    match = FIGURE_CAPTION_RE.match(caption)
    if match is None:
        return None
    tail = normalize_visible_text(match.group("tail"))
    if not tail:
        return None
    return int(match.group("number")), f"Figure {int(match.group('number'))}: {tail}"


def _paragraph_object_stats(
    paragraph: ET.Element,
    relationships: dict[str, str],
    chart_drawing_map: dict[str, list[str]],
) -> FigureObjectStats:
    blip_targets = sorted(
        {
            relationships[relationship_id]
            for blip in paragraph.findall(".//a:blip", W_NS)
            for relationship_id in (
                blip.attrib.get(f"{{{W_NS['r']}}}embed"),
                blip.attrib.get(f"{{{W_NS['r']}}}link"),
            )
            if relationship_id and relationship_id in relationships
        }
    )
    chart_targets = sorted(
        {
            relationships[relationship_id]
            for chart in paragraph.findall(".//c:chart", W_NS)
            for relationship_id in (chart.attrib.get(f"{{{W_NS['r']}}}id"),)
            if relationship_id and relationship_id in relationships
        }
    )
    drawing_targets = sorted(
        {
            drawing_target
            for chart_target in chart_targets
            for drawing_target in chart_drawing_map.get(chart_target, [])
        }
    )
    return FigureObjectStats(
        blip_targets=blip_targets,
        chart_targets=chart_targets,
        drawing_targets=drawing_targets,
        anchor_count=len(paragraph.findall(".//wp:anchor", W_NS)),
        inline_count=len(paragraph.findall(".//wp:inline", W_NS)),
        vshape_count=len(paragraph.findall(".//v:shape", W_NS)),
        wps_shape_count=len(paragraph.findall(".//wps:wsp", W_NS)),
    )


def _merge_stats(stats_list: list[FigureObjectStats]) -> FigureObjectStats:
    return FigureObjectStats(
        blip_targets=sorted(
            {target for stats in stats_list for target in stats.blip_targets}
        ),
        chart_targets=sorted(
            {target for stats in stats_list for target in stats.chart_targets}
        ),
        drawing_targets=sorted(
            {target for stats in stats_list for target in stats.drawing_targets}
        ),
        anchor_count=sum(stats.anchor_count for stats in stats_list),
        inline_count=sum(stats.inline_count for stats in stats_list),
        vshape_count=sum(stats.vshape_count for stats in stats_list),
        wps_shape_count=sum(stats.wps_shape_count for stats in stats_list),
    )


def classify_figure(stats: FigureObjectStats) -> str:
    if stats.chart_targets:
        return "chart"
    if stats.vshape_count or stats.wps_shape_count:
        if len(stats.blip_targets) > 1:
            return "composite"
        return "shape_group"
    if any(target.endswith((".emf", ".wmf")) for target in stats.blip_targets):
        return "vector_media"
    if len(stats.blip_targets) > 1:
        return "multi_photo"
    if stats.blip_targets:
        return "bitmap"
    return "unknown"


def _looks_like_body_sentence(text: str) -> bool:
    words = text.split()
    if len(words) >= 14:
        return True
    return len(words) >= 9 and text.endswith((".", "?", "!"))


def _is_cluster_member(scan: ParagraphScan) -> bool:
    if scan.objects.has_objects():
        return True
    if not scan.text:
        return True
    if scan.caption_number is not None or scan.is_heading:
        return False
    if _looks_like_body_sentence(scan.text):
        return False
    return len(scan.text.split()) <= 12


def _cluster_bounds(scans: list[ParagraphScan], caption_index: int) -> tuple[int, int]:
    start = caption_index
    while start > 0:
        candidate = scans[start - 1]
        if candidate.chapter_title != scans[caption_index].chapter_title:
            break
        if candidate.caption_number is not None or candidate.is_heading:
            break
        if not _is_cluster_member(candidate):
            break
        start -= 1

    end = caption_index
    while end + 1 < len(scans):
        candidate = scans[end + 1]
        if candidate.chapter_title != scans[caption_index].chapter_title:
            break
        if candidate.caption_number is not None or candidate.is_heading:
            break
        if not _is_cluster_member(candidate):
            break
        end += 1

    return start, end


def _published_asset_candidates(images_dir: Path, figure_number: int) -> list[str]:
    prefix = f"figure-{figure_number:03d}"
    candidates = [
        path
        for path in images_dir.glob(prefix + "*")
        if path.is_file() and path.name != "figures.zip" and path.stat().st_size > 0
    ]
    if not candidates:
        return []

    extension_priority = {
        ".webp": 0,
        ".svg": 1,
        ".png": 2,
        ".jpg": 3,
        ".jpeg": 4,
    }
    by_stem: dict[str, list[Path]] = {}
    for candidate in candidates:
        by_stem.setdefault(candidate.stem, []).append(candidate)

    selected: list[str] = []
    for stem in sorted(by_stem):
        preferred = min(
            by_stem[stem],
            key=lambda candidate: (
                extension_priority.get(candidate.suffix.lower(), 999),
                candidate.name,
            ),
        )
        selected.append(preferred.name)
    return selected


def _record_score(record: FigureRecord) -> tuple[int, int]:
    return (
        record.objects.score(),
        record.object_paragraph_end - record.object_paragraph_start,
    )


def build_figure_inventory(
    docx_path: Path,
    chapters_dir: Path,
    summary_path: Path,
) -> list[FigureRecord]:
    title_to_path, chapter_number_to_path, chapter_number_to_title = _chapter_map(summary_path)
    active_chapter_paths = set(chapter_number_to_path.values())
    (
        figure_number_to_path,
        figure_number_to_caption,
        chapter_path_to_title,
    ) = _figure_index_map(chapters_dir)
    images_dir = chapters_dir.parent / "images"

    with ZipFile(docx_path) as archive:
        document_root = _read_xml(archive, "word/document.xml")
        if document_root is None:
            return []
        document_relationships = _build_relationship_map(archive, "word/document.xml")
        chart_parts = sorted(
            {target for target in document_relationships.values() if "/charts/" in target}
        )
        chart_drawing_map = _build_chart_drawing_map(archive, chart_parts)

        scans: list[ParagraphScan] = []
        current_chapter_title = ""
        current_chapter_path = ""
        pending_chapter_number: int | None = None

        for index, paragraph in enumerate(document_root.findall(".//w:body/w:p", W_NS)):
            text = _paragraph_text(paragraph)
            style_id = _paragraph_style(paragraph)
            normalized_text = normalize_visible_text(text)
            chapter_match = CHAPTER_MARKER_RE.match(text)
            if chapter_match is not None:
                chapter_target = _resolve_chapter_marker(
                    chapter_match,
                    normalized_text=normalized_text,
                    title_to_path=title_to_path,
                    chapter_number_to_path=chapter_number_to_path,
                    chapter_number_to_title=chapter_number_to_title,
                )
                if chapter_target is not None:
                    current_chapter_title, current_chapter_path = chapter_target
                    pending_chapter_number = None
                elif not normalize_visible_text(chapter_match.group("title") or ""):
                    pending_chapter_number = int(chapter_match.group("number"))
            elif _title_key(normalized_text) in title_to_path and _is_heading_paragraph(style_id, text):
                current_chapter_path = title_to_path[_title_key(normalized_text)]
                current_chapter_title = chapter_path_to_title.get(current_chapter_path, "")
                if not current_chapter_title:
                    chapter_number = next(
                        (
                            number
                            for number, chapter_path in chapter_number_to_path.items()
                            if chapter_path == current_chapter_path
                        ),
                        None,
                    )
                    current_chapter_title = (
                        chapter_number_to_title.get(chapter_number, normalized_text)
                        if chapter_number is not None
                        else normalized_text
                    )
                pending_chapter_number = None
            elif pending_chapter_number is not None:
                if normalized_text:
                    chapter_target = _resolve_pending_chapter_title(
                        pending_chapter_number,
                        normalized_text=normalized_text,
                        chapter_number_to_path=chapter_number_to_path,
                        chapter_number_to_title=chapter_number_to_title,
                    )
                    pending_chapter_number = None
                    if chapter_target is not None:
                        current_chapter_title, current_chapter_path = chapter_target

            if not current_chapter_title:
                continue

            caption = _extract_caption(text)
            scans.append(
                ParagraphScan(
                    index=index,
                    text=text,
                    chapter_title=current_chapter_title,
                    chapter_path=current_chapter_path,
                    style_id=style_id,
                    is_heading=_is_heading_paragraph(style_id, text),
                    caption_number=caption[0] if caption else None,
                    caption_text=caption[1] if caption else None,
                    objects=_paragraph_object_stats(
                        paragraph,
                        relationships=document_relationships,
                        chart_drawing_map=chart_drawing_map,
                    ),
                )
            )

    records_by_number: dict[int, FigureRecord] = {}
    ranking_by_number: dict[int, tuple[int, int, int]] = {}
    for scan_index, scan in enumerate(scans):
        if scan.caption_number is None or scan.caption_text is None:
            continue
        start, end = _cluster_bounds(scans, scan_index)
        merged_stats = _merge_stats([candidate.objects for candidate in scans[start : end + 1]])
        chapter_path = figure_number_to_path.get(scan.caption_number, scan.chapter_path)
        if chapter_path not in active_chapter_paths:
            chapter_path = scan.chapter_path
        chapter_title = chapter_path_to_title.get(chapter_path, scan.chapter_title)
        figure_index_path = figure_number_to_path.get(scan.caption_number, "")
        figure_index_caption = (
            figure_number_to_caption.get(scan.caption_number)
            if figure_index_path == chapter_path and figure_index_path in active_chapter_paths
            else None
        )
        record = FigureRecord(
            number=scan.caption_number,
            caption=figure_index_caption or scan.caption_text,
            chapter_title=chapter_title,
            chapter_path=chapter_path,
            caption_paragraph_index=scan.index,
            object_paragraph_start=scans[start].index,
            object_paragraph_end=scans[end].index,
            kind=classify_figure(merged_stats),
            objects=merged_stats,
            published_assets=_published_asset_candidates(images_dir, scan.caption_number),
        )
        existing = records_by_number.get(record.number)
        ranking = (
            1 if scan.style_id.lower() == "caption" else 0,
            *_record_score(record),
        )
        if existing is None or ranking > ranking_by_number.get(record.number, (0, -1, -1)):
            records_by_number[record.number] = record
            ranking_by_number[record.number] = ranking

    return [records_by_number[number] for number in sorted(records_by_number)]
