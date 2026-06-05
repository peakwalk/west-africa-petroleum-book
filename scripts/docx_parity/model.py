from dataclasses import dataclass, field


@dataclass(frozen=True)
class OutlineEntry:
    level: int
    number: str
    title: str


@dataclass(frozen=True)
class BodyBlock:
    kind: str
    text: str


@dataclass(frozen=True)
class ChapterSemanticModel:
    source_path: str
    title: str
    outline: list[OutlineEntry] = field(default_factory=list)
    body: list[BodyBlock] = field(default_factory=list)


@dataclass(frozen=True)
class BookSemanticModel:
    chapters: list[ChapterSemanticModel] = field(default_factory=list)


@dataclass(frozen=True)
class ParityDiff:
    chapter_path: str
    diff_type: str
    docx_value: str
    markdown_value: str
    hint: str
