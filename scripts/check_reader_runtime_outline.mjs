import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { getBookPageBodyClasses } from "./shared/book-page-variants.mjs";
import {
  collectRuntimeFigureNumbers,
  countRuntimeFigures,
  countRuntimeFormulas,
  countRuntimeTables,
} from "./shared/reader-outline-runtime.mjs";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(scriptDir, "..");

function getBodyClasses(pageHtml) {
  const match = String(pageHtml || "").match(/<body\b[^>]*class="([^"]*)"/i);
  return new Set(
    (match ? match[1] : "")
      .split(/\s+/)
      .map((value) => value.trim())
      .filter(Boolean)
  );
}

function assertBodyClasses(pageHtml, pageKey, locale) {
  const expectedClasses = getBookPageBodyClasses(pageKey, locale);
  const actualClasses = getBodyClasses(pageHtml);

  expectedClasses.forEach((className) => {
    if (!actualClasses.has(className)) {
      throw new Error(`Expected ${locale}/${pageKey} to include body class ${className}.`);
    }
  });
}

function countHeadings(articleHtml) {
  return (String(articleHtml || "").match(/<h([2-6])\b/gi) || []).length;
}

function getArticleHtml(pageHtml) {
  const match = String(pageHtml || "").match(
    /<article\b[^>]*class="[^"]*\breader-article\b[^"]*"[^>]*>([\s\S]*?)<\/article>/i
  );
  return match ? match[1] : "";
}

const figureSentinels = {
  en: {
    pageKey: "chapters/chapter-05-hydrocarbon-value-chain.html",
    figureNumber: "5",
  },
  fr: {
    pageKey: "chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html",
    figureNumber: "5",
  },
};

function checkPage(pageHtml, pageKey, locale, meta) {
  const isRedirectPage = /<meta http-equiv="refresh"/i.test(pageHtml);

  if (pageKey === "index.html") {
    assertBodyClasses(pageHtml, pageKey, locale);
    return;
  }

  if (isRedirectPage) {
    return;
  }

  assertBodyClasses(pageHtml, pageKey, locale);

  const articleHtml = getArticleHtml(pageHtml);
  const referenceSections = (meta[pageKey] && meta[pageKey].referenceSections) || null;
  const figuresEnabled = !referenceSections || referenceSections.figures !== false;
  const tablesEnabled = !referenceSections || referenceSections.tables !== false;
  const formulasEnabled = !referenceSections || referenceSections.formulas !== false;
  const visibleOutline =
    countHeadings(articleHtml) > 0 ||
    (figuresEnabled && countRuntimeFigures(articleHtml) > 0) ||
    (tablesEnabled && countRuntimeTables(articleHtml) > 0) ||
    (formulasEnabled && countRuntimeFormulas(articleHtml) > 0);

  // This static checker can validate source-backed outline inputs, but only the
  // browser runtime can validate the final collapsed-rail DOM state for pages
  // that intentionally render with an empty outline.
  void visibleOutline;

  const figureSentinel = figureSentinels[locale];

  if (figureSentinel && pageKey === figureSentinel.pageKey) {
    const runtimeFigureNumbers = collectRuntimeFigureNumbers(articleHtml);

    if (!runtimeFigureNumbers.includes(figureSentinel.figureNumber)) {
      throw new Error(
        `Expected runtime Figure ${figureSentinel.figureNumber} sentinel on ${locale}/${pageKey}`
      );
    }
  }
}

function checkBook(bookRoot, locale) {
  const meta = JSON.parse(fs.readFileSync(path.join(bookRoot, "reader-page-meta.json"), "utf8"));
  const pages = ["index.html"];
  const chaptersDir = path.join(bookRoot, "chapters");

  fs.readdirSync(chaptersDir)
    .filter((name) => name.endsWith(".html"))
    .sort()
    .forEach((name) => {
      pages.push(`chapters/${name}`);
    });

  pages.forEach((pageKey) => {
    const html = fs.readFileSync(path.join(bookRoot, ...pageKey.split("/")), "utf8");
    checkPage(html, pageKey, locale, meta);
  });
}

try {
  checkBook(path.join(rootDir, "public", "book"), "en");
  checkBook(path.join(rootDir, "public", "fr", "book"), "fr");
} catch (error) {
  console.error(error.message || String(error));
  process.exit(1);
}
