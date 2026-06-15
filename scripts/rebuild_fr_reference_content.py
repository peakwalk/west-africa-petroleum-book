from __future__ import annotations

import argparse
import html
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.docx_parity import extract_docx_chapter_by_anchors
from scripts.docx_parity.model import BodyBlock, ChapterSemanticModel, OutlineEntry

FR_DOCX = ROOT_DIR / "resources" / "editions" / "fr" / "reference.docx"
TXT_EXPORT = ROOT_DIR / ".tmp" / "fr-reference.txt"
HTML_EXPORT = ROOT_DIR / ".tmp" / "fr-reference.html"
SRC_FR_DIR = ROOT_DIR / "src-fr" / "chapters"
SRC_EN_DIR = ROOT_DIR / "src" / "chapters"


@dataclass(frozen=True)
class ChapterTarget:
    number: int
    anchor: str
    title: str
    file_name: str


CHAPTER_TARGETS = [
    ChapterTarget(
        number=1,
        anchor="CHAINE DES VALEURS DU SECTEUR DES HYDROCARBURES",
        title="Chapitre 1 : Chaîne des valeurs du secteur des hydrocarbures",
        file_name="chapter-01-value-chain-of-the-hydrocarbon-sector.md",
    ),
    ChapterTarget(
        number=2,
        anchor="DIFFERENTES PHASES DE L’AMONT PETROLIER ET ROLES DES ETATS",
        title="Chapitre 2 : Différentes phases de l’amont pétrolier et rôles des États",
        file_name="chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md",
    ),
    ChapterTarget(
        number=3,
        anchor="REGIMES FISCAUX DANS LE SECTEUR PETROLIER",
        title="Chapitre 3 : Régimes fiscaux dans le secteur pétrolier",
        file_name="chapter-03-tax-regimes-in-the-petroleum-sector.md",
    ),
    ChapterTarget(
        number=4,
        anchor="ETUDE COMPAREE DES REGIMES FISCAUX DANS CERTAINS PAYS DE L’AFRIQUE DE L’OUEST",
        title="Chapitre 4 : Étude comparée des régimes fiscaux dans certains pays de l’Afrique de l’Ouest",
        file_name="chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md",
    ),
    ChapterTarget(
        number=5,
        anchor="PRINCIPAUX DETERMINANTS SOCIO-POLITIQUES DE LA PERFORMANCE DU SECTEUR PETROLIER",
        title="Chapitre 5 : Principaux déterminants socio-politiques de la performance du secteur pétrolier",
        file_name="chapter-05-key-socio-political-determinants-of-oil-sector-performance.md",
    ),
    ChapterTarget(
        number=6,
        anchor="AFRIQUE DE L'OUEST : ANALYSES APPROFONDIES PAR PAYS",
        title="Chapitre 6 : Afrique de l’Ouest : analyses approfondies par pays",
        file_name="chapter-06-west-africa-in-depth-country-analysis.md",
    ),
]

NON_CHAPTER_TARGETS = [
    ("CONCLUSION GENERALE", "Conclusion générale", "general-conclusion.md"),
    ("GLOSSAIRE", "Glossaire", "glossary.md"),
    ("REFERENCES BIBLIOGRAPHIQUES", "Références bibliographiques", "bibliographical-references.md"),
]

PARITY_IGNORE_START = "<!-- parity-ignore:start -->"
PARITY_IGNORE_END = "<!-- parity-ignore:end -->"

