# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""check:文档即代码骨架合规检查(PE-01 至 PE-12)。

用法: uv run check.py [目标项目]
退出码: 0 全部通过(含 SKIP)/ 1 存在 FAIL / 2 出错。检查只读,不改目标项目。
规则对象:AGENTS 五节合同、docs/adr 与 docs/requirements 的 ADR/REQ 状态机与索引一致、
写作规范(六态/标题/禁字)与引用断链。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mdrules import file_violations  # noqa: E402

AGENT_SECTIONS = ["Commands", "Must", "Must not", "Read first"]
DOC_DIRS = ["adr", "requirements", "guides", "diary", "research"]
ADR_STATUS = {"proposed", "accepted", "superseded"}
REQ_STATUS = {"draft", "implemented", "rejected"}
SIX_STATES = r"\[(实证|推断|经验|记忆|假设|直觉)[:\]]"
_BAD_NAME = re.compile(r"[()\s:]")


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _frontmatter(text: str) -> dict[str, str]:
    """解析 --- 围住的 YAML frontmatter 为扁平键值(列表/空值按原文串返回)。"""
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    fm: dict[str, str] = {}
    for ln in text[4:end].splitlines():
        if ":" in ln and not ln.startswith((" ", "-", "\t")):
            k, v = ln.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm


def _numbered(d: Path, prefix: str) -> list[tuple[Path, str]]:
    """目录下 (文件, frontmatter) 对;跳过 README 与模板。"""
    out = []
    if d.is_dir():
        for p in sorted(d.glob("*.md")):
            if p.name in ("README.md",) or p.name.startswith("0000-template"):
                continue
            out.append((p, _frontmatter(_read(p))))
    return out


