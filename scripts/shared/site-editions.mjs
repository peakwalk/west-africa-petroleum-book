import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, "../..");
const REGISTRY_PATH = path.join(ROOT, "config", "editions.json");

const registry = JSON.parse(readFileSync(REGISTRY_PATH, "utf8"));

const editions = registry.editions.map((edition) => {
  const catalogPath = path.join(ROOT, edition.localeCatalog);
  const localeStrings = JSON.parse(readFileSync(catalogPath, "utf8"));
  return {
    ...edition,
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

export function resolveEditionPath(edition, relativePath = "") {
  return path.join(edition.outputRoot, relativePath);
}
