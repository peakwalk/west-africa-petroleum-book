import { promises as fs } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  CONTACT_EMAIL,
  CONTACT_HREF,
  WEBSITE_LEGAL_LINKS,
  renderBrandLink,
  resolveShellLinks,
  renderLandingFooter,
  renderLandingHead,
} from "./shared/landing-shell.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, "..");
const LEGAL_SRC_DIR = path.join(ROOT, "src", "legal");

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

function renderLegalNav(currentKey) {
  const navItems = [
    { key: "terms", href: WEBSITE_LEGAL_LINKS.terms, label: "Terms of Use" },
    { key: "privacy", href: WEBSITE_LEGAL_LINKS.privacy, label: "Privacy Policy" },
    { key: "cookie", href: WEBSITE_LEGAL_LINKS.cookie, label: "Cookie Policy" },
  ];

  return `      <nav class="legal-page-nav" aria-label="Legal documents">
${navItems
  .map(({ key, href, label }) => {
    const current = key === currentKey ? ' aria-current="page"' : "";
    return `        <a href="${escapeHtml(href)}"${current}>${escapeHtml(label)}</a>`;
  })
  .join("\n")}
      </nav>`;
}

function renderContactBlock() {
  return `        <section class="legal-section legal-contact-section">
          <h2>Contact</h2>
          <p>If you need the current approved legal text for this public website, contact <a href="${escapeHtml(
            CONTACT_HREF
          )}">${escapeHtml(CONTACT_EMAIL)}</a>.</p>
        </section>`;
}

function renderLegalPage(page, content) {
  const links = resolveShellLinks("legal");

  return `<!doctype html>
<html lang="en">
  <head>
${renderLandingHead({
  description: content.description,
  extraStylesheets: ["assets/css/legal.css"],
  title: `${content.title} | Upstream Atlas`,
})}
  </head>
  <body class="legal-page">
    <main class="legal-page-main">
${renderBrandLink({
  ariaLabel: "Upstream Atlas home",
  brandHref: links.brandHref,
  indent: "      ",
  imageClass: "legal-page-brand-image",
  linkClass: "legal-page-brand",
  width: 200,
  height: 53,
})}
      <header class="legal-page-header">
        <p class="legal-page-kicker">Website legal document</p>
        <h1>${escapeHtml(content.title)}</h1>
        <p class="legal-page-status-line">${escapeHtml(content.statusLine)}</p>
        <p class="legal-page-updated-at">${escapeHtml(content.updatedAt)}</p>
      </header>
${renderLegalNav(page.key)}
      <article class="legal-page-article">
        <section class="legal-status-panel" aria-label="Publication status">
          <h2>${escapeHtml(content.noticeTitle)}</h2>
          <p>${escapeHtml(content.noticeBody)}</p>
${renderStatusItems(content.statusItems)}
        </section>
${renderSections(content.sections)}
${renderContactBlock()}
      </article>
    </main>

${renderLandingFooter({ currentPage: "legal" })}
  </body>
</html>
`;
}

async function main() {
  await Promise.all(
    PAGES.map(async (page) => {
      const sourcePath = path.join(LEGAL_SRC_DIR, page.source);
      const outputPath = path.join(ROOT, page.output);
      const raw = await fs.readFile(sourcePath, "utf8");
      const content = JSON.parse(raw);
      const html = renderLegalPage(page, content);
      await fs.writeFile(outputPath, html, "utf8");
    })
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
