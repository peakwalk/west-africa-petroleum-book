import re
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from .model import BodyBlock, BookSemanticModel, ChapterSemanticModel, OutlineEntry
from .normalize import (
    normalize_formula_text,
    normalize_heading_number,
    normalize_visible_text,
    split_heading_label,
)

W_NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
}
CHAPTER_TITLE_RE = re.compile(r"^Chapter\s+(?P<number>\d+)\s*:", re.IGNORECASE)
CAPTION_START_RE = re.compile(r"(Figure|Table)\s+\d+\s*:", re.IGNORECASE)
BARE_CAPTION_PLACEHOLDER_RE = re.compile(r"^(Figure|Table)\s+\d+\s*:\s*$", re.IGNORECASE)
FORMULA_CHAIN_START_RE = re.compile(r"[A-Z][A-Za-z0-9()/' -]{2,80}=")
TEMPERATURE_AXIS_LABEL_RE = re.compile(
    r"^(?:\d+\s*(?:to|-)\s*)?\d+(?:-\d+)?°C(?:-\d+°C)?$",
    re.IGNORECASE,
)
CHAPTER_MARKER_RE = re.compile(r"^Chapter\s+\d+$", re.IGNORECASE)
FLOWCHART_LABEL_MARKERS = (
    "flow chart",
    "gross income:",
    "post-royalty income",
    "net cash flow",
    "partner net cash flow",
    "total gross cash flow",
    "state participation",
    "corporate tax",
    "profit tax",
    "gross cash flow",
    "taxable",
    "imposable/taxable",
    "streamer",
)
SOURCE_CREDIT_MARKERS = (
    "report",
    "ministr",
    "economics",
    "trading economics",
    "energy",
    "bank",
)


def _read_xml(archive: ZipFile, member: str) -> ET.Element | None:
    try:
        return ET.fromstring(archive.read(member))
    except KeyError:
        return None


def _build_style_level_map(styles_root: ET.Element | None) -> dict[str, int]:
    if styles_root is None:
        return {}

    style_levels: dict[str, int] = {}
    for style in styles_root.findall("w:style", W_NS):
        style_id = style.attrib.get(f"{{{W_NS['w']}}}styleId", "")
        name_node = style.find("w:name", W_NS)
        name = name_node.attrib.get(f"{{{W_NS['w']}}}val", "") if name_node is not None else ""
        for candidate in (style_id, name):
            lowered = candidate.lower()
            if lowered.startswith("heading "):
                try:
                    style_levels[style_id] = int(lowered.split(" ", 1)[1])
                except ValueError:
                    pass
                break
    return style_levels


def _build_numbering_map(
    numbering_root: ET.Element | None,
) -> dict[str, dict[int, dict[str, int | str]]]:
    if numbering_root is None:
        return {}

    abstract_levels: dict[str, dict[int, dict[str, int | str]]] = {}
    for abstract in numbering_root.findall("w:abstractNum", W_NS):
        abstract_id = abstract.attrib[f"{{{W_NS['w']}}}abstractNumId"]
        level_map: dict[int, dict[str, int | str]] = {}
        for level in abstract.findall("w:lvl", W_NS):
            ilvl = int(level.attrib[f"{{{W_NS['w']}}}ilvl"])
            lvl_text = level.find("w:lvlText", W_NS)
            start_node = level.find("w:start", W_NS)
            if lvl_text is None:
                continue
            level_map[ilvl] = {
                "text": lvl_text.attrib[f"{{{W_NS['w']}}}val"],
                "start": int(
                    start_node.attrib.get(f"{{{W_NS['w']}}}val", "1")
                    if start_node is not None
                    else "1"
                ),
            }
        abstract_levels[abstract_id] = level_map

    numbering_map: dict[str, dict[int, dict[str, int | str]]] = {}
    for num in numbering_root.findall("w:num", W_NS):
        num_id = num.attrib[f"{{{W_NS['w']}}}numId"]
        abstract_num_id = num.find("w:abstractNumId", W_NS)
        if abstract_num_id is None:
            continue
        abstract_id = abstract_num_id.attrib[f"{{{W_NS['w']}}}val"]
        numbering_map[num_id] = abstract_levels.get(abstract_id, {})
    return numbering_map


def _paragraph_text(paragraph: ET.Element) -> str:
    parts: list[str] = []
    for node in paragraph.findall(".//w:t", W_NS):
        if node.text:
            parts.append(node.text)
    return normalize_visible_text("".join(parts))


