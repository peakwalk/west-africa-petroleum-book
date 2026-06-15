import fs from "node:fs/promises";
import path from "node:path";

const sidebarReferenceIconSvgs = {
  conclusion:
    '<svg viewBox="0 0 24 24" focusable="false" aria-hidden="true"><path d="M7 4.75h7.75L18.5 8.5v10.75a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1v-13.5a1 1 0 0 1 1-1Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"></path><path d="M14.5 4.75V8.5h3.75" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"></path><path d="M9 12h6M9 15h6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"></path></svg>',
  glossary:
    '<svg viewBox="0 0 24 24" focusable="false" aria-hidden="true"><path d="M6.5 5.75h8.25a2.5 2.5 0 0 1 2.5 2.5v10.5H9a2.5 2.5 0 0 0-2.5 2.5V5.75Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"></path><path d="M17.25 18.75H9a2.5 2.5 0 0 0-2.5 2.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"></path><path d="M9.5 10.25h4.75M9.5 13.25h4.75" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"></path></svg>',
  references:
    '<svg viewBox="0 0 24 24" focusable="false" aria-hidden="true"><path d="M4.75 7.25h10.5a2 2 0 0 1 2 2v8.5H6.75a2 2 0 0 0-2 2V7.25Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"></path><path d="M9 7.25V5.75a1 1 0 0 1 1-1h9.25v11H17.25" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"></path><path d="M8.5 11h5M8.5 14h5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"></path></svg>',
};

const sidebarSectionIconSvgs = {
  "front-matter":
    '<svg viewBox="0 0 24 24" focusable="false" aria-hidden="true"><path d="M5.25 6.25a1.5 1.5 0 0 1 1.5-1.5H11c1.18 0 2.31.31 3.3.9v13.6a5.9 5.9 0 0 0-3.3-.95H6.75a1.5 1.5 0 0 0-1.5 1.5V6.25Z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"></path><path d="M18.75 6.25a1.5 1.5 0 0 0-1.5-1.5H13c-1.18 0-2.31.31-3.3.9v13.6a5.9 5.9 0 0 1 3.3-.95h4.25a1.5 1.5 0 0 1 1.5 1.5V6.25Z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"></path><path d="M12 5.75v13.4" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"></path></svg>',
};

function normalizeText(text) {
  return String(text || "").replace(/\s+/g, " ").trim();
}

function stripTags(html) {
  return String(html || "").replace(/<[^>]+>/g, " ");
}

function decodeHtmlEntities(value) {
  return String(value || "").replace(/&(#x?[0-9a-f]+|[a-z]+);/gi, function (match, entity) {
    const normalized = String(entity).toLowerCase();

    if (normalized === "amp") {
      return "&";
    }

    if (normalized === "lt") {
      return "<";
    }

    if (normalized === "gt") {
      return ">";
    }

    if (normalized === "quot") {
      return '"';
    }

    if (normalized === "apos") {
      return "'";
    }

    if (normalized === "nbsp") {
      return " ";
    }

    if (normalized.startsWith("#x")) {
      const codePoint = Number.parseInt(normalized.slice(2), 16);
      return Number.isFinite(codePoint) ? String.fromCodePoint(codePoint) : match;
    }

    if (normalized.startsWith("#")) {
      const codePoint = Number.parseInt(normalized.slice(1), 10);
      return Number.isFinite(codePoint) ? String.fromCodePoint(codePoint) : match;
    }

    return match;
  });
}

function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function parseSidebarSectionHeading(text) {
  const normalized = normalizeText(text);
  const partMatch = normalized.match(/^(Part\s+[IVXLC]+)\s*:\s*(.+)$/i);
  const frenchPartMatch = normalized.match(
    /^((?:Première|Deuxième|Troisième)\s+partie)\s*:\s*(.+)$/i
  );

  if (/^Front Matter$/i.test(normalized)) {
    return { type: "front-matter", kicker: "", title: "Front Matter" };
  }

  if (/^Back Matter$/i.test(normalized)) {
    return { type: "back-matter", kicker: "", title: "Back Matter" };
  }

  if (partMatch) {
    return {
      type: "part",
      kicker: normalizeText(partMatch[1]),
      title: normalizeText(partMatch[2]),
    };
  }

  if (frenchPartMatch) {
    return {
      type: "part",
      kicker: normalizeText(frenchPartMatch[1]),
      title: normalizeText(frenchPartMatch[2]),
    };
  }

  return {
    type: "part",
    kicker: "",
    title: normalized,
  };
}

