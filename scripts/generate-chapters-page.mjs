import { promises as fs } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  renderLandingFooter,
  renderLandingHead,
  renderLandingHeader,
} from "./shared/landing-shell.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, "..");
const SRC_DIR = path.join(ROOT, "src");
const SUMMARY_PATH = path.join(SRC_DIR, "SUMMARY.md");

const outputDirArg = process.argv[2] || path.join(ROOT, "chapters");
const outputDir = path.resolve(ROOT, outputDirArg);
const outputPath = path.join(outputDir, "index.html");

const GENERIC_DESCRIPTIONS = new Map([
  ["Book Front Matter", "Opening material and publication framing for the web edition."],
  ["Foreword", "Context for the book's purpose, scope, and relevance to petroleum resource governance."],
  ["General Introduction", "Introduces the analytical framework, research objective, and the structure of the book."],
  ["General Conclusion", "Closing synthesis of the book's findings on petroleum operations, fiscal systems, and governance."],
  ["Glossary", "Reference definitions for technical, fiscal, and institutional terminology used throughout the book."],
  ["Bibliographical References", "Academic, policy, and industry sources cited across the book."],
]);

const SECTION_TAGS = new Map([
  ["Front Matter", "Prelude"],
  ["Part I: General Information on the Oil Industry", "Foundations"],
  ["Part II: Oil Contracts and Oil Taxation in West Africa", "Fiscal Systems"],
  ["Part III: Political Stability, Governance and Corruption", "Governance"],
  ["Back Matter", "Reference"],
]);

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function splitSectionHeading(heading) {
  const match = /^(Part\s+[IVX]+):\s+(.+)$/.exec(heading);
  if (!match) {
    return { kicker: heading, title: heading };
  }

  return { kicker: match[1], title: match[2] };
}

