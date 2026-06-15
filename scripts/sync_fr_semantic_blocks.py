from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.docx_parity import extract_docx_book

SRC_FR_DIR = ROOT_DIR / "src-fr" / "chapters"
FR_DOCX = ROOT_DIR / "resources" / "editions" / "fr" / "reference.docx"

LIST_ITEM_RE = re.compile(r"^(?P<indent>\s*)(?:[-*+]|\d+[.)])\s+(?P<text>.+)$")
HEADING_RE = re.compile(r"^(?P<hashes>#{2,6})\s+.+$")
HTML_BLOCK_OPEN_RE = re.compile(r"^<(?P<tag>table|section|div)\b", re.IGNORECASE)


CHAPTER_FILES = [
    "chapter-01-value-chain-of-the-hydrocarbon-sector.md",
    "chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md",
    "chapter-03-tax-regimes-in-the-petroleum-sector.md",
    "chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md",
    "chapter-05-key-socio-political-determinants-of-oil-sector-performance.md",
    "chapter-06-west-africa-in-depth-country-analysis.md",
]


SOURCE_TITLES = {
    "chapter-01-value-chain-of-the-hydrocarbon-sector.md": "Chapitre 1 : Chaîne des valeurs du secteur des hydrocarbures",
    "chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md": "Chapitre 2 : Différentes phases de l’amont pétrolier et rôles des États",
    "chapter-03-tax-regimes-in-the-petroleum-sector.md": "Chapitre 3 : Régimes fiscaux dans le secteur pétrolier",
    "chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md": "Chapitre 4 : Étude comparée des régimes fiscaux dans certains pays de l’Afrique de l’Ouest",
    "chapter-05-key-socio-political-determinants-of-oil-sector-performance.md": "Chapitre 5 : Principaux déterminants socio-politiques de la performance du secteur pétrolier",
    "chapter-06-west-africa-in-depth-country-analysis.md": "Chapitre 6 : Afrique de l’Ouest : analyses approfondies par pays",
}


DOC_TITLES = {
    "chapter-01-value-chain-of-the-hydrocarbon-sector.md": "CHAINE DES VALEURS DU SECTEUR DES HYDROCARBURES",
    "chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md": "DIFFERENTES PHASES DE L’AMONT PETROLIER ET ROLES DES ETATS",
    "chapter-03-tax-regimes-in-the-petroleum-sector.md": "REGIMES FISCAUX DANS LE SECTEUR PETROLIER",
    "chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md": "ETUDE COMPAREE DES REGIMES FISCAUX DANS CERTAINS PAYS DE L’AFRIQUE DE L’OUEST :",
    "chapter-05-key-socio-political-determinants-of-oil-sector-performance.md": "PRINCIPAUX DETERMINANTS SOCIO-POLITIQUES DE LA PERFORMANCE DU SECTEUR PETROLIER",
    "chapter-06-west-africa-in-depth-country-analysis.md": "AFRIQUE DE L'OUEST : ANALYSES APPROFONDIES PAR PAYS",
}