function parseSidebarRow(text) {
  const normalized = normalizeText(text);
  const chapterMatch = normalized.match(/^(Chapter|Chapitre)\s+(\d+)\s*:\s*(.+)$/i);

  if (!chapterMatch) {
    return {
      type: "reference",
      index: "",
      title: normalized,
    };
  }

  return {
    type: "chapter",
    index: String(Number(chapterMatch[2])).padStart(2, "0"),
    title: normalizeText(chapterMatch[3]),
  };
}

function getSidebarReferenceIcon(href) {
  if (!href) {
    return null;
  }

  const normalizedHref = href.replace(/\/+$/, "");

  if (normalizedHref.endsWith("chapters/general-conclusion.html")) {
    return "conclusion";
  }

  if (normalizedHref.endsWith("chapters/glossary.html")) {
    return "glossary";
  }

  if (normalizedHref.endsWith("chapters/bibliographical-references.html")) {
    return "references";
  }

  return null;
}

function toPosixPath(value) {
  return value.split(path.sep).join("/");
}

function resolveSidebarActivePageKey(pageKey) {
  if (pageKey === "index.html" || pageKey === "chapters/front-matter.html") {
    return "chapters/cover.html";
  }

  return pageKey;
}

function collectSidebarProjectionGroups(tocHtml) {
  const match = tocHtml.match(/<ol class="chapter">([\s\S]*?)<\/ol>/i);

  if (!match) {
    throw new Error("Could not locate <ol class=\"chapter\"> in toc.html");
  }

  const groups = [];
  let currentGroup = null;
  const tokenPattern = /<li class="part-title">([\s\S]*?)<\/li>|<a href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/gi;
  let tokenMatch = tokenPattern.exec(match[1]);

  while (tokenMatch) {
    const [, rawPartTitle, rawHref, rawLinkText] = tokenMatch;

    if (rawPartTitle !== undefined) {
      currentGroup = Object.assign(
        { items: [] },
        parseSidebarSectionHeading(decodeHtmlEntities(stripTags(rawPartTitle)))
      );
      groups.push(currentGroup);
      tokenMatch = tokenPattern.exec(match[1]);
      continue;
    }

    if (!currentGroup) {
      currentGroup = { type: "front-matter", kicker: "", title: "Front Matter", items: [] };
      groups.push(currentGroup);
    }

    currentGroup.items.push({
      href: normalizeText(rawHref),
      text: normalizeText(decodeHtmlEntities(stripTags(rawLinkText))),
    });

    tokenMatch = tokenPattern.exec(match[1]);
  }

  return groups.filter(function (group) {
    return group.items.length > 0;
  });
}

function buildSidebarReferenceIcon(iconName) {
  return `<span class="reader-sidebar-row-icon reader-sidebar-row-icon--${iconName}" aria-hidden="true">${sidebarReferenceIconSvgs[iconName]}</span>`;
}

function buildSidebarSectionIcon(iconName) {
  return `<span class="reader-sidebar-section-icon reader-sidebar-section-icon--${iconName}" aria-hidden="true">${sidebarSectionIconSvgs[iconName]}</span>`;
}

function resolveRowHref(pageKey, itemHref) {
  const pageDir = path.posix.dirname(pageKey);
  return path.posix.relative(pageDir, itemHref) || path.posix.basename(itemHref);
}

function buildSidebarProjectionRow(pageKey, item) {
  const parsed = parseSidebarRow(item.text);
  const referenceIcon = parsed.type === "reference" ? getSidebarReferenceIcon(item.href) : null;
  const rowClasses = [
    "reader-sidebar-row",
    parsed.type === "chapter" ? "reader-sidebar-row--chapter" : "reader-sidebar-row--reference",
  ];
  const isActive = resolveSidebarActivePageKey(pageKey) === item.href;

  if (isActive) {
    rowClasses.push("reader-sidebar-row--active");
  }

  if (referenceIcon) {
    rowClasses.push("reader-sidebar-row--with-icon");
  }

  return [
    `<a class="${rowClasses.join(" ")}" href="${escapeHtml(resolveRowHref(pageKey, item.href))}"${
      isActive ? ' aria-current="page"' : ""
    }>`,
    referenceIcon ? buildSidebarReferenceIcon(referenceIcon) : "",
    parsed.type === "chapter"
      ? `<span class="reader-sidebar-row-index">${escapeHtml(parsed.index)}</span>`
      : "",
    `<span class="reader-sidebar-row-title">${escapeHtml(parsed.title)}</span>`,
    "</a>",
  ].join("");
}

