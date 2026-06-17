from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT_DIR / "config" / "editions.json"


@dataclass(frozen=True)
class EditionConfig:
    locale: str
    edition_root: Path
    book_root: Path
    book_config_path: Path
    route_prefix: str
    site_root: Path
    landing_main_path: Path
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


def _derive_edition_paths(edition_root: Path) -> dict[str, Path]:
    return {
        "book_config_path": edition_root / "book.toml",
        "site_root": edition_root / "site",
        "landing_main_path": edition_root / "site" / "index-main.html",
        "legal_root": edition_root / "site" / "legal",
        "locale_catalog_path": edition_root / "locale.json",
        "source_root": edition_root / "content",
        "summary_path": edition_root / "content" / "SUMMARY.md",
        "chapter_root": edition_root / "content" / "chapters",
        "figure_root": edition_root / "content" / "images",
        "figure_manifest_path": edition_root / "content" / "images" / "figure-manifest.json",
    }


def load_edition_registry() -> dict[str, EditionConfig]:
    payload = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    editions: dict[str, EditionConfig] = {}

    for item in payload["editions"]:
        edition_root = ROOT_DIR / item["editionRoot"]
        derived_paths = _derive_edition_paths(edition_root)
        editions[item["locale"]] = EditionConfig(
            locale=item["locale"],
            edition_root=edition_root,
            book_root=edition_root,
            book_config_path=derived_paths["book_config_path"],
            route_prefix=item["routePrefix"],
            site_root=derived_paths["site_root"],
            landing_main_path=derived_paths["landing_main_path"],
            source_root=derived_paths["source_root"],
            summary_path=derived_paths["summary_path"],
            chapter_root=derived_paths["chapter_root"],
            legal_root=derived_paths["legal_root"],
            figure_root=derived_paths["figure_root"],
            figure_manifest_path=derived_paths["figure_manifest_path"],
            docx_path=ROOT_DIR / item["manuscripts"]["docx"],
            pdf_path=_resolve_optional_path(item["manuscripts"].get("pdf")),
            locale_catalog_path=derived_paths["locale_catalog_path"],
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
