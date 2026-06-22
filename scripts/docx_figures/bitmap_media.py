from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
from zipfile import ZipFile

from .model import FigureRecord
from .raster_assets import find_sips_binary


def _normalized_extension(target: str) -> str:
    suffix = Path(target).suffix.lower()
    if suffix == ".jpeg":
        return ".jpg"
    return suffix


def output_name_for_blip(
    *,
    figure_number: int,
    blip_target: str,
    index: int,
    total: int,
) -> str:
    suffix = ".png"
    if total == 1:
        return f"figure-{figure_number:03d}{suffix}"
    label = chr(ord("a") + index)
    return f"figure-{figure_number:03d}-{label}{suffix}"


def extract_bitmap_blip(docx_path: Path, blip_target: str) -> bytes:
    with ZipFile(docx_path) as archive:
        return archive.read(blip_target)


def write_bitmap_blip_png(docx_path: Path, blip_target: str, output_path: Path) -> None:
    source_bytes = extract_bitmap_blip(docx_path, blip_target)
    source_suffix = _normalized_extension(blip_target)
    if source_suffix == ".png":
        output_path.write_bytes(source_bytes)
        return

    sips_binary = find_sips_binary()
    if sips_binary is None:
        raise RuntimeError(f"No PNG encoder is available for {blip_target}.")

    with tempfile.TemporaryDirectory() as tmpdir:
        source_path = Path(tmpdir) / f"source{source_suffix or '.img'}"
        source_path.write_bytes(source_bytes)
        result = subprocess.run(
            [
                str(sips_binary),
                "-s",
                "format",
                "png",
                str(source_path),
                "--out",
                str(output_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0 or not output_path.exists():
            raise RuntimeError(
                f"Failed to convert {blip_target} to PNG.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )


def render_bitmap_figure_assets(
    *,
    docx_path: Path,
    records: list[FigureRecord],
    output_dir: Path,
) -> list[tuple[int, Path]]:
    rendered: list[tuple[int, Path]] = []
    for record in records:
        if not record.objects.blip_targets:
            continue
        total = len(record.objects.blip_targets)
        for index, blip_target in enumerate(record.objects.blip_targets):
            output_name = output_name_for_blip(
                figure_number=record.number,
                blip_target=blip_target,
                index=index,
                total=total,
            )
            output_path = output_dir / output_name
            write_bitmap_blip_png(docx_path, blip_target, output_path)
            rendered.append((record.number, output_path))
    return rendered
