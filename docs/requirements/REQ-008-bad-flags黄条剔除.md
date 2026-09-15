---
id: REQ-008
title: bad-flags 黄条剔除
status: implemented
priority: must
trace: docs/research/S003-浏览器静默化定制清单.md
---

# REQ-008:bad-flags 黄条剔除

关联:旧 PRD D02-7,2026-09-14 立项（lan 机 AppBridge userns 限制须 --no-sandbox 启动,每次弹黄条）,2026-09-15 交付。

## Scenario

`--no-sandbox` 等不受支持的命令行标记不再触发「不受支持的命令行标记」警告 infobar。

## Criteria

- [x] bad_flags_prompt.cc 守卫变量式锚（无死代码无 unused 风险）
- [x] 本机整屏截图目检 `--no-sandbox` 启动无黄条
- [x] 三台同步与验收
