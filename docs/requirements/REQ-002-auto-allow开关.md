---
id: REQ-002
title: auto-allow-devtools-connections 开关
status: implemented
priority: must
trace: docs/research/S002-CDP调试-提示限制与检测特征全景.md
---

# REQ-002:auto-allow-devtools-connections 开关

关联:旧 PRD D02 主线,2026-09-13 三平台验收全绿;决策依据 ADR-0001。

## Scenario

agent 自动化经 CDP 附着本机浏览器时,每个远程调试连接不经确认对话框直接放行。

## Criteria

- [x] 开关 `--auto-allow-devtools-connections` 入产物（findstr chrome.dll 命中）
- [x] `AcceptDebugging()` 开头短路回 `kAllow`（替换式锚定,禁提前 return）
- [x] WS 握手无确认对话框（10ms 秒通,auto-allow 生效直接证据）
- [x] CDP `/json/version` 端点可用,JSON-RPC 双向响应
