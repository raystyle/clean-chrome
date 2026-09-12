# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""net-audit.py -- capture and summarize the browser's outbound network talk.

Launches the deployed chromium with --log-net-log on a throwaway profile,
lets background services spin up (signin probes, variations, telemetry...),
then kills it and aggregates every host the browser tried to reach straight
from the net-log. NetLog covers browser-process traffic too, which the CDP
Network domain does not -- that is where accounts.google.com & friends hide.

Usage:
  uv run tools/net-audit.py [--exe C:/browse-rs/chromium-152.0.7977.84/chrome.exe]
                            [--secs 25] [--keep]

Output: per-host table (attempts + sample URLs), split google/telemetry vs
the rest, plus the raw netlog path for deeper digging.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlsplit

HOST_RE = re.compile(r'"host":\s*"([^"]+)"')
URL_RE = re.compile(r'"url":\s*"([^"]+)"')

# hosts considered google-touch / telemetry for the split view.
GOOGLE_HINTS = (
    "google.com", "googleapis.com", "googlesource.com", "gstatic.com",
    "googleusercontent.com", "ggpht.com", "googlevideo.com", "blogger.com",
    "crashlytics", "chromium",
)


def main() -> int:
    ap = argparse.ArgumentParser(description="audit outbound network of chromium")
    ap.add_argument("--exe", default="C:/browse-rs/chromium-152.0.7977.84/chrome.exe")
    ap.add_argument("--secs", type=int, default=25)
    ap.add_argument("--keep", action="store_true", help="keep the netlog file")
    args = ap.parse_args()

    tmp = Path(tempfile.mkdtemp(prefix="netaudit-"))
    netlog = tmp / "netlog.json"
    udd = tmp / "profile"

    exe = [str(args.exe), f"--log-net-log={netlog}",
           "--net-log-capture-mode=Everything", f"--user-data-dir={udd}",
           "--no-first-run"]
    print(f"launching: {args.exe}")
    print(f"netlog: {netlog}  (profile: {udd})")
    p = subprocess.Popen(exe)
    try:
        time.sleep(args.secs)
    finally:
        # NetLog only lands on disk at graceful shutdown; a hard kill leaves
        # a 0-byte file. taskkill without /F sends WM_CLOSE to the window,
        # which walks the normal shutdown path and flushes the log.
        subprocess.run(["taskkill", "/PID", str(p.pid)],
                       capture_output=True)
        try:
            p.wait(timeout=15)
        except subprocess.TimeoutExpired:
            subprocess.run(["taskkill", "/F", "/PID", str(p.pid)],
                           capture_output=True)
            p.wait(timeout=10)
    # extra beat so the log gets flushed on shutdown
    time.sleep(2)

    if not netlog.is_file():
        raise SystemExit("netlog was not produced")

    text = netlog.read_text(encoding="utf-8", errors="replace")
    hosts = Counter(HOST_RE.findall(text))
    urls_by_host: dict[str, set[str]] = defaultdict(set)
    for u in URL_RE.findall(text):
        h = urlsplit(u).hostname or ""
        if h:
            urls_by_host[h].add(u)

    google, other = [], []
    for h, n in hosts.most_common():
        (google if any(g in h for g in GOOGLE_HINTS) else other).append((h, n))

    def dump(title: str, rows: list[tuple[str, int]]) -> None:
        print(f"\n=== {title} ({len(rows)} hosts) ===")
        for h, n in rows:
            sample = sorted(urls_by_host.get(h, []))[:2]
            for s in sample:
                s = s[:110]
            print(f"{n:5d}  {h}" + (f"   e.g. {sample[0][:90]}" if sample else ""))

    dump("GOOGLE / TELEMETRY touchpoints", google)
    dump("other hosts", other)
    print(f"\nnetlog kept at {netlog}" if args.keep else f"\nraw netlog: {netlog}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
