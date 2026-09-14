# TODO：当前目标任务进度清单

> 角色：当前目标的任务进度清单。目标完成后回填 docs/proven 对应方案，起新清单。
> 2026-09-15 快照：D02-6/D02-7 收官;linux 编译机已换 lan-ubuntu 并 48 锚对齐。

## 任务进度清单

| 任务项 | 进行中 | 说明 | 日期 |
| --- | --- | --- | --- |
| D02-7 bad-flags 黄条剔除 | 已完成 | 48 锚 33 文件（bad_flags_prompt.cc 守卫变量式锚,无死代码）;三台同步（本机 ok=1/mac ok=1/ubuntu ok=7）,patch 双形态 33 文件等价;本机 `--no-sandbox` 整屏截图目检无黄条;Release+Dev 增量重编过 | 2026-09-15 |
| 部署版 browse-rs 刷新（48 锚） | 已完成 | 2026-09-15 刷新并验收:开关入 dll/无参 9222/`--no-sandbox` 无黄条（整屏截图目检） | 2026-09-15 |
| lan-mac 48 锚 | 已完成 | ok=1/skip=47,增量 6 步 28.9s | 2026-09-15 |
| lan-ubuntu 换机分发 | 已完成 | rsync 全量 61.9GB（含 out/）,同路径保增量态;48 锚 ok=7/skip=41;增量 4 步 21.6s;首跑验收过（marker/开关/9222/about:blank） | 2026-09-15 |
| 文档同步 + 提交推送（D02-7 批） | 已完成 | README/R001 坑18/CHANGELOG/INDEX/PRD/GOAL/diary/TODO;feat: 一笔 | 2026-09-15 |