def _append_component(
    components: list[tuple[str, str]], kind: str, raw_value: str
) -> None:
    normalized = (
        normalize_formula_text(raw_value)
        if kind == "math"
        else normalize_visible_text(raw_value)
    )
    if not normalized:
        return
    if components and components[-1][0] == kind:
        merged = (
            f"{components[-1][1]}{normalized}"
            if kind == "math"
            else normalize_visible_text(
                f"{components[-1][1]}{normalized}"
                if normalized[:1] in ":;,.?!)]}"
                else f"{components[-1][1]} {normalized}"
            )
        )
        components[-1] = (kind, merged)
        return
    components.append((kind, normalized))


def _serialize_math_node(node: ET.Element) -> str:
    if node.tag == f"{{{W_NS['m']}}}t":
        return node.text or ""
    if node.tag == f"{{{W_NS['m']}}}f":
        numerator = _serialize_math_node(node.find("m:num", W_NS)) if node.find("m:num", W_NS) is not None else ""
        denominator = _serialize_math_node(node.find("m:den", W_NS)) if node.find("m:den", W_NS) is not None else ""
        if numerator and denominator:
            return f"{numerator}/{denominator}"
        return numerator or denominator
    parts: list[str] = []
    for child in list(node):
        text = _serialize_math_node(child)
        if text:
            parts.append(text)
    return "".join(parts)


def _run_components(run: ET.Element) -> list[tuple[str, str]]:
    components: list[tuple[str, str]] = []
    for child in list(run):
        if child.tag == f"{{{W_NS['w']}}}t" and child.text:
            _append_component(components, "text", child.text)
            continue

        if child.tag.startswith(f"{{{W_NS['m']}}}") or child.find(".//m:t", W_NS) is not None:
            value = _serialize_math_node(child)
            if value:
                _append_component(components, "math", value)
            continue

        nested_text = "".join(
            node.text for node in child.findall(".//w:t", W_NS) if node.text
        )
        if nested_text:
            _append_component(components, "text", nested_text)

    return components


def _paragraph_components(paragraph: ET.Element) -> list[tuple[str, str]]:
    components: list[tuple[str, str]] = []
    for child in list(paragraph):
        if child.tag == f"{{{W_NS['w']}}}r":
            for kind, value in _run_components(child):
                _append_component(components, kind, value)
            continue
        if child.tag == f"{{{W_NS['w']}}}hyperlink":
            for run in child.findall("w:r", W_NS):
                for kind, value in _run_components(run):
                    _append_component(components, kind, value)
    return components


def _paragraph_level(paragraph: ET.Element, style_levels: dict[str, int]) -> int | None:
    style_node = paragraph.find("w:pPr/w:pStyle", W_NS)
    if style_node is not None:
        style_id = style_node.attrib.get(f"{{{W_NS['w']}}}val", "")
        if style_id in style_levels:
            return style_levels[style_id]

    outline_node = paragraph.find("w:pPr/w:outlineLvl", W_NS)
    if outline_node is not None:
        try:
            return int(outline_node.attrib[f"{{{W_NS['w']}}}val"]) + 1
        except ValueError:
            return None

    return None


def _num_pr(paragraph: ET.Element) -> ET.Element | None:
    return paragraph.find("w:pPr/w:numPr", W_NS)


def _extract_num_values(num_pr: ET.Element | None) -> tuple[str | None, int | None]:
    if num_pr is None:
        return None, None
    num_id_node = num_pr.find("w:numId", W_NS)
    ilvl_node = num_pr.find("w:ilvl", W_NS)
    if num_id_node is None or ilvl_node is None:
        return None, None
    return (
        num_id_node.attrib.get(f"{{{W_NS['w']}}}val"),
        int(ilvl_node.attrib.get(f"{{{W_NS['w']}}}val", "0")),
    )


def _chapter_number_from_title(title: str) -> int | None:
    match = CHAPTER_TITLE_RE.match(title)
    if match is None:
        return None
    return int(match.group("number"))


def _section_prefix(number: str) -> str:
    return normalize_heading_number(number).rstrip("-.")


def _matches_anchor_text(text: str, anchor: str | None) -> bool:
    if not anchor:
        return False
    normalized_anchor = normalize_visible_text(anchor)
    if text == normalized_anchor:
        return True
    _, literal_title = split_heading_label(text)
    return bool(literal_title) and literal_title == normalized_anchor


def _parent_prefix_from_child(number: str, parent_level: int) -> str | None:
    normalized = _section_prefix(number)
    parts = [part for part in normalized.split(".") if part]
    if len(parts) < parent_level:
        return None
    return ".".join(parts[:parent_level])


def _extract_caption_from_spillover(text: str) -> str | None:
    starts = [match.start() for match in CAPTION_START_RE.finditer(text)]
    if not starts:
        return None
    caption = text[starts[0] :].strip()
    if len(starts) > 1:
        caption = text[starts[0] : starts[1]].strip()
    caption = normalize_visible_text(caption)
    words = caption.split()
    if words and len(words) % 2 == 0:
        midpoint = len(words) // 2
        if words[:midpoint] == words[midpoint:]:
            caption = " ".join(words[:midpoint])
    return caption