KNOWN_HEADING_FIXUPS = {
    "chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md": {
        "4.2- Key tax elements applied in selected West African countries": "4.2- Principaux éléments fiscaux appliqués dans certains pays de l’Afrique de l’Ouest",
        "4.2.2 - Recoverable Petroleum Costs": "4.2.2 - Coûts pétroliers récupérables",
        "4.2.3- Oil Profit": "4.2.3- Pétrole profit",
        "4.2.4- Profit/corporate tax": "4.2.4- Impôt sur le bénéfice et les sociétés",
        "4.2.5-State participation": "4.2.5- Participation de l’État",
        "4.3- In-depth analysis of tax regimes by country": "4.3- Analyse approfondie des régimes fiscaux par pays",
        "4.3.6- Other West African countries": "4.3.6- Autres pays d’Afrique de l’Ouest",
        "4.4- State/Contractor income associated with the tax system in selected West African countries": "4.4- Revenus État-contractant associés au système fiscal dans certains pays de l’Afrique de l’Ouest",
        "4.5- Analysis and interpretations": "4.5- Analyses et interprétations",
        "4.5.1- On the net income of States/contractors and attractiveness to foreign investment": "4.5.1- Sur les revenus nets des États et contractants et l’attractivité pour l’investissement étranger",
        "4.5.2- On the overall State/Contracting Party cash flows": "4.5.2- Sur les cash-flow globaux de l’État et du contractant",
        "4.6- Some suggestions for maximizing the oil revenues of the States": "4.6- Quelques suggestions pour maximiser les revenus pétroliers des États",
        "4.7- Partial conclusion": "4.7- Conclusion partielle",
    },
    "chapter-05-key-socio-political-determinants-of-oil-sector-performance.md": {
        "5.1-Political stability and its impact on the oil sector": "5.1- Stabilité politique et son impact sur le secteur pétrolier",
        "5.2- Governance Structures in the Petroleum Sector": "5.2- Structures de gouvernance dans le secteur pétrolier",
        "5.3- Corruption in the oil sector": "5.3- Corruption dans le secteur pétrolier",
        "5.4- Interrelationship between stability, governance and corruption": "5.4- Interrelations entre stabilité, gouvernance et corruption",
        "5.5- Stakeholder Risk Mitigation Strategies": "5.5- Stratégies d’atténuation des risques par les parties prenantes",
        "5.5.1- Roles of operators": "5.5.1- Rôles des opérateurs",
        "5.5.2 - Responsibilities of States": "5.5.2 - Responsabilités des États",
        "5.5.3- Roles of international institutions": "5.5.3- Rôles des institutions internationales",
        "5.6-Future trends and emerging risks": "5.6- Tendances futures et risques émergents",
    },
    "chapter-06-west-africa-in-depth-country-analysis.md": {
        "6.7- Other West African countries": "6.7- Autres pays d’Afrique de l’Ouest",
        "6.7.1- Mauritania": "6.7.1- Mauritanie",
        "6.7.2- Sierra Leone": "6.7.2- Sierra Leone",
        "6.7.3- Liberia": "6.7.3- Liberia",
        "6.7.4- Guinea and Guinea-Bissau": "6.7.4- Guinée et Guinée-Bissau",
        "6.7.5- The Gambia": "6.7.5- Gambie",
        "6.8- Regional synthesis": "6.8- Synthèse régionale",
    },
}


@dataclass
class BlockSpan:
    kind: str
    start: int
    end: int
    level: int | None = None
    indent: str = ""