function buildSidebarProjectionSection(pageKey, group) {
  const sectionClasses = ["reader-sidebar-section", `reader-sidebar-section--${group.type}`];

  if (
    group.items.some(function (item) {
      return resolveSidebarActivePageKey(pageKey) === item.href;
    })
  ) {
    sectionClasses.push("reader-sidebar-section--active");
  }

  return [
    `<section class="${sectionClasses.join(" ")}">`,
    '<header class="reader-sidebar-section-header">',
    group.type === "front-matter" ? buildSidebarSectionIcon("front-matter") : "",
    group.kicker
      ? `<span class="reader-sidebar-section-kicker">${escapeHtml(group.kicker)}</span>`
      : "",
    `<span class="reader-sidebar-section-title">${escapeHtml(group.title)}</span>`,
    "</header>",
    '<div class="reader-sidebar-section-body">',
    group.items
      .map(function (item) {
        return buildSidebarProjectionRow(pageKey, item);
      })
      .join(""),
    "</div>",
    "</section>",
  ].join("");
}

function buildSidebarProjection(pageKey, groups) {
  return [
    '<div class="reader-sidebar-projection" aria-hidden="false">',
    groups
      .map(function (group) {
        return buildSidebarProjectionSection(pageKey, group);
      })
      .join(""),
    "</div>",
  ].join("");
}

async function listTargetPages(bookDir) {
  const pages = ["index.html"];
  const chaptersDir = path.join(bookDir, "chapters");
  const chapterEntries = await fs.readdir(chaptersDir, { withFileTypes: true });

  chapterEntries
    .filter(function (entry) {
      return entry.isFile() && entry.name.endsWith(".html");
    })
    .sort(function (left, right) {
      return left.name.localeCompare(right.name);
    })
    .forEach(function (entry) {
      pages.push(path.posix.join("chapters", entry.name));
    });

  return pages;
}

function addProjectedSidebarClass(html) {
  return html.replace(
    /<nav id="mdbook-sidebar" class="([^"]*)"/,
    function (match, className) {
      if (className.includes("book-sidebar-shell--projected")) {
        return match;
      }

      return `<nav id="mdbook-sidebar" class="${className} book-sidebar-shell--projected"`;
    }
  );
}

function setScrollboxAriaHidden(html) {
  return html.replace(
    '<mdbook-sidebar-scrollbox class="sidebar-scrollbox"></mdbook-sidebar-scrollbox>',
    '<mdbook-sidebar-scrollbox class="sidebar-scrollbox" aria-hidden="true"></mdbook-sidebar-scrollbox>'
  );
}

async function injectSidebarProjection(bookDir, pageKey, groups) {
  const filePath = path.join(bookDir, ...pageKey.split("/"));
  const projectionMarkup = buildSidebarProjection(pageKey, groups);
  let html = await fs.readFile(filePath, "utf8");

  if (!html.includes('<div class="reader-sidebar-projection" aria-hidden="true"></div>')) {
    return;
  }

  html = html.replace(
    '<div class="reader-sidebar-projection" aria-hidden="true"></div>',
    projectionMarkup
  );
  html = addProjectedSidebarClass(html);
  html = setScrollboxAriaHidden(html);

  await fs.writeFile(filePath, html);
}

async function main() {
  const bookDir = path.resolve(process.cwd(), process.argv[2] || "book");
  const tocPath = path.join(bookDir, "toc.html");
  const tocHtml = await fs.readFile(tocPath, "utf8");
  const groups = collectSidebarProjectionGroups(tocHtml);
  const pages = await listTargetPages(bookDir);

  if (!groups.length) {
    throw new Error("No sidebar groups were extracted from toc.html");
  }

  for (const pageKey of pages) {
    await injectSidebarProjection(bookDir, toPosixPath(pageKey), groups);
  }
}

main().catch(function (error) {
  console.error(error instanceof Error ? error.message : error);
  process.exitCode = 1;
});
