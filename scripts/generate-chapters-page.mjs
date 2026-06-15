import { promises as fs } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  renderLandingFooter,
  renderLandingHead,
  renderLandingHeader,
} from "./shared/landing-shell.mjs";
import { listSiteEditions, resolveEditionPath } from "./shared/site-editions.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, "..");
const DEFAULT_GENERIC_DESCRIPTIONS = new Map([
  ["cover", "Opening material and publication framing for the web edition."],
  ["foreword", "Context for the book's purpose, scope, and relevance to petroleum resource governance."],
  ["general-introduction", "Introduces the analytical framework, research objective, and the structure of the book."],
  ["general-conclusion", "Closing synthesis of the book's findings on petroleum operations, fiscal systems, and governance."],
  ["glossary", "Reference definitions for technical, fiscal, and institutional terminology used throughout the book."],
  ["bibliographical-references", "Academic, policy, and industry sources cited across the book."]
]);

const SECTION_PRIMARY_TAGS = {
  en: {
    "front matter": "Prelude",
    "part i: general information on the oil industry": "Foundations",
    "part ii: oil contracts and oil taxation in west africa": "Fiscal Systems",
    "part iii: political stability, governance and corruption": "Governance",
    "back matter": "Reference"
  },
  fr: {
    "front matter": "Ouverture",
    "première partie : généralités sur l’industrie pétrolière": "Fondements",
    "deuxième partie : contrats pétroliers et fiscalité pétrolière en afrique de l’ouest": "Fiscalité",
    "troisième partie : stabilité politique, gouvernance et corruption": "Gouvernance",
    "back matter": "Référence"
  }
};

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function splitSectionHeading(heading) {
  const match =
    /^(Part\s+[IVX]+):\s+(.+)$/.exec(heading) ||
    /^((?:Première|Deuxième|Troisième)\s+partie)\s*:\s*(.+)$/i.exec(heading);
  if (!match) {
    return { kicker: heading, title: heading };
  }

  return { kicker: match[1], title: match[2] };
}

