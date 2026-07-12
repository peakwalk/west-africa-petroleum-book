import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  bookPageVariantClassNames,
  getBookPageBodyClasses,
} from "./shared/book-page-variants.mjs";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(scriptDir, "..");

const customCssPattern = /<link\b[^>]*href="([^"]*theme\/custom-[^"]*\.css)"/gi;
const customJsPattern = /<script\b[^>]*src="([^"]*theme\/custom-[^"]*\.js)"/gi;
const localeBookRoots = {
  en: path.join(rootDir, "public", "book"),
  fr: path.join(rootDir, "public", "fr", "book"),
};

const sentinelPages = [
  {
    locale: "en",
    pageKey: "index.html",
    requiredClasses: ["book-page-cover"],
    forbiddenClasses: ["book-outline-empty", "book-page-aux-index", "book-page-front-matter-outline-rail"],
  },
  {
    locale: "en",
    pageKey: "chapters/list-of-figures.html",
    requiredClasses: [
      "book-page-front-matter-outline-rail",
      "book-page-figure-index",
      "book-page-aux-index",
      "book-outline-empty",
    ],
    requireReaderShell: true,
  },
  {
    locale: "en",
    pageKey: "chapters/chapter-05-hydrocarbon-value-chain.html",
    forbiddenClasses: ["book-outline-empty", "book-page-aux-index", "book-page-front-matter-outline-rail"],
    requireReaderShell: true,
  },
  {
    locale: "en",
    pageKey: "chapters/chapter-10-socio-political-determinants.html",
    forbiddenClasses: ["book-outline-empty", "book-page-aux-index", "book-page-front-matter-outline-rail"],
    requireReaderShell: true,
  },
  {
    locale: "en",
    pageKey: "chapters/chapter-11-general-conclusion.html",
    requiredClasses: ["book-page-front-matter-outline-rail"],
    forbiddenClasses: ["book-outline-empty", "book-page-aux-index"],
    requireReaderShell: true,
  },
  {
    locale: "fr",
    pageKey: "index.html",
    requiredClasses: ["book-page-cover"],
    forbiddenClasses: ["book-outline-empty", "book-page-aux-index", "book-page-front-matter-outline-rail"],
  },
  {
    locale: "fr",
    pageKey: "chapters/list-of-figures.html",
    requiredClasses: [
      "book-page-front-matter-outline-rail",
      "book-page-figure-index",
      "book-page-aux-index",
      "book-outline-empty",
    ],
    requireReaderShell: true,
  },
  {
    locale: "fr",
    pageKey: "chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html",
    forbiddenClasses: ["book-outline-empty", "book-page-aux-index", "book-page-front-matter-outline-rail"],
    requireReaderShell: true,
  },
  {
    locale: "fr",
    pageKey: "chapters/chapter-05-key-socio-political-determinants-of-oil-sector-performance.html",
    forbiddenClasses: ["book-outline-empty", "book-page-aux-index", "book-page-front-matter-outline-rail"],
    requireReaderShell: true,
  },
  {
    locale: "fr",
    pageKey: "chapters/general-conclusion.html",
    requiredClasses: ["book-page-front-matter-outline-rail"],
    forbiddenClasses: ["book-outline-empty", "book-page-aux-index"],
    requireReaderShell: true,
  },
];

const jsContractTokens = [
  "window.__readerRuntimeState = state;",
  "document.documentElement.dataset.readerRuntimeState = state;",
  'document.body.classList.toggle("book-outline-empty", !hasVisibleOutlineContent);',
  "readerRuntimeSidebarRefreshInFlight",
  "readerRuntimeSidebarRefreshPending",
];

const cssContractTokens = [
  "body.book-outline-empty .reader-layout",
  "grid-template-columns: minmax(0, 1fr);",
  "body.book-outline-empty .reader-outline",
  "display: none;",
];

function readText(filePath) {
  return fs.readFileSync(filePath, "utf8");
}

function getPagePath(bookRoot, pageKey) {
  return path.join(bookRoot, ...pageKey.split("/"));
}

function getBodyClasses(pageHtml) {
  const match = String(pageHtml || "").match(/<body\b[^>]*class="([^"]*)"/i);
  return new Set(
    (match ? match[1] : "")
      .split(/\s+/)
      .map((value) => value.trim())
      .filter(Boolean)
  );
}

