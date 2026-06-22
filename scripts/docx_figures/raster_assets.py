from __future__ import annotations

from pathlib import Path
import shutil
import subprocess


def find_cwebp_binary() -> Path | None:
    resolved = shutil.which("cwebp")
    if resolved:
        return Path(resolved)
    for candidate in (Path("/opt/homebrew/bin/cwebp"), Path("/usr/local/bin/cwebp")):
        if candidate.exists():
            return candidate
    return None


def find_sips_binary() -> Path | None:
    resolved = shutil.which("sips")
    if resolved:
        return Path(resolved)
    candidate = Path("/usr/bin/sips")
    if candidate.exists():
        return candidate
    return None


def ensure_lossless_webp_outputs(
    *,
    output_dir: Path,
    figure_numbers: list[int],
    cwebp_binary: Path | None = None,
    sips_binary: Path | None = None,
    cwebp_args: list[str] | None = None,
    detect_binaries: bool = True,
) -> list[int]:
    binary = cwebp_binary if not detect_binaries else cwebp_binary or find_cwebp_binary()
    sips = sips_binary if not detect_binaries else sips_binary or find_sips_binary()
    if binary is None and sips is None:
        return []

    rendered: list[int] = []
    cwebp_extra_args = cwebp_args or ["-z", "9"]
    for figure_number in figure_numbers:
        png_path = output_dir / f"figure-{figure_number:03d}.png"
        webp_path = output_dir / f"figure-{figure_number:03d}.webp"
        if not png_path.exists():
            continue
        if binary is not None:
            result = subprocess.run(
                [
                    str(binary),
                    "-quiet",
                    "-lossless",
                    *cwebp_extra_args,
                    str(png_path),
                    "-o",
                    str(webp_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        else:
            result = subprocess.run(
                [
                    str(sips),
                    "-s",
                    "format",
                    "webp",
                    str(png_path),
                    "--out",
                    str(webp_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        if result.returncode == 0 and webp_path.exists():
            rendered.append(figure_number)
    return rendered
