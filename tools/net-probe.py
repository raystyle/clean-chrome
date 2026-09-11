# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""chromium 构建网络通道稳定性评估(量化,全平台,零依赖)。

对 chromium 构建相关的七个网络通道做多轮采样,输出成功率与延迟统计,
并给出综合判定:直接走 R001 三节标准检出,还是启用网络受阻替代路线。
通道集与判级依据 2026-09-11 实战(M006/M007/M008)。

用法:
  uv run tools/net-probe.py                  # 每通道 3 轮
  uv run tools/net-probe.py --count 5        # 加密采样
  uv run tools/net-probe.py --timeout 30     # 放宽单轮超时
  uv run tools/net-probe.py --repo google/skia  # codeload 通道改测指定仓

仅做轻探测(ls-remote / HEAD 请求 / ssh -T),不产生大流量。
注意: git 通道的"握手通"不代表大 pack 传输通,判定要结合 M007 现象。
依赖仓兜底: 凡 GitHub 有官方镜像的仓,可 aria2 从 codeload 按
revision(sha/tag)拉 tar.gz 落地工作区,git 元数据留待窗口期归化(R001 三节)。
已知镜像映射: skia->google/skia, devtools-frontend->ChromeDevTools/devtools-frontend,
quiche->google/quiche, v8->v8/v8, angle->google/angle, pdfium->google/pdfium,
boringssl->google/boringssl。
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

CHANNELS = [
    ("googlesource-git", "git", "https://chromium.googlesource.com/chromium/src.git"),
    ("googlesource-web", "http", "https://chromium.googlesource.com/"),
    ("github-git-https", "git", "https://github.com/chromium/chromium.git"),
    ("github-ssh-22", "ssh", "git@github.com"),
    ("github-ssh-443", "ssh443", "git@ssh.github.com"),
    ("codeload-http", "http", "https://codeload.github.com/{repo}/tar.gz/HEAD"),
    ("cipd-api", "http",
     "https://chrome-infra-packages.appspot.com/_ah/api/repo/v1/instance/resolve"
     "?package_name=infra/3pp/tools/git/windows-amd64&version=latest"),
]


def probe(kind: str, target: str, timeout: int) -> tuple[bool, str]:
    """单轮探测,返回 (成功, 备注)。"""
    try:
        if kind == "git":
            r = subprocess.run(
                ["git", "ls-remote", target, "HEAD"],
                capture_output=True, text=True, timeout=timeout)
            ok = bool(re.match(r"^[0-9a-f]{40}", r.stdout.strip()))
            return ok, "" if ok else (r.stderr.strip() or r.stdout.strip())[:60]
        if kind in ("ssh", "ssh443"):
            cmd = ["ssh", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes",
                   "-o", "StrictHostKeyChecking=accept-new", "-T", target]
            if kind == "ssh443":
                cmd += ["-p", "443"]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            ok = "successfully authenticated" in (r.stdout + r.stderr)
            return ok, "" if ok else (r.stderr.strip() or r.stdout.strip())[:60]
        # http
        req = urllib.request.Request(target, method="HEAD",
                                     headers={"User-Agent": "net-probe/1"})
        with urllib.request.urlopen(req, timeout=min(timeout, 15)) as resp:
            ok = 200 <= resp.status < 400
            return ok, "" if ok else f"HTTP{resp.status}"
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception as e:  # noqa: BLE001 探测器要吞一切异常
        return False, str(e)[:60]


def sample_channel(name: str, kind: str, target: str, count: int, timeout: int) -> dict:
    ok_n, times = 0, []
    for _ in range(count):
        t0 = time.perf_counter()
        ok, _note = probe(kind, target, timeout)
        ms = (time.perf_counter() - t0) * 1000
        if ok:
            ok_n += 1
            times.append(ms)
        time.sleep(0.3)
    rate = round(100 * ok_n / count)
    return {
        "channel": name,
        "ok": f"{ok_n}/{count}",
        "rate": rate,
        "avg_ms": round(sum(times) / len(times)) if times else None,
        "grade": "GREEN" if rate == 100 else ("YELLOW" if rate >= 50 else "RED"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="chromium 构建网络通道评估")
    ap.add_argument("--count", type=int, default=3, help="每通道采样轮数")
    ap.add_argument("--timeout", type=int, default=20, help="单轮超时秒数")
    ap.add_argument("--repo", default="chromium/chromium",
                    help="codeload 通道探测的仓(org/name)")
    args = ap.parse_args()

    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    channels = [(n, k, t.format(repo=args.repo) if "{repo}" in t else t)
                for n, k, t in CHANNELS]

    print(f"== net-probe: {args.count} 轮/通道, 单轮超时 {args.timeout}s, "
          f"repo={args.repo} ==")
    with ThreadPoolExecutor(max_workers=len(channels)) as pool:
        rows = list(pool.map(
            lambda c: sample_channel(c[0], c[1], c[2], args.count, args.timeout),
            channels))

    rows.sort(key=lambda r: (r["grade"] not in ("RED",), r["channel"]))
    w = max(len(r["channel"]) for r in rows) + 2
    print(f"{'channel':<{w}}{'ok':>6}  {'rate':>5}  {'avg_ms':>8}  grade")
    for r in rows:
        avg = r["avg_ms"] if r["avg_ms"] is not None else "-"
        print(f"{r['channel']:<{w}}{r['ok']:>6}  {str(r['rate']) + '%':>5}  {avg:>8}  {r['grade']}")

    by = {r["channel"]: r for r in rows}
    print("-- 判定 --")
    gs = by["googlesource-git"]
    if gs["grade"] == "GREEN":
        print("googlesource git 稳定: 直接走 R001 三节标准检出流程。")
    else:
        print(f"googlesource git 不稳({gs['rate']}%): "
              "走 R001 三节替代路线(aria2 codeload tarball + SSH 归化 + insteadOf 注入)。")
        if any(by[c]["grade"] == "GREEN" for c in ("github-ssh-22", "github-ssh-443")):
            print("GitHub SSH 可用: 主仓归化与镜像注入可行。")
        if by["codeload-http"]["grade"] == "GREEN":
            print("codeload 可用: tarball 落地路线可行(主仓与有镜像的依赖仓)。")
    print("脚注: git 通道仅测握手(ls-remote);大 pack 传输被掐时握手仍可能绿。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
