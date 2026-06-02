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
const MAIN_CONTENT_PATH = path.join(ROOT, "src", "index-main.html");
const OUTPUT_PATH = path.join(ROOT, "index.html");

async function main() {
  const mainContent = await fs.readFile(MAIN_CONTENT_PATH, "utf8");
  const html = `<!doctype html>
<html lang="en">
  <head>
${renderLandingHead({
  description:
    "A professional online edition of Exploration and Exploitation of Petroleum Resources in West Africa.",
  title: "Exploration and Exploitation of Petroleum Resources in West Africa",
})}
  </head>
  <body class="landing-shell">
${renderLandingHeader({ currentPage: "home" })}

${mainContent.trim()}

${renderLandingFooter({ currentPage: "home" })}
  </body>
</html>
`;

  await fs.writeFile(OUTPUT_PATH, html, "utf8");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
