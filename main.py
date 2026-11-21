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
    # Guard against a truncated copy: the runner's artifact must be
    # byte-identical to the source image, so verify the size matches.
    if os.path.getsize(dest) != os.path.getsize(SRC):
        raise IOError(f"copy to {dest} is incomplete")
    return dest


def main():
    if not os.path.isfile(SRC):
        print(f"error: {SRC} not found; run python3 generate.py first", file=sys.stderr)
        return 1
    dests = []
    # Primary target: the grader's output dir. The grader sets
    # MAKEFUN_OUTPUT_DIR (usually /output) and mounts the repository
    # read-only, so the local mirror below must never fail the run.
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or GLOBAL_OUT
    if os.path.isdir(out_dir):
        try:
            dests.append(copy_to(out_dir))
        except OSError as exc:
            print(f"warning: cannot write {out_dir}: {exc}", file=sys.stderr)
    # Best-effort mirror next to the script; skip it quietly when the
    # repository tree is read-only (as in the grader).
    try:
        dests.append(copy_to(LOCAL_OUT))
    except OSError as exc:
        print(f"warning: cannot write {LOCAL_OUT}: {exc}", file=sys.stderr)
    if not dests:
        print("error: no output written", file=sys.stderr)
        return 1
    for dest in dests:
        print(f"copied entry.png -> {dest} ({os.path.getsize(dest)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