def _is_spillover_caption(text: str, caption: str) -> bool:
    start = text.find(caption)
    if start < 0:
        return False

    prefix = text[:start]
    suffix = normalize_visible_text(text[start + len(caption) :])

    if caption and caption in suffix:
        return True

    if prefix:
        last_character = prefix[-1]
        if not last_character.isspace() and last_character not in "([{\"'":
            return True

    return False


def _looks_like_duplicated_graphic_label(text: str) -> bool:
    normalized = normalize_visible_text(text)
    if len(normalized) % 2 == 0:
        midpoint = len(normalized) // 2
        if normalized[:midpoint] == normalized[midpoint:]:
            return True

    words = normalized.split()
    if not words or len(words) > 8:
        return False
    if len(words) % 2 != 0:
        return False
    midpoint = len(words) // 2
    return words[:midpoint] == words[midpoint:]


def _looks_like_pre_heading_figure_label(text: str) -> bool:
    normalized = normalize_visible_text(text)
    if not normalized:
        return False
    if any(punctuation in normalized for punctuation in ",.!?;:"):
        return False
    return len(normalized.split()) <= 6 or len(normalized) <= 80


def _looks_like_short_graphic_label_fragment(text: str) -> bool:
    lowered = text.lower()
    words = text.split()

    if re.fullmatch(r"[0-9+.,%() /-]+", text):
        return True

    if len(words) <= 8 and any(marker in lowered for marker in FLOWCHART_LABEL_MARKERS):
        return True

    if len(words) <= 8 and "." not in text and any(character.isdigit() for character in text):
        return True

    if words and len(words) == 1 and all(word.isupper() for word in words):
        return True

    return False


def _looks_like_concatenated_label_cluster(text: str) -> bool:
    normalized = _dedupe_exact_double(text)
    if normalized.startswith(("Figure ", "Table ")):
        return False
    if any(punctuation in normalized for punctuation in ".!?;"):
        return False
    return len(re.findall(r"(?<=[a-z0-9%)])(?=[A-Z])", normalized)) >= 1


def _looks_like_pre_caption_graphic_fragment(text: str) -> bool:
    normalized = _dedupe_exact_double(text)
    lowered = normalized.lower()
    words = normalized.split()

    if "=" in normalized:
        return False

    if "FLOW CHART" in normalized:
        return True

    if "streamer" in lowered and "source" in lowered:
        return True

    if _looks_like_concatenated_label_cluster(normalized):
        return True

    chunks = _split_consecutive_doubled_chunks(normalized)
    if len(chunks) > 1 and all(_looks_like_short_graphic_label_fragment(chunk) for chunk in chunks):
        return True

    if (
        "," in normalized
        and not any(character.isdigit() for character in normalized)
        and not any(marker in lowered for marker in FLOWCHART_LABEL_MARKERS)
    ):
        return False

    return _looks_like_short_graphic_label_fragment(normalized)


def _looks_like_semantic_callout(text: str) -> bool:
    normalized = normalize_visible_text(text)
    if "=" in normalized:
        return True
    if "," in normalized:
        return True

    words = normalized.split()
    if len(words) < 2:
        return False

    if all(re.fullmatch(r"[A-Z][A-Z0-9/&()'.-]*", word) for word in words):
        return True

    connectors = {"and", "of", "the", "to", "in", "for", "with", "or"}
    if len(words) >= 3 and all(
        re.fullmatch(r"[A-Z][A-Za-z0-9/&()'.-]*", word) or word.lower() in connectors
        for word in words
    ):
        return True

    return False


def _looks_like_source_credit(text: str) -> bool:
    normalized = normalize_visible_text(text)
    lowered = normalized.lower()
    if not normalized or len(normalized.split()) > 8:
        return False
    return any(marker in lowered for marker in SOURCE_CREDIT_MARKERS)


def _looks_like_immediate_pre_caption_label(text: str) -> bool:
    normalized = _dedupe_exact_double(text)
    if not normalized or any(punctuation in normalized for punctuation in ",.!?;:"):
        return False

    words = normalized.split()
    if not 1 <= len(words) <= 4:
        return False
    if all(word.isupper() for word in words):
        return False

    connectors = {"and", "of", "the", "to", "in", "for", "with", "or"}
    return all(
        re.fullmatch(r"[A-Z][A-Za-z0-9/&()'.-]*", word) or word.lower() in connectors
        for word in words
    )


