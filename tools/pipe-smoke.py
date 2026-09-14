# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""pipe-smoke.py -- launch clean-chrome over the CDP pipe channel and verify.

Implements the upstream Windows contract (content/browser/devtools/
devtools_agent_host_impl.cc AdoptPipes): the launcher creates two pipes,
passes the child-read and child-write handle values via
--remote-debugging-io-pipes=<in>,<out> and speaks ASCIIZ CDP
(JSON messages NUL-terminated). POSIX launchers instead wire fd 3/4.

Channel selection is done by the browser via CLEAN_CHROME_DEBUG
(port default | pipe | both, S005).

Usage:
  uv run tools/pipe-smoke.py --exe C:/clean-chrome/chromium/src/out/Release/chrome.exe \
      [--mode pipe|both] [--keep]
"""
from __future__ import annotations

import argparse
import json
import msvcrt
import os
import socket
import subprocess
import sys
import time


def port_listening(port: int) -> bool:
    s = socket.socket()
    s.settimeout(2)
    try:
        s.connect(("127.0.0.1", port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def main() -> int:
    ap = argparse.ArgumentParser(description="clean-chrome pipe channel smoke")
    ap.add_argument("--exe", default="C:/clean-chrome/chromium/src/out/Release/chrome.exe")
    ap.add_argument("--mode", default="pipe", choices=["pipe", "both"],
                    help="CLEAN_CHROME_DEBUG value to set (default pipe)")
    ap.add_argument("--profile", default="C:/temp/pipe-smoke-profile")
    ap.add_argument("--timeout", type=int, default=20)
    ap.add_argument("--keep", action="store_true", help="keep browser running")
    args = ap.parse_args()

    in_r, in_w = os.pipe()     # child reads in_r; we write in_w
    out_r, out_w = os.pipe()   # child writes out_w; we read out_r
    os.set_inheritable(in_r, True)
    os.set_inheritable(out_w, True)
    in_h = msvcrt.get_osfhandle(in_r)
    out_h = msvcrt.get_osfhandle(out_w)

    env = dict(os.environ)
    env["CLEAN_CHROME_DEBUG"] = args.mode
    cmd = [
        args.exe,
        "--remote-debugging-io-pipes=%d,%d" % (in_h, out_h),
        "--user-data-dir=" + args.profile,
    ]
    proc = subprocess.Popen(cmd, env=env, close_fds=False)
    print("[launch] pid=%d mode=%s io-pipes=%d,%d" % (proc.pid, args.mode, in_h, out_h))

    try:
        request = json.dumps({"id": 1, "method": "Target.getTargets"}).encode() + b"\0"
        os.write(in_w, request)
        deadline = time.time() + args.timeout
        response = b""
        while time.time() < deadline and b"\0" not in response:
            chunk = os.read(out_r, 65536)
            if chunk:
                response += chunk
        if b"\0" not in response:
            print("[fail] no CDP response within %ds (raw %d bytes)" % (args.timeout, len(response)))
            return 1
        msg = json.loads(response.split(b"\0")[0])
        result = msg.get("result", msg)
        version = result.get("product") or result.get("browserVersion") or json.dumps(result)[:120]
        print("[cdp] id=%s Target.getBrowserVersion -> %s" % (msg.get("id"), version))

        listening = port_listening(9222)
        expect = args.mode == "both"
        print("[port] 9222 listening=%s (expected %s)" % (listening, expect))
        if listening != expect:
            print("[fail] port state mismatch")
            return 1
        print("[ok] mode=%s pipe-CDP roundtrip + port state correct" % args.mode)
        return 0
    finally:
        if not args.keep:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
            for fd in (in_r, in_w, out_r, out_w):
                try:
                    os.close(fd)
                except OSError:
                    pass


if __name__ == "__main__":
    sys.exit(main())