FIGURE_RE = re.compile(r"^Figure\s+(?P<number>\d+)\s*:\s*(?P<text>.+)$")
TABLE_RE = re.compile(r"^Tableau\s+(?P<number>\d+)\s*:\s*(?P<text>.+)$")
BULLET_RE = re.compile(r"^(?P<indent>\s*)[•*-]\s*(?P<text>.+)$")
GLOSSARY_ENTRY_RE = re.compile(r"^(?P<term>[^:]{2,}?)\s*:\s*(?P<definition>.+)$")
CHAPTER_MARKER_RE = re.compile(r"^Chapitre\s+(?P<number>\d+)\s*:?\s*$", re.IGNORECASE)
HEADING_NUMBER_PREFIX_RE = re.compile(r"^\d+(?:\.\d+)*\s*[-–.:]?\s*")
TABLE_ROW_RE = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.IGNORECASE | re.DOTALL)
TABLE_CELL_RE = re.compile(r"<td\b[^>]*>(.*?)</td>", re.IGNORECASE | re.DOTALL)
TABLE_TAG_RE = re.compile(r"<[^>]+>")
APPLE_SPACE_RE = re.compile(
    r"<span\b[^>]*Apple-converted-space[^>]*>\s*(?:&nbsp;|&#160;|\u00a0)\s*</span>",
    re.IGNORECASE,
)
EMPTY_TABLE_PARAGRAPH_RE = re.compile(
    r"<p\b[^>]*>\s*(?:(?:<(?:strong|b|em|i)>\s*</(?:strong|b|em|i)>)|<br\s*/?>|&nbsp;|&#160;|\u00a0|\s)*</p>",
    re.IGNORECASE | re.DOTALL,
)


def _normalize(text: str) -> str:
    normalized = text.replace("\x0c", " ").replace("\u00a0", " ").replace("’", "'")
    return re.sub(r"\s+", " ", normalized).strip().upper()


def _clean_line(text: str) -> str:
    cleaned = text.replace("\x0c", " ").replace("\u00a0", " ")
    return re.sub(r"\s+", " ", cleaned).strip()


def _heading_key(text: str) -> str:
    return re.sub(r"\s*[:.]+$", "", _normalize(text))


def _heading_candidate_key(text: str) -> str:
    candidate = _clean_line(text)
    bullet_match = BULLET_RE.match(candidate)
    if bullet_match:
        candidate = bullet_match.group("text")
    candidate = HEADING_NUMBER_PREFIX_RE.sub("", candidate)
    return _heading_key(candidate)


def _ensure_exports() -> None:
    TXT_EXPORT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["textutil", "-convert", "txt", "-output", str(TXT_EXPORT), str(FR_DOCX)],
        cwd=ROOT_DIR,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        ["textutil", "-convert", "html", "-output", str(HTML_EXPORT), str(FR_DOCX)],
        cwd=ROOT_DIR,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _load_txt_lines() -> list[str]:
    return TXT_EXPORT.read_text(encoding="utf-8").splitlines()


def _find_anchor(lines: list[str], anchor: str, minimum_line: int) -> int:
    normalized_anchor = _heading_key(anchor)
    for index, raw_line in enumerate(lines):
        if index < minimum_line:
            continue
        if normalized_anchor in _heading_key(raw_line):
            return index
    raise ValueError(f"Unable to find anchor {anchor!r} after line {minimum_line}")


def _find_chapter_anchor_line(lines: list[str], target: ChapterTarget, minimum_line: int) -> int:
    normalized_anchor = _heading_key(target.anchor)
    for index, raw_line in enumerate(lines):
        if index < minimum_line:
            continue
        marker_match = CHAPTER_MARKER_RE.match(_clean_line(raw_line))
        if marker_match is None or int(marker_match.group("number")) != target.number:
            continue
        for lookahead in range(index + 1, min(index + 20, len(lines))):
            if normalized_anchor in _heading_key(lines[lookahead]):
                return lookahead
    raise ValueError(f"Unable to find chapter {target.number} anchor {target.anchor!r}")


def _extract_sections(lines: list[str]) -> dict[str, list[str]]:
    anchors: list[tuple[str, int]] = []
    for target in CHAPTER_TARGETS:
        anchors.append((target.anchor, _find_chapter_anchor_line(lines, target, 200)))
    for anchor, _, _ in NON_CHAPTER_TARGETS:
        anchors.append((anchor, _find_anchor(lines, anchor, 3000)))

    anchors.sort(key=lambda item: item[1])
    sections: dict[str, list[str]] = {}
    for index, (anchor, start_line) in enumerate(anchors):
        end_line = anchors[index + 1][1] if index + 1 < len(anchors) else len(lines)
        sections[anchor] = lines[start_line + 1 : end_line]
    return sections


