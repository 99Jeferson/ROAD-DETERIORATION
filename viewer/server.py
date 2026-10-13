"""Serve a lightweight, local viewer for the Uganda Roads shapefile."""

from __future__ import annotations

import json
import struct
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "uganda_roads"
VIEWER_DIR = Path(__file__).resolve().parent


def read_dbf(path: Path) -> tuple[list[str], list[dict[str, object]]]:
    """Read the dBASE attribute table using only the Python standard library."""
    content = path.read_bytes()
    if len(content) < 33:
        raise ValueError("DBF file is too short to contain a header")

    record_count = struct.unpack_from("<I", content, 4)[0]
    header_length, record_length = struct.unpack_from("<HH", content, 8)
    fields: list[tuple[str, str, int, int]] = []
    offset = 32
    while offset < header_length and content[offset] != 0x0D:
        descriptor = content[offset : offset + 32]
        if len(descriptor) != 32:
            raise ValueError("DBF field descriptor is truncated")
        name = descriptor[:11].split(b"\0", 1)[0].decode("ascii")
        fields.append((name, chr(descriptor[11]), descriptor[16], descriptor[17]))
        offset += 32

    rows: list[dict[str, object]] = []
    for row_number in range(record_count):
        start = header_length + row_number * record_length
        record = content[start : start + record_length]
        if len(record) != record_length:
            raise ValueError(f"DBF record {row_number + 1} is truncated")
        if record[:1] == b"*":
            continue
        cursor = 1
        row: dict[str, object] = {}
        for name, kind, width, decimals in fields:
            raw = record[cursor : cursor + width]
            cursor += width
            value = raw.decode("cp1252").strip()
            if not value:
                row[name] = None
            elif kind in ("N", "F"):
                number = float(value)
                row[name] = int(number) if decimals == 0 else number
            else:
                row[name] = value
        rows.append(row)

    return [field[0] for field in fields], rows


def read_polylines(path: Path) -> list[list[list[list[float]]]]:
    """Read PolyLine records as feature -> parts -> [longitude, latitude]."""
    content = path.read_bytes()
    if len(content) < 100 or struct.unpack_from(">i", content, 0)[0] != 9994:
        raise ValueError("SHP header is missing or invalid")
    shape_type = struct.unpack_from("<i", content, 32)[0]
    if shape_type != 3:
        raise ValueError(f"Expected PolyLine (shape type 3), found {shape_type}")

    features: list[list[list[list[float]]]] = []
    offset = 100
    while offset < len(content):
        if offset + 8 > len(content):
            raise ValueError("SHP record header is truncated")
        _record_number, content_words = struct.unpack_from(">2i", content, offset)
        start = offset + 8
        end = start + content_words * 2
        if end > len(content):
            raise ValueError("SHP record content is truncated")
        record = content[start:end]
        record_type = struct.unpack_from("<i", record, 0)[0]
        if record_type == 0:
            features.append([])
        elif record_type == 3:
            part_count, point_count = struct.unpack_from("<2i", record, 36)
            parts = list(struct.unpack_from(f"<{part_count}i", record, 44))
            points_offset = 44 + part_count * 4
            points = [
                list(struct.unpack_from("<2d", record, points_offset + i * 16))
                for i in range(point_count)
            ]
            parts.append(point_count)
            features.append(
                [points[parts[i] : parts[i + 1]] for i in range(part_count)]
            )
        else:
            raise ValueError(f"Unexpected shape type {record_type} in SHP record")
        offset = end

    return features


def load_features() -> tuple[list[str], list[dict[str, object]]]:
    """Combine geometry and attributes, refusing mismatched component files."""
    fields, rows = read_dbf(DATA_DIR / "Uganda_Roads.dbf")
    geometries = read_polylines(DATA_DIR / "Uganda_Roads.shp")
    if len(rows) != len(geometries):
        raise ValueError(
            f"SHP/DBF count mismatch: {len(geometries)} geometries, {len(rows)} rows"
        )
    features = [
        {"id": index, "properties": row, "parts": geometries[index]}
        for index, row in enumerate(rows)
    ]
    return fields, features


FIELDS, FEATURES = load_features()


class ViewerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, directory=str(VIEWER_DIR), **kwargs)

    def do_GET(self) -> None:
        if urlparse(self.path).path == "/api/roads":
            body = json.dumps(
                {"fields": FIELDS, "features": FEATURES},
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        if urlparse(self.path).path == "/":
            self.path = "/index.html"
        super().do_GET()


def main() -> None:
    address = ("127.0.0.1", 8000)
    print(f"Uganda Roads viewer: http://{address[0]}:{address[1]}")
    print(f"Loaded {len(FEATURES)} road features from {DATA_DIR}")
    ThreadingHTTPServer(address, partial(ViewerHandler)).serve_forever()


if __name__ == "__main__":
    main()