def check(root: Path) -> tuple[list[tuple[str, str, str]], bool]:
    """返回 (结果列表[(编号, 状态, 说明)], ok)。状态:PASS/FAIL/SKIP。"""
    r: list[tuple[str, str, str]] = []

    # PE-01 AGENTS 五节合同(Commands/Must/Must not/Read first 四硬节 + 环境软节)
    agents = _read(root / "AGENTS.md")
    if not agents:
        r.append(("PE-01", "FAIL", "AGENTS.md 不存在"))
    else:
        heads = re.findall(r"^##\s+(.+?)\s*$", agents, re.M)
        miss = [s for s in AGENT_SECTIONS if s not in heads]
        note = "五节合同齐备" if not miss and "环境" in heads else (
            f"缺节: {', '.join(miss)}" if miss else "四硬节齐备,缺可选环境节")
        r.append(("PE-01", "FAIL" if miss else "PASS", note))

    # PE-02 docs/adr 目录与索引
    ok2 = (root / "docs" / "adr").is_dir() and (root / "docs" / "adr" / "README.md").is_file()
    r.append(("PE-02", "PASS" if ok2 else "FAIL",
              "docs/adr 目录与 README 索引在位" if ok2 else "缺 docs/adr 目录或其 README.md"))

    # PE-03 docs/requirements 目录与索引
    ok3 = (root / "docs" / "requirements").is_dir() and \
        (root / "docs" / "requirements" / "README.md").is_file()
    r.append(("PE-03", "PASS" if ok3 else "FAIL",
              "docs/requirements 目录与 README 索引在位" if ok3 else "缺 docs/requirements 目录或其 README.md"))

    # PE-04 CLAUDE.md 单行桥接(存在才查)
    claude = root / "CLAUDE.md"
    if not claude.exists():
        r.append(("PE-04", "SKIP", "CLAUDE.md 不存在"))
    else:
        lines = [ln for ln in _read(claude).splitlines() if ln.strip()]
        ok = len(lines) == 1 and lines[0].strip() == "@AGENTS.md"
        r.append(("PE-04", "PASS" if ok else "FAIL",
                  "" if ok else f"应仅一行 @AGENTS.md,实际 {len(lines)} 行"))

    # PE-05 docs 下文件名规范(无空格/括号/冒号;README 豁免)
    bad: list[str] = []
    if (root / "docs").is_dir():
        for p in (root / "docs").rglob("*.md"):
            if p.name == "README.md":
                continue
            if _BAD_NAME.search(p.name):
                bad.append(p.relative_to(root).as_posix())
    r.append(("PE-05", "FAIL" if bad else "PASS",
              f"命名含空格/括号/冒号: {', '.join(bad[:5])}" if bad else "文件名规范"))

    # PE-06 ADR 命名与状态机
    adrs = _numbered(root / "docs" / "adr", "ADR")
    adr_bad: list[str] = []
    adr_ids = {fm.get("id") or p.stem for p, fm in adrs}
    for p, fm in adrs:
        rel = p.relative_to(root).as_posix()
        if not re.match(r"^ADR-\d{4}", p.stem):
            adr_bad.append(f"{rel}(命名非 ADR-NNNN)")
            continue
        status = fm.get("status", "")
        if status not in ADR_STATUS:
            adr_bad.append(f"{rel}(status 非法: {status or '缺失'})")
            continue
        sup = fm.get("superseded_by", "")
        if status == "superseded" and (sup in ("", "null") or sup not in adr_ids):
            adr_bad.append(f"{rel}(superseded_by 悬空: {sup or '缺失'})")
    has_adr = bool(adrs)
    r.append(("PE-06", "FAIL" if adr_bad else ("PASS" if has_adr else "SKIP"),
              f"{'; '.join(adr_bad[:4])}" if adr_bad else ("ADR 状态机合法" if has_adr else "adr 空,跳过")))

    # PE-07 REQ 命名与状态机(implemented 须带 trace)
    reqs = _numbered(root / "docs" / "requirements", "REQ")
    req_bad: list[str] = []
    for p, fm in reqs:
        rel = p.relative_to(root).as_posix()
        if not re.match(r"^REQ-\d{3}", p.stem):
            req_bad.append(f"{rel}(命名非 REQ-NNN)")
            continue
        status = fm.get("status", "")
        if status not in REQ_STATUS:
            req_bad.append(f"{rel}(status 非法: {status or '缺失'})")
            continue
        if status == "implemented":
            trace = fm.get("trace", "")
            if not trace or trace.strip() == "null":
                req_bad.append(f"{rel}(implemented 缺 trace)")
    has_req = bool(reqs)
    r.append(("PE-07", "FAIL" if req_bad else ("PASS" if has_req else "SKIP"),
              f"{'; '.join(req_bad[:4])}" if req_bad else ("REQ 状态机合法" if has_req else "requirements 空,跳过")))

    # PE-08 ADR/REQ 索引一致(每个文件登记进各自 README)
    unreg: list[str] = []
    for sub, items in (("adr", adrs), ("requirements", reqs)):
        idx = _read(root / "docs" / sub / "README.md")
        for p, fm in items:
            key = fm.get("id") or p.stem
            if key not in idx:
                unreg.append(f"{sub}/{p.name}")
    r.append(("PE-08", "FAIL" if unreg else "PASS",
              f"未登记索引: {', '.join(unreg[:5])}" if unreg else "ADR/REQ 均已登记索引"))

    # PE-09 六态标记(research 有文档时)
    mark = False
    has_r = False
    rdir = root / "docs" / "research"
    if rdir.is_dir():
        for p in rdir.glob("*.md"):
            if p.name == "README.md":
                continue
            has_r = True
            if re.search(SIX_STATES, _read(p)):
                mark = True
    r.append(("PE-09", "PASS" if mark else ("SKIP" if not has_r else "FAIL"),
              "" if mark or not has_r else "research 文档无六态标记"))

    # PE-10 标题禁括号(跳过围栏代码块内的 # 注释行)
    badh: list[str] = []
    cands10 = [root / "AGENTS.md", root / "README.md"] + list((root / "docs").rglob("*.md"))
    for p in [p for p in cands10 if p.exists()]:
        in_fence = False
        for i, ln in enumerate(_read(p).splitlines(), 1):
            if ln.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if not in_fence and ln.startswith("#") and "(" in ln:
                badh.append(f"{p.name}:{i}")
    r.append(("PE-10", "FAIL" if badh else "PASS",
              f"标题含括号: {', '.join(badh[:5])}" if badh else "标题无括号"))

    # PE-11 四类禁字(emoji/破折号/箭头/智能引号等;豁免区感知,与 scan 同源)
    em: list[str] = []
    cands11 = [root / f for f in ("AGENTS.md", "README.md", "CHANGELOG.md")] + \
        list((root / "docs").rglob("*.md"))
    for p in [p for p in cands11 if p.exists()]:
        v = file_violations(_read(p))
        if v:
            first = min(v)
            em.append(f"{p.name}:{first}({'+'.join(v[first])})")
    r.append(("PE-11", "FAIL" if em else "PASS",
              f"含禁字: {', '.join(em[:5])}" if em else "无四类禁字"))

    # PE-12 AGENTS 与 docs 各 README 反引号路径断链粗检
    dead: list[str] = []
    idx_files = [root / "AGENTS.md"] + list((root / "docs").glob("*/README.md"))
    for idx in [p for p in idx_files if p.exists()]:
        for m in re.finditer(r"`([\w\-\\/\.]+\.(?:md|py|rs|toml|ts))`", _read(idx)):
            rel = m.group(1).replace("\\", "/")
            if not (root / rel).exists():
                dead.append(rel)
    r.append(("PE-12", "FAIL" if dead else "PASS",
              f"引用不存在: {', '.join(dead[:5])}" if dead else "README 引用可达"))

    ok = all(s != "FAIL" for _, s, _ in r)
    return r, ok


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if stream.encoding and stream.encoding.lower().replace("-", "") != "utf8":
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="check.py", description="诊断骨架合规(只读;退出码 0/1/2)")
    parser.add_argument("path", nargs="?", help="目标项目根目录(默认当前目录)")
    args = parser.parse_args(argv)

    root = Path(args.path).resolve() if args.path else Path.cwd()
    if not root.is_dir():
        print(f"error: 目标目录不存在:{root}", file=sys.stderr)
        return 2
    results, ok = check(root)
    for pid, status, note in results:
        print(f"{status:<5} {pid}  {note}".rstrip())
    print(f"{'合规: 全部通过' if ok else '不合规: 存在 FAIL'}(PASS {sum(1 for _, s, _ in results if s == 'PASS')}"
          f" / FAIL {sum(1 for _, s, _ in results if s == 'FAIL')}"
          f" / SKIP {sum(1 for _, s, _ in results if s == 'SKIP')})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