def _lookahead_texts(paragraphs: list[ET.Element], start_index: int, limit: int = 2) -> list[str]:
    lookahead: list[str] = []
    for paragraph in paragraphs[start_index + 1 :]:
        text = _paragraph_text(paragraph)
        if not text:
            continue
        lookahead.append(text)
        if len(lookahead) >= limit:
            break
    return lookahead


def _is_caption_candidate(text: str) -> bool:
    if text.startswith(("Figure ", "Table ")):
        return True

    spillover_caption = _extract_caption_from_spillover(text)
    if spillover_caption is None:
        return False

    return _is_spillover_caption(text, spillover_caption)


def _should_skip_post_caption_graphic_label(
    blocks: list[BodyBlock], text: str, seen_outline: bool
) -> bool:
    if not blocks or blocks[-1].kind != "caption":
        return False
    if _is_caption_candidate(_dedupe_exact_double(text)):
        return False
    if _looks_like_concatenated_label_cluster(text):
        return True
    if _looks_like_semantic_callout(_dedupe_exact_double(text)):
        return False
    return _looks_like_duplicated_graphic_label(text) or _looks_like_pre_caption_graphic_fragment(text)


def _dedupe_exact_double(text: str) -> str:
    normalized = normalize_visible_text(text)
    if len(normalized) % 2 == 0:
        midpoint = len(normalized) // 2
        if normalized[:midpoint] == normalized[midpoint:]:
            return normalized[:midpoint]
    return normalized


