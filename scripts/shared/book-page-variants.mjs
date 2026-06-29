const coverPath = "cover.html";
const tableOfContentsPath = "table-of-contents.html";
const listOfFiguresPath = "list-of-figures.html";
const listOfTablesPath = "list-of-tables.html";
const listOfEquationsPath = "list-of-equations.html";
const abbreviationsPath = "abbreviations-acronyms-and-abbreviations.html";
const disclaimerPath = "disclaimer.html";
const prefacePath = "preface.html";
const forewordPath = "foreword.html";
const generalIntroductionPath = "general-introduction.html";
const generalConclusionPath = "general-conclusion.html";
const chapterElevenGeneralConclusionPath = "chapter-11-general-conclusion.html";
const glossaryPath = "glossary.html";
const bibliographicalReferencesPath = "bibliographical-references.html";
const frontMatterOutlineRailClass = "book-page-front-matter-outline-rail";
const coverPageClass = "book-page-cover";
const figureIndexClass = "book-page-figure-index";
const tableIndexClass = "book-page-table-index";
const equationIndexClass = "book-page-equation-index";
const abbreviationsIndexClass = "book-page-abbreviations-index";
const auxIndexClass = "book-page-aux-index";
const outlineEmptyClass = "book-outline-empty";

export const bookPageVariantClassNames = Object.freeze([
  frontMatterOutlineRailClass,
  coverPageClass,
  figureIndexClass,
  tableIndexClass,
  equationIndexClass,
  abbreviationsIndexClass,
  auxIndexClass,
  outlineEmptyClass,
]);

function normalizePageKey(pageKey) {
  return String(pageKey || "")
    .replace(/\\/g, "/")
    .replace(/^\/+/, "")
    .replace(/\/+$/, "") || "index.html";
}

function getChapterPath(pageKey) {
  const normalized = normalizePageKey(pageKey);
  return normalized.startsWith("chapters/") ? normalized.slice("chapters/".length) : "";
}

export function getPreserveOutlinePaths(locale) {
  if (locale === "fr") {
    return [
      coverPath,
      tableOfContentsPath,
      listOfFiguresPath,
      listOfTablesPath,
      listOfEquationsPath,
      abbreviationsPath,
      forewordPath,
      generalIntroductionPath,
      generalConclusionPath,
      chapterElevenGeneralConclusionPath,
      glossaryPath,
      bibliographicalReferencesPath,
    ];
  }

  return [
    coverPath,
    tableOfContentsPath,
    listOfFiguresPath,
    listOfTablesPath,
    listOfEquationsPath,
    abbreviationsPath,
    disclaimerPath,
    prefacePath,
    forewordPath,
    chapterElevenGeneralConclusionPath,
    glossaryPath,
    bibliographicalReferencesPath,
  ];
}

export function getBookPageVariantFromPageKey(pageKey, locale) {
  const normalized = normalizePageKey(pageKey);
  const chapterPath = getChapterPath(normalized);
  const preserveOutlineRail = chapterPath
    ? getPreserveOutlinePaths(locale).includes(chapterPath)
    : false;
  const isCoverPage = normalized === "index.html" || chapterPath === coverPath;
  const isTableOfContentsPage = chapterPath === tableOfContentsPath;
  const isListOfFiguresPage = chapterPath === listOfFiguresPath;
  const isListOfTablesPage = chapterPath === listOfTablesPath;
  const isListOfEquationsPage = chapterPath === listOfEquationsPath;
  const isAbbreviationsPage = chapterPath === abbreviationsPath;
  const isAuxIndexPage =
    isTableOfContentsPage ||
    isListOfFiguresPage ||
    isListOfTablesPage ||
    isListOfEquationsPage ||
    isAbbreviationsPage;

  return {
    preserveOutlineRail,
    isCoverPage,
    isTableOfContentsPage,
    isListOfFiguresPage,
    isListOfTablesPage,
    isListOfEquationsPage,
    isAbbreviationsPage,
    isAuxIndexPage,
  };
}

export function getBookPageBodyClasses(pageKey, locale) {
  const pageVariant = getBookPageVariantFromPageKey(pageKey, locale);
  const classes = [];

  if (pageVariant.preserveOutlineRail) {
    classes.push(frontMatterOutlineRailClass);
  }

  if (pageVariant.isCoverPage) {
    classes.push(coverPageClass);
  }

  if (pageVariant.isListOfFiguresPage) {
    classes.push(figureIndexClass);
  }

  if (pageVariant.isListOfTablesPage) {
    classes.push(tableIndexClass);
  }

  if (pageVariant.isListOfEquationsPage) {
    classes.push(equationIndexClass);
  }

  if (pageVariant.isAbbreviationsPage) {
    classes.push(abbreviationsIndexClass);
  }

  if (pageVariant.isAuxIndexPage) {
    classes.push(auxIndexClass, outlineEmptyClass);
  }

  return classes;
}
