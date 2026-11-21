#!/usr/bin/env python3
"""Verification for make.fun news-image-20261120.

Checks the entry image against the expected deterministic artifact and
confirms main.py reproduces it byte-identically across runs.

Checks:
  1. entry.png exists in the repo directory.
  2. entry.png is a PNG file (8-byte signature).
  3. entry.png is 1024x1024 pixels (parsed from the IHDR chunk).
  4. entry.png is at most 1,048,576 bytes (1 MiB).
  5. entry.png sha256 matches the verified expected digest.
  6. Running main.py twice produces identical output/entry.png bytes.

Prints a PASS/FAIL line per check and exits non-zero on any failure.
Standard library only.
"""
import hashlib
import os
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENTRY = os.path.join(HERE, "entry.png")
OUTPUT = os.path.join(HERE, "output", "entry.png")
EXPECTED_SHA256 = "3f46b62dbf1bd2f5be0f519ac844e8f43e8b6d6511da748e5ac9d0e873aa48db"
EXPECTED_W = 1024
EXPECTED_H = 1024
MAX_BYTES = 1048576
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

failures = []


def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    line = f"[{status}] {name}"
    if detail:
        line += f" — {detail}"
    print(line)
    if not ok:
        failures.append(name)


def read_png_size(path):
    """Return (width, height) parsed from the PNG IHDR chunk."""
    with open(path, "rb") as fh:
        header = fh.read(8)
        if header != PNG_SIGNATURE:
            raise ValueError("not a PNG file (bad signature)")
        chunk_len = struct.unpack(">I", fh.read(4))[0]
        chunk_type = fh.read(4)
        if chunk_type != b"IHDR" or chunk_len != 13:
            raise ValueError("first chunk is not IHDR")
        width, height = struct.unpack(">II", fh.read(8))
    return width, height


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    # 1. entry.png exists
    exists = os.path.isfile(ENTRY)
    check("entry.png exists", exists, ENTRY if exists else "missing")

    if not exists:
        print("FAIL: cannot run remaining checks without entry.png")
        return 1

    # 2. PNG signature
    with open(ENTRY, "rb") as fh:
        signature = fh.read(8)
    check("PNG signature", signature == PNG_SIGNATURE,
          "signature ok" if signature == PNG_SIGNATURE else f"got {signature!r}")

    # 3. Dimensions 1024x1024
    try:
        width, height = read_png_size(ENTRY)
        check("dimensions 1024x1024", (width, height) == (EXPECTED_W, EXPECTED_H),
              f"{width}x{height}")
    except ValueError as exc:
        check("dimensions 1024x1024", False, str(exc))

    # 4. Size at most 1 MiB
    size = os.path.getsize(ENTRY)
    check("size <= 1048576 bytes", size <= MAX_BYTES, f"{size} bytes")

    # 5. sha256 matches expected digest
    digest = sha256_file(ENTRY)
    check("sha256 matches expected", digest == EXPECTED_SHA256,
          f"sha256={digest}")

    # 6. main.py is deterministic across two runs
    for run in (1, 2):
        result = subprocess.run(
            [sys.executable, "main.py"],
            cwd=HERE,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            check(f"main.py run {run} exits 0", False, result.stderr.strip())
            print("FAIL: main.py did not complete; skipping determinism check")
            return 1
        check(f"main.py run {run} exits 0", True, result.stdout.strip())
        with open(OUTPUT, "rb") as fh:
            data = fh.read()
        if run == 1:
            first_bytes = data
        else:
            check("two main.py runs produce identical output bytes",
                  data == first_bytes,
                  f"run1={len(first_bytes)} bytes, run2={len(data)} bytes")

    if failures:
        print(f"\nFAIL: {len(failures)} check(s) failed: {', '.join(failures)}")
        return 1
    print("\nPASS: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
