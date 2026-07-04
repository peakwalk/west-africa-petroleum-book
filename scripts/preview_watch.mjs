import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";

const DEFAULT_WATCH_ROOTS = ["assets", "config", "editions", "scripts", "theme"];
const DEFAULT_DEBOUNCE_MS = 200;
const SCAN_INTERVAL_MS = 250;

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(scriptDir, "..");

function fail(message) {
  console.error(`[preview-watch] ${message}`);
  process.exit(1);
}

function parseArgs(argv) {
  const args = {
    debounceMs: DEFAULT_DEBOUNCE_MS,
    scanMs: SCAN_INTERVAL_MS,
    reloadTokenFile: "",
    watchPaths: [],
    command: [],
  };

  const separatorIndex = argv.indexOf("--");
  const optionArgs = separatorIndex === -1 ? argv : argv.slice(0, separatorIndex);
  args.command = separatorIndex === -1 ? [] : argv.slice(separatorIndex + 1);

  for (let index = 0; index < optionArgs.length; index += 1) {
    const arg = optionArgs[index];
    if (arg === "--reload-token-file") {
      args.reloadTokenFile = optionArgs[index + 1] || "";
      index += 1;
      continue;
    }

    if (arg === "--watch-path") {
      const watchPath = optionArgs[index + 1] || "";
      if (watchPath) {
        args.watchPaths.push(watchPath);
      }
      index += 1;
      continue;
    }

    if (arg === "--debounce-ms") {
      const value = Number(optionArgs[index + 1] || "");
      if (!Number.isFinite(value) || value < 0) {
        fail(`Invalid --debounce-ms value: ${optionArgs[index + 1] || ""}`);
      }
      args.debounceMs = value;
      index += 1;
      continue;
    }

    if (arg === "--scan-ms") {
      const value = Number(optionArgs[index + 1] || "");
      if (!Number.isFinite(value) || value <= 0) {
        fail(`Invalid --scan-ms value: ${optionArgs[index + 1] || ""}`);
      }
      args.scanMs = value;
      index += 1;
      continue;
    }

    fail(`Unknown argument: ${arg}`);
  }

  if (!args.reloadTokenFile) {
    fail("Missing required --reload-token-file argument");
  }

  if (args.command.length === 0) {
    fail("Missing build command. Pass it after --");
  }

  if (args.watchPaths.length === 0) {
    args.watchPaths = DEFAULT_WATCH_ROOTS.map((watchRoot) => path.join(rootDir, watchRoot));
  }

  return args;
}

function writeReloadToken(reloadTokenFile) {
  fs.mkdirSync(path.dirname(reloadTokenFile), { recursive: true });
  fs.writeFileSync(reloadTokenFile, `${Date.now()}\n`, "utf8");
}

function readWatchState(targetPath, entries) {
  let stats;

  try {
    stats = fs.statSync(targetPath);
  } catch (error) {
    if (error && error.code === "ENOENT") {
      return;
    }
    throw error;
  }

  entries.set(targetPath, `${stats.isDirectory() ? "d" : "f"}:${stats.mtimeMs}:${stats.size}`);

  if (!stats.isDirectory()) {
    return;
  }

  for (const entry of fs.readdirSync(targetPath, { withFileTypes: true })) {
    if (entry.isDirectory()) {
      readWatchState(path.join(targetPath, entry.name), entries);
      continue;
    }

    if (entry.isFile()) {
      readWatchState(path.join(targetPath, entry.name), entries);
    }
  }
}

function runCommand(command, cwd, onSpawn) {
  return new Promise((resolve) => {
    const child = spawn(command[0], command.slice(1), {
      cwd,
      env: process.env,
      stdio: "inherit",
    });

    onSpawn(child);

    child.on("exit", (code, signal) => {
      if (signal) {
        resolve(1);
        return;
      }

      resolve(code ?? 1);
    });

    child.on("error", (error) => {
      console.error(`[preview-watch] Failed to start build command: ${error.message}`);
      resolve(1);
    });
  });
}

const options = parseArgs(process.argv.slice(2));
const reloadTokenFile = path.resolve(rootDir, options.reloadTokenFile);
const watchPaths = options.watchPaths.map((watchPath) => path.resolve(rootDir, watchPath));

let buildTimer = null;
let scanTimer = null;
let buildInProgress = false;
let rerunRequested = false;
let activeChild = null;
const pendingReasons = new Set();
let previousState = new Map();

function captureWatchState() {
  const nextState = new Map();
  for (const watchPath of watchPaths) {
    readWatchState(watchPath, nextState);
  }
  return nextState;
}

function diffWatchState(nextState) {
  const reasons = [];

  for (const [entryPath, signature] of nextState) {
    if (!previousState.has(entryPath)) {
      reasons.push(`added:${path.relative(rootDir, entryPath)}`);
      continue;
    }

    if (previousState.get(entryPath) !== signature) {
      reasons.push(`changed:${path.relative(rootDir, entryPath)}`);
    }
  }

  for (const entryPath of previousState.keys()) {
    if (!nextState.has(entryPath)) {
      reasons.push(`removed:${path.relative(rootDir, entryPath)}`);
    }
  }

  previousState = nextState;
  return reasons;
}

function scanForChanges() {
  const reasons = diffWatchState(captureWatchState());
  for (const reason of reasons) {
    scheduleBuild(reason);
  }
}

function scheduleBuild(reason) {
  pendingReasons.add(reason);

  if (buildInProgress) {
    rerunRequested = true;
    return;
  }

  if (buildTimer) {
    clearTimeout(buildTimer);
  }

  buildTimer = setTimeout(() => {
    buildTimer = null;
    void runBuild();
  }, options.debounceMs);
}

async function runBuild() {
  if (buildInProgress) {
    rerunRequested = true;
    return;
  }

  buildInProgress = true;
  const reasons = [...pendingReasons];
  pendingReasons.clear();

  console.error(`[preview-watch] Rebuilding after ${reasons.join(", ")}`);

  const exitCode = await runCommand(options.command, rootDir, (child) => {
    activeChild = child;
  });
  activeChild = null;

  if (exitCode === 0) {
    writeReloadToken(reloadTokenFile);
    console.error("[preview-watch] Rebuild complete.");
  } else {
    console.error(`[preview-watch] Rebuild failed with exit code ${exitCode}.`);
  }

  buildInProgress = false;

  if (rerunRequested || pendingReasons.size > 0) {
    rerunRequested = false;
    scheduleBuild("queued-change");
  }
}

function shutdown(signal) {
  if (buildTimer) {
    clearTimeout(buildTimer);
    buildTimer = null;
  }

  if (scanTimer) {
    clearInterval(scanTimer);
    scanTimer = null;
  }

  if (activeChild) {
    activeChild.kill(signal);
  }
}

process.on("SIGINT", () => {
  shutdown("SIGINT");
  process.exit(0);
});

process.on("SIGTERM", () => {
  shutdown("SIGTERM");
  process.exit(0);
});

writeReloadToken(reloadTokenFile);
previousState = captureWatchState();
scanTimer = setInterval(scanForChanges, options.scanMs);
console.error("[preview-watch] Watching render-affecting sources for changes.");
