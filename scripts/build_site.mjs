import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

import { listSiteEditions } from "./shared/site-editions.mjs";
import { runMdbook } from "./shared/run-mdbook.mjs";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(scriptDir, "..");
const publicDir = path.join(rootDir, "public");
const assetsDir = path.join(rootDir, "assets");

const SHARED_PUBLIC_ASSET_PATHS = [
  "css",
  "js/ga.js",
  "icons/homepage-sprite.svg",
  "images/prototype-hero-graywhite-left.webp",
  "images/prototype-hero-graywhite-right.webp",
  "images/upstream-atlas-apple-touch-icon.png",
  "images/upstream-atlas-favicon-32.png",
  "images/upstream-atlas-favicon.png",
  "images/upstream-atlas-hero-v7-clean-left.webp",
  "images/upstream-atlas-icon.png",
  "images/upstream-atlas-nav-logo.webp",
];

const FRENCH_ONLY_PUBLIC_ASSET_PATHS = [
  "icons/homepage/icon-audience-operators.svg",
  "icons/homepage/icon-audience-policy.svg",
  "icons/homepage/icon-audience-research.svg",
  "icons/homepage/icon-industry-monitoring.svg",
  "icons/homepage/icon-intelligence.svg",
  "icons/homepage/icon-research.svg",
];

const ENGLISH_ONLY_PUBLIC_ASSET_PATHS = [
  "icons/homepage/hero-arrow.svg",
  "icons/homepage-cropped/icon-audience-operators.webp",
  "icons/homepage-cropped/icon-audience-policy.webp",
  "icons/homepage-cropped/icon-audience-research.webp",
  "icons/homepage-cropped/icon-exploration.webp",
  "icons/homepage-cropped/icon-fiscal.webp",
  "icons/homepage-cropped/icon-industry-monitoring.webp",
  "icons/homepage-cropped/icon-intelligence.webp",
  "icons/homepage-cropped/icon-production.webp",
  "icons/homepage-cropped/icon-regulation.webp",
  "icons/homepage-cropped/icon-research.webp",
  "images/homepage-west-africa-map-panel.svg",
  "images/upstream-atlas-hero-book.webp",
];

function copyPathSync(sourcePath, destinationPath) {
  if (typeof fs.cpSync === "function") {
    const sourceStats = fs.lstatSync(sourcePath);
    if (sourceStats.isDirectory()) {
      fs.cpSync(sourcePath, destinationPath, { recursive: true });
    } else {
      fs.cpSync(sourcePath, destinationPath);
    }
    return;
  }

  const sourceStats = fs.lstatSync(sourcePath);

  if (sourceStats.isSymbolicLink()) {
    const linkTarget = fs.readlinkSync(sourcePath);
    fs.mkdirSync(path.dirname(destinationPath), { recursive: true });
    try {
      fs.symlinkSync(linkTarget, destinationPath);
    } catch (error) {
      if (error && error.code === "EEXIST") {
        fs.rmSync(destinationPath, { recursive: true, force: true });
        fs.symlinkSync(linkTarget, destinationPath);
      } else {
        throw error;
      }
    }
    return;
  }

  if (sourceStats.isDirectory()) {
    fs.mkdirSync(destinationPath, { recursive: true });
    for (const entry of fs.readdirSync(sourcePath)) {
      copyPathSync(path.join(sourcePath, entry), path.join(destinationPath, entry));
    }
    return;
  }

  fs.mkdirSync(path.dirname(destinationPath), { recursive: true });
  fs.copyFileSync(sourcePath, destinationPath);
}

function runNodeScript(relativeScriptPath, args = []) {
  const result = spawnSync(process.execPath, [path.join(rootDir, relativeScriptPath), ...args], {
    cwd: rootDir,
    env: process.env,
    stdio: "inherit",
  });

  if (result.status !== 0) {
    throw new Error(`${relativeScriptPath} failed with exit status ${result.status}`);
  }
}

function copyAssetManifest(destinationAssetsDir, assetRelativePaths) {
  assetRelativePaths.forEach((relativePath) => {
    copyPathSync(path.join(assetsDir, relativePath), path.join(destinationAssetsDir, relativePath));
  });
}

function copyIntoPublic() {
  const englishAssetsDir = path.join(publicDir, "assets");
  const frenchAssetsDir = path.join(publicDir, "fr", "assets");

  fs.mkdirSync(englishAssetsDir, { recursive: true });
  fs.mkdirSync(frenchAssetsDir, { recursive: true });

  copyAssetManifest(englishAssetsDir, SHARED_PUBLIC_ASSET_PATHS);
  copyAssetManifest(englishAssetsDir, ENGLISH_ONLY_PUBLIC_ASSET_PATHS);
  copyAssetManifest(frenchAssetsDir, SHARED_PUBLIC_ASSET_PATHS);
  copyAssetManifest(frenchAssetsDir, FRENCH_ONLY_PUBLIC_ASSET_PATHS);
}

function buildBookEdition(edition) {
  const bookRoot = path.resolve(rootDir, edition.bookRoot);
  const bookDest = path.join(publicDir, edition.routePrefix || "", "book");

  fs.mkdirSync(path.dirname(bookDest), { recursive: true });
  runMdbook(["build", "--dest-dir", bookDest, bookRoot], { cwd: rootDir });
  runNodeScript("scripts/strip_mdbook_onunload.mjs", [bookDest]);
  runNodeScript("scripts/build_static_reader_sidebar.mjs", [bookDest]);
  runNodeScript("scripts/build_reader_page_meta.mjs", [
    bookDest,
    edition.summaryPath,
    edition.sourceRoot,
  ]);
  runNodeScript("scripts/localize_reader_shell.mjs", [
    bookDest,
    edition.locale,
    edition.routePrefix || "",
  ]);
}

function injectBookSeo(edition) {
  const bookDest = path.join(publicDir, edition.routePrefix || "", "book");
  runNodeScript("scripts/inject_book_seo.mjs", [bookDest, edition.locale]);
}

function main() {
  fs.rmSync(publicDir, { recursive: true, force: true });
  fs.mkdirSync(publicDir, { recursive: true });

  runNodeScript("scripts/generate-index-page.mjs", ["--output-root", publicDir]);
  runNodeScript("scripts/generate-legal-pages.mjs", ["--output-root", publicDir]);
  runNodeScript("scripts/generate-chapters-page.mjs", ["--output-root", publicDir]);
  copyIntoPublic();

  const editions = listSiteEditions();
  editions.forEach(buildBookEdition);
  editions.forEach(injectBookSeo);
  runNodeScript("scripts/generate_legacy_book_redirects.mjs", [publicDir]);
  runNodeScript("scripts/generate_book_sitemap.mjs", [publicDir]);
  runNodeScript("scripts/generate_site_robots.mjs", [publicDir]);
}

main();