def _extract_figure_image_map(chapter_dir: Path) -> dict[int, list[str]]:
    figure_map: dict[int, list[str]] = {}
    for chapter_path in sorted(chapter_dir.glob("*.md")):
        pending_images: list[str] = []
        for raw_line in chapter_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if line.startswith("!["):
                pending_images.append(raw_line.rstrip())
                continue
            figure_match = FIGURE_RE.match(_clean_line(raw_line))
            if figure_match and pending_images:
                figure_map[int(figure_match.group("number"))] = pending_images.copy()
                pending_images.clear()
                continue
            if line and not line.startswith("<sup>"):
                pending_images.clear()
    return figure_map


def _build_figure_image_map() -> dict[int, list[str]]:
    figure_map = _extract_figure_image_map(SRC_EN_DIR)
    figure_map.update(_extract_figure_image_map(SRC_FR_DIR))
    return figure_map


def _strip_table_caption_lines(table_lines: list[str]) -> list[str]:
    stripped: list[str] = []
    skipping_caption = False
    for line in table_lines:
        lowered = line.lower()
        if "<caption" in lowered:
            skipping_caption = True
        if not skipping_caption:
            stripped.append(line)
        if "</caption>" in lowered:
            skipping_caption = False
    return stripped


def _build_table_html_map() -> dict[int, list[str]]:
    html_lines = HTML_EXPORT.read_text(encoding="utf-8").splitlines()
    table_map: dict[int, list[str]] = {}
    index = 0
    while index < len(html_lines):
        line = html_lines[index]
        match = re.search(r"Tableau\s+(\d+)\s*:", _clean_line(line))
        if not match:
            index += 1
            continue
        table_number = int(match.group(1))
        next_index = index + 1
        while next_index < len(html_lines) and "<table" not in html_lines[next_index].lower():
            next_index += 1
        if next_index >= len(html_lines):
            index += 1
            continue
        table_lines: list[str] = []
        depth = 0
        while next_index < len(html_lines):
            candidate = html_lines[next_index]
            lowered = candidate.lower()
            table_lines.append(candidate.rstrip())
            if "<table" in lowered:
                depth += lowered.count("<table")
            if "</table>" in lowered:
                depth -= lowered.count("</table>")
                if depth <= 0:
                    break
            next_index += 1
        table_map[table_number] = _strip_table_caption_lines(table_lines)
        index = next_index + 1
    return table_map


def _looks_like_numbered_heading(line: str) -> bool:
    return bool(re.match(r"^\d+(?:\.\d+)*\s*[-–.:]", line))


def _first_section_anchor(lines: list[str]) -> str:
    for raw_line in lines:
        line = _clean_line(raw_line)
        if not line:
            continue
        bullet_match = BULLET_RE.match(raw_line)
        if bullet_match:
            candidate = _clean_line(bullet_match.group("text"))
            if candidate.isupper() and len(candidate.split()) <= 12:
                continue
            return candidate
        if CHAPTER_MARKER_RE.match(line):
            continue
        if _looks_like_numbered_heading(line):
            continue
        return line
    raise ValueError("Unable to derive first visible section anchor from French DOCX section")


def _chapter_model_by_target(sections: dict[str, list[str]]) -> dict[str, ChapterSemanticModel]:
    start_anchors = {
        target.anchor: _first_section_anchor(sections[target.anchor]) for target in CHAPTER_TARGETS
    }
    chapter_map: dict[str, ChapterSemanticModel] = {}
    for index, target in enumerate(CHAPTER_TARGETS):
        next_anchor = None
        if index + 1 < len(CHAPTER_TARGETS):
            next_anchor = start_anchors[CHAPTER_TARGETS[index + 1].anchor]
        chapter_map[target.anchor] = extract_docx_chapter_by_anchors(
            FR_DOCX,
            chapter_title=target.title,
            start_anchor=start_anchors[target.anchor],
            end_anchor=next_anchor,
        ).chapters[0]
    return chapter_map


def _strip_html_text(text: str) -> str:
    plain = TABLE_TAG_RE.sub(" ", text)
    plain = html.unescape(plain).replace("\u00a0", " ")
    return re.sub(r"\s+", " ", plain).strip()


