const BOOK_NAV_EQUIVALENT_PAGE_MAP = {
  en: {
    "index.html": "index.html",
    "chapters/cover.html": "index.html",
    "chapters/front-matter.html": "index.html",
    "chapters/disclaimer.html": "index.html",
    "chapters/preface.html": "index.html",
    "chapters/table-of-contents.html": "index.html",
    "chapters/list-of-figures.html": "chapters/list-of-figures.html",
    "chapters/list-of-tables.html": "chapters/list-of-tables.html",
    "chapters/list-of-equations.html": "chapters/list-of-equations.html",
    "chapters/abbreviations-acronyms-and-abbreviations.html":
      "chapters/abbreviations-acronyms-and-abbreviations.html",
    "chapters/foreword.html": "index.html",
    "chapters/foreword-to-the-french-edition.html": "chapters/foreword.html",
    "chapters/chapter-01-general-introduction.html": "chapters/general-introduction.html",
    "chapters/chapter-02-emerging-petroleum-provinces-in-west-africa.html": "index.html",
    "chapters/chapter-03-west-africa-country-analysis.html":
      "chapters/chapter-06-west-africa-in-depth-country-analysis.html",
    "chapters/chapter-04-national-oil-companies-in-west-africa.html": "index.html",
    "chapters/chapter-05-hydrocarbon-value-chain.html":
      "chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html",
    "chapters/chapter-06-upstream-operations-and-government-roles.html":
      "chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html",
    "chapters/chapter-08-petroleum-fiscal-regimes.html":
      "chapters/chapter-03-tax-regimes-in-the-petroleum-sector.html",
    "chapters/chapter-09-west-african-fiscal-regimes.html":
      "chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html",
    "chapters/chapter-10-socio-political-determinants.html":
      "chapters/chapter-05-key-socio-political-determinants-of-oil-sector-performance.html",
    "chapters/chapter-07-petroleum-data-management-in-west-africa.html": "index.html",
    "chapters/chapter-11-general-conclusion.html": "chapters/general-conclusion.html",
    "chapters/chapter-12-vision-for-west-africa-2050.html": "index.html",
    "chapters/glossary.html": "chapters/glossary.html",
    "chapters/bibliographical-references.html": "chapters/bibliographical-references.html",
  },
  fr: {
    "index.html": "index.html",
    "chapters/cover.html": "index.html",
    "chapters/front-matter.html": "index.html",
    "chapters/list-of-figures.html": "chapters/list-of-figures.html",
    "chapters/list-of-tables.html": "chapters/list-of-tables.html",
    "chapters/list-of-equations.html": "chapters/list-of-equations.html",
    "chapters/abbreviations-acronyms-and-abbreviations.html":
      "chapters/abbreviations-acronyms-and-abbreviations.html",
    "chapters/foreword.html": "chapters/foreword-to-the-french-edition.html",
    "chapters/general-introduction.html": "chapters/chapter-01-general-introduction.html",
    "chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html":
      "chapters/chapter-05-hydrocarbon-value-chain.html",
    "chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html":
      "chapters/chapter-06-upstream-operations-and-government-roles.html",
    "chapters/chapter-03-tax-regimes-in-the-petroleum-sector.html":
      "chapters/chapter-08-petroleum-fiscal-regimes.html",
    "chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html":
      "chapters/chapter-09-west-african-fiscal-regimes.html",
    "chapters/chapter-05-key-socio-political-determinants-of-oil-sector-performance.html":
      "chapters/chapter-10-socio-political-determinants.html",
    "chapters/chapter-06-west-africa-in-depth-country-analysis.html":
      "chapters/chapter-03-west-africa-country-analysis.html",
    "chapters/general-conclusion.html": "chapters/chapter-11-general-conclusion.html",
    "chapters/glossary.html": "chapters/glossary.html",
    "chapters/bibliographical-references.html": "chapters/bibliographical-references.html",
  },
};

