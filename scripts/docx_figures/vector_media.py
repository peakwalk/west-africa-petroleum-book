from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path
from typing import Iterator
from zipfile import ZipFile

EMF_COMMENT_RECORD = 70
EMFPLUS_OBJECT_RECORD = 0x4008
EMFPLUS_DRAW_IMAGE_POINTS_RECORD = 0x401B
EMFPLUS_SAVE_RECORD = 0x4025
EMFPLUS_RESTORE_RECORD = 0x4026
EMFPLUS_SET_WORLD_TRANSFORM_RECORD = 0x402A
EMFPLUS_IMAGE_OBJECT_TYPE = 5
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

Rgba = tuple[int, int, int, int]
RasterRows = list[list[Rgba]]


def _read_member_bytes(docx_path: Path, member: str) -> bytes:
    with ZipFile(docx_path) as archive:
        return archive.read(member)


def _parse_emf_comments(payload: bytes) -> Iterator[bytes]:
    offset = 0
    while offset + 8 <= len(payload):
        record_type, record_size = struct.unpack_from("<II", payload, offset)
        if record_size <= 0 or offset + record_size > len(payload):
            break
        if record_type == EMF_COMMENT_RECORD:
            comment_size = struct.unpack_from("<I", payload, offset + 8)[0]
            comment = payload[offset + 12 : offset + 12 + comment_size]
            if comment.startswith(b"EMF+"):
                yield comment
        offset += record_size


def _parse_emfplus_records(comment: bytes) -> Iterator[tuple[int, int, bytes]]:
    offset = 4
    while offset + 12 <= len(comment):
        record_type, flags = struct.unpack_from("<HH", comment, offset)
        size, data_size = struct.unpack_from("<II", comment, offset + 4)
        if size < 12 or offset + size > len(comment):
            break
        data = comment[offset + 12 : offset + size]
        if len(data) < data_size:
            break
        yield record_type, flags, data[:data_size]
        offset += size


