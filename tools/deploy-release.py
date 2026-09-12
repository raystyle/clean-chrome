# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""deploy-release.py -- deploy the Release chromium build to a standalone dir.

Copies the chrome.exe runtime set (whitelist: browser binaries + runtime DLLs
+ data paks + locales + inspector overlay) from out/Release into a
self-contained target directory, plus initial_preferences for silent first
run (S003). Build tools (torque/protoc/mksnapshot/...), pdbs, libs and Siso
state are never copied -- the target stays a clean runnable browser dir.

Usage:
  uv run tools/deploy-release.py [--src .../out/Release] [--dest DIR]
      [--prefs .../out/Dev/initial_preferences]

Default dest is C:/browse-rs/<version> (version tag from the SxS manifest),
so C:/browse-rs stays a browse root holding versioned self-contained dirs.
Refuses to touch an existing non-empty dest unless it looks like a previous
deployment (contains chrome.exe), in which case it is rebuilt clean.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

# chrome.exe runtime set, excluding build tools and debug symbol data.
FILES = [
    # browser core
    "chrome.exe", "chrome.dll", "chrome_elf.dll", "chrome_proxy.exe",
    "chrome_pwa_launcher.exe", "chrome_wer.dll",
    "elevation_service.exe", "notification_helper.exe",
    "elevated_tracing_service.exe", "eventlog_provider.dll",
    # v8 / icu data
    "icudtl.dat", "snapshot_blob.bin", "v8_context_snapshot.bin",
    # resource paks
    "resources.pak", "chrome_100_percent.pak", "chrome_200_percent.pak",
    # VC / windows runtime dlls shipped in the output dir
    "vcruntime140.dll", "vcruntime140_1.dll", "msvcp140.dll",
    "msvcp140_atomic_wait.dll", "vccorlib140.dll",
    "d3dcompiler_47.dll", "dbgcore.dll", "dbghelp.dll",
    # graphics stack (ANGLE / SwiftShader / DX12 shaders)
    "libEGL.dll", "libGLESv2.dll", "vk_swiftshader.dll", "vulkan-1.dll",
    "dxcompiler.dll", "dxil.dll",
]

# Subdirectories the browser reads at runtime. Missing ones are skipped
# (e.g. angledata only exists on some configurations).
DIRS = [
    "locales",                              # 456 packed locales
    "resources",                            # accessibility + inspector_overlay (CDP)
    "MEIPreload",
    "hyphen-data",
    "PrivacySandboxAttestationsPreloaded",
    "angledata",
]


def main() -> int:
    ap = argparse.ArgumentParser(description="deploy Release chromium to a standalone dir")
    ap.add_argument("--src", default="C:/clean-chrome/chromium/src/out/Release")
    ap.add_argument("--dest", default=None,
                    help="default: C:/browse-rs/<version> (version read from the SxS manifest)")
    ap.add_argument("--prefs", default="C:/clean-chrome/chromium/src/out/Dev/initial_preferences")
    args = ap.parse_args()

    src = Path(args.src)
    manifests = sorted(src.glob("*.manifest"))
    if not manifests:
        raise SystemExit(f"no SxS version manifest (*.manifest) under {src}")
    if args.dest:
        dest = Path(args.dest)
    else:
        dest = Path("C:/browse-rs") / f"chromium-{manifests[0].stem}"
    print(f"deploying to {dest}")
    if not (src / "chrome.exe").is_file():
        raise SystemExit(f"no chrome.exe under {src}")

    if dest.exists() and any(dest.iterdir()):
        if (dest / "chrome.exe").exists():
            print(f"[rebuild] {dest} looks like a previous deployment; recreating clean")
            shutil.rmtree(dest)
        else:
            raise SystemExit(f"{dest} exists and is not a previous deployment; refusing")
    dest.mkdir(parents=True, exist_ok=True)

    missing = [n for n in FILES if not (src / n).is_file()]
    if missing:
        raise SystemExit(f"missing runtime files in {src}: {', '.join(missing)}")

    total = 0
    for name in FILES:
        shutil.copy2(src / name, dest / name)
        total += 1
    # SxS version manifest next to chrome.exe -- without it Windows refuses to
    # start the exe ("side-by-side configuration is incorrect"). Name carries
    # the tag, so glob instead of hardcoding.
    for mf in manifests:
        shutil.copy2(mf, dest / mf.name)
        total += 1
        print(f"[ok]   {mf.name} (SxS manifest, required at runtime)")
    for d in DIRS:
        sdir = src / d
        if not sdir.is_dir():
            print(f"[skip] {d}/ not present")
            continue
        shutil.copytree(sdir, dest / d, dirs_exist_ok=True)
        total += sum(1 for _ in sdir.rglob("*") if _.is_file())
        print(f"[dir]  {d}/")

    prefs = Path(args.prefs)
    if prefs.is_file():
        shutil.copy2(prefs, dest / "initial_preferences")
        total += 1
        print("[ok]   initial_preferences (silent first run, S003)")
    else:
        print("[warn] no initial_preferences found; first run will not be silenced")

    size_mb = sum(f.stat().st_size for f in dest.rglob("*") if f.is_file()) / 2**20
    print(f"\nDeployed {total} files ({size_mb:.0f} MB) -> {dest}")
    print(f"Run:  {dest}\\chrome.exe   (no args needed: port 9222 by default)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
