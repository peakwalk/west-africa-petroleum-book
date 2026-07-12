import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { buildBookCanonicalUrl, escapeHtml } from "./shared/book-seo.mjs";
import { listLegacyBookRedirects } from "./shared/book-page-maps.mjs";
import { listSiteEditions, resolveEditionPath } from "./shared/site-editions.mjs";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(scriptDir, "..");
const requestedPublicDir = process.argv[2] || path.join(rootDir, "public");
const publicDir = path.resolve(rootDir, requestedPublicDir);

function relativeTargetHref(sourcePageKey, targetPageKey) {
  const relativePath = path.posix.relative(path.posix.dirname(sourcePageKey), targetPageKey);
  return relativePath.startsWith(".") ? relativePath : `./${relativePath}`;
}

function buildRedirectPage({ edition, sourcePageKey, targetPageKey }) {
  const targetHref = relativeTargetHref(sourcePageKey, targetPageKey);
  const canonicalUrl = buildBookCanonicalUrl(edition, targetPageKey);

  return `<!doctype html>
<html lang="${escapeHtml(edition.locale)}">
  <head>
    <meta charset="utf-8">
    <title>Redirecting to Upstream Atlas</title>
    <meta name="robots" content="noindex,follow">
    <link rel="canonical" href="${escapeHtml(canonicalUrl)}">
    <meta http-equiv="refresh" content="0; url=${escapeHtml(targetHref)}">
    <script>
      const target = new URL(${JSON.stringify(targetHref)}, window.location.href);
      target.search = window.location.search;
      target.hash = window.location.hash;
      window.location.replace(target.href);
    </script>
  </head>
  <body>
    <p>This chapter has moved. <a href="${escapeHtml(targetHref)}">Continue to the chapter</a>.</p>
  </body>
</html>
`;
}

function main() {
  listSiteEditions().forEach((edition) => {
    const bookDir = resolveEditionPath(edition, "book", publicDir);

    listLegacyBookRedirects(edition.locale).forEach(({ sourcePageKey, targetPageKey }) => {
      const targetPath = path.join(bookDir, ...targetPageKey.split("/"));
      if (!fs.existsSync(targetPath)) {
        throw new Error(`Missing legacy redirect target: ${targetPageKey}`);
      }

      const sourcePath = path.join(bookDir, ...sourcePageKey.split("/"));
      fs.mkdirSync(path.dirname(sourcePath), { recursive: true });
      fs.writeFileSync(
        sourcePath,
        buildRedirectPage({ edition, sourcePageKey, targetPageKey })
      );
    });
  });
}

main();