def _decode_png(png_bytes: bytes) -> tuple[int, int, RasterRows]:
    if not png_bytes.startswith(PNG_SIGNATURE):
        raise ValueError("Expected a PNG payload.")

    offset = 8
    width = 0
    height = 0
    color_type = -1
    idat_chunks: list[bytes] = []
    while offset + 8 <= len(png_bytes):
        chunk_length = struct.unpack(">I", png_bytes[offset : offset + 4])[0]
        chunk_type = png_bytes[offset + 4 : offset + 8]
        chunk_data = png_bytes[offset + 8 : offset + 8 + chunk_length]
        offset += 12 + chunk_length
        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, _, _, interlace = struct.unpack(
                ">IIBBBBB",
                chunk_data,
            )
            if bit_depth != 8 or interlace != 0:
                raise ValueError("Only non-interlaced 8-bit PNG chunks are supported.")
        elif chunk_type == b"IDAT":
            idat_chunks.append(chunk_data)
        elif chunk_type == b"IEND":
            break

    channels_by_color_type = {0: 1, 2: 3, 4: 2, 6: 4}
    channels = channels_by_color_type.get(color_type)
    if channels is None:
        raise ValueError(f"Unsupported PNG color type {color_type}.")

    raw = zlib.decompress(b"".join(idat_chunks))
    stride = width * channels
    rows: RasterRows = []
    cursor = 0
    previous_row = bytearray(stride)

    for _ in range(height):
        filter_type = raw[cursor]
        cursor += 1
        row = bytearray(raw[cursor : cursor + stride])
        cursor += stride

        if filter_type == 1:
            for index in range(channels, stride):
                row[index] = (row[index] + row[index - channels]) & 0xFF
        elif filter_type == 2:
            for index in range(stride):
                row[index] = (row[index] + previous_row[index]) & 0xFF
        elif filter_type == 3:
            for index in range(stride):
                left = row[index - channels] if index >= channels else 0
                up = previous_row[index]
                row[index] = (row[index] + ((left + up) // 2)) & 0xFF
        elif filter_type == 4:
            for index in range(stride):
                left = row[index - channels] if index >= channels else 0
                up = previous_row[index]
                up_left = previous_row[index - channels] if index >= channels else 0
                predictor = left + up - up_left
                choose_left = abs(predictor - left)
                choose_up = abs(predictor - up)
                choose_up_left = abs(predictor - up_left)
                best = (
                    left
                    if choose_left <= choose_up and choose_left <= choose_up_left
                    else up
                    if choose_up <= choose_up_left
                    else up_left
                )
                row[index] = (row[index] + best) & 0xFF
        elif filter_type != 0:
            raise ValueError(f"Unsupported PNG filter type {filter_type}.")

        pixels: list[Rgba] = []
        if color_type == 6:
            for index in range(0, stride, 4):
                pixels.append(tuple(row[index : index + 4]))  # type: ignore[arg-type]
        elif color_type == 2:
            for index in range(0, stride, 3):
                red, green, blue = row[index : index + 3]
                pixels.append((red, green, blue, 255))
        elif color_type == 0:
            for value in row:
                pixels.append((value, value, value, 255))
        elif color_type == 4:
            for index in range(0, stride, 2):
                gray, alpha = row[index : index + 2]
                pixels.append((gray, gray, gray, alpha))
        rows.append(pixels)
        previous_row = row

    return width, height, rows


def _encode_png(width: int, height: int, rows: RasterRows) -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    raw = bytearray()
    for row in rows:
        raw.append(0)
        for red, green, blue, alpha in row:
            raw.extend((red, green, blue, alpha))

    png = bytearray(PNG_SIGNATURE)
    png.extend(
        chunk(
            b"IHDR",
            struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0),
        )
    )
    png.extend(chunk(b"IDAT", zlib.compress(bytes(raw), 9)))
    png.extend(chunk(b"IEND", b""))
    return bytes(png)


def _apply_transform(transform: tuple[float, float, float, float, float, float], point: tuple[int, int]) -> tuple[float, float]:
    x, y = point
    a, b, c, d, tx, ty = transform
    return (a * x + c * y + tx, b * x + d * y + ty)


def _parse_draw_image_points(record_data: bytes) -> list[tuple[int, int]]:
    if len(record_data) < 28:
        raise ValueError("DrawImagePoints record is too short.")
    count = struct.unpack_from("<I", record_data, 24)[0]
    points: list[tuple[int, int]] = []
    offset = 28
    for _ in range(count):
        if offset + 4 > len(record_data):
            break
        points.append(struct.unpack_from("<hh", record_data, offset))
        offset += 4
    return points


def render_vector_blip_png(docx_path: Path, blip_target: str) -> tuple[int, int, bytes]:
    emf_bytes = _read_member_bytes(docx_path, blip_target)
    current_transform = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
    saved_transforms: dict[int, tuple[float, float, float, float, float, float]] = {}
    image_objects: dict[int, tuple[int, int, RasterRows]] = {}
    placements: list[tuple[tuple[int, int, RasterRows], tuple[float, float], tuple[float, float], tuple[float, float]]] = []

    for comment in _parse_emf_comments(emf_bytes):
        for record_type, flags, record_data in _parse_emfplus_records(comment):
            if record_type == EMFPLUS_SET_WORLD_TRANSFORM_RECORD:
                current_transform = struct.unpack("<6f", record_data)
            elif record_type == EMFPLUS_SAVE_RECORD:
                state_id = struct.unpack_from("<I", record_data, 0)[0]
                saved_transforms[state_id] = current_transform
            elif record_type == EMFPLUS_RESTORE_RECORD:
                state_id = struct.unpack_from("<I", record_data, 0)[0]
                current_transform = saved_transforms.get(state_id, current_transform)
            elif record_type == EMFPLUS_OBJECT_RECORD:
                object_id = flags & 0xFF
                object_type = (flags >> 8) & 0xFF
                png_offset = record_data.find(PNG_SIGNATURE)
                if object_type == EMFPLUS_IMAGE_OBJECT_TYPE and png_offset >= 0:
                    image_objects[object_id] = _decode_png(record_data[png_offset:])
            elif record_type == EMFPLUS_DRAW_IMAGE_POINTS_RECORD:
                object_id = flags & 0xFF
                image = image_objects.get(object_id)
                if image is None:
                    continue
                points = _parse_draw_image_points(record_data)
                if len(points) < 3:
                    continue
                p0, p1, p2 = (_apply_transform(current_transform, point) for point in points[:3])
                placements.append((image, p0, p1, p2))

    if not placements:
        raise ValueError(f"No EMF+ image placements could be recovered from {blip_target}.")

    min_x = math.floor(min(min(p0[0], p1[0], p2[0]) for _, p0, p1, p2 in placements))
    min_y = math.floor(min(min(p0[1], p1[1], p2[1]) for _, p0, p1, p2 in placements))
    max_x = math.ceil(max(max(p0[0], p1[0], p2[0]) for _, p0, p1, p2 in placements))
    max_y = math.ceil(max(max(p0[1], p1[1], p2[1]) for _, p0, p1, p2 in placements))
    width = max_x - min_x
    height = max_y - min_y
    canvas: RasterRows = [[(255, 255, 255, 255) for _ in range(width)] for _ in range(height)]

    for (source_width, source_height, pixels), p0, p1, p2 in placements:
        target_x = int(round(min(p0[0], p1[0], p2[0]) - min_x))
        target_y = int(round(min(p0[1], p1[1], p2[1]) - min_y))
        target_width = max(1, int(round(abs(p1[0] - p0[0]) or math.dist(p0, p1))))
        target_height = max(1, int(round(abs(p2[1] - p0[1]) or math.dist(p0, p2))))
        flip_x = p1[0] < p0[0]
        flip_y = p2[1] < p0[1]

        for output_y in range(target_height):
            sample_y = target_height - 1 - output_y if flip_y else output_y
            source_y = min(source_height - 1, int(sample_y * source_height / target_height))
            row = pixels[source_y]
            canvas_y = target_y + output_y
            if canvas_y < 0 or canvas_y >= height:
                continue
            canvas_row = canvas[canvas_y]
            for output_x in range(target_width):
                sample_x = target_width - 1 - output_x if flip_x else output_x
                source_x = min(source_width - 1, int(sample_x * source_width / target_width))
                red, green, blue, alpha = row[source_x]
                if alpha == 0:
                    continue
                canvas_x = target_x + output_x
                if canvas_x < 0 or canvas_x >= width:
                    continue
                background_red, background_green, background_blue, _ = canvas_row[canvas_x]
                alpha_ratio = alpha / 255.0
                canvas_row[canvas_x] = (
                    int(red * alpha_ratio + background_red * (1.0 - alpha_ratio)),
                    int(green * alpha_ratio + background_green * (1.0 - alpha_ratio)),
                    int(blue * alpha_ratio + background_blue * (1.0 - alpha_ratio)),
                    255,
                )

    return width, height, _encode_png(width, height, canvas)
