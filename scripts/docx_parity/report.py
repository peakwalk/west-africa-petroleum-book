import json

from .model import ParityDiff


def render_text_report(diffs: list[ParityDiff]) -> str:
    lines: list[str] = []
    for diff in diffs:
        lines.extend(
            [
                diff.chapter_path,
                f"  type: {diff.diff_type}",
                f"  docx:      {diff.docx_value}",
                f"  markdown:  {diff.markdown_value}",
                f"  hint: {diff.hint}",
            ]
        )
    return "\n".join(lines)


def render_json_report(diffs: list[ParityDiff]) -> str:
    return json.dumps([diff.__dict__ for diff in diffs], indent=2, ensure_ascii=False)
