import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { SITE_ORIGIN } from "./shared/book-seo.mjs";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(scriptDir, "..");
const requestedPublicDir = process.argv[2] || path.join(rootDir, "public");
const publicDir = path.resolve(rootDir, requestedPublicDir);
const requestedSitemaps = process.argv.slice(3);
const robotsBasePath = path.join(rootDir, "config", "robots.base.txt");

function readRobotsBase() {
  if (!fs.existsSync(robotsBasePath)) {
    return "";
  }

  return fs.readFileSync(robotsBasePath, "utf8").trimEnd();
}

function buildRobotsTxt() {
  const sections = [];
  const robotsBase = readRobotsBase();
  const sitemaps =
    requestedSitemaps.length > 0 ? requestedSitemaps : [`${SITE_ORIGIN}/book-sitemap.xml`];

  if (robotsBase) {
    sections.push(robotsBase);
  }

  sitemaps.forEach((sitemapUrl) => {
    sections.push(`Sitemap: ${sitemapUrl}`);
  });

  return `${sections.join("\n")}\n`;
}

function main() {
  fs.writeFileSync(path.join(publicDir, "robots.txt"), buildRobotsTxt());
}

main();
