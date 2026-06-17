import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

import { listSiteEditions } from "./shared/site-editions.mjs";
import { runMdbook } from "./shared/run-mdbook.mjs";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(scriptDir, "..");
const publicDir = path.join(rootDir, "public");

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

function copyIntoPublic() {
  copyPathSync(path.join(rootDir, "assets"), path.join(publicDir, "assets"));
  fs.mkdirSync(path.join(publicDir, "fr"), { recursive: true });
  copyPathSync(path.join(rootDir, "assets"), path.join(publicDir, "fr", "assets"));
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

function main() {
  fs.rmSync(publicDir, { recursive: true, force: true });
  fs.mkdirSync(publicDir, { recursive: true });

  runNodeScript("scripts/generate-index-page.mjs", ["--output-root", publicDir]);
  runNodeScript("scripts/generate-legal-pages.mjs", ["--output-root", publicDir]);
  runNodeScript("scripts/generate-chapters-page.mjs", ["--output-root", publicDir]);
  copyIntoPublic();

  listSiteEditions().forEach(buildBookEdition);
}

main();
