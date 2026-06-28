import fs from "node:fs";
import path from "node:path";

import { getPeerSiteEdition } from "./site-editions.mjs";
import {
  isCanonicalBookPageKey,
  isRedirectOnlyBookPageKey,
  normalizeBookSeoPageKey,
  resolveBookSeoPeerPageKey,
} from "./book-page-maps.mjs";

export const SITE_ORIGIN = "https://upstreamatlas.com";
export const BOOK_TITLE_SUFFIX = "Upstream Atlas";

function collapseWhitespace(value) {
  return String(value || "").replace(/\s+/g, " ").trim();
}

function trimDescription(value, maxLength = 170) {
  const normalized = collapseWhitespace(value);
  if (normalized.length <= maxLength) {
    return normalized;
  }

  const candidate = normalized.slice(0, maxLength - 3);
  const boundary = Math.max(
    candidate.lastIndexOf("."),
    candidate.lastIndexOf(","),
    candidate.lastIndexOf(" ")
  );
  const clipped = boundary > 110 ? candidate.slice(0, boundary) : candidate;
  return `${clipped.trimEnd()}...`;
}

function chapterTitleSeparator(eyebrow) {
  return /^Chapitre\b/i.test(eyebrow) ? " : " : ": ";
}

function buildDisplayTitle(pageMetaEntry) {
  if (!pageMetaEntry) {
    return "";
  }

  const eyebrow = collapseWhitespace(pageMetaEntry.eyebrow);
  const title = collapseWhitespace(pageMetaEntry.title);

  if (eyebrow && title) {
    return `${eyebrow}${chapterTitleSeparator(eyebrow)}${title}`;
  }

  return title;
}

function slugForPageKey(pageKey) {
  return path.posix.basename(pageKey, ".html");
}

function metaKeyForPageKey(pageKey) {
  const normalizedPageKey = normalizeBookSeoPageKey(pageKey);
  if (normalizedPageKey === "index.html") {
    return "chapters/cover.html";
  }

  return normalizedPageKey;
}

function readReaderPageMeta(bookDir) {
  const readerPageMetaPath = path.join(bookDir, "reader-page-meta.json");
  return JSON.parse(fs.readFileSync(readerPageMetaPath, "utf8"));
}

function readEditionBookSeoConfig(edition, rootDir) {
  return JSON.parse(
    fs.readFileSync(path.join(rootDir, edition.bookSeoConfigPath), "utf8")
  );
}

export function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

export function listBuiltBookPageKeys(bookDir) {
  const pages = ["index.html"];
  const chaptersDir = path.join(bookDir, "chapters");

  fs.readdirSync(chaptersDir)
    .filter((entry) => entry.endsWith(".html"))
    .sort((left, right) => left.localeCompare(right))
    .forEach((entry) => {
      pages.push(path.posix.join("chapters", entry));
    });

  return pages;
}

export { isCanonicalBookPageKey };

export function buildBookCanonicalUrl(edition, pageKey) {
  const normalizedPageKey = normalizeBookSeoPageKey(pageKey);
  const baseUrl = edition.routePrefix
    ? `${SITE_ORIGIN}/${edition.routePrefix}/book/`
    : `${SITE_ORIGIN}/book/`;

  if (normalizedPageKey === "index.html") {
    return baseUrl;
  }

  return `${baseUrl}${normalizedPageKey}`;
}

function buildDefaultAlternateUrl(edition, pageKey) {
  const peerEdition = getPeerSiteEdition(edition.locale);
  const peerPageKey = resolveBookSeoPeerPageKey(edition.locale, pageKey);

  if (edition.locale === "fr" && peerEdition && peerPageKey) {
    return buildBookCanonicalUrl(peerEdition, peerPageKey);
  }

  return buildBookCanonicalUrl(edition, pageKey);
}

function isChapterPageKey(pageKey) {
  return /^chapters\/chapter-\d+/i.test(pageKey);
}

function classifyBookPage(edition, pageKey) {
  const normalizedPageKey = normalizeBookSeoPageKey(pageKey);

  if (normalizedPageKey === "index.html") {
    return "landing";
  }

  if (isChapterPageKey(normalizedPageKey)) {
    return "chapter";
  }

  const peerPageKey = resolveBookSeoPeerPageKey(edition.locale, normalizedPageKey);
  if (peerPageKey && isChapterPageKey(peerPageKey)) {
    return "chapter";
  }

  return "reference";
}

function bookBreadcrumbLabel(locale) {
  return locale === "fr" ? "Livre" : "Book";
}

function buildBreadcrumbList({ edition, canonicalUrl, title }) {
  const homeUrl = edition.routePrefix ? `${SITE_ORIGIN}/${edition.routePrefix}/` : `${SITE_ORIGIN}/`;
  const bookUrl = buildBookCanonicalUrl(edition, "index.html");

  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      {
        "@type": "ListItem",
        position: 1,
        name: "Upstream Atlas",
        item: homeUrl,
      },
      {
        "@type": "ListItem",
        position: 2,
        name: bookBreadcrumbLabel(edition.locale),
        item: bookUrl,
      },
      {
        "@type": "ListItem",
        position: 3,
        name: title,
        item: canonicalUrl,
      },
    ],
  };
}

