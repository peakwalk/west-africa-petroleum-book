import re

INLINE_MARKUP_RE = re.compile(r"[*_`]+")
MARKDOWN_ESCAPE_RE = re.compile(r"\\([\\`*_{}\[\]()#+\-.!|$<>])")
WHITESPACE_RE = re.compile(r"\s+")
HEADING_NUMBER_RE = re.compile(
    r"^(?P<number>\d+(?:\.\d+)*(?:\s*-\s*|[.-]))(?P<title>.+)$"
)
LATEX_DEGREE_RE = re.compile(r"\{?\^\\circ\}?")
LATEX_WRAPPER_RE = re.compile(r"\\(?:mathbf|text|mathrm)\{([^{}]*)\}")
LATEX_FRACTION_RE = re.compile(r"\\frac\{([^{}]*)\}\{([^{}]*)\}")
DOUBLE_BRACE_RE = re.compile(r"\{\{([^{}]*)\}\}")


def normalize_visible_text(value: str) -> str:
    unescaped = MARKDOWN_ESCAPE_RE.sub(r"\1", value)
    stripped = INLINE_MARKUP_RE.sub("", unescaped)
    collapsed = WHITESPACE_RE.sub(" ", stripped.replace("\u00a0", " "))
    return collapsed.strip()


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