const BOOK_SEO_EQUIVALENT_PAGE_MAP = {
  en: {
    "index.html": "index.html",
    "chapters/list-of-figures.html": "chapters/list-of-figures.html",
    "chapters/list-of-tables.html": "chapters/list-of-tables.html",
    "chapters/list-of-equations.html": "chapters/list-of-equations.html",
    "chapters/abbreviations-acronyms-and-abbreviations.html":
      "chapters/abbreviations-acronyms-and-abbreviations.html",
    "chapters/foreword-to-the-french-edition.html": "chapters/foreword.html",
    "chapters/chapter-01-general-introduction.html": "chapters/general-introduction.html",
    "chapters/chapter-03-west-africa-country-analysis.html":
      "chapters/chapter-06-west-africa-in-depth-country-analysis.html",
    "chapters/chapter-05-hydrocarbon-value-chain.html":
      "chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html",
    "chapters/chapter-06-upstream-operations-and-government-roles.html":
      "chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html",
    "chapters/chapter-08-petroleum-fiscal-regimes.html":
      "chapters/chapter-03-tax-regimes-in-the-petroleum-sector.html",
    "chapters/chapter-09-west-african-fiscal-regimes.html":
      "chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html",
    "chapters/chapter-10-socio-political-determinants.html":
      "chapters/chapter-05-key-socio-political-determinants-of-oil-sector-performance.html",
    "chapters/chapter-11-general-conclusion.html": "chapters/general-conclusion.html",
    "chapters/glossary.html": "chapters/glossary.html",
    "chapters/bibliographical-references.html": "chapters/bibliographical-references.html",
  },
  fr: {
    "index.html": "index.html",
    "chapters/list-of-figures.html": "chapters/list-of-figures.html",
    "chapters/list-of-tables.html": "chapters/list-of-tables.html",
    "chapters/list-of-equations.html": "chapters/list-of-equations.html",
    "chapters/abbreviations-acronyms-and-abbreviations.html":
      "chapters/abbreviations-acronyms-and-abbreviations.html",
    "chapters/foreword.html": "chapters/foreword-to-the-french-edition.html",
    "chapters/general-introduction.html": "chapters/chapter-01-general-introduction.html",
    "chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html":
      "chapters/chapter-05-hydrocarbon-value-chain.html",
    "chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html":
      "chapters/chapter-06-upstream-operations-and-government-roles.html",
    "chapters/chapter-03-tax-regimes-in-the-petroleum-sector.html":
      "chapters/chapter-08-petroleum-fiscal-regimes.html",
    "chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html":
      "chapters/chapter-09-west-african-fiscal-regimes.html",
    "chapters/chapter-05-key-socio-political-determinants-of-oil-sector-performance.html":
      "chapters/chapter-10-socio-political-determinants.html",
    "chapters/chapter-06-west-africa-in-depth-country-analysis.html":
      "chapters/chapter-03-west-africa-country-analysis.html",
    "chapters/general-conclusion.html": "chapters/chapter-11-general-conclusion.html",
    "chapters/glossary.html": "chapters/glossary.html",
    "chapters/bibliographical-references.html": "chapters/bibliographical-references.html",
  },
};

const LEGACY_BOOK_REDIRECT_TARGETS = {
  en: {
    "chapters/chapter-07-petroleum-fiscal-regimes.html":
      "chapters/chapter-08-petroleum-fiscal-regimes.html",
    "chapters/chapter-08-west-african-fiscal-regimes.html":
      "chapters/chapter-09-west-african-fiscal-regimes.html",
    "chapters/chapter-09-socio-political-determinants.html":
      "chapters/chapter-10-socio-political-determinants.html",
    "chapters/chapter-10-petroleum-data-management-in-west-africa.html":
      "chapters/chapter-07-petroleum-data-management-in-west-africa.html",
  },
  fr: {},
};

const REDIRECT_ONLY_BOOK_PAGE_KEYS = new Set([
  "chapters/front-matter.html",
  "chapters/cover.html",
  ...Object.keys(LEGACY_BOOK_REDIRECT_TARGETS.en),
]);
const NON_CANONICAL_BOOK_PAGE_KEYS = new Set();

export function normalizeBookSeoPageKey(pageKey) {
  if (pageKey === "chapters/cover.html") {
    return "index.html";
  }

  return pageKey;
}

export function isRedirectOnlyBookPageKey(pageKey) {
  return REDIRECT_ONLY_BOOK_PAGE_KEYS.has(pageKey);
}

export function isCanonicalBookPageKey(pageKey) {
  return !isRedirectOnlyBookPageKey(pageKey) && !NON_CANONICAL_BOOK_PAGE_KEYS.has(pageKey);
}

export function listLegacyBookRedirects(locale) {
  return Object.entries(LEGACY_BOOK_REDIRECT_TARGETS[locale] || {}).map(
    ([sourcePageKey, targetPageKey]) => ({ sourcePageKey, targetPageKey })
  );
}

export function resolveBookNavPeerPageKey(locale, pageKey) {
  const localeMap = BOOK_NAV_EQUIVALENT_PAGE_MAP[locale] || {};
  if (Object.prototype.hasOwnProperty.call(localeMap, pageKey)) {
    return localeMap[pageKey];
  }

  if (pageKey.startsWith("chapters/")) {
    return "index.html";
  }

  return pageKey;
}

export function resolveBookSeoPeerPageKey(locale, pageKey) {
  if (isRedirectOnlyBookPageKey(pageKey)) {
    return null;
  }

  const normalizedPageKey = normalizeBookSeoPageKey(pageKey);
  const localeMap = BOOK_SEO_EQUIVALENT_PAGE_MAP[locale] || {};

  if (Object.prototype.hasOwnProperty.call(localeMap, normalizedPageKey)) {
    return localeMap[normalizedPageKey];
  }

  return null;
}