function stripMarkdown(markdown) {
  return markdown
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

function estimateReadingTime(markdown, { title, sectionTitle }) {
  const analysis = analyzeMarkdown(markdown);
  const figureCount = Math.max(analysis.imageCount, analysis.figureCaptionCount);
  const tableCount = analysis.markdownTableCount + analysis.htmlTableCount;
  const subsectionCount = Math.max(0, analysis.headingCount - 1);

  const proseWords = analysis.wordCount.toLocaleString("en-US");
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
      label: `${minutes} min read`,
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
      label: `${minutes} min read`,
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
      label: `${minutes} min read`,
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
    label: `${minutes} min read`,
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

function extractDescription(markdown, title) {
  if (GENERIC_DESCRIPTIONS.has(title)) {
    return GENERIC_DESCRIPTIONS.get(title);
  }

  const body = markdown
    .replace(/\r/g, "")
    .replace(/^# .+$/m, "")
    .replace(/^!\[[^\]]*\]\([^)]+\)\s*$/gm, "")
    .replace(/^Figure .+$/gm, "")
    .trim();

  const paragraphs = body.split(/\n\s*\n/);

  for (const paragraph of paragraphs) {
    const cleaned = stripMarkdown(paragraph);
    const wordCount = cleaned.split(/\s+/).filter(Boolean).length;

    if (wordCount < 14) {
      continue;
    }

    return trimSentence(normalizeDescription(cleaned));
  }

  return "Structured exploration of petroleum resource management, fiscal design, and governance in West Africa.";
}

function deriveTags(sectionTitle, title) {
  const tags = [];
  const primaryTag = SECTION_TAGS.get(sectionTitle);
  if (primaryTag) {
    tags.push(primaryTag);
  }

  if (/tax|fiscal|royalty|contract/i.test(title)) {
    tags.push("Taxation");
  } else if (/governance|political|corruption/i.test(title)) {
    tags.push("Policy");
  } else if (/country|west africa/i.test(title)) {
    tags.push("Regional Analysis");
  } else if (/glossary/i.test(title)) {
    tags.push("Terminology");
  } else if (/references/i.test(title)) {
    tags.push("Sources");
  } else if (/introduction|foreword/i.test(title)) {
    tags.push("Context");
  } else {
    tags.push("Reading");
  }

  return tags.slice(0, 2);
}

function parseSummary(summary) {
  const sections = [];
  let currentSection = null;

  for (const line of summary.split(/\r?\n/)) {
    const sectionMatch = /^#\s+(.+)$/.exec(line.trim());
    if (sectionMatch) {
      const heading = sectionMatch[1];

      if (heading === "Summary") {
        currentSection = null;
        continue;
      }

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

function getCardLabel(title, sectionTitle) {
  const chapterMatch = /^(Chapter\s+\d+):\s*(.+)$/.exec(title);
  if (chapterMatch) {
    return {
      number: chapterMatch[1],
      heading: chapterMatch[2],
    };
  }

  return {
    number: sectionTitle === "Front Matter" ? "Prelude" : "Reference",
    heading: title,
  };
}

async function buildChapterData() {
  const summary = await fs.readFile(SUMMARY_PATH, "utf8");
  const sections = parseSummary(summary);

  const enrichedSections = [];

  for (const section of sections) {
    const items = [];

    for (const item of section.items) {
      const sourcePath = path.join(SRC_DIR, item.relativeSourcePath);
      const markdown = await fs.readFile(sourcePath, "utf8");
      const card = getCardLabel(item.title, section.title);
      const bookHref = `../book/${item.relativeSourcePath.replace(/\.md$/, ".html")}`;

      items.push({
        sectionTitle: section.title,
        title: card.heading,
        number: card.number,
        href: bookHref,
        description: extractDescription(markdown, item.title),
        readingTime: estimateReadingTime(markdown, { title: item.title, sectionTitle: section.title }),
        tags: deriveTags(section.title, item.title),
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

function renderAdditionalResources() {
  const resources = [
    {
      title: "Glossary of Terms",
      href: "../book/chapters/glossary.html",
      description: "Technical and fiscal terminology used throughout the book.",
    },
    {
      title: "References & Citations",
      href: "../book/chapters/bibliographical-references.html",
      description: "Academic, policy, and industry sources cited across the study.",
    },
    {
      title: "General Conclusion",
      href: "../book/chapters/general-conclusion.html",
      description: "Closing synthesis of the book's findings on petroleum operations and governance.",
    },
  ];

  return `
      <section class="additional-resources">
        <h3>Additional Resources</h3>
        <div class="additional-resources-grid">
          ${resources
            .map(
              (resource) => `
                <a class="additional-resource-card" href="${escapeHtml(resource.href)}">
                  <div class="additional-resource-title">${escapeHtml(resource.title)}</div>
                  <p>${escapeHtml(resource.description)}</p>
                </a>
              `
            )
            .join("\n")}
        </div>
      </section>
  `;
}

function renderPage(sections) {
  return `<!doctype html>
<html lang="en">
  <head>
${renderLandingHead({
  basePath: "../",
  description:
    "Browse the chapter library for Exploration and Exploitation of Petroleum Resources in West Africa.",
  extraStylesheets: ["assets/css/chapters.css"],
  title: "Chapter Library | Exploration and Exploitation of Petroleum Resources in West Africa",
})}
  </head>
  <body class="landing-shell chapters-shell">
${renderLandingHeader({ currentPage: "chapters", logoBasePath: "../" })}

    <main class="chapters-main">
      <section class="chapters-hero">
        <p class="eyebrow">Chapter Library</p>
        <h1>Browse the book by part, chapter, and reference section.</h1>
        <p class="chapters-intro">
          A structured entry point into West Africa petroleum resource management, from upstream operations and fiscal design to governance, country analysis, and reference material.
        </p>
      </section>

      <div class="chapters-sections">
        ${sections.map(renderSection).join("\n")}
      </div>

      ${renderAdditionalResources()}
    </main>

${renderLandingFooter({ currentPage: "chapters", logoBasePath: "../" })}
  </body>
</html>
`;
}

async function main() {
  const sections = await buildChapterData();
  await fs.mkdir(outputDir, { recursive: true });
  await fs.writeFile(outputPath, renderPage(sections), "utf8");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
