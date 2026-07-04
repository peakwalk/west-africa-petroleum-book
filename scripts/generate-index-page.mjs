import { promises as fs } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  renderLandingFooter,
  renderLandingHead,
  renderLandingHeader,
} from "./shared/landing-shell.mjs";
import { listSiteEditions, resolveEditionPath } from "./shared/site-editions.mjs";
import {
  getFrenchCompatibilityCopy,
  renderFrenchHomepageSearchScope,
  renderHomepageMain,
  resolveHomepageLinks,
} from "./shared/homepage-content.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, "..");
const outputRootArgIndex = process.argv.indexOf("--output-root");
const outputRoot =
  outputRootArgIndex >= 0 && process.argv[outputRootArgIndex + 1]
    ? path.resolve(ROOT, process.argv[outputRootArgIndex + 1])
    : ROOT;

async function main() {
  await Promise.all(
    listSiteEditions().map(async (edition) => {
      const outputPath = resolveEditionPath(edition, "index.html", outputRoot);
      const mainContent =
        edition.locale === "en"
          ? renderHomepageMain(edition)
          : await renderFrenchCompatibilityHomepage(edition);
      const html = `<!doctype html>
<html lang="${edition.locale}">
  <head>
${renderLandingHead({
  currentPage: "home",
  description: edition.localeStrings.meta.homeDescription,
  edition,
  title: edition.localeStrings.meta.homeTitle,
})}
  </head>
  <body class="landing-shell">
${renderLandingHeader({ currentPage: "home", edition })}

${mainContent.trim()}

${renderLandingFooter({ currentPage: "home", edition })}
  </body>
</html>
`;

      await fs.mkdir(path.dirname(outputPath), { recursive: true });
      await fs.writeFile(outputPath, html, "utf8");
    })
  );
}

async function renderFrenchCompatibilityHomepage(edition) {
  const mainContentPath = path.join(ROOT, edition.landingMainPath);
  const mainContent = await fs.readFile(mainContentPath, "utf8");
  const copy = getFrenchCompatibilityCopy();
  const links = resolveHomepageLinks("home", edition);
  const searchChips = renderFrenchHomepageSearchScope()
    .map(
      (tag) =>
        `          <a class="search-scope-chip" href="${links.ctaHref}?search=${encodeURIComponent(
          tag
        )}">${tag}</a>`
    )
    .join("\n");
  const topicCards = copy.topics
    .map(
      (topic) => `        <article class="topic-card topic-card-compact">
          <p class="topic-card-kicker">${topic.kicker}</p>
          <h3>${topic.title}</h3>
          <p>${topic.description}</p>
          <a class="topic-card-link" href="${topic.href}">Explorer <span aria-hidden="true">→</span></a>
        </article>`
    )
    .join("\n");

  return mainContent
    .replace(
      /<section class="hero-panel">[\s\S]*?<\/section>/,
      `<section class="hero-panel hero-panel-compact">
    <div class="hero-media" aria-hidden="true"></div>
    <div class="hero-overlay" aria-hidden="true"></div>
    <div class="hero-grid" aria-hidden="true"></div>
    <div class="hero-content">
      <div class="hero-layout hero-layout-compact">
        <div class="hero-copy-block hero-copy-block-compact">
          <p class="eyebrow">${copy.heroEyebrow}</p>
          <h1>${copy.heroTitle}</h1>
          <p class="hero-copy">${copy.heroCopy}</p>
          <div class="hero-actions">
            <a class="button button-primary" href="${links.ctaHref}">${copy.heroPrimaryCta}</a>
            <a class="button button-secondary" href="${links.chapterLibraryHref}">${copy.heroSecondaryCta}</a>
          </div>
        </div>
      </div>
    </div>
  </section>`
    )
    .replace(
      /<section id="countries" class="section section-muted">[\s\S]*?<\/section>/,
      `<section id="countries" class="section section-muted fr-compatibility-section">
    <div class="section-heading">
      <p class="eyebrow">${copy.countriesEyebrow}</p>
      <h2>${copy.countriesTitle}</h2>
      <p class="section-lead">${copy.countriesBody}</p>
    </div>
    <div class="fr-compatibility-card">
      <a class="button button-primary" href="${links.viewAllCountriesHref}">${copy.countriesCta}</a>
    </div>
  </section>`
    )
    .replace(
      /<section id="resources" class="section section-muted">[\s\S]*?<\/section>/,
      `<section id="search" class="section section-search-surface fr-compatibility-section">
    <div class="section-heading section-heading-centered">
      <p class="eyebrow">${copy.searchEyebrow}</p>
      <h2>${copy.searchTitle}</h2>
    </div>
    <form class="homepage-search-form" action="${links.ctaHref}" method="get" role="search">
      <label class="sr-only" for="homepage-search-input-fr">${copy.searchTitle}</label>
      <input
        id="homepage-search-input-fr"
        type="search"
        name="search"
        placeholder="${copy.searchPlaceholder}"
      >
      <button class="button button-primary" type="submit">${copy.searchButton}</button>
    </form>
    <div class="search-scope-grid">
${searchChips}
    </div>
  </section>

  <section id="topics" class="section section-topic-discovery fr-compatibility-section">
    <div class="section-heading">
      <p class="eyebrow">${copy.topicsEyebrow}</p>
      <h2>${copy.topicsTitle}</h2>
      <p class="section-lead">${copy.topicsLead}</p>
    </div>
    <div class="topic-grid topic-grid-compact">
${topicCards}
    </div>
  </section>`
    );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
