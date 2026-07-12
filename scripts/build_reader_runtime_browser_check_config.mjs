import { getPreserveOutlinePaths } from "./shared/book-page-variants.mjs";

function toChapterPaths(paths) {
  return paths.map((pagePath) => `chapters/${pagePath}`);
}

const config = {
  skippedPages: ["chapters/cover.html", "chapters/front-matter.html"],
  preserveOutlinePages: {
    en: toChapterPaths(getPreserveOutlinePaths("en")),
    fr: toChapterPaths(getPreserveOutlinePaths("fr")),
  },
  smokePages: {
    en: [
      "index.html",
      "chapters/list-of-figures.html",
      "chapters/chapter-05-hydrocarbon-value-chain.html",
      "chapters/chapter-10-socio-political-determinants.html",
      "chapters/chapter-11-general-conclusion.html",
    ],
    fr: [
      "index.html",
      "chapters/list-of-figures.html",
      "chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html",
      "chapters/chapter-05-key-socio-political-determinants-of-oil-sector-performance.html",
      "chapters/general-conclusion.html",
    ],
  },
};

process.stdout.write(JSON.stringify(config, null, 2) + "\n");
