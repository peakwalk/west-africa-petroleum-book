from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT_DIR / "artifacts" / "stakeholder_icons_trace_rebuild"


class StakeholderTraceRebuildAcceptanceTests(unittest.TestCase):
    @unittest.skipUnless(
        shutil.which("magick") and shutil.which("rsvg-convert"),
        "stakeholder trace rebuild acceptance check requires magick and rsvg-convert",
    )
    def test_generated_trace_rebuild_package_passes_baseline_acceptance(self) -> None:
        self.assertTrue(PACKAGE_DIR.exists(), f"Missing package dir: {PACKAGE_DIR}")
        subprocess.run(
            [
                "python3",
                "scripts/check_stakeholder_trace_rebuild_acceptance.py",
                "--package-dir",
                str(PACKAGE_DIR),
                "--profile",
                "baseline",
            ],
            cwd=ROOT_DIR,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    @unittest.skipUnless(
        shutil.which("magick") and shutil.which("rsvg-convert"),
        "stakeholder trace rebuild acceptance check requires magick and rsvg-convert",
    )
    def test_generated_trace_rebuild_package_passes_production_polish_acceptance(self) -> None:
        self.assertTrue(PACKAGE_DIR.exists(), f"Missing package dir: {PACKAGE_DIR}")
        subprocess.run(
            [
                "python3",
                "scripts/check_stakeholder_trace_rebuild_acceptance.py",
                "--package-dir",
                str(PACKAGE_DIR),
                "--profile",
                "production",
            ],
            cwd=ROOT_DIR,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


if __name__ == "__main__":
    unittest.main()
