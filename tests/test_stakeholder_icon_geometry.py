from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


class StakeholderIconGeometryTests(unittest.TestCase):
    @unittest.skipUnless(
        shutil.which("magick"),
        "stakeholder icon geometry check requires magick",
    )
    def test_stakeholder_icon_geometry_checker_passes(self) -> None:
        subprocess.run(
            ["python3", "scripts/check_stakeholder_icon_geometry.py"],
            cwd=ROOT_DIR,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
