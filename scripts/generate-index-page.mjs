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

async function main() {
  await Promise.all(
    listSiteEditions().map(async (edition) => {
      const mainContentPath = path.join(ROOT, edition.sourceRoot, "index-main.html");
      const outputPath = resolveEditionPath(edition, "index.html");
      const mainContent = await fs.readFile(mainContentPath, "utf8");
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

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