def _is_html_only(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("<") and stripped.endswith(">")


def _formula_like_text(text: str) -> bool:
    normalized = re.sub(r"\s+", " ", text).strip()
    return any(
        marker in normalized
        for marker in (
            "=",
            "Facteur-R",
            "R-Factor",
            "Revenu Post Royalty",
            "Pétrole profit",
            "Oil Profit",
        )
    )


def _collect_html_block(lines: list[str], start_index: int) -> tuple[int, str]:
    match = HTML_BLOCK_OPEN_RE.match(lines[start_index].strip())
    if not match:
        return start_index, "html"

    tag = match.group("tag").lower()
    depth = 0
    block_lines: list[str] = []
    index = start_index

    while index < len(lines):
        stripped = lines[index].strip()
        lowered = stripped.lower()
        block_lines.append(stripped)
        if lowered.startswith(f"<{tag}"):
            depth += lowered.count(f"<{tag}")
        if f"</{tag}>" in lowered:
            depth -= lowered.count(f"</{tag}>")
            if depth <= 0:
                break
        index += 1

    block_text = " ".join(block_lines).lower()
    if tag == "table":
        return index, "html_table"
    if "formula" in block_text:
        return index, "html_formula"
    return index, "html"


def _collect_block_spans(lines: list[str]) -> tuple[int | None, list[BlockSpan], list[BlockSpan]]:
    title_index: int | None = None
    heading_spans: list[BlockSpan] = []
    body_spans: list[BlockSpan] = []
    index = 0

    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped:
            index += 1
            continue
        if stripped.startswith("# "):
            title_index = index
            index += 1
            continue
        heading_match = HEADING_RE.match(stripped)
        if heading_match:
            heading_spans.append(
                BlockSpan(
                    kind="heading",
                    start=index,
                    end=index,
                    level=len(heading_match.group("hashes")),
                )
            )
            index += 1
            continue
        if stripped.startswith("![") or stripped.startswith("<!--"):
            index += 1
            continue
        html_block_match = HTML_BLOCK_OPEN_RE.match(stripped)
        if html_block_match:
            html_end, html_kind = _collect_html_block(lines, index)
            body_spans.append(BlockSpan(kind=html_kind, start=index, end=html_end))
            index = html_end + 1
            continue
        if _is_html_only(lines[index]):
            index += 1
            continue
        list_match = LIST_ITEM_RE.match(lines[index])
        if list_match:
            start = index
            indent = list_match.group("indent")
            index += 1
            while index < len(lines):
                candidate = lines[index]
                candidate_stripped = candidate.strip()
                if (
                    not candidate_stripped
                    or HEADING_RE.match(candidate_stripped)
                    or candidate_stripped.startswith(("# ", "![", "<!--"))
                    or _is_html_only(candidate)
                    or LIST_ITEM_RE.match(candidate)
                ):
                    break
                index += 1
            body_spans.append(BlockSpan(kind="list_item", start=start, end=index - 1, indent=indent))
            continue
        kind = "caption" if stripped.startswith(("Figure ", "Table ")) else "paragraph"
        start = index
        index += 1
        while index < len(lines):
            candidate = lines[index]
            candidate_stripped = candidate.strip()
            if (
                not candidate_stripped
                or HEADING_RE.match(candidate_stripped)
                or candidate_stripped.startswith(("# ", "![", "<!--"))
                or _is_html_only(candidate)
                or LIST_ITEM_RE.match(candidate)
            ):
                break
            index += 1
        body_spans.append(BlockSpan(kind=kind, start=start, end=index - 1))

    return title_index, heading_spans, body_spans


def _format_heading(level: int, number: str, title: str, file_name: str) -> str:
    text = f"{number} {title}".strip()
    replacements = KNOWN_HEADING_FIXUPS.get(file_name, {})
    text = replacements.get(text, text)
    return f"{'#' * level} {text}"


def _replace_semantic_blocks(file_name: str, doc_chapter, remove_unmatched: bool = False) -> None:
    chapter_path = SRC_FR_DIR / file_name
    lines = chapter_path.read_text(encoding="utf-8").splitlines()
    title_index, heading_spans, body_spans = _collect_block_spans(lines)

    replacements: list[tuple[int, int, list[str]]] = []
    if title_index is not None:
        replacements.append((title_index, title_index, [f"# {SOURCE_TITLES[file_name]}"]))

    for span, outline in zip(heading_spans, doc_chapter.outline):
        replacements.append(
            (
                span.start,
                span.end,
                [_format_heading(span.level or outline.level, outline.number, outline.title, file_name)],
            )
        )

    if remove_unmatched and len(heading_spans) > len(doc_chapter.outline):
        for span in heading_spans[len(doc_chapter.outline) :]:
            replacements.append((span.start, span.end, []))

    doc_body_index = 0
    for span in body_spans:
        if span.kind == "html_formula":
            while doc_body_index < len(doc_chapter.body) and _formula_like_text(
                doc_chapter.body[doc_body_index].text
            ):
                doc_body_index += 1
            continue
        if span.kind.startswith("html_"):
            continue
        while doc_body_index < len(doc_chapter.body) and doc_chapter.body[doc_body_index].kind != span.kind:
            doc_body_index += 1
        if doc_body_index >= len(doc_chapter.body):
            if remove_unmatched:
                replacements.append((span.start, span.end, []))
            continue
        block = doc_chapter.body[doc_body_index]
        doc_body_index += 1
        if span.kind == "list_item":
            replacements.append((span.start, span.end, [f"{span.indent}- {block.text}"]))
        else:
            replacements.append((span.start, span.end, [block.text]))

    if remove_unmatched:
        for span in body_spans:
            if span.kind.startswith("html_"):
                continue
            if span.start < len(lines) and all(
                not (span.start == start and span.end == end) for start, end, _ in replacements
            ):
                replacements.append((span.start, span.end, []))

    for start, end, new_lines in sorted(replacements, key=lambda item: item[0], reverse=True):
        lines[start : end + 1] = new_lines

    chapter_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    doc_book = extract_docx_book(FR_DOCX)
    doc_chapters = {chapter.title: chapter for chapter in doc_book.chapters}

    planned = []
    for file_name in CHAPTER_FILES:
        doc_title = DOC_TITLES[file_name]
        doc_chapter = doc_chapters.get(doc_title)
        if doc_chapter is None:
            raise SystemExit(f"Missing DOCX chapter for {file_name}: {doc_title}")
        planned.append((file_name, doc_chapter))

    if not args.write:
        for file_name, doc_chapter in planned:
            print(file_name, len(doc_chapter.outline), len(doc_chapter.body))
        return 0

    for file_name, doc_chapter in planned:
        _replace_semantic_blocks(
            file_name,
            doc_chapter,
            remove_unmatched=True,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
