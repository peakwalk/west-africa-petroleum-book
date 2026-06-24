from __future__ import annotations

import argparse
import html
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.docx_figures.inventory import build_figure_inventory
from scripts.docx_parity.extract_docx import extract_docx_book
from scripts.docx_parity.extract_markdown import extract_markdown_book
from scripts.docx_parity.render_markdown import render_markdown_chapter
from scripts.edition_config import get_edition


DOCX_CHAPTER_TITLE_RE = re.compile(
    r"^(?:Chapter|Chapitre)\s+\d+\s*:\s*(?P<title>.+)$",
    re.IGNORECASE,
)
TABLE_RE = re.compile(r"^Table\s+(?P<number>\d+)\s*:?\s*(?P<text>.+)$", re.IGNORECASE)
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
SRC_EN_DIR = ROOT_DIR / "editions" / "en" / "content" / "chapters"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rebuild English body chapters from the replacement DOCX semantic model."
    )
    parser.add_argument("--edition", default="en")
    parser.add_argument("--docx")
    parser.add_argument("--summary")
    parser.add_argument("--chapters-dir")
    parser.add_argument("--write", action="store_true")
    return parser.parse_args()


def _include_docx_title(chapter_path: Path) -> bool:
    if chapter_path.name.startswith("chapter-"):
        return True
    # The English reference DOCX merges the preface with auxiliary indexes.
    # Keep the curated web front matter pages out of the automatic rebuild flow.
    return chapter_path.name in {
        "disclaimer.md",
        "glossary.md",
        "bibliographical-references.md",
    }


def _docx_expected_title(title: str) -> str:
    match = DOCX_CHAPTER_TITLE_RE.match(title)
    if match is not None:
        return match.group("title").strip()
    return title.strip()


def _figure_image_map(docx_path: Path, summary_path: Path, chapters_dir: Path) -> dict[int, list[str]]:
    figure_inventory = build_figure_inventory(docx_path, chapters_dir, summary_path)
    image_map: dict[int, list[str]] = {}
    for record in figure_inventory:
        if not record.published_assets:
            continue
        image_map[record.number] = [
            f"![Figure {record.number:03d}](../images/{asset})"
            for asset in record.published_assets
        ]
    return image_map


def _clean_line(text: str) -> str:
    cleaned = text.replace("\x0c", " ").replace("\u00a0", " ")
    return re.sub(r"\s+", " ", cleaned).strip()


def _replace_once(markdown: str, old: str, new: str, *, context: str) -> str:
    if old not in markdown:
        raise ValueError(f"Missing expected English source block for {context}")
    return markdown.replace(old, new, 1)


def _replace_if_present(markdown: str, old: str, new: str) -> str:
    if old not in markdown:
        return markdown
    return markdown.replace(old, new, 1)


def _extract_required_formula_snippet(file_name: str, pattern: str, *, context: str) -> str:
    source = (SRC_EN_DIR / file_name).read_text(encoding="utf-8")
    match = re.search(pattern, source, re.DOTALL)
    if match is None:
        raise ValueError(f"Missing preserved English formula snippet for {context}")
    return match.group(0)


