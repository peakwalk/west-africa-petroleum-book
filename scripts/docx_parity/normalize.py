import re

INLINE_MARKUP_RE = re.compile(r"[*_`]+")
LEADING_SUP_MARKER_RE = re.compile(
    r"^\s*(?:<[^>]+>\s*)*<sup>\s*\d+\s*</sup>\s*",
    re.IGNORECASE,
)
HTML_TAG_RE = re.compile(r"<[^>]+>")
MARKDOWN_ESCAPE_RE = re.compile(r"\\([\\`*_{}\[\]()#+\-.!|$<>])")
WHITESPACE_RE = re.compile(r"\s+")
HEADING_NUMBER_RE = re.compile(
    r"^(?P<number>\d+(?:\.\d+)*(?:\s*-\s*|[.-]))(?P<title>.+)$"
)
LATEX_DEGREE_RE = re.compile(r"\{?\^\\circ\}?")
LATEX_WRAPPER_RE = re.compile(r"\\(?:mathbf|text|mathrm)\{([^{}]*)\}")
LATEX_FRACTION_RE = re.compile(r"\\frac\{([^{}]*)\}\{([^{}]*)\}")
DOUBLE_BRACE_RE = re.compile(r"\{\{([^{}]*)\}\}")
CAPTION_PREFIXES = ("Figure ", "Table ", "Tableau ")
FIGURE_REFERENCE_SENTENCE_RE = re.compile(
    r"^Figures?\s+\d+"
    r"(?:(?:\s*,\s*|\s+and\s+|\s+to\s+|\s*-\s*)(?:Figures?\s+)?\d+)*"
    r"\s+(?:show|shows|illustrate|illustrates|present|presents|depict|depicts|contain|contains)\b",
    re.IGNORECASE,
)


def normalize_visible_text(value: str) -> str:
    unescaped = MARKDOWN_ESCAPE_RE.sub(r"\1", value)
    unescaped = LEADING_SUP_MARKER_RE.sub("", unescaped)
    unescaped = HTML_TAG_RE.sub(" ", unescaped)
    unescaped = unescaped.replace("−", "-").replace("–", "-")
    stripped = INLINE_MARKUP_RE.sub("", unescaped)
    collapsed = WHITESPACE_RE.sub(" ", stripped.replace("\u00a0", " "))
    return collapsed.strip()


def is_narrative_figure_reference(value: str) -> bool:
    return FIGURE_REFERENCE_SENTENCE_RE.match(normalize_visible_text(value)) is not None


def is_caption_text(value: str) -> bool:
    normalized = normalize_visible_text(value)
    if not normalized.startswith(CAPTION_PREFIXES):
        return False
    return not is_narrative_figure_reference(normalized)


def normalize_heading_number(value: str) -> str:
    compact = normalize_visible_text(value)
    compact = re.sub(r"\s*-\s*$", "-", compact)
    compact = compact.replace(" -", "-").replace(". ", ".")
    return compact.strip()


def normalize_formula_text(value: str) -> str:
    compact = value.strip()
    compact = compact.replace("\\mathbf", "").replace("\\text", "").replace("\\mathrm", "")
    compact = LATEX_DEGREE_RE.sub("°", compact)
    while True:
        updated = DOUBLE_BRACE_RE.sub(r"{\1}", compact)
        if updated == compact:
            break
        compact = updated
    while True:
        updated = LATEX_WRAPPER_RE.sub(r"\1", compact)
        updated = LATEX_FRACTION_RE.sub(r"\1/\2", updated)
        if updated == compact:
            break
        compact = updated
    compact = compact.replace("\\", "")
    compact = compact.replace("{", "").replace("}", "")
    compact = compact.replace("−", "-")
    compact = WHITESPACE_RE.sub("", compact.replace("\u00a0", " "))
    return compact.strip()


def split_heading_label(raw_heading: str) -> tuple[str, str]:
    normalized = normalize_visible_text(raw_heading)
    match = HEADING_NUMBER_RE.match(normalized)
    if not match:
        return "", normalized
    return normalize_heading_number(match.group("number")), match.group("title").strip()