function buildStructuredData({ edition, pageKey, title, description, canonicalUrl, seoConfig }) {
  const pageType = classifyBookPage(edition, pageKey);
  const landingSchema = seoConfig.landing || {};

  if (pageType === "landing") {
    return [
      {
        "@context": "https://schema.org",
        "@type": "Book",
        name: landingSchema.bookSchemaName || title,
        description: landingSchema.bookSchemaDescription || description,
        url: canonicalUrl,
        inLanguage: edition.locale,
        publisher: {
          "@type": "Organization",
          name: "Upstream Atlas",
          url: SITE_ORIGIN,
        },
      },
    ];
  }

  const primaryType = pageType === "chapter" ? "Chapter" : "WebPage";
  return [
    {
      "@context": "https://schema.org",
      "@type": primaryType,
      name: title,
      description,
      url: canonicalUrl,
      inLanguage: edition.locale,
      isPartOf: {
        "@type": "Book",
        name: landingSchema.bookSchemaName || seoConfig.landing.title,
        url: buildBookCanonicalUrl(edition, "index.html"),
      },
    },
    buildBreadcrumbList({ edition, canonicalUrl, title }),
  ];
}

function resolvePageOverride(seoConfig, pageKey) {
  const normalizedPageKey = normalizeBookSeoPageKey(pageKey);
  return (
    (seoConfig.pageOverrides && seoConfig.pageOverrides[pageKey]) ||
    (seoConfig.pageOverrides && seoConfig.pageOverrides[normalizedPageKey]) ||
    null
  );
}

function resolvePageDescription({ pageKey, pageMetaEntry, localeStrings, seoConfig }) {
  const normalizedPageKey = normalizeBookSeoPageKey(pageKey);
  const override = resolvePageOverride(seoConfig, pageKey);
  if (override && override.description) {
    return trimDescription(override.description);
  }

  if (normalizedPageKey === "index.html" && seoConfig.landing && seoConfig.landing.description) {
    return trimDescription(seoConfig.landing.description);
  }

  const genericDescriptions =
    (localeStrings.chaptersPage && localeStrings.chaptersPage.genericDescriptions) || {};
  const genericDescription = genericDescriptions[slugForPageKey(normalizedPageKey)];
  if (genericDescription) {
    return trimDescription(genericDescription);
  }

  if (pageMetaEntry && pageMetaEntry.lede) {
    return trimDescription(pageMetaEntry.lede);
  }

  return "";
}

function resolvePageTitle({ pageKey, pageMetaEntry, seoConfig }) {
  const normalizedPageKey = normalizeBookSeoPageKey(pageKey);
  const override = resolvePageOverride(seoConfig, pageKey);
  if (override && override.title) {
    return collapseWhitespace(override.title);
  }

  if (normalizedPageKey === "index.html" && seoConfig.landing && seoConfig.landing.title) {
    return collapseWhitespace(seoConfig.landing.title);
  }

  return collapseWhitespace(buildDisplayTitle(pageMetaEntry));
}

function buildAlternateLinks({ edition, pageKey }) {
  const canonicalUrl = buildBookCanonicalUrl(edition, pageKey);
  const alternates = [{ hreflang: edition.locale, href: canonicalUrl }];
  const peerEdition = getPeerSiteEdition(edition.locale);
  const peerPageKey = resolveBookSeoPeerPageKey(edition.locale, pageKey);

  if (peerEdition && peerPageKey) {
    alternates.push({
      hreflang: peerEdition.locale,
      href: buildBookCanonicalUrl(peerEdition, peerPageKey),
    });
  }

  alternates.push({
    hreflang: "x-default",
    href: buildDefaultAlternateUrl(edition, pageKey),
  });

  return alternates;
}

function assertUniqueCanonicalMetadata(records) {
  const seenPairs = new Map();

  for (const [pageKey, record] of records.entries()) {
    if (!isCanonicalBookPageKey(pageKey)) {
      continue;
    }

    const key = `${record.title}\u0000${record.description}`;
    const firstPage = seenPairs.get(key);
    if (firstPage) {
      throw new Error(
        `Duplicate canonical book metadata detected for ${firstPage} and ${pageKey}: ${record.title}`
      );
    }

    seenPairs.set(key, pageKey);
  }
}

export function buildBookSeoRecords({ bookDir, edition, rootDir }) {
  const pageMeta = readReaderPageMeta(bookDir);
  const localeStrings = edition.localeStrings || {};
  const seoConfig = readEditionBookSeoConfig(edition, rootDir);
  const records = new Map();

  listBuiltBookPageKeys(bookDir).forEach((pageKey) => {
    if (isRedirectOnlyBookPageKey(pageKey)) {
      return;
    }

    const pageMetaEntry = pageMeta[metaKeyForPageKey(pageKey)] || null;
    const title = resolvePageTitle({ pageKey, pageMetaEntry, seoConfig });
    const description = resolvePageDescription({ pageKey, pageMetaEntry, localeStrings, seoConfig });

    if (!title) {
      throw new Error(`Missing SEO title for ${edition.locale} ${pageKey}`);
    }

    if (!description) {
      throw new Error(`Missing SEO description for ${edition.locale} ${pageKey}`);
    }

    const canonicalUrl = buildBookCanonicalUrl(edition, pageKey);
    records.set(pageKey, {
      canonicalUrl,
      description,
      structuredData: buildStructuredData({
        edition,
        pageKey,
        title,
        description,
        canonicalUrl,
        seoConfig,
      }),
      title: `${title} | ${BOOK_TITLE_SUFFIX}`,
      alternates: buildAlternateLinks({ edition, pageKey }),
    });
  });

  assertUniqueCanonicalMetadata(records);
  return records;
}
