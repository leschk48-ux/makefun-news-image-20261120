#!/usr/bin/env python3
"""Entry point for make.fun news-image-20261120.

Copies the pre-generated entry.png into output/entry.png so the bounty
runner has a canonical artifact location. Deterministic: the copy is
byte-for-byte identical to entry.png every run. Standard library only.

Also mirrors to /output/entry.png when that directory exists (some
runners mount /output as the artifact volume).
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
LOCAL_OUT = os.path.join(HERE, "output")
GLOBAL_OUT = "/output"


def copy_to(directory):
    os.makedirs(directory, exist_ok=True)
    dest = os.path.join(directory, "entry.png")
    shutil.copyfile(SRC, dest)
    return dest


def main():
    if not os.path.isfile(SRC):
        print(f"error: {SRC} not found; run python3 generate.py first", file=sys.stderr)
        return 1
    dests = [copy_to(LOCAL_OUT)]
    if os.path.isdir(GLOBAL_OUT):
        dests.append(copy_to(GLOBAL_OUT))
    for dest in dests:
        print(f"copied entry.png -> {dest} ({os.path.getsize(dest)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
