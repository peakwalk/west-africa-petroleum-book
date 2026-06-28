import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, "../..");
const REGISTRY_PATH = path.join(ROOT, "config", "editions.json");

const registry = JSON.parse(readFileSync(REGISTRY_PATH, "utf8"));

function deriveEditionPaths(editionRoot) {
  return {
    bookConfigPath: path.join(editionRoot, "book.toml"),
    bookSeoConfigPath: path.join(editionRoot, "site", "book-seo.json"),
    siteRoot: path.join(editionRoot, "site"),
    landingMainPath: path.join(editionRoot, "site", "index-main.html"),
    legalRoot: path.join(editionRoot, "site", "legal"),
    localeCatalog: path.join(editionRoot, "locale.json"),
    sourceRoot: path.join(editionRoot, "content"),
    summaryPath: path.join(editionRoot, "content", "SUMMARY.md"),
    chapterRoot: path.join(editionRoot, "content", "chapters"),
    figureRoot: path.join(editionRoot, "content", "images"),
    figureManifestPath: path.join(editionRoot, "content", "images", "figure-manifest.json"),
  };
}

const editions = registry.editions.map((edition) => {
  const derivedPaths = deriveEditionPaths(edition.editionRoot);
  const catalogPath = path.join(ROOT, derivedPaths.localeCatalog);
  const localeStrings = JSON.parse(readFileSync(catalogPath, "utf8"));
  return {
    ...edition,
    ...derivedPaths,
    bookRoot: edition.editionRoot,
    localeStrings,
    outputRoot: edition.routePrefix ? path.join(ROOT, edition.routePrefix) : ROOT,
  };
});

export function listSiteEditions() {
  return editions.map((edition) => ({ ...edition }));
}

export function getSiteEdition(locale) {
  return editions.find((edition) => edition.locale === locale) || null;
}

export function getPeerSiteEdition(locale) {
  return editions.find((edition) => edition.locale !== locale) || null;
}

export function resolveEditionPath(edition, relativePath = "", outputRoot = ROOT) {
  const resolvedOutputRoot = path.resolve(outputRoot);
  const editionOutputRoot = edition.routePrefix
    ? path.join(resolvedOutputRoot, edition.routePrefix)
    : resolvedOutputRoot;
  return path.join(editionOutputRoot, relativePath);
}
