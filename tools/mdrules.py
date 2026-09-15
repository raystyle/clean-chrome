"""markdown 禁字检测基元(唯一权威;check PE-12 / scan / md-guard 同源引用)。

标准:《中英文 Markdown 技术文档字符与标点硬禁令》四类禁字。
本模块只提供逐行检测与判定,不做修正(修正属人工/编辑器职责)。
豁免区判定:YAML frontmatter、围栏代码块、行内代码、markdown 链接/图片、裸 URL。
零第三方依赖,标准库即可运行。
"""

from __future__ import annotations

import re

DASHES = "—–―−ー"
DOUBLE_DASH = "——"
ARROWS = re.compile("[←-⇿➜⬅⬆⬇⬀-⬏]")
EMOJI = re.compile("[☀-➿\U0001f000-\U0001faff✅⚠]")
SMART_QUOTES = re.compile("[“”‘’]")
FW_ALNUM = re.compile("[Ａ-Ｚａ-ｚ０-９]")
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache",
             ".claude", ".agents", ".rumdl_cache", "target", "dist", "build"}

_INLINE = re.compile(r"(`[^`]+`)|(\[[^\]]*\]\([^)\s]*(?:\([^)]*\)[^)\s]*)*\))|(https?://[^\s)\]]+)")


def strip_inline_exemptions(line: str) -> str:
    """去掉行内豁免段(行内代码/链接/URL),返回待判定文本。"""
    return _INLINE.sub("", line)


def line_violations(raw_line: str, in_fence: bool) -> list[str]:
    """单行违规类别(空列表=合规)。in_fence 时整行豁免。

    error 级四类:破折号/连接号、Unicode 箭头、emoji、智能引号与全角字母数字。
    中文语境半角标点属排版偏好,不做 error 告警(修正交由人工,同家族 mdcharlint 分级)。
    """
    if in_fence or raw_line.lstrip().startswith("```"):
        return []
    line = strip_inline_exemptions(raw_line)
    out = []
    if DOUBLE_DASH in line or any(c in line for c in DASHES):
        out.append("破折号/连接号")
    if ARROWS.search(line):
        out.append("Unicode 箭头")
    if EMOJI.search(line):
        out.append("emoji")
    if SMART_QUOTES.search(line):
        out.append("智能引号")
    if FW_ALNUM.search(line):
        out.append("全角字母数字")
    return out


def file_violations(text: str) -> dict[int, list[str]]:
    """整文件逐行扫描(YAML frontmatter 与围栏块豁免),返回 {行号(1 起): 类别列表}。"""
    out: dict[int, list[str]] = {}
    in_fence = False
    lines = text.splitlines()
    start = 0
    if lines[:1] == ["---"]:
        close = next((i for i in range(1, len(lines)) if lines[i] == "---"), None)
        if close is not None:
            start = close + 1
    for i in range(start, len(lines)):
        if lines[i].lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        v = line_violations(lines[i], in_fence)
        if v:
            out[i + 1] = v
    return out