function stripMarkdown(markdown) {
  return markdown
    .replace(/<([a-z0-9-]+)\b[^>]*\bdata-reading-time-ignore\b[^>]*>[\s\S]*?<\/\1>/gi, "")
    .replace(/<\/?(?:table|thead|tbody|tr|th|td|colgroup|col|caption)\b[^>]*>/gi, " ")
    .replace(/\r/g, "")
    .replace(/^```[\s\S]*?^```$/gm, "")
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/!\[[^\]]*\]\([^)]+\)/g, "")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/\|/g, " ")
    .replace(/^\s*[-*+]\s+/gm, "")
    .replace(/^\s*\d+[.)]\s+/gm, "")
    .replace(/[*_`>#]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function pluralize(count, singular, plural = `${singular}s`) {
  return `${count} ${count === 1 ? singular : plural}`;
}

function countMatches(markdown, pattern) {
  return (markdown.match(pattern) || []).length;
}

function analyzeMarkdown(markdown) {
  return {
    wordCount: stripMarkdown(markdown).split(/\s+/).filter(Boolean).length,
    imageCount: countMatches(markdown, /!\[[^\]]*\]\([^)]+\)/g),
    figureCaptionCount: countMatches(markdown, /^Figure\s+\d+/gm),
    markdownTableCount: countMatches(markdown, /^\|[:\-\s|]+\|\s*$/gm),
    htmlTableCount: countMatches(markdown, /<table\b/gi),
    headingCount: countMatches(markdown, /^#{2,6}\s+/gm),
    glossaryEntryCount: countMatches(markdown, /^\*\*[^*\n][^:\n]*:/gm),
    referenceItemCount: countMatches(markdown, /^\d+\.\s+/gm),
  };
}

function buildEstimateTooltip(minutes, pieces, modeLabel) {
  const detail = pieces.length > 0 ? pieces.join(", ") : "content length";
  return `Estimated reading time based on ${detail} and a ${modeLabel}. Actual time varies by reading speed and how closely you study figures, tables, and notes.`;
}

function estimateReadingTime(markdown, { locale, title, sectionTitle }) {
  const analysis = analyzeMarkdown(markdown);
  const figureCount = Math.max(analysis.imageCount, analysis.figureCaptionCount);
  const tableCount = analysis.markdownTableCount + analysis.htmlTableCount;
  const subsectionCount = Math.max(0, analysis.headingCount - 1);

  const proseWords = analysis.wordCount.toLocaleString(locale === "fr" ? "fr-FR" : "en-US");
  const detailPieces = [`about ${proseWords} words`];

  if (tableCount > 0) {
    detailPieces.push(pluralize(tableCount, "table"));
  }

  if (figureCount > 0) {
    detailPieces.push(pluralize(figureCount, "figure"));
  }

  if (sectionTitle === "Front Matter") {
    const minutes = Math.max(
      5,
      Math.round(analysis.wordCount / 210 + figureCount * 0.18 + subsectionCount * 0.08)
    );
    return {
      label: locale === "fr" ? `${minutes} min de lecture` : `${minutes} min read`,
      tooltip: buildEstimateTooltip(minutes, detailPieces, "front-matter overview pace"),
    };
  }

  if (/glossary/i.test(title)) {
    detailPieces.push(pluralize(analysis.glossaryEntryCount, "term"));
    const minutes = Math.max(
      8,
      Math.round(analysis.wordCount / 260 + analysis.glossaryEntryCount * 0.1)
    );
    return {
      label: locale === "fr" ? `${minutes} min de lecture` : `${minutes} min read`,
      tooltip: buildEstimateTooltip(minutes, detailPieces, "browse-and-study glossary pace"),
    };
  }

  if (/bibliographical references|references/i.test(title)) {
    detailPieces.push(pluralize(analysis.referenceItemCount, "citation"));
    const minutes = Math.max(
      6,
      Math.round(analysis.wordCount / 280 + analysis.referenceItemCount * 0.12)
    );
    return {
      label: locale === "fr" ? `${minutes} min de lecture` : `${minutes} min read`,
      tooltip: buildEstimateTooltip(minutes, detailPieces, "browse-and-study reference pace"),
    };
  }

  const minutes = Math.max(
    6,
    Math.round(
      analysis.wordCount / 185 +
        figureCount * 0.35 +
        tableCount * 0.75 +
        subsectionCount * 0.1
    )
  );

  return {
    label: locale === "fr" ? `${minutes} min de lecture` : `${minutes} min read`,
    tooltip: buildEstimateTooltip(minutes, detailPieces, "slower technical-reading pace"),
  };
}

function trimSentence(value, maxLength = 220) {
  if (value.length <= maxLength) {
    return value;
  }

  const candidate = value.slice(0, maxLength - 3);
  const boundary = Math.max(candidate.lastIndexOf("."), candidate.lastIndexOf(","), candidate.lastIndexOf(" "));
  const clipped = boundary > 120 ? candidate.slice(0, boundary) : candidate;
  return `${clipped.trimEnd()}...`;
}

function normalizeDescription(value) {
  const normalized = value
    .replace(/^As shown in Figure\s+\d+[,:\s-]*/i, "")
    .replace(/\(Figure\s+\d+\)/gi, "")
    .replace(/\s+:\s+/g, ": ")
    .replace(/\s+/g, " ")
    .trim();

  if (!normalized) {
    return normalized;
  }

  return normalized.charAt(0).toUpperCase() + normalized.slice(1);
}

function extractDescription(markdown, title, relativeSourcePath, localeStrings) {
  const contentKey = path.basename(relativeSourcePath, ".md");
  const catalogDescriptions = localeStrings.chaptersPage.genericDescriptions || {};
  if (catalogDescriptions[contentKey]) {
    return catalogDescriptions[contentKey];
  }

  if (DEFAULT_GENERIC_DESCRIPTIONS.has(contentKey)) {
    return DEFAULT_GENERIC_DESCRIPTIONS.get(contentKey);
  }

  const body = markdown
    .replace(/\r/g, "")
    .replace(/^# .+$/m, "")
    .replace(/^!\[[^\]]*\]\([^)]+\)\s*$/gm, "")
    .replace(/^Figure .+$/gm, "")
    .trim();

  const paragraphs = body.split(/\n\s*\n/);

  for (const paragraph of paragraphs) {
    const cleaned = stripMarkdown(paragraph.replace(/<\/?[a-z][^>]*>/gi, " "));
    const wordCount = cleaned.split(/\s+/).filter(Boolean).length;

    if (wordCount < 14) {
      continue;
    }

    return trimSentence(normalizeDescription(cleaned));
  }

  return "Structured exploration of petroleum resource management, fiscal design, and governance in West Africa.";
}

function deriveTags(sectionTitle, title, locale) {
  const tags = [];
  const primaryTag = (SECTION_PRIMARY_TAGS[locale] || {})[sectionTitle.toLowerCase()];
  if (primaryTag) {
    tags.push(primaryTag);
  }

  if (/tax|fiscal|royalty|contract|contrat|fiscalité/i.test(title)) {
    tags.push(locale === "fr" ? "Fiscalité" : "Taxation");
  } else if (/governance|political|corruption|gouvernance|politique/i.test(title)) {
    tags.push(locale === "fr" ? "Politique" : "Policy");
  } else if (/country|west africa|afrique de l’ouest|afrique de l'ouest|pays/i.test(title)) {
    tags.push(locale === "fr" ? "Analyse régionale" : "Regional Analysis");
  } else if (/glossary|glossaire/i.test(title)) {
    tags.push(locale === "fr" ? "Terminologie" : "Terminology");
  } else if (/references|références/i.test(title)) {
    tags.push(locale === "fr" ? "Sources" : "Sources");
  } else if (/introduction|foreword|avant-propos/i.test(title)) {
    tags.push(locale === "fr" ? "Contexte" : "Context");
  } else {
    tags.push(locale === "fr" ? "Lecture" : "Reading");
  }

  return tags.slice(0, 2);
}

function parseSummary(summary) {
  const sections = [];
  let currentSection = null;
  let skippedBookHeading = false;

  for (const line of summary.split(/\r?\n/)) {
    const sectionMatch = /^#\s+(.+)$/.exec(line.trim());
    if (sectionMatch) {
      if (!skippedBookHeading) {
        skippedBookHeading = true;
        currentSection = null;
        continue;
      }

      const heading = sectionMatch[1];
      currentSection = { title: heading, items: [] };
      sections.push(currentSection);
      continue;
    }

    const itemMatch = /^-\s+\[(.+?)\]\((.+?)\)$/.exec(line.trim());
    if (!itemMatch || !currentSection) {
      continue;
    }

    const [, title, relativeSourcePath] = itemMatch;
    if (title === "Home") {
      continue;
    }

    currentSection.items.push({ title, relativeSourcePath });
  }

  return sections.filter((section) => section.items.length > 0);
}

function getCardLabel(title, sectionTitle, locale) {
  const chapterMatch = /^(?:Chapter|Chapitre)\s+(\d+)\s*:\s*(.+)$/i.exec(title);
  if (chapterMatch) {
    return {
      number: locale === "fr" ? `Chapitre ${chapterMatch[1]}` : `Chapter ${chapterMatch[1]}`,
      heading: chapterMatch[2],
    };
  }

  return {
    number:
      sectionTitle.toLowerCase() === "front matter"
        ? locale === "fr"
          ? "Ouverture"
          : "Prelude"
        : locale === "fr"
          ? "Référence"
          : "Reference",
    heading: title,
  };
}

async function buildChapterData(edition) {
  const srcDir = path.join(ROOT, edition.sourceRoot);
  const summaryPath = path.join(ROOT, edition.summaryPath);
  const baseBookHref = edition.routePrefix ? `/${edition.routePrefix}/book/` : "/book/";
  const summary = await fs.readFile(summaryPath, "utf8");
  const sections = parseSummary(summary);

  const enrichedSections = [];

  for (const section of sections) {
    const items = [];

    for (const item of section.items) {
      const sourcePath = path.join(srcDir, item.relativeSourcePath);
      const markdown = await fs.readFile(sourcePath, "utf8");
      const card = getCardLabel(item.title, section.title, edition.locale);
      const bookHref = `${baseBookHref}${item.relativeSourcePath.replace(/\.md$/, ".html")}`;

      items.push({
        sectionTitle: section.title,
        title: card.heading,
        number: card.number,
        href: bookHref,
        description: extractDescription(
          markdown,
          item.title,
          item.relativeSourcePath,
          edition.localeStrings
        ),
        readingTime: estimateReadingTime(markdown, {
          locale: edition.locale,
          title: item.title,
          sectionTitle: section.title
        }),
        tags: deriveTags(section.title, item.title, edition.locale),
      });
    }

    enrichedSections.push({
      ...splitSectionHeading(section.title),
      fullTitle: section.title,
      items,
    });
  }

  return enrichedSections;
}

function renderTags(tags) {
  return tags
    .map((tag) => `
      <span class="chapter-card-tag">
        <span class="chapter-card-tag-icon" aria-hidden="true">
          <svg viewBox="0 0 16 16" focusable="false" role="img">
            <path d="M2.5 3.5A1.5 1.5 0 0 1 4 2h4.05c.4 0 .78.16 1.06.44l4.45 4.45a1.5 1.5 0 0 1 0 2.12l-4.55 4.55a1.5 1.5 0 0 1-2.12 0L2.44 9.11A1.5 1.5 0 0 1 2 8.05V3.5Zm1.5 0v4.55L8 12.05l4.5-4.5-4.45-4.05H4Z" fill="currentColor"/>
            <circle cx="6" cy="5" r="1" fill="currentColor"/>
          </svg>
        </span>
        <span>${escapeHtml(tag)}</span>
      </span>
    `)
    .join("");
}

function renderStatus(item) {
  if (!/^Chapter\s+\d+/i.test(item.number)) {
    return "";
  }

  return `
    <span class="chapter-card-status" aria-hidden="true">
      <svg viewBox="0 0 16 16" focusable="false" role="img">
        <circle cx="8" cy="8" r="6.75" fill="none" stroke="currentColor" stroke-width="1.5"/>
        <path d="M5.35 8.1 7.1 9.85 10.7 6.25" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </span>
  `;
}

function renderCard(item) {
  return `
    <a class="chapter-card" href="${escapeHtml(item.href)}">
      <div class="chapter-card-header">
        <span class="chapter-card-number">${escapeHtml(item.number)}</span>
        ${renderStatus(item)}
      </div>
      <div class="chapter-card-body">
        <h3>${escapeHtml(item.title)}</h3>
        <p>${escapeHtml(item.description)}</p>
      </div>
      <div class="chapter-card-footer">
        <span
          class="chapter-card-reading"
          data-tooltip="${escapeHtml(item.readingTime.tooltip)}"
          aria-label="${escapeHtml(item.readingTime.tooltip)}"
        >
          <span class="chapter-card-reading-icon" aria-hidden="true">
            <svg viewBox="0 0 16 16" focusable="false" role="img">
              <circle cx="8" cy="8" r="6.25" fill="none" stroke="currentColor" stroke-width="1.5"/>
              <path d="M8 4.6v3.8l2.35 1.35" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
          <span>${escapeHtml(item.readingTime.label.replace(/ read$/, ""))}</span>
        </span>
        <div class="chapter-card-tags">${renderTags(item.tags)}</div>
      </div>
    </a>
  `;
}

function renderSection(section) {
  return `
    <section class="chapter-library-section">
      <div class="chapter-library-heading">
        <h2>${escapeHtml(section.fullTitle)}</h2>
      </div>
      <div class="chapter-library-list">
        ${section.items.map(renderCard).join("\n")}
      </div>
    </section>
  `;
}

function renderAdditionalResources(edition) {
  const resources = [
    {
      key: "glossary",
      href: `${edition.routePrefix ? `/${edition.routePrefix}` : ""}/book/chapters/glossary.html`,
    },
    {
      key: "references",
      href: `${edition.routePrefix ? `/${edition.routePrefix}` : ""}/book/chapters/bibliographical-references.html`,
    },
    {
      key: "conclusion",
      href: `${edition.routePrefix ? `/${edition.routePrefix}` : ""}/book/chapters/general-conclusion.html`,
    },
  ];
  const copy = edition.localeStrings.chaptersPage.additionalResources;

  return `
      <section class="additional-resources">
        <h3>${escapeHtml(edition.localeStrings.chaptersPage.additionalResourcesHeading)}</h3>
        <div class="additional-resources-grid">
          ${resources
            .map(
              (resource) => `
                <a class="additional-resource-card" href="${escapeHtml(resource.href)}">
                  <div class="additional-resource-title">${escapeHtml(copy[resource.key].title)}</div>
                  <p>${escapeHtml(copy[resource.key].description)}</p>
                </a>
              `
            )
            .join("\n")}
        </div>
      </section>
  `;
}

function renderPage(sections, edition) {
  const localeStrings = edition.localeStrings;
  return `<!doctype html>
<html lang="${edition.locale}">
  <head>
${renderLandingHead({
  basePath: "../",
  currentPage: "chapters",
  description: localeStrings.meta.chaptersDescription,
  edition,
  extraStylesheets: ["assets/css/chapters.css"],
  title: localeStrings.meta.chaptersTitle,
})}
  </head>
  <body class="landing-shell chapters-shell">
${renderLandingHeader({ currentPage: "chapters", edition, logoBasePath: "../" })}

    <main class="chapters-main">
      <section class="chapters-hero">
        <p class="eyebrow">${escapeHtml(localeStrings.chaptersPage.eyebrow)}</p>
        <h1>${escapeHtml(localeStrings.chaptersPage.heroTitle)}</h1>
        <p class="chapters-intro">
          ${escapeHtml(localeStrings.chaptersPage.intro)}
        </p>
      </section>

      <div class="chapters-sections">
        ${sections.map(renderSection).join("\n")}
      </div>

      ${renderAdditionalResources(edition)}
    </main>

${renderLandingFooter({ currentPage: "chapters", edition, logoBasePath: "../" })}
  </body>
</html>
`;
}

async function main() {
  await Promise.all(
    listSiteEditions().map(async (edition) => {
      const outputDir = resolveEditionPath(edition, "chapters");
      const outputPath = path.join(outputDir, "index.html");
      const sections = await buildChapterData(edition);
      await fs.mkdir(outputDir, { recursive: true });
      await fs.writeFile(outputPath, renderPage(sections, edition), "utf8");
    })
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