def _split_consecutive_doubled_chunks(text: str) -> list[str]:
    parts: list[str] = []
    position = 0
    normalized = _dedupe_exact_double(text)
    while position < len(normalized):
        found = None
        remaining = len(normalized) - position
        for length in range(4, remaining // 2 + 1):
            first = normalized[position : position + length]
            second = normalized[position + length : position + 2 * length]
            if first == second:
                found = first
                break
        if found is None:
            if position == 0:
                return [normalized]
            parts.append(normalized[position:])
            break
        parts.append(found)
        position += len(found) * 2
    return [part for part in (normalize_visible_text(part) for part in parts) if part]


def _split_formula_chain(text: str) -> list[str]:
    split_points: list[int] = []
    for index, character in enumerate(text):
        if index == 0 or not character.isupper():
            continue
        if index + 1 >= len(text) or not (
            text[index + 1].islower() or text[index + 1] in "-("
        ):
            continue
        previous_character = text[index - 1]
        if previous_character.isspace() or previous_character in "([/-=":
            continue
        tail = text[index : index + 96]
        equation_index = tail.find("=")
        if equation_index == -1:
            continue
        candidate = tail[:equation_index]
        if (
            " " not in candidate.strip()
            and "-" not in candidate
            and "/" not in candidate
        ):
            continue
        if FORMULA_CHAIN_START_RE.fullmatch(candidate + "=") is None:
            continue
        split_points.append(index)

    if not split_points:
        return [text]

    parts: list[str] = []
    start = 0
    for split_point in split_points:
        parts.append(text[start:split_point])
        start = split_point
    parts.append(text[start:])
    return [normalize_visible_text(part) for part in parts if normalize_visible_text(part)]


def _split_glued_uppercase_heading(text: str) -> list[str]:
    normalized = normalize_visible_text(text)
    match = re.fullmatch(r"([A-Z][A-Z /&,'()-]*\bAND)([A-Z][A-Z /&,'()-]+)", normalized)
    if match is None:
        return [normalized]
    return [normalize_visible_text(match.group(1)), normalize_visible_text(match.group(2))]


def _split_evaluation_option_cluster(text: str) -> list[BodyBlock] | None:
    heading = "EVALUATION DES OPTIONS DE RECUPERATION"
    if not text.startswith(heading):
        return None

    markers = [
        "Recovery Methods",
        "Types/types of wells",
        "Etc",
    ]
    positions: list[int] = []
    for marker in markers:
        position = text.find(marker)
        if position < 0:
            return None
        positions.append(position)

    blocks = [BodyBlock(kind="paragraph", text=heading)]
    for index, position in enumerate(positions):
        next_position = positions[index + 1] if index + 1 < len(positions) else len(text)
        item = normalize_visible_text(text[position:next_position])
        if item:
            blocks.append(BodyBlock(kind="list_item", text=item))
    return blocks


def _normalize_merged_paragraph_parts(text: str) -> list[str]:
    deduped = _dedupe_exact_double(text)
    heading_parts = _split_glued_uppercase_heading(deduped)
    if len(heading_parts) > 1:
        return heading_parts

    doubled_chunks = _split_consecutive_doubled_chunks(deduped)
    if len(doubled_chunks) > 1:
        return doubled_chunks

    formula_parts = _split_formula_chain(deduped)
    if len(formula_parts) > 1:
        return formula_parts

    return [deduped]


def _should_merge_fragment_with_next(current: BodyBlock, following: BodyBlock) -> bool:
    if current.kind != "paragraph" or following.kind != "paragraph":
        return False

    if not re.fullmatch(r"[A-Za-zØ]{1,3}", current.text):
        return False

    return bool(re.match(r"[A-Za-zØ][A-Za-zØa-z0-9()/' -]{0,64}=", following.text))


def _is_split_chapter_marker(
    paragraphs: list[ET.Element], start_index: int, style_levels: dict[str, int]
) -> bool:
    current_text = _paragraph_text(paragraphs[start_index])
    if CHAPTER_MARKER_RE.fullmatch(current_text) is None:
        return False

    for paragraph in paragraphs[start_index + 1 :]:
        text = _paragraph_text(paragraph)
        if not text:
            continue
        return _paragraph_level(paragraph, style_levels) == 1
    return False


def _is_target_split_chapter_marker(
    paragraphs: list[ET.Element],
    start_index: int,
    style_levels: dict[str, int],
    chapter_number: int | None,
) -> bool:
    if chapter_number is None:
        return False
    current_text = _paragraph_text(paragraphs[start_index])
    if current_text.lower() != f"chapter {chapter_number}".lower():
        return False
    return _is_split_chapter_marker(paragraphs, start_index, style_levels)


def _has_target_chapter_marker(
    paragraphs: list[ET.Element],
    style_levels: dict[str, int],
    normalized_chapter_title: str,
    chapter_number: int | None,
) -> bool:
    for index, paragraph in enumerate(paragraphs):
        components = _paragraph_components(paragraph)
        text = _paragraph_text(paragraph)
        if not text and components:
            text = " ".join(value for kind, value in components if kind == "text").strip()
            if not text:
                text = " ".join(value for kind, value in components if kind == "math").strip()
        if not text:
            continue
        level = _paragraph_level(paragraph, style_levels)
        if level == 1 and text == normalized_chapter_title:
            return True
        if _is_target_split_chapter_marker(paragraphs, index, style_levels, chapter_number):
            return True
    return False


def _postprocess_body_blocks(blocks: list[BodyBlock]) -> list[BodyBlock]:
    normalized: list[BodyBlock] = []
    index = 0
    while index < len(blocks):
        current = blocks[index]
        if (
            current.kind == "paragraph"
            and normalized
            and normalized[-1].kind == "caption"
            and TEMPERATURE_AXIS_LABEL_RE.fullmatch(current.text)
        ):
            index += 1
            continue
        if index + 1 < len(blocks) and _should_merge_fragment_with_next(current, blocks[index + 1]):
            merged_text = _dedupe_exact_double(current.text + blocks[index + 1].text)
            normalized.append(BodyBlock(kind="paragraph", text=merged_text))
            index += 2
            continue
        normalized.append(current)
        index += 1
    return normalized


def _normalize_paragraph_body_blocks(text: str) -> list[BodyBlock]:
    deduped = _dedupe_exact_double(text)

    list_cluster = _split_evaluation_option_cluster(deduped)
    if list_cluster is not None:
        return list_cluster

    if deduped.startswith(("Figure ", "Table ")):
        return [BodyBlock(kind="caption", text=deduped)]

    return [
        BodyBlock(kind="paragraph", text=paragraph_part)
        for paragraph_part in _normalize_merged_paragraph_parts(deduped)
    ]


def _reconcile_outline_numbers(outline: list[OutlineEntry]) -> list[OutlineEntry]:
    reconciled: list[OutlineEntry] = []
    for index, entry in enumerate(outline):
        if entry.level != 2:
            reconciled.append(entry)
            continue

        descendant_prefix = None
        for descendant in outline[index + 1 :]:
            if descendant.level <= entry.level:
                break
            descendant_prefix = _parent_prefix_from_child(descendant.number, entry.level)
            if descendant_prefix:
                break

        if descendant_prefix is None:
            reconciled.append(entry)
            continue

        current_prefix = _section_prefix(entry.number)
        if descendant_prefix == current_prefix:
            reconciled.append(entry)
            continue

        reconciled.append(
            OutlineEntry(level=entry.level, number=f"{descendant_prefix}-", title=entry.title)
        )

    return reconciled


def _render_number(
    level_template: str, counters: dict[int, int], chapter_number: int | None
) -> str:
    rendered = level_template
    for token in re.findall(r"%(\d+)", level_template):
        level_index = int(token) - 1
        value = counters.get(level_index, 0)
        if value == 0 and level_index == 0 and chapter_number is not None:
            value = chapter_number
        rendered = rendered.replace(f"%{token}", str(value))
    rendered = rendered.replace(" -", "-").replace(". ", ".").strip()
    return normalize_heading_number(rendered)


def _advance_number_counter(
    num_counters: dict[int, int], ilvl: int, level_meta: dict[str, int | str]
) -> None:
    if ilvl not in num_counters or num_counters[ilvl] == 0:
        num_counters[ilvl] = int(level_meta.get("start", 1)) - 1
    num_counters[ilvl] += 1


def _open_docx_roots(
    docx_path: Path,
) -> tuple[ET.Element | None, ET.Element | None, ET.Element | None]:
    with ZipFile(docx_path) as archive:
        document_root = _read_xml(archive, "word/document.xml")
        numbering_root = _read_xml(archive, "word/numbering.xml")
        styles_root = _read_xml(archive, "word/styles.xml")
    return document_root, numbering_root, styles_root


def extract_docx_book(
    docx_path: str | Path, expected_titles: list[str] | None = None
) -> BookSemanticModel:
    docx_path = Path(docx_path)
    document_root, numbering_root, styles_root = _open_docx_roots(docx_path)

    if document_root is None:
        return BookSemanticModel()

    style_levels = _build_style_level_map(styles_root)
    numbering_map = _build_numbering_map(numbering_root)

    expected_queue = list(expected_titles or [])
    wait_for_expected_title = bool(expected_queue)
    counters: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    section_level_counters: dict[tuple[str, int, str], int] = {}
    chapters: list[ChapterSemanticModel] = []

    current_title = ""
    current_outline: list[OutlineEntry] = []
    current_body: list[BodyBlock] = []
    current_source = "docx:front-matter"
    current_chapter_number: int | None = None
    current_section_prefix = ""
    seen_outline = False
    suppress_pre_heading_figure_labels = False

    def flush_chapter() -> None:
        nonlocal current_title, current_outline, current_body, current_source, current_section_prefix, seen_outline, suppress_pre_heading_figure_labels
        if not current_title:
            return
        chapters.append(
            ChapterSemanticModel(
                source_path=current_source,
                title=current_title,
                outline=_reconcile_outline_numbers(current_outline),
                body=_postprocess_body_blocks(current_body),
            )
        )
        current_title = ""
        current_outline = []
        current_body = []
        current_source = f"docx:{len(chapters) + 1}"
        current_section_prefix = ""
        seen_outline = False
        suppress_pre_heading_figure_labels = False

    paragraphs = document_root.findall(".//w:body/w:p", W_NS)

    for index, paragraph in enumerate(paragraphs):
        components = _paragraph_components(paragraph)
        text = _paragraph_text(paragraph)
        if not text and components:
            text = " ".join(value for kind, value in components if kind == "text").strip()
            if not text:
                text = " ".join(value for kind, value in components if kind == "math").strip()
        if not text:
            continue
        next_texts = _lookahead_texts(paragraphs, index)
        future_texts = _lookahead_texts(paragraphs, index, limit=30)

        if BARE_CAPTION_PLACEHOLDER_RE.fullmatch(text):
            continue

        if expected_queue and text == expected_queue[0]:
            flush_chapter()
            current_title = text
            current_source = f"docx:{len(chapters) + 1}"
            current_chapter_number = _chapter_number_from_title(text)
            expected_queue.pop(0)
            wait_for_expected_title = False
            continue

        if wait_for_expected_title and not current_title:
            continue

        level = _paragraph_level(paragraph, style_levels)
        num_pr = _num_pr(paragraph)
        num_id, ilvl = _extract_num_values(num_pr)

        if not current_title and level == 1:
            current_title = text
            current_source = f"docx:{len(chapters) + 1}"
            current_chapter_number = _chapter_number_from_title(text)
            continue

        if level is not None and level > 1:
            literal_number, literal_title = split_heading_label(text)
            if literal_number:
                current_outline.append(
                    OutlineEntry(level=level, number=literal_number, title=literal_title)
                )
                if level == 2:
                    current_section_prefix = _section_prefix(literal_number)
                seen_outline = True
                suppress_pre_heading_figure_labels = False
                continue

            if num_id is not None and ilvl is not None:
                level_meta = numbering_map.get(num_id, {}).get(ilvl, {})
                if level >= 3 and current_section_prefix:
                    key = (current_section_prefix, ilvl, num_id)
                    if key not in section_level_counters:
                        section_level_counters[key] = int(level_meta.get("start", 1)) - 1
                    section_level_counters[key] += 1
                    rendered_number = normalize_heading_number(
                        f"{current_section_prefix}.{section_level_counters[key]}-"
                    )
                else:
                    num_counters = counters[num_id]
                    if ilvl > 0 and num_counters.get(0, 0) == 0 and current_chapter_number:
                        num_counters[0] = current_chapter_number
                    _advance_number_counter(num_counters, ilvl, level_meta)
                    for deeper in list(num_counters.keys()):
                        if deeper > ilvl:
                            num_counters[deeper] = 0
                    rendered_number = _render_number(
                        str(level_meta.get("text", "")),
                        num_counters,
                        current_chapter_number,
                    )
                current_outline.append(
                    OutlineEntry(level=level, number=rendered_number, title=text)
                )
                if level == 2:
                    current_section_prefix = _section_prefix(rendered_number)
                seen_outline = True
                suppress_pre_heading_figure_labels = False
                continue

        semantic_callout = _looks_like_semantic_callout(_dedupe_exact_double(text)) or _looks_like_source_credit(text)
        pre_caption_graphic_fragment = _looks_like_pre_caption_graphic_fragment(text)
        if (
            num_id is None
            and any(_is_caption_candidate(candidate) for candidate in future_texts)
            and not _is_caption_candidate(_dedupe_exact_double(text))
            and (
                (pre_caption_graphic_fragment and not _looks_like_source_credit(text))
                or
                (
                    next_texts
                    and _is_caption_candidate(next_texts[0])
                    and _looks_like_immediate_pre_caption_label(text)
                )
                or (
                    not semantic_callout
                    and (
                        pre_caption_graphic_fragment
                        or _looks_like_duplicated_graphic_label(text)
                        or _looks_like_pre_heading_figure_label(text)
                    )
                )
            )
        ):
            continue

        spillover_caption = _extract_caption_from_spillover(text)
        if spillover_caption is not None and (
            not seen_outline or _is_spillover_caption(text, spillover_caption)
        ):
            current_body.append(BodyBlock(kind="caption", text=spillover_caption))
            if not seen_outline:
                suppress_pre_heading_figure_labels = True
            continue
        if not seen_outline:
            if suppress_pre_heading_figure_labels and (
                _looks_like_duplicated_graphic_label(text)
                or _looks_like_pre_heading_figure_label(text)
            ) and not semantic_callout:
                continue
        if _should_skip_post_caption_graphic_label(current_body, text, seen_outline):
            continue

        if num_id is not None:
            kind = "list_item"
        elif text.startswith("Figure ") or text.startswith("Table "):
            kind = "caption"
            if not seen_outline:
                suppress_pre_heading_figure_labels = True
        else:
            kind = "paragraph"
        if kind == "paragraph" and any(component_kind == "math" for component_kind, _ in components):
            for component_kind, component_text in components:
                if component_kind == "math":
                    current_body.append(
                        BodyBlock(
                            kind="paragraph", text=_dedupe_exact_double(component_text)
                        )
                    )
                else:
                    current_body.extend(_normalize_paragraph_body_blocks(component_text))
        elif kind == "paragraph":
            current_body.extend(_normalize_paragraph_body_blocks(text))
        else:
            current_body.append(BodyBlock(kind=kind, text=text))

    flush_chapter()
    return BookSemanticModel(chapters=chapters)


def extract_docx_chapter_by_anchors(
    docx_path: str | Path,
    chapter_title: str,
    start_anchor: str,
    end_anchor: str | None = None,
) -> BookSemanticModel:
    docx_path = Path(docx_path)
    document_root, numbering_root, styles_root = _open_docx_roots(docx_path)

    if document_root is None:
        return BookSemanticModel()

    style_levels = _build_style_level_map(styles_root)
    numbering_map = _build_numbering_map(numbering_root)
    counters: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    section_level_counters: dict[tuple[str, int, str], int] = {}
    chapter_number = _chapter_number_from_title(chapter_title)
    outline: list[OutlineEntry] = []
    body: list[BodyBlock] = []
    started = False
    in_target_chapter = False
    current_section_prefix = ""
    seen_outline = False
    suppress_pre_heading_figure_labels = False
    normalized_chapter_title = normalize_visible_text(chapter_title)

    paragraphs = document_root.findall(".//w:body/w:p", W_NS)
    if not _has_target_chapter_marker(
        paragraphs, style_levels, normalized_chapter_title, chapter_number
    ):
        in_target_chapter = True

    for index, paragraph in enumerate(paragraphs):
        components = _paragraph_components(paragraph)
        text = _paragraph_text(paragraph)
        if not text and components:
            text = " ".join(value for kind, value in components if kind == "text").strip()
            if not text:
                text = " ".join(value for kind, value in components if kind == "math").strip()
        if not text:
            continue
        level = _paragraph_level(paragraph, style_levels)
        next_texts = _lookahead_texts(paragraphs, index)
        future_texts = _lookahead_texts(paragraphs, index, limit=30)

        if BARE_CAPTION_PLACEHOLDER_RE.fullmatch(text):
            continue

        if not in_target_chapter:
            if level == 1 and text == normalized_chapter_title:
                in_target_chapter = True
            elif _is_target_split_chapter_marker(
                paragraphs, index, style_levels, chapter_number
            ):
                in_target_chapter = True
            else:
                continue

        if not started:
            if not _matches_anchor_text(text, start_anchor):
                continue
            started = True

        if _matches_anchor_text(text, end_anchor):
            break

        if started and _is_split_chapter_marker(paragraphs, index, style_levels):
            break

        if started and level == 1 and text != normalized_chapter_title:
            break

        if started and text.upper() == "TABLE OF CONTENTS":
            break

        num_pr = _num_pr(paragraph)
        num_id, ilvl = _extract_num_values(num_pr)

        if level is not None and level > 1:
            literal_number, literal_title = split_heading_label(text)
            if literal_number:
                outline.append(
                    OutlineEntry(level=level, number=literal_number, title=literal_title)
                )
                if level == 2:
                    current_section_prefix = _section_prefix(literal_number)
                seen_outline = True
                suppress_pre_heading_figure_labels = False
                continue

            if num_id is not None and ilvl is not None:
                level_meta = numbering_map.get(num_id, {}).get(ilvl, {})
                if level >= 3 and current_section_prefix:
                    key = (current_section_prefix, ilvl, num_id)
                    if key not in section_level_counters:
                        section_level_counters[key] = int(level_meta.get("start", 1)) - 1
                    section_level_counters[key] += 1
                    rendered_number = normalize_heading_number(
                        f"{current_section_prefix}.{section_level_counters[key]}-"
                    )
                else:
                    num_counters = counters[num_id]
                    if ilvl > 0 and num_counters.get(0, 0) == 0 and chapter_number:
                        num_counters[0] = chapter_number
                    _advance_number_counter(num_counters, ilvl, level_meta)
                    for deeper in list(num_counters.keys()):
                        if deeper > ilvl:
                            num_counters[deeper] = 0
                    rendered_number = _render_number(
                        str(level_meta.get("text", "")), num_counters, chapter_number
                    )
                outline.append(
                    OutlineEntry(level=level, number=rendered_number, title=text)
                )
                if level == 2:
                    current_section_prefix = _section_prefix(rendered_number)
                seen_outline = True
                suppress_pre_heading_figure_labels = False
                continue

        semantic_callout = _looks_like_semantic_callout(_dedupe_exact_double(text)) or _looks_like_source_credit(text)
        pre_caption_graphic_fragment = _looks_like_pre_caption_graphic_fragment(text)
        if (
            num_id is None
            and any(_is_caption_candidate(candidate) for candidate in future_texts)
            and not _is_caption_candidate(_dedupe_exact_double(text))
            and (
                (pre_caption_graphic_fragment and not _looks_like_source_credit(text))
                or
                (
                    next_texts
                    and _is_caption_candidate(next_texts[0])
                    and _looks_like_immediate_pre_caption_label(text)
                )
                or (
                    not semantic_callout
                    and (
                        pre_caption_graphic_fragment
                        or _looks_like_duplicated_graphic_label(text)
                        or _looks_like_pre_heading_figure_label(text)
                    )
                )
            )
        ):
            continue

        spillover_caption = _extract_caption_from_spillover(text)
        if spillover_caption is not None and (
            not seen_outline or _is_spillover_caption(text, spillover_caption)
        ):
            body.append(BodyBlock(kind="caption", text=spillover_caption))
            if not seen_outline:
                suppress_pre_heading_figure_labels = True
            continue
        if not seen_outline:
            if suppress_pre_heading_figure_labels and (
                _looks_like_duplicated_graphic_label(text)
                or _looks_like_pre_heading_figure_label(text)
            ) and not semantic_callout:
                continue
        if _should_skip_post_caption_graphic_label(body, text, seen_outline):
            continue

        if num_id is not None:
            kind = "list_item"
        elif text.startswith("Figure ") or text.startswith("Table "):
            kind = "caption"
            if not seen_outline:
                suppress_pre_heading_figure_labels = True
        else:
            kind = "paragraph"
        if kind == "paragraph" and any(component_kind == "math" for component_kind, _ in components):
            for component_kind, component_text in components:
                if component_kind == "math":
                    body.append(
                        BodyBlock(
                            kind="paragraph", text=_dedupe_exact_double(component_text)
                        )
                    )
                else:
                    body.extend(_normalize_paragraph_body_blocks(component_text))
        elif kind == "paragraph":
            body.extend(_normalize_paragraph_body_blocks(text))
        else:
            body.append(BodyBlock(kind=kind, text=text))

    return BookSemanticModel(
        chapters=[
            ChapterSemanticModel(
                source_path="docx:chapter-anchor",
                title=chapter_title,
                outline=_reconcile_outline_numbers(outline),
                body=_postprocess_body_blocks(body),
            )
        ]
    )
