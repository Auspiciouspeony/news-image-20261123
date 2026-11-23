#!/usr/bin/env python3
"""news-image-20261123: write the 23 November 2026 front page to /output.

The image is rendered by render.py (Pillow, deterministic) and shipped in
this repository as entry.png. This program copies it to the output
directory, verifying the gate rules first: a whole PNG, at most 1 MiB and
at most 1024 by 1024 pixels. No network, no clock, no randomness, so two
runs write byte-identical files.
"""
import os
import shutil
import struct
import sys

MAX_BYTES = 1048576
MAX_DIM = 1024


def check_png(path):
    """Return (width, height) of a PNG, raising on any gate violation."""
    with open(path, "rb") as fh:
        head = fh.read(33)
    if len(head) < 33 or head[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("entry.png is not a PNG file")
    if head[12:16] != b"IHDR":
        raise SystemExit("entry.png has no IHDR chunk")
    width, height = struct.unpack(">II", head[16:24])
    if width > MAX_DIM or height > MAX_DIM:
        raise SystemExit("entry.png is larger than 1024x1024")
    if os.path.getsize(path) > MAX_BYTES:
        raise SystemExit("entry.png is larger than 1 MiB")
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    width, height = check_png(src)
    os.makedirs(out_dir, exist_ok=True)
    try:
        os.chmod(out_dir, 0o755)
    except OSError:
        pass
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    os.chmod(dst, 0o644)
    size = os.path.getsize(dst)
    # Verify the copy before reporting success: the bytes on disk must be
    # exactly the bytes that passed the gate above.
    with open(src, "rb") as fh:
        want = fh.read()
    with open(dst, "rb") as fh:
        got = fh.read()
    if got != want:
        raise SystemExit("output differs from entry.png after copy")
    print("wrote %s (%dx%d, %d bytes)" % (dst, width, height, size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
