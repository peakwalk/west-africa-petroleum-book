import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(scriptDir, "..");
const requestedBookDir = process.argv[2] || path.join("public", "book");
const requestedSummaryPath = process.argv[3] || path.join("editions", "en", "content", "SUMMARY.md");
const requestedSourceRoot = process.argv[4] || path.join("editions", "en", "content");

const bookDir = path.resolve(rootDir, requestedBookDir);
const summaryPath = path.resolve(rootDir, requestedSummaryPath);
const sourceRoot = path.resolve(rootDir, requestedSourceRoot);
const bookIndexPath = path.join(bookDir, "index.html");
const outputPath = path.join(bookDir, "reader-page-meta.json");

function normalizeText(text) {
  return (text || "").replace(/\s+/g, " ").trim();
}

function countMatches(text, pattern) {
  return (text.match(pattern) || []).length;
}

function stripMarkdown(text) {
  return normalizeText(
    text
      .replace(/!\[[^\]]*]\([^)]*\)/g, "")
      .replace(/\[([^\]]+)]\([^)]*\)/g, "$1")
      .replace(/<[^>]+>/g, "")
      .replace(/`+/g, "")
      .replace(/\*{1,3}/g, "")
      .replace(/_{1,3}/g, "")
  );
}

function parseSummary(summarySource) {
  const entries = [];
  let currentPartLabel = "";

  summarySource.split(/\r?\n/).forEach((line) => {
    const headingMatch = line.match(/^#\s+(.+)$/);
    if (headingMatch) {
      currentPartLabel = normalizeText(headingMatch[1]);
      return;
    }

    const chapterMatch = line.match(/^\s*-\s+\[(.+)]\((chapters\/[^)]+\.md)\)\s*$/);
    if (!chapterMatch) {
      return;
    }

    entries.push({
      title: normalizeText(chapterMatch[1]),
      sourcePath: chapterMatch[2],
      partLabel: currentPartLabel,
    });
  });

  return entries;
}

function parseChapterTitle(title) {
  const normalized = normalizeText(title);
  const match = normalized.match(/^(Chapter|Chapitre)\s+(\d+)\s*:\s*(.+)$/i);

  if (!match) {
    return {
      eyebrow: "",
      title: normalized,
    };
  }

  return {
    eyebrow: `${match[1]} ${match[2]}`,
    title: normalizeText(match[3]),
  };
}

function extractFirstParagraph(markdownSource) {
  const blocks = markdownSource.split(/\n\s*\n/);

  for (const rawBlock of blocks) {
    const block = normalizeText(rawBlock);

    if (!block) {
      continue;
    }

    if (
      /^#/.test(block) ||
      /^!\[/.test(block) ||
      /^(Figure|Table)\s+\d+/i.test(block) ||
      /^\|/.test(block) ||
      /^[-*+]\s/.test(block) ||
      /^<sup>/i.test(block)
    ) {
      continue;
    }

    const stripped = stripMarkdown(block);
    if (stripped) {
      return stripped;
    }
  }

  return "";
}

function deriveHtmlPath(markdownPath) {
  return markdownPath.replace(/\.md$/i, ".html");
}

function buildReferenceSections(markdownSource) {
  const figureCount =
    countMatches(markdownSource, /!\[[^\]]*]\([^)]+\)/g) +
    countMatches(markdownSource, /^Figure\s+\d+\s*:/gim);
  const markdownTableCount = countMatches(
    markdownSource,
    /^\s*\|?(?:\s*:?-+:?\s*\|)+\s*:?-+:?\s*\|?\s*$/gm
  );
  const htmlTableCount = countMatches(markdownSource, /<table\b/gi);
  const labeledFormulaCount = countMatches(markdownSource, /\bdata-equation-label\s*=/gi);
  const standaloneFormulaCount = countMatches(markdownSource, /<div class="book-formula\b/gi);

  return {
    figures: figureCount > 0,
    tables: markdownTableCount > 0 || htmlTableCount > 0,
    formulas: labeledFormulaCount > 0 || standaloneFormulaCount > 0,
  };
}

function getUpdatedAt(relativeSourcePath) {
  try {
    const updatedAt = execFileSync(
      "git",
      ["log", "-1", "--format=%cs", "--", relativeSourcePath],
      { cwd: rootDir, encoding: "utf8" }
    ).trim();

    if (updatedAt) {
      return updatedAt;
    }
  } catch (error) {
    // Fall back to the file modification date if git metadata is unavailable.
  }

  const absolutePath = path.join(rootDir, relativeSourcePath);
  return new Date(fs.statSync(absolutePath).mtimeMs).toISOString().slice(0, 10);
}

function buildPageMeta() {
  const summarySource = fs.readFileSync(summaryPath, "utf8");
  const summaryEntries = parseSummary(summarySource);
  const pageMeta = {};

  summaryEntries.forEach((entry) => {
    const absoluteSourcePath = path.join(sourceRoot, entry.sourcePath);
    const markdownSource = fs.readFileSync(absoluteSourcePath, "utf8");
    const parsedTitle = parseChapterTitle(entry.title);
    const lede = extractFirstParagraph(markdownSource);
    const pageKey = deriveHtmlPath(entry.sourcePath);
    const relativeSourcePath = path.relative(rootDir, absoluteSourcePath);

    pageMeta[pageKey] = {
      eyebrow: parsedTitle.eyebrow,
      title: parsedTitle.title,
      partLabel: entry.partLabel,
      updatedAt: getUpdatedAt(relativeSourcePath),
      lede,
      referenceSections: buildReferenceSections(markdownSource),
    };
  });

  return pageMeta;
}

function normalizeRootIndexChapterPaths() {
  if (!fs.existsSync(bookIndexPath)) {
    return;
  }

  const source = fs.readFileSync(bookIndexPath, "utf8");
  const normalized = source
    .split('src="../images/').join('src="images/')
    .split('href="../chapters/').join('href="chapters/');

  if (normalized !== source) {
    fs.writeFileSync(bookIndexPath, normalized);
  }
}

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, JSON.stringify(buildPageMeta(), null, 2) + "\n");
normalizeRootIndexChapterPaths();
