import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(scriptDir, "..");
const requestedDir = process.argv[2] || "book";
const outputDir = path.resolve(rootDir, requestedDir);
const unloadSnippet = "window.onunload = function() { };";

if (!fs.existsSync(outputDir)) {
  throw new Error(`Missing mdBook output directory: ${outputDir}`);
}

const bookBundlePath = fs
  .readdirSync(outputDir)
  .find((fileName) => /^book-.*\.js$/.test(fileName));

if (!bookBundlePath) {
  throw new Error(`Missing generated mdBook core bundle in: ${outputDir}`);
}

const absoluteBundlePath = path.join(outputDir, bookBundlePath);
const source = fs.readFileSync(absoluteBundlePath, "utf8");

if (!source.includes(unloadSnippet)) {
  process.exit(0);
}

fs.writeFileSync(absoluteBundlePath, source.replace(unloadSnippet, ""));