def _restore_english_formula_semantics(file_name: str, markdown: str) -> str:
    if file_name != "chapter-06-upstream-operations-and-government-roles.md":
        return markdown

    volumetric_block = _extract_required_formula_snippet(
        file_name,
        (
            r'<!-- parity-ignore:start -->[\s\S]*?'
            r'<p hidden>CGR \(Condensate-Gas Ratio\) - the ratio of produced condensate volume to produced gas volume\.</p>'
            r'(?=\n\n\*\*Prospect Ranking and Appraisal\*\*)'
        ),
        context="chapter 6 volumetric formulas",
    )
    markdown = _replace_once(
        markdown,
        (
            "VHcP=GRV×N/G×ϕ×Shc×1/FVF\n\n"
            "Where:\n\n"
            "GRV (Gross Rock Volume) - the gross volume of the reservoir rock. It is determined from the geometric shape and thickness of the reservoir.\n\n"
            "GRV=∑(ReservoirArea×ReservoirThickness)\n\n"
            "N/G (Net-to-Gross Ratio) - the ratio of net reservoir thickness to gross reservoir thickness. Reservoir intervals rarely exhibit uniform lithology and are often interbedded with impermeable shale layers.\n\n"
            "φ (Phi) - Reservoir Porosity - estimated from well logs, core measurements, and analogue reservoir data. It is defined as:\n\n"
            "ϕ=PoreVolume(Vv)/BulkReservoirVolume(V)\n\n"
            "Shc (Hydrocarbon Saturation) - determined from the water saturation (Sw). It is generally calculated from well log data within the effective porosity interval.\n\n"
            "Shc=1-Sw\n\n"
            "FVF (Formation Volume Factor) - expresses the change in fluid volume between reservoir conditions and standard surface conditions (pressure = 1 atmosphere and temperature = 15°C). For oil, the formation volume factor is represented by Bo, while for gas it is represented by Bg.\n\n"
            "FVF=ReservoirVolume/SurfaceVolume\n\n"
            "**Oil Volumes**\n\n"
            "For oil:\n\n"
            "FVF=Bo\n\n"
            "Shc=So\n\n"
            "where So is the oil saturation.\n\n"
            "Therefore:\n\n"
            "STOIIP=GRV×N/G×ϕ×So×1/Bo\n\n"
            "The volume of associated gas in place is calculated as:\n\n"
            "AssociatedGasInPlace=STOIIP×GOR\n\n"
            "**Gas Volumes**\n\n"
            "For gas:\n\n"
            "FVF=Bg\n\n"
            "Shc=Sg\n\n"
            "where Sg is the gas saturation.\n\n"
            "Therefore:\n\n"
            "GIIP=GRV×N/G×ϕ×Sg×1/Bg\n\n"
            "The volume of condensate in place is calculated as:\n\n"
            "CondensateInPlace=GIIP×CGR\n\n"
            "Where:\n\n"
            "GOR (Gas-Oil Ratio) - the ratio of produced gas volume to produced oil volume.\n\n"
            "CGR (Condensate-Gas Ratio) - the ratio of produced condensate volume to produced gas volume."
        ),
        volumetric_block,
        context="chapter 6 volumetric formulas",
    )
    gcos_primary_block = _extract_required_formula_snippet(
        file_name,
        r'<div class="book-formula" data-equation-label="6\.2"[\s\S]*?</div>',
        context="chapter 6 GCoS primary formula",
    )
    gcos_examples_block = _extract_required_formula_snippet(
        file_name,
        r'<div class="book-formula" data-equation-label="6\.3" role="img" aria-label="GCoS equals 0\.90 times 0\.80 times 0\.85 times 0\.90 and equals 0\.55 or 55 percent">[\s\S]*?</div>',
        context="chapter 6 GCoS example formulas",
    )
    markdown = _replace_if_present(
        markdown,
        "**GCoS = Ps × Pr × Pse × Pt**",
        gcos_primary_block,
    )
    markdown = _replace_if_present(
        markdown,
        "GCoS = Ps × Pr × Pse × Pt",
        gcos_primary_block,
    )
    markdown = _replace_if_present(
        markdown,
        "GCoS = 0.90 × 0.80 × 0.85 × 0.90\n\n= 0.55 (55%)",
        gcos_examples_block,
    )
    return markdown


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
    cleaned = re.sub(
        r"<(p|ul|ol|li)\b[^>]*>",
        lambda match: f"<{match.group(1)}>",
        cleaned,
        flags=re.IGNORECASE,
    )
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
    if row_index == 0 and all(
        _cell_looks_like_first_row_header(cell) for cell in meaningful_cells
    ):
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


