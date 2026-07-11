import { promises as fs } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  CONTACT_EMAIL,
  CONTACT_HREF,
  WEBSITE_LEGAL_LINKS,
  renderLandingFooter,
  renderLandingHead,
  renderLandingHeader,
} from "./shared/landing-shell.mjs";
import { listSiteEditions, resolveEditionPath } from "./shared/site-editions.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, "..");
const outputRootArgIndex = process.argv.indexOf("--output-root");
const outputRoot =
  outputRootArgIndex >= 0 && process.argv[outputRootArgIndex + 1]
    ? path.resolve(ROOT, process.argv[outputRootArgIndex + 1])
    : path.join(ROOT, "public");

const PAGES = [
  { key: "terms", output: WEBSITE_LEGAL_LINKS.terms, source: "terms-of-use.json" },
  { key: "privacy", output: WEBSITE_LEGAL_LINKS.privacy, source: "privacy-policy.json" },
  { key: "cookie", output: WEBSITE_LEGAL_LINKS.cookie, source: "cookie-policy.json" },
];

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function renderParagraphs(paragraphs = []) {
  return paragraphs
    .map((paragraph) => `          <p>${escapeHtml(paragraph)}</p>`)
    .join("\n");
}

function renderBullets(items = []) {
  if (!items.length) {
    return "";
  }

  return `          <ul>
${items.map((item) => `            <li>${escapeHtml(item)}</li>`).join("\n")}
          </ul>`;
}

function renderSections(sections = []) {
  return sections
    .map((section) => {
      return `        <section class="legal-section">
          <h2>${escapeHtml(section.heading)}</h2>
${renderParagraphs(section.paragraphs)}
${renderBullets(section.bullets)}
        </section>`;
    })
    .join("\n");
}

function renderStatusItems(items = []) {
  if (!items.length) {
    return "";
  }

  return `        <ul class="legal-status-list">
${items.map((item) => `          <li>${escapeHtml(item)}</li>`).join("\n")}
        </ul>`;
}

function renderLegalNav(currentKey, localeStrings) {
  const navItems = [
    { key: "terms", href: WEBSITE_LEGAL_LINKS.terms, label: localeStrings.legal.links.terms },
    { key: "privacy", href: WEBSITE_LEGAL_LINKS.privacy, label: localeStrings.legal.links.privacy },
    { key: "cookie", href: WEBSITE_LEGAL_LINKS.cookie, label: localeStrings.legal.links.cookie },
  ];

  return `      <nav class="legal-page-nav" aria-label="${escapeHtml(
    localeStrings.legal.documentsAriaLabel
  )}">
${navItems
  .map(({ key, href, label }) => {
    const current = key === currentKey ? ' aria-current="page"' : "";
    return `        <a href="${escapeHtml(href)}"${current}>${escapeHtml(label)}</a>`;
  })
  .join("\n")}
      </nav>`;
}

function renderContactBlock(localeStrings) {
  return `        <section class="legal-section legal-contact-section">
          <h2>${escapeHtml(localeStrings.legal.contactHeading)}</h2>
          <p>${escapeHtml(localeStrings.legal.contactBodyPrefix)} <a href="${escapeHtml(
            CONTACT_HREF
          )}">${escapeHtml(CONTACT_EMAIL)}</a>.</p>
        </section>`;
}

function renderLegalPage(page, content, edition) {
  const localeStrings = edition.localeStrings;

  return `<!doctype html>
<html lang="${edition.locale}">
  <head>
${renderLandingHead({
  currentLegalPage: page.key,
  currentPage: "legal",
  description: content.description,
  edition,
  extraStylesheets: ["assets/css/legal.css"],
  title: `${content.title} | Upstream Atlas`,
})}
  </head>
  <body class="legal-page">
${renderLandingHeader({ currentLegalPage: page.key, currentPage: "legal", edition })}
    <main class="legal-page-main">
      <header class="legal-page-header">
        <p class="legal-page-kicker">${escapeHtml(localeStrings.legal.pageKicker)}</p>
        <h1>${escapeHtml(content.title)}</h1>
        <p class="legal-page-status-line">${escapeHtml(content.statusLine)}</p>
        <p class="legal-page-updated-at">${escapeHtml(content.updatedAt)}</p>
      </header>
${renderLegalNav(page.key, localeStrings)}
      <article class="legal-page-article">
        <section class="legal-status-panel" aria-label="${escapeHtml(
          localeStrings.legal.publicationStatusAriaLabel
        )}">
          <h2>${escapeHtml(content.noticeTitle)}</h2>
          <p>${escapeHtml(content.noticeBody)}</p>
${renderStatusItems(content.statusItems)}
        </section>
${renderSections(content.sections)}
${renderContactBlock(localeStrings)}
      </article>
    </main>

${renderLandingFooter({ currentLegalPage: page.key, currentPage: "legal", edition })}
  </body>
</html>
`;
}

async function main() {
  await Promise.all(
    listSiteEditions().flatMap((edition) =>
      PAGES.map(async (page) => {
        const sourcePath = path.join(ROOT, edition.legalRoot, page.source);
        const outputPath = resolveEditionPath(edition, page.output, outputRoot);
        const raw = await fs.readFile(sourcePath, "utf8");
        const content = JSON.parse(raw);
        const html = renderLegalPage(page, content, edition);
        await fs.mkdir(path.dirname(outputPath), { recursive: true });
        await fs.writeFile(outputPath, html, "utf8");
      })
    )
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
