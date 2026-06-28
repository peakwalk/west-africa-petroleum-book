import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { isRedirectOnlyBookPageKey } from "./shared/book-page-maps.mjs";
import {
  buildBookCanonicalUrl,
  buildBookSeoRecords,
  escapeHtml,
  listBuiltBookPageKeys,
} from "./shared/book-seo.mjs";
import { getSiteEdition } from "./shared/site-editions.mjs";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(scriptDir, "..");

const requestedBookDir = process.argv[2] || path.join("public", "book");
const locale = process.argv[3] || "en";

const bookDir = path.resolve(rootDir, requestedBookDir);
const edition = getSiteEdition(locale);
const MANAGED_SEO_BLOCK_START = "<!-- upstream-atlas-book-seo:start -->";
const MANAGED_SEO_BLOCK_END = "<!-- upstream-atlas-book-seo:end -->";
const REDIRECT_PAGE_COPY = {
  en: {
    title: "Redirecting to book",
    body: "This page has moved to the book home page.",
    cta: "Open the book home page",
  },
  fr: {
    title: "Redirection vers le livre",
    body: "Cette page a été déplacée vers la page d'accueil du livre.",
    cta: "Ouvrir la page d'accueil du livre",
  },
};

function replaceTitle(html, title) {
  return html.replace(/<title>[\s\S]*?<\/title>/i, `<title>${escapeHtml(title)}</title>`);
}

function replaceMetaDescription(html, description) {
  if (/<meta name="description" content="[^"]*">/i.test(html)) {
    return html.replace(
      /<meta name="description" content="[^"]*">/i,
      `<meta name="description" content="${escapeHtml(description)}">`
    );
  }

  return html.replace(
    /<meta name="viewport" content="width=device-width, initial-scale=1">/i,
    `<meta name="description" content="${escapeHtml(description)}">\n        <meta name="viewport" content="width=device-width, initial-scale=1">`
  );
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function stripManagedSeoBlock(html) {
  const managedBlockPattern = new RegExp(
    `\\s*${escapeRegExp(MANAGED_SEO_BLOCK_START)}[\\s\\S]*?${escapeRegExp(MANAGED_SEO_BLOCK_END)}\\n?`,
    "i"
  );
  return html.replace(managedBlockPattern, "");
}

function wrapManagedSeoMarkup(markup) {
  return `        ${MANAGED_SEO_BLOCK_START}\n${markup}\n        ${MANAGED_SEO_BLOCK_END}`;
}

function buildSeoMarkup(record) {
  const linkMarkup = [
    `<link rel="canonical" href="${escapeHtml(record.canonicalUrl)}">`,
    ...record.alternates.map(
      (alternate) =>
        `<link rel="alternate" hreflang="${escapeHtml(alternate.hreflang)}" href="${escapeHtml(
          alternate.href
        )}">`
    ),
  ].join("\n        ");

  const structuredDataMarkup = record.structuredData
    .map(
      (block) =>
        `<script type="application/ld+json">\n${JSON.stringify(block, null, 2)}\n        </script>`
    )
    .join("\n        ");

  return `        ${linkMarkup}\n        ${structuredDataMarkup}`;
}

function injectSeoMarkup(html, record) {
  const withoutManagedSeoBlock = stripManagedSeoBlock(html)
    .replace(/\s*<link rel="canonical"[^>]*>\n?/gi, "")
    .replace(/\s*<link rel="alternate" hreflang="[^"]+"[^>]*>\n?/gi, "");

  return withoutManagedSeoBlock.replace(
    /<\/head>/i,
    `${wrapManagedSeoMarkup(buildSeoMarkup(record))}\n    </head>`
  );
}

function buildRedirectOnlySeoMarkup(canonicalUrl) {
  return [
    `        <meta name="robots" content="noindex,follow">`,
    `        <link rel="canonical" href="${escapeHtml(canonicalUrl)}">`,
  ].join("\n");
}

function resolveRedirectOnlyCanonicalUrl() {
  return buildBookCanonicalUrl(edition, "index.html");
}

function resolveBookRootHref(pageKey) {
  const pageDir = path.posix.dirname(pageKey);
  const relativeDir = path.posix.relative(pageDir, ".");
  return relativeDir ? `${relativeDir}/` : "./";
}

function resolveRedirectOnlyTargetPath(pageKey) {
  return resolveBookRootHref(pageKey);
}

function buildRedirectOnlyPageHtml(pageKey, canonicalUrl) {
  const copy = REDIRECT_PAGE_COPY[edition.locale] || REDIRECT_PAGE_COPY.en;
  const targetPath = resolveRedirectOnlyTargetPath(pageKey);

  return `<!doctype html>
<html lang="${escapeHtml(edition.locale)}">
  <head>
    <meta charset="utf-8">
    <title>${escapeHtml(copy.title)}</title>
    <meta http-equiv="refresh" content="0; url=${escapeHtml(targetPath)}">
    <script>
      const target = ${JSON.stringify(targetPath)} + window.location.search + window.location.hash;
      window.location.replace(target);
    </script>
${wrapManagedSeoMarkup(buildRedirectOnlySeoMarkup(canonicalUrl))}
  </head>
  <body>
    <p>${escapeHtml(copy.body)} <a href="${escapeHtml(targetPath)}">${escapeHtml(copy.cta)}</a>.</p>
  </body>
</html>
`;
}

function normalizeCoverAliasHref(pageKey, href) {
  if (pageKey.startsWith("chapters/")) {
    if (
      href === "cover.html" ||
      href === "../chapters/cover.html" ||
      href === "chapters/cover.html"
    ) {
      return resolveBookRootHref(pageKey);
    }

    return href;
  }

  if (href === "chapters/cover.html" || href === "cover.html") {
    return resolveBookRootHref(pageKey);
  }

  return href;
}

function normalizeCoverAliasLinks(html, pageKey) {
  return html.replace(/href="([^"]+)"/g, (match, href) => {
    const normalizedHref = normalizeCoverAliasHref(pageKey, href);
    return normalizedHref === href ? match : `href="${normalizedHref}"`;
  });
}

function main() {
  if (!edition) {
    throw new Error(`Unknown site edition for locale "${locale}"`);
  }

  const records = buildBookSeoRecords({ bookDir, edition, rootDir });

  for (const pageKey of listBuiltBookPageKeys(bookDir)) {
    const filePath = path.join(bookDir, ...pageKey.split("/"));
    let html = fs.readFileSync(filePath, "utf8");

    if (isRedirectOnlyBookPageKey(pageKey)) {
      html = buildRedirectOnlyPageHtml(pageKey, resolveRedirectOnlyCanonicalUrl());
    } else {
      const record = records.get(pageKey);
      if (!record) {
        throw new Error(`Missing SEO record for ${pageKey}`);
      }

      html = normalizeCoverAliasLinks(html, pageKey);
      html = replaceTitle(html, record.title);
      html = replaceMetaDescription(html, record.description);
      html = injectSeoMarkup(html, record);
    }

    fs.writeFileSync(filePath, html);
  }
}

main();
