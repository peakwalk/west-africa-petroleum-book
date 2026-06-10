import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(scriptDir, "..");
const summaryPath = path.join(rootDir, "src", "SUMMARY.md");
const bookIndexPath = path.join(rootDir, "public", "book", "index.html");
const outputPath = path.join(rootDir, "public", "book", "reader-page-meta.json");

function normalizeText(text) {
  return (text || "").replace(/\s+/g, " ").trim();
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
  const match = normalizeText(title).match(/^(Chapter\s+\d+)\s*:\s*(.+)$/i);

  if (!match) {
    return {
      eyebrow: "",
      title: normalizeText(title),
    };
  }

  return {
    eyebrow: match[1],
    title: normalizeText(match[2]),
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
    const absoluteSourcePath = path.join(rootDir, "src", entry.sourcePath);
    const markdownSource = fs.readFileSync(absoluteSourcePath, "utf8");
    const parsedTitle = parseChapterTitle(entry.title);
    const lede = extractFirstParagraph(markdownSource);
    const pageKey = deriveHtmlPath(entry.sourcePath);

    pageMeta[pageKey] = {
      eyebrow: parsedTitle.eyebrow,
      title: parsedTitle.title,
      partLabel: entry.partLabel,
      updatedAt: getUpdatedAt(path.join("src", entry.sourcePath)),
      lede,
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
