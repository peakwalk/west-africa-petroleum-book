from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT_DIR / "config" / "editions.json"


@dataclass(frozen=True)
class EditionConfig:
    locale: str
    book_root: Path
    route_prefix: str
    source_root: Path
    summary_path: Path
    chapter_root: Path
    legal_root: Path
    figure_root: Path
    figure_manifest_path: Path
    docx_path: Path
    pdf_path: Path | None
    locale_catalog_path: Path
    figure_text_replacement_map_path: Path | None = None


def _resolve_optional_path(relative_path: str | None) -> Path | None:
    if not relative_path:
        return None
    return ROOT_DIR / relative_path


def load_edition_registry() -> dict[str, EditionConfig]:
    payload = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    editions: dict[str, EditionConfig] = {}

    for item in payload["editions"]:
        editions[item["locale"]] = EditionConfig(
            locale=item["locale"],
            book_root=ROOT_DIR / item["bookRoot"],
            route_prefix=item["routePrefix"],
            source_root=ROOT_DIR / item["sourceRoot"],
            summary_path=ROOT_DIR / item["summaryPath"],
            chapter_root=ROOT_DIR / item["chapterRoot"],
            legal_root=ROOT_DIR / item["legalRoot"],
            figure_root=ROOT_DIR / item["figureRoot"],
            figure_manifest_path=ROOT_DIR / item["figureManifestPath"],
            docx_path=ROOT_DIR / item["manuscripts"]["docx"],
            pdf_path=_resolve_optional_path(item["manuscripts"].get("pdf")),
            locale_catalog_path=ROOT_DIR / item["localeCatalog"],
            figure_text_replacement_map_path=_resolve_optional_path(
                item.get("figureTextReplacementMapPath")
            ),
        )

    return editions


def available_edition_locales() -> tuple[str, ...]:
    return tuple(load_edition_registry().keys())


def get_edition(locale: str) -> EditionConfig:
    editions = load_edition_registry()
    try:
        return editions[locale]
    except KeyError as error:
        available = ", ".join(sorted(editions))
        raise KeyError(f"Unknown edition {locale!r}. Available editions: {available}") from error
