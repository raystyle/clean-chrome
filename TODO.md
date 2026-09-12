# TODO：当前目标任务进度清单

> 角色：当前目标的任务进度清单。目标完成后回填 docs/proven 对应方案，起新清单。
> 2026-09-12 深夜快照：项目已更名 clean-chrome（GitHub 已改 raystyle/clean-chrome；本地目录改名由用户重启后执行 `Rename-Item C:\unsafe-chrome clean-chrome`，项目文件与脚本默认路径均已写为 C:\clean-chrome）。

## 任务进度清单

| 任务项 | 进行中 | 说明 | 日期 |
| --- | --- | --- | --- |
| **三平台原子化全编（用户裁定：全停全清从起点，直到完美产物）** | 编译中 | 三台同步 43 锚 clean-chrome 版后同时全新起编：本机 -j16（out 已清+重 gen）、lan-linux -j8（~74k 步缓存回放中）、lan-mac -j6（caffeinate）；M016 protobuf 修复 venv 已失（重建按需）,若复发按 M016 树内 runtime 覆盖两处 | 2026-09-12 |
| 三平台验收链 | 待编译 | 各台四条验收（开关入二进制/无参 9222/零对话框/about:blank）+ 本机 net-audit 0 外联 + bh 附着冒烟 + deploy-release 刷新 C:\browse-rs | 2026-09-12 |
| 43 锚产物 net-audit 复测 | 待编译 | `uv run tools/net-audit.py`（默认指 out\Release）；19/26/34 锚版实测 Google 触点分别为 19/5/3 域，43 锚版目标 0（此前 43 锚 unsafe-chrome 版已实测 0） | 2026-09-12 |
| 本机 Dev 目录重建 | 待办（Release 后串行） | out\Dev 已删（M018 同族作废）；Release 编完后 gn gen out\Dev（component+symbol_level=1）+ 全编 | 2026-09-12 |
| 项目文件 clean-chrome 更名 | 已完成 | 11 文件 86 处替换；GitHub repo 已 rename；remote URL 已更新 | 2026-09-12 |
| 本地目录改名 C:\clean-chrome | 已完成 | 用户重启 session 后执行（2026-09-12 夜）；连带 M018/M019 当场修复入库 | 2026-09-12 |
| 提交推送（更名 + S004 + 43 锚 + M014-M017） | 已完成 | 359781b/6038d88 已推；文档批次 609e11e 已推 | 2026-09-12 |
| CHANGELOG / diary / GOAL / README 回填 | 已完成 | 本 session 补齐 GOAL 进程/历史与 INDEX | 2026-09-12 |
| R001 补充分发节 | 已完成 | 新八节 + 坑表 16/17 | 2026-09-12 |
| 双机 43 锚同步 | 已完成 | 预检矩阵过 M001-M019 后：清 index.lock（M006）,checkout 回滚 19 锚（13 M+137/154 D 占位还原）,分发脚本,mac 43 ok / linux 43 skip（幂等等价）,三台 32 M 文件清单逐字节一致（原子态核验） | 2026-09-12 |
| M020 补丁脚本 py3.9 兼容 | 已完成 | write_text(newline=) 换 open() 显式句柄；mac CLT 3.9.6 实证通过 | 2026-09-12 |
