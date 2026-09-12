# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""pack-tree.py -- pack the chromium checkout for cross-machine distribution.

Walks the chromium/ tree (source + all dependency .git dirs), skips build
outputs and platform-specific caches, writes a plain tar (PAX format for long
paths). Windows bsdtar segfaults (0xC0000005) on this tree; this walker is the
stable replacement (M014 family).

Usage:
  uv run tools/pack-tree.py [--root C:/clean-chrome] [--out chromium-tree.tar]
"""
from __future__ import annotations

import argparse
import sys
import tarfile
from pathlib import Path

EXCLUDE_DIRS = {
    "out",            # build outputs (platform-specific, huge)
    ".cipd_bin",      # platform-specific hook binaries
    "__pycache__",
    ".vpython-root",
}
EXCLUDE_FILES = {
    "chromium-tree.tar",
    "autoninja-dev.log",
    "autoninja-release.log",
    "chromium-152.tar.gz",
}


def main() -> int:
    ap = argparse.ArgumentParser(description="pack chromium tree for distribution")
    ap.add_argument("--root", default="C:/clean-chrome")
    ap.add_argument("--out", default="C:/clean-chrome/chromium-tree.tar")
    args = ap.parse_args()

    root = Path(args.root)
    base = root / "chromium"
    if not base.is_dir():
        raise SystemExit(f"no chromium dir under {root}")

    n = 0
    skipped = 0
    with tarfile.open(args.out, "w", format=tarfile.PAX_FORMAT) as tf:
        # .gclient lives at chromium/ level; include it explicitly.
        for f in base.parent.glob(".gclient*"):
            pass
        gc = root / ".gclient"
        # .gclient is at chromium/.gclient
        gc = base / ".gclient"
        if gc.is_file():
            tf.add(gc, arcname="chromium/.gclient", recursive=False)
            n += 1
        for path in base.rglob("*"):
            rel = path.relative_to(root).as_posix()
            if path.is_dir():
                if path.name in EXCLUDE_DIRS:
                    skipped += 1
                continue
            if not path.is_file():
                continue  # skip anything odd (junction leftovers)
            parts = path.relative_to(root).parts
            if any(p in EXCLUDE_DIRS for p in parts):
                continue
            if path.name in EXCLUDE_FILES:
                continue
            try:
                tf.add(path, arcname=rel, recursive=False)
                n += 1
                if n % 50000 == 0:
                    print(f"... {n} files", flush=True)
            except OSError as e:
                print(f"[skip-file] {rel}: {e}", flush=True)
                skipped += 1

    size_gb = Path(args.out).stat().st_size / 2**30
    print(f"packed {n} files ({size_gb:.1f} GB), skipped {skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
