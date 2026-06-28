import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { buildBookSeoRecords, isCanonicalBookPageKey } from "./shared/book-seo.mjs";
import { listSiteEditions, resolveEditionPath } from "./shared/site-editions.mjs";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(scriptDir, "..");
const requestedPublicDir = process.argv[2] || path.join(rootDir, "public");
const publicDir = path.resolve(rootDir, requestedPublicDir);

function buildSitemapXml(urls) {
  const urlEntries = urls
    .map(
      (url) =>
        `  <url>\n    <loc>${url}</loc>\n  </url>`
    )
    .join("\n");

  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urlEntries}\n</urlset>\n`;
}

function main() {
  const urls = [];

  listSiteEditions().forEach((edition) => {
    const bookDir = resolveEditionPath(edition, "book", publicDir);
    const records = buildBookSeoRecords({ bookDir, edition, rootDir });

    for (const [pageKey, record] of records.entries()) {
      if (!isCanonicalBookPageKey(pageKey)) {
        continue;
      }

      urls.push(record.canonicalUrl);
    }
  });

  fs.writeFileSync(path.join(publicDir, "book-sitemap.xml"), buildSitemapXml(urls));
}

main();