function assertCondition(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function assertHasClass(bodyClasses, className, pageLabel) {
  assertCondition(bodyClasses.has(className), `Expected ${pageLabel} to include body class ${className}.`);
}

function assertLacksClass(bodyClasses, className, pageLabel) {
  assertCondition(!bodyClasses.has(className), `Expected ${pageLabel} to omit body class ${className}.`);
}

function assertIncludes(haystack, needle, label) {
  assertCondition(String(haystack || "").includes(needle), `Expected ${label} to contain ${needle}.`);
}

function assertHasRenderedClass(pageHtml, className, pageLabel) {
  const classPattern = new RegExp(`class="[^"]*\\b${className}\\b[^"]*"`);
  assertCondition(classPattern.test(pageHtml), `Expected ${pageLabel} to render class token ${className}.`);
}

function collectCustomAssets(pageHtml, pattern, label) {
  const assets = Array.from(String(pageHtml || "").matchAll(pattern), (match) => match[1]);
  const uniqueAssets = [...new Set(assets)];

  assertCondition(uniqueAssets.length > 0, `Expected ${label} to reference a hashed custom asset.`);
  return uniqueAssets;
}

function assertSharedVariantCoverage(bookRoot, locale) {
  assertCondition(fs.existsSync(bookRoot), `Missing built book root: ${bookRoot}`);

  const pages = ["index.html"];
  const chaptersDir = path.join(bookRoot, "chapters");

  fs.readdirSync(chaptersDir)
    .filter((name) => name.endsWith(".html"))
    .sort()
    .forEach((name) => {
      pages.push(`chapters/${name}`);
    });

  pages.forEach((pageKey) => {
    const pagePath = getPagePath(bookRoot, pageKey);
    const pageLabel = `${locale}/${pageKey}`;
    const pageHtml = readText(pagePath);
    const bodyClasses = getBodyClasses(pageHtml);
    const isRedirectPage = /<meta http-equiv="refresh"/i.test(pageHtml);

    if (isRedirectPage) {
      return;
    }

    assertHasClass(bodyClasses, "book-layout-booting", pageLabel);

    const expectedClasses = new Set(getBookPageBodyClasses(pageKey, locale));

    expectedClasses.forEach((className) => {
      assertHasClass(bodyClasses, className, pageLabel);
    });

    bookPageVariantClassNames.forEach((className) => {
      if (!expectedClasses.has(className)) {
        assertLacksClass(bodyClasses, className, pageLabel);
      }
    });
  });
}

function checkSentinelPage(page, assetPaths) {
  const bookRoot = localeBookRoots[page.locale];
  const pagePath = getPagePath(bookRoot, page.pageKey);
  const pageLabel = `${page.locale}/${page.pageKey}`;
  const pageHtml = readText(pagePath);
  const bodyClasses = getBodyClasses(pageHtml);

  assertHasClass(bodyClasses, "book-layout-booting", pageLabel);

  (page.requiredClasses || []).forEach((className) => {
    assertHasClass(bodyClasses, className, pageLabel);
  });

  (page.forbiddenClasses || []).forEach((className) => {
    assertLacksClass(bodyClasses, className, pageLabel);
  });

  if (page.requireReaderShell) {
    assertHasRenderedClass(pageHtml, "reader-layout", pageLabel);
    assertHasRenderedClass(pageHtml, "reader-outline", pageLabel);
    assertHasRenderedClass(pageHtml, "reader-article", pageLabel);
  }

  collectCustomAssets(pageHtml, customCssPattern, `${pageLabel} CSS`)
    .map((assetRef) => path.resolve(path.dirname(pagePath), assetRef))
    .forEach((assetPath) => assetPaths.css.add(assetPath));
  collectCustomAssets(pageHtml, customJsPattern, `${pageLabel} JavaScript`)
    .map((assetRef) => path.resolve(path.dirname(pagePath), assetRef))
    .forEach((assetPath) => assetPaths.js.add(assetPath));
}

function assertAssetContracts(assetPaths) {
  assetPaths.css.forEach((assetPath) => {
    assertCondition(fs.existsSync(assetPath), `Missing referenced custom CSS asset ${assetPath}.`);
    const css = readText(assetPath);
    cssContractTokens.forEach((token) => {
      assertIncludes(css, token, assetPath);
    });
  });

  assetPaths.js.forEach((assetPath) => {
    assertCondition(fs.existsSync(assetPath), `Missing referenced custom JavaScript asset ${assetPath}.`);
    const js = readText(assetPath);
    jsContractTokens.forEach((token) => {
      assertIncludes(js, token, assetPath);
    });
  });
}

try {
  Object.entries(localeBookRoots).forEach(([locale, bookRoot]) => {
    assertSharedVariantCoverage(bookRoot, locale);
  });

  const assetPaths = {
    css: new Set(),
    js: new Set(),
  };

  sentinelPages.forEach((page) => {
    checkSentinelPage(page, assetPaths);
  });

  assertAssetContracts(assetPaths);
} catch (error) {
  console.error(error.message || String(error));
  process.exit(1);
}
