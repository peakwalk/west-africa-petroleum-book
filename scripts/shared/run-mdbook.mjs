import { spawnSync } from "node:child_process";
import fs from "node:fs";

const CANDIDATES = [process.env.MDBOOK_BIN, "mdbook", "/opt/homebrew/bin/mdbook"].filter(Boolean);

export function runMdbook(args, options = {}) {
  let lastError = null;

  for (const candidate of CANDIDATES) {
    const isAbsolute = candidate.startsWith("/");
    if (isAbsolute && !fs.existsSync(candidate)) {
      continue;
    }

    const result = spawnSync(candidate, args, {
      cwd: options.cwd,
      env: process.env,
      stdio: "inherit",
    });

    if (!result.error && result.status === 0) {
      return;
    }

    if (result.error && result.error.code === "ENOENT") {
      lastError = result.error;
      continue;
    }

    if (result.status !== 0) {
      throw new Error(`mdBook command failed with exit status ${result.status}`);
    }
  }

  throw lastError || new Error("Unable to locate an mdBook binary.");
}
