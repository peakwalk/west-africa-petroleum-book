from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


class BuildSiteCompatTests(unittest.TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(ROOT_DIR / "public", ignore_errors=True)

    def test_build_site_succeeds_when_fs_cp_sync_is_unavailable(self) -> None:
        compat_script = """
const fs = require("fs");
fs.cpSync = undefined;
const { syncBuiltinESMExports } = require("module");
const { pathToFileURL } = require("url");
const path = require("path");
syncBuiltinESMExports();
import(pathToFileURL(path.join(process.cwd(), "scripts/build_site.mjs")).href)
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
"""

        result = subprocess.run(
            ["node", "-e", compat_script],
            cwd=ROOT_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