def _table_html_map(docx_path: Path) -> dict[int, list[tuple[str, list[str]]]]:
    with tempfile.TemporaryDirectory(prefix="en-reference-html-") as temp_dir:
        html_export = Path(temp_dir) / "reference.html"
        subprocess.run(
            ["textutil", "-convert", "html", "-output", str(html_export), str(docx_path)],
            cwd=ROOT_DIR,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        html_lines = html_export.read_text(encoding="utf-8").splitlines()

    table_map: dict[int, list[tuple[str, list[str]]]] = {}
    index = 0
    while index < len(html_lines):
        line = html_lines[index]
        match = re.search(r"Table\s+(\d+)\b", _clean_line(line))
        if not match:
            index += 1
            continue

        caption_text = html.unescape(_clean_line(TABLE_TAG_RE.sub(" ", line)))
        if "Apple-tab-span" in line:
            caption_text = re.sub(r"\s+\d+\s*$", "", caption_text)
        caption_match = TABLE_RE.match(caption_text)
        if caption_match is None:
            index += 1
            continue
        caption_body = caption_match.group("text").lstrip()
        if caption_body and caption_body[0].isalpha() and caption_body[0].islower():
            index += 1
            continue

        table_number = int(match.group(1))
        next_index = index + 1
        while next_index < len(html_lines) and "<table" not in html_lines[next_index].lower():
            next_index += 1
        if next_index >= len(html_lines):
            index += 1
            continue
        if next_index - index > 12:
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

        table_map.setdefault(table_number, []).append(
            (
                caption_text,
                _semanticize_table_html(
                    caption_text,
                    _strip_table_caption_lines(table_lines),
                ),
            )
        )
        index = next_index + 1

    return table_map


def build_rendered_outputs(
    docx_path: Path,
    summary_path: Path,
    chapters_dir: Path,
) -> list[tuple[Path, str]]:
    markdown_book = extract_markdown_book(summary_path, chapters_dir)
    expected_markdown_chapters = [
        chapter
        for chapter in markdown_book.chapters
        if _include_docx_title(Path(chapter.source_path))
    ]

    docx_book = extract_docx_book(
        docx_path,
        expected_titles=[_docx_expected_title(chapter.title) for chapter in expected_markdown_chapters],
    )
    if len(docx_book.chapters) != len(expected_markdown_chapters):
        raise SystemExit(
            f"Expected {len(expected_markdown_chapters)} DOCX sections, got {len(docx_book.chapters)}."
        )

    figure_image_map = _figure_image_map(docx_path, summary_path, chapters_dir)
    table_html_map = _table_html_map(docx_path)
    rendered_outputs: list[tuple[Path, str]] = []
    for docx_chapter, markdown_chapter in zip(docx_book.chapters, expected_markdown_chapters):
        rendered_markdown = render_markdown_chapter(
            type(docx_chapter)(
                source_path=docx_chapter.source_path,
                title=markdown_chapter.title,
                outline=docx_chapter.outline,
                body=docx_chapter.body,
                outline_body_indices=docx_chapter.outline_body_indices,
            ),
            figure_image_map=figure_image_map,
            table_html_map=table_html_map,
        )
        rendered_outputs.append(
            (
                Path(markdown_chapter.source_path),
                _restore_english_formula_semantics(
                    Path(markdown_chapter.source_path).name,
                    rendered_markdown,
                ),
            )
        )

    return rendered_outputs


def main() -> int:
    args = parse_args()
    edition = get_edition(args.edition)
    docx_path = Path(args.docx) if args.docx else edition.docx_path
    summary_path = Path(args.summary) if args.summary else edition.summary_path
    chapters_dir = Path(args.chapters_dir) if args.chapters_dir else edition.chapter_root

    rendered_outputs = build_rendered_outputs(docx_path, summary_path, chapters_dir)

    if not args.write:
        for output_path, markdown in rendered_outputs:
            print(f"{output_path.name}: {len(markdown.splitlines())} lines")
        return 0

    for output_path, markdown in rendered_outputs:
        output_path.write_text(markdown, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