def _clean_table_cell_html(cell_html: str) -> str:
    cleaned = cell_html.replace("\u00a0", " ")
    cleaned = APPLE_SPACE_RE.sub(" ", cleaned)
    cleaned = re.sub(r"</?span\b[^>]*>", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.replace("<b>", "<strong>").replace("</b>", "</strong>")
    cleaned = cleaned.replace("<i>", "<em>").replace("</i>", "</em>")
    cleaned = re.sub(r"<(p|ul|ol|li)\b[^>]*>", lambda match: f"<{match.group(1)}>", cleaned, flags=re.IGNORECASE)
    cleaned = EMPTY_TABLE_PARAGRAPH_RE.sub("", cleaned)
    cleaned = re.sub(r"<br\s*/?>", "<br />", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+\n", "\n", cleaned)
    cleaned = re.sub(r"\n\s+", "\n", cleaned)
    return cleaned.strip()


def _cell_looks_header_like(cell_html: str) -> bool:
    text = _strip_html_text(cell_html)
    if not text:
        return True
    if re.search(r"<(?:strong|b|em|i)\b", cell_html, re.IGNORECASE):
        return True
    letters_only = re.sub(r"[^A-Za-zÀ-ÿ]", "", text)
    return bool(letters_only) and text == text.upper()


def _cell_looks_like_first_row_header(cell_html: str) -> bool:
    text = _strip_html_text(cell_html)
    if not text:
        return True
    if re.search(r"\d", text):
        return False
    if len(text.split()) > 6:
        return False
    return True


def _row_looks_like_header(cells: list[str], row_index: int) -> bool:
    meaningful_cells = [cell for cell in cells if _strip_html_text(cell)]
    if not meaningful_cells:
        return False
    if row_index > 0 and any(
        "<ul" in cell.lower()
        or "<ol" in cell.lower()
        or len(_strip_html_text(cell).split()) > 8
        or re.search(r"\d", _strip_html_text(cell))
        for cell in meaningful_cells
    ):
        return False
    if all(_cell_looks_header_like(cell) for cell in meaningful_cells):
        return True
    if row_index == 0 and all(_cell_looks_like_first_row_header(cell) for cell in meaningful_cells):
        return True
    return False


def _render_table_row(cells: list[str], tag_name: str) -> list[str]:
    rendered = ["<tr>"]
    for cell_html in cells:
        cleaned = _clean_table_cell_html(cell_html)
        rendered.append(f"  <{tag_name}>{cleaned}</{tag_name}>")
    rendered.append("</tr>")
    return rendered


def _semanticize_table_html(caption_text: str, table_lines: list[str]) -> list[str]:
    table_html = "\n".join(table_lines)
    row_html_blocks = TABLE_ROW_RE.findall(table_html)
    parsed_rows = [TABLE_CELL_RE.findall(row_html) for row_html in row_html_blocks]
    parsed_rows = [cells for cells in parsed_rows if cells]

    if not parsed_rows:
        return [
            "<table>",
            f"<caption><p>{html.escape(caption_text)}</p></caption>",
            *table_lines,
            "</table>",
        ]

    header_rows: list[list[str]] = []
    body_rows: list[list[str]] = []

    for row_index, cells in enumerate(parsed_rows):
        if not body_rows and _row_looks_like_header(cells, row_index):
            header_rows.append(cells)
            continue
        body_rows.append(cells)

    if not header_rows:
        header_rows = [parsed_rows[0]]
        body_rows = parsed_rows[1:]

    rendered = [
        "<table>",
        f"<caption><p>{html.escape(caption_text)}</p></caption>",
        "<thead>",
    ]
    for cells in header_rows:
        rendered.extend(_render_table_row(cells, "th"))
    rendered.append("</thead>")
    rendered.append("<tbody>")
    for cells in body_rows:
        rendered.extend(_render_table_row(cells, "td"))
    rendered.append("</tbody>")
    rendered.append("</table>")
    return rendered


def _find_outline_line(lines: list[str], outline: OutlineEntry, start_index: int) -> int | None:
    expected_key = _heading_key(outline.title)
    expected_number = _heading_key(outline.number)
    for index in range(start_index, len(lines)):
        line = _clean_line(lines[index])
        if not line:
            continue
        candidate_key = _heading_candidate_key(line)
        if not candidate_key:
            continue
        normalized_line = _normalize(line)
        if candidate_key == expected_key:
            return index
        if expected_number and normalized_line.startswith(expected_number) and expected_key in candidate_key:
            return index
    return None


def _match_body_block_index(candidate: str, body: list[BodyBlock], start_index: int) -> int | None:
    candidate_key = _heading_key(candidate)
    if len(candidate_key) < 3:
        return None
    for index in range(start_index, len(body)):
        block_key = _heading_key(body[index].text)
        if candidate_key == block_key or candidate_key in block_key or block_key in candidate_key:
            return index
    return None


def _find_body_index_after_heading(
    lines: list[str],
    heading_line: int | None,
    body: list[BodyBlock],
    start_index: int,
    remaining_outline: list[OutlineEntry],
) -> int:
    if heading_line is None:
        return start_index
    remaining_heading_keys = {_heading_key(entry.title) for entry in remaining_outline}
    for index in range(heading_line + 1, len(lines)):
        line = _clean_line(lines[index])
        if not line:
            continue
        candidate_key = _heading_candidate_key(line)
        if candidate_key in remaining_heading_keys:
            continue
        block_index = _match_body_block_index(line, body, start_index)
        if block_index is not None:
            return block_index
    return start_index


def _build_heading_insertions(
    lines: list[str],
    chapter: ChapterSemanticModel,
) -> dict[int, list[OutlineEntry]]:
    insertions: dict[int, list[OutlineEntry]] = {}
    line_cursor = 0
    body_cursor = 0
    for outline_index, outline in enumerate(chapter.outline):
        heading_line = _find_outline_line(lines, outline, line_cursor)
        block_index = _find_body_index_after_heading(
            lines,
            heading_line,
            chapter.body,
            body_cursor,
            chapter.outline[outline_index + 1 :],
        )
        insertions.setdefault(block_index, []).append(outline)
        if heading_line is not None:
            line_cursor = heading_line + 1
        body_cursor = block_index
    return insertions


def _markdown_heading(outline: OutlineEntry) -> str:
    return f"{'#' * outline.level} {outline.number} {outline.title}"


def _render_block(
    block: BodyBlock,
    figure_map: dict[int, list[str]],
    table_map: dict[int, list[str]],
) -> list[str]:
    rendered: list[str] = []
    figure_match = FIGURE_RE.match(block.text)
    if block.kind == "caption" and figure_match:
        figure_number = int(figure_match.group("number"))
        image_lines = figure_map.get(figure_number, [])
        if image_lines:
            for image_line in image_lines:
                rendered.append(image_line)
                rendered.append("")
        rendered.append(block.text)
        rendered.append("")
        return rendered

    table_match = TABLE_RE.match(block.text)
    if table_match:
        table_number = int(table_match.group("number"))
        table_lines = table_map.get(table_number, [])
        if table_lines:
            rendered.extend(_semanticize_table_html(block.text, table_lines))
            rendered.append("")
            return rendered
        rendered.append(block.text)
        rendered.append("")
        return rendered

    if block.kind == "list_item":
        rendered.append(f"- {block.text}")
        return rendered

    rendered.append(block.text)
    rendered.append("")
    return rendered


def _render_chapter_markdown(
    target: ChapterTarget,
    lines: list[str],
    chapter: ChapterSemanticModel,
    figure_map: dict[int, list[str]],
    table_map: dict[int, list[str]],
) -> str:
    rendered: list[str] = [f"# {target.title}", ""]
    insertions = _build_heading_insertions(lines, chapter)
    previous_block_kind: str | None = None

    for block_index, block in enumerate(chapter.body):
        if previous_block_kind == "list_item" and (
            insertions.get(block_index) or block.kind != "list_item"
        ):
            rendered.append("")
        for outline in insertions.get(block_index, []):
            rendered.append(_markdown_heading(outline))
            rendered.append("")
        rendered.extend(_render_block(block, figure_map, table_map))
        previous_block_kind = block.kind

    for outline in insertions.get(len(chapter.body), []):
        if previous_block_kind == "list_item":
            rendered.append("")
        rendered.append(_markdown_heading(outline))
        rendered.append("")

    markdown = "\n".join(rendered).rstrip() + "\n"
    if target.file_name == "chapter-01-value-chain-of-the-hydrocarbon-sector.md":
        markdown = _normalize_chapter_one_table_one_notes(markdown)
    return _restore_french_formula_semantics(target.file_name, markdown)


def _normalize_chapter_one_table_one_notes(markdown: str) -> str:
    table_match = re.search(
        r"<table>\n<caption><p>Tableau 1:.*?</table>",
        markdown,
        re.DOTALL,
    )
    if table_match is None:
        return markdown

    table_block = table_match.group(0)
    normalized_table_block = re.sub(r"\*\*(\s*</p>)", r"<sup>2</sup>\1", table_block)
    normalized_table_block = re.sub(r"\*(\s*</p>)", r"<sup>1</sup>\1", normalized_table_block)

    note_block = (
        f"{PARITY_IGNORE_START}\n"
        "<sup>1</sup> Données des ministères\n"
        f"{PARITY_IGNORE_END}\n\n"
        "<p><sup>2</sup> Rapport \n"
        f"{PARITY_IGNORE_START}\n"
        "de \n"
        f"{PARITY_IGNORE_END}\n"
        "RPS Energy, 2006</p>"
    )
    normalized_table_block = f"{normalized_table_block}\n\n{note_block}"

    updated_markdown = markdown.replace(table_block, normalized_table_block, 1)
    return updated_markdown.replace("\n\nRapport RPS Energy, 2006\n\n", "\n\n", 1)


def _replace_once(markdown: str, old: str, new: str, *, context: str) -> str:
    if old not in markdown:
        raise ValueError(f"Missing expected French formula source block for {context}")
    return markdown.replace(old, new, 1)


def _extract_required_formula_snippet(
    file_name: str,
    pattern: str,
    *,
    context: str,
) -> str:
    source = (SRC_FR_DIR / file_name).read_text(encoding="utf-8")
    match = re.search(pattern, source, re.DOTALL)
    if match is None:
        raise ValueError(f"Missing preserved French formula snippet for {context}")
    return match.group(0)


def _restore_french_formula_semantics(file_name: str, markdown: str) -> str:
    if file_name == "chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md":
        prospect_block = _extract_required_formula_snippet(
            file_name,
            r'<section class="formula-group formula-group--prospect" data-equation-label="2\.1"[\s\S]*?</section>',
            context="chapter 2 equation 2.1",
        )
        volumetric_block = _extract_required_formula_snippet(
            file_name,
            r'<section class="formula-group formula-group--volumetric" data-equation-label="2\.2"[\s\S]*?</section>',
            context="chapter 2 equation 2.2",
        )
        markdown = _replace_once(
            markdown,
            (
                "P(prospect) = P(roche mère) x P(réservoir) x P(piège)\n\n"
                "Piège étanche + couverture imperméable\n\n"
                "Porosité et perméabilité de la Roche réservoir\n\n"
                "Risques géologiques\n\n"
                "Maturité de la roche-mère et par conséquent son degré de migration vers le réservoir"
            ),
            prospect_block,
            context="chapter 2 equation 2.1",
        )
        markdown = _replace_once(
            markdown,
            (
                "VHcP = GRV x N/G x Ø x Shc x 1/FVF\n\n"
                "Avec\n\n"
                "GRV= Gross Rock Volume (Volume Brut de la Roche réservoir) : il est déterminé en tenant compte de la forme géométrique du réservoir et de son épaisseur\n\n"
                "GRV = ∑Surface du gisement x Epaisseur du gisement\n\n"
                "N/G : C’est le rapport entre l’épaisseur net du réservoir et l’épaisseur brut du réservoir. Il faut noter que l’épaisseur du gisement n’a pas souvent une lithologie uniforme. Il est souvent intercalé par des couches d’argile imperméable.\n\n"
                "Ø (Phi) = Porosité du réservoir qui est estimée à partir des diagraphies électriques, des mesures sur les carottes et des connaissances provenant des formations similaires. Elle se détermine comme suit :\n\n"
                "Porosité (Ø) = Volume des pores (Vv)/ Volume du Réservoir (V)\n\n"
                "Shc = Saturation en hydrocarbures déterminé en connaissant la saturation en eau Sw. Il est généralement calculé à partir des digraphies de puits dans la zone de porosité effective.\n\n"
                "Shc = 1-Sw\n\n"
                "FVF : C’est le Facteur Volumétrique de Formation. Elle exprime le changement de volume de l’huile du réservoir à la surface dans les conditions standard de pression et de température (pression : 1 atm et température : 15° Celsius). FVF de l’huile est Bo et pour le gaz est Bg.\n\n"
                "FVF = Volume réservoir/Volume à la surface\n\n"
                "- Pour l’huile\n\n"
                "FVF = Bo et Shc = So (saturation en huile)\n\n"
                "Ainsi,\n\n"
                "STIIOP = GRV x N/G x Ø x So x 1/BoGaz associé en place = STOIIP x GOR\n\n"
                "- Pour le gaz\n\n"
                "FVF = Bg et Shc = Sg (Saturation en gaz)\n\n"
                "Ainsi,\n\n"
                "GIIP = GRV x N/G x Ø x Sg x 1/Bg\n\n"
                "Condensat en place = GIIP x CGR\n\n"
                "avec:\n\n"
                "GOR : appelé Gaz-Oil Ratio est le rapport volume de gaz sur volume d’huile produite\n\n"
                "CGR : appelé Condensate-Gaz Ratio est le rapport volume de condensat sur le volume de gaz produit"
            ),
            volumetric_block,
            context="chapter 2 equation 2.2",
        )
        return markdown

    if file_name == "chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md":
        post_royalty_block = _extract_required_formula_snippet(
            file_name,
            r'<div class="book-formula" data-equation-label="4\.1"[\s\S]*?</div>',
            context="chapter 4 equation 4.1",
        )
        oil_profit_block = _extract_required_formula_snippet(
            file_name,
            r'<!-- parity-ignore:start -->\s*<section class="formula-group formula-group--split formula-group--oil-profit" data-equation-label="4\.2"[\s\S]*?<!-- parity-ignore:end -->\s*<p hidden>Pétrole profit = Revenue post Royalty - Coûts récupérables ouPétrole Profit = Revenu brut - Royalty - Coûts récupérables</p>',
            context="chapter 4 equation 4.2",
        )
        r_factor_block = _extract_required_formula_snippet(
            file_name,
            r'<section class="formula-panel formula-panel--r-factor" data-equation-label="4\.3"[\s\S]*?</section>',
            context="chapter 4 equation 4.3",
        )
        markdown = _replace_once(
            markdown,
            "Revenu Post Royalty = Revenu brut - Royalty",
            post_royalty_block,
            context="chapter 4 equation 4.1",
        )
        markdown = _replace_once(
            markdown,
            "Pétrole profit = Revenue post Royalty - Coûts récupérables ouPétrole Profit = Revenu brut - Royalty - Coûts récupérables",
            oil_profit_block,
            context="chapter 4 equation 4.2",
        )
        markdown = _replace_once(
            markdown,
            (
                "Facteur-R=Revenus cumulés/Coût cumulé\n\n"
                "Facteur-R= (Revenus cumulés - Opex cumulés) /Capex cumulés\n\n"
                "Facteur-R= (Revenus cumulés - bénéfices cumulés) / (investissements cumulés + Opex cumulées)\n\n"
                "Facteur-R=Revenu net cumulé/Coûts cumulés"
            ),
            r_factor_block,
            context="chapter 4 equation 4.3",
        )
        return markdown

    if file_name == "glossary.md":
        api_formula_block = _extract_required_formula_snippet(
            file_name,
            r'<div class="book-formula api-density-formula"[\s\S]*?</div>',
            context="glossary API density formula",
        )
        return _replace_once(
            markdown,
            (
                "Densité API : Echelle adoptée par American Petroleum Institute (API) qui évalue si le pétrole est léger ou lourd par rapport à l’eau. Elle est calculée par la formule :\n\n"
                "- Pétrole léger (API > 30°)"
            ),
            (
                "Densité API : Echelle adoptée par American Petroleum Institute (API) qui évalue si le pétrole est léger ou lourd par rapport à l’eau. Elle est calculée par la formule :\n\n"
                f"{api_formula_block}\n\n"
                "- Pétrole léger (API > 30°)"
            ),
            context="glossary API density formula",
        )

    return markdown


def _render_conclusion(lines: list[str]) -> str:
    rendered = ["# Conclusion générale", ""]
    bullets: list[str] = []
    paragraph_lines: list[str] = []

    def flush_paragraph() -> None:
        if paragraph_lines:
            rendered.append(" ".join(paragraph_lines).strip())
            rendered.append("")
            paragraph_lines.clear()

    for raw_line in lines:
        line = _clean_line(raw_line)
        if not line:
            flush_paragraph()
            continue
        bullet_match = BULLET_RE.match(raw_line)
        if bullet_match:
            flush_paragraph()
            bullets.append(f"- {_clean_line(bullet_match.group('text'))}")
            continue
        if bullets:
            rendered.extend(bullets)
            rendered.append("")
            bullets.clear()
        paragraph_lines.append(line)

    flush_paragraph()
    if bullets:
        rendered.extend(bullets)
        rendered.append("")
    return "\n".join(rendered).rstrip() + "\n"


def _render_glossary(lines: list[str]) -> str:
    rendered = ["# Glossaire", ""]
    current_entry: list[str] = []

    def flush_entry() -> None:
        if current_entry:
            rendered.append(" ".join(current_entry).strip())
            rendered.append("")
            current_entry.clear()

    for raw_line in lines:
        line = _clean_line(raw_line)
        if not line:
            flush_entry()
            continue
        if line.startswith("REFERENCES BIBLIOGRAPHIQUES"):
            break
        bullet_match = BULLET_RE.match(raw_line)
        if bullet_match:
            flush_entry()
            rendered.append(f"- {_clean_line(bullet_match.group('text'))}")
            continue
        if GLOSSARY_ENTRY_RE.match(line) and current_entry:
            flush_entry()
        current_entry.append(line)

    flush_entry()
    return _restore_french_formula_semantics("glossary.md", "\n".join(rendered).rstrip() + "\n")


def _render_references(lines: list[str]) -> str:
    rendered = ["# Références bibliographiques", ""]
    for raw_line in lines:
        line = _clean_line(raw_line)
        if not line or line == "TABLE DES MATIERES":
            continue
        bullet_match = BULLET_RE.match(raw_line)
        if bullet_match:
            rendered.append(f"- {_clean_line(bullet_match.group('text'))}")
    return "\n".join(rendered).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    _ensure_exports()
    lines = _load_txt_lines()
    sections = _extract_sections(lines)
    figure_map = _build_figure_image_map()
    table_map = _build_table_html_map()
    chapter_map = _chapter_model_by_target(sections)

    outputs: dict[str, str] = {}
    for target in CHAPTER_TARGETS:
        outputs[target.file_name] = _render_chapter_markdown(
            target,
            sections[target.anchor],
            chapter_map[target.anchor],
            figure_map,
            table_map,
        )

    outputs["general-conclusion.md"] = _render_conclusion(sections["CONCLUSION GENERALE"])
    outputs["glossary.md"] = _render_glossary(sections["GLOSSAIRE"])
    outputs["bibliographical-references.md"] = _render_references(
        sections["REFERENCES BIBLIOGRAPHIQUES"]
    )

    if not args.write:
        for file_name, content in outputs.items():
            print(file_name, len(content.splitlines()))
        return 0

    for file_name, content in outputs.items():
        (SRC_FR_DIR / file_name).write_text(content, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
