# TODO：当前目标任务进度清单

> 角色：当前目标的任务进度清单。目标完成后回填 docs/proven 对应方案，起新清单。
> 2026-09-12 深夜快照：项目已更名 clean-chrome（GitHub 已改 raystyle/clean-chrome；本地目录改名由用户重启后执行 `Rename-Item C:\unsafe-chrome clean-chrome`，项目文件与脚本默认路径均已写为 C:\clean-chrome）。

## 任务进度清单

| 任务项 | 进行中 | 说明 | 日期 |
| --- | --- | --- | --- |
| Release 全编 + 部署 C:\browse-rs | 部署待刷新 | 19 锚版已部署验收过（9222+about:blank 全绿）；43 锚 clean-chrome 版编译完成后需 `uv run tools/deploy-release.py` 刷新 | 2026-09-12 |
| 43 锚增量编译（clean-chrome marker 版） | 编译中 | 后台 autoninja -C out\Release chrome；若 session 重启打断，直接重跑同命令（Siso 增量自愈续编） | 2026-09-12 |
| 43 锚产物 net-audit 复测 | 待编译 | `uv run tools/net-audit.py`（默认指 out\Release）；19/26/34 锚版实测 Google 触点分别为 19/5/3 域，43 锚版目标 0（此前 43 锚 unsafe-chrome 版已实测 0） | 2026-09-12 |
| 项目文件 clean-chrome 更名 | 已完成 | 11 文件 86 处替换；GitHub repo 已 rename；remote URL 已更新；chromium 树 43 锚已回滚重打（clean-chrome marker） | 2026-09-12 |
| 本地目录改名 C:\clean-chrome | 用户执行 | session 重启后 `Rename-Item C:\unsafe-chrome clean-chrome`（harness shell 池锁目录，session 内不可改） | 2026-09-12 |
| 提交推送（更名 + S004 + 43 锚 + M014-M017） | 待办 | 分笔：docs:（S004/MISTAKES/INDEX/TODO 等文档）+ feat:（43 锚补丁脚本与 patch 文件、tools 三脚本）；推 origin main | 2026-09-12 |
| CHANGELOG / diary / GOAL / README 回填 | 待办 | 43 锚与 S004 与更名均需回填；README 自称已是 clean-chrome | 2026-09-12 |
| R001 补充分发节 | 待办 | git archive 干净 depot_tools、pack-tree.py、双机 sync 修法（M014/M015）、deploy-release.py 部署套路（SxS manifest 必带） | 2026-09-12 |
| lan-linux 编译 | 编译中 | 三连修（执行位/sync/node_modules）+ protobuf 修复后进入 CXX；产物为 19 锚版（无网络触点剔除）；完成后需重打 43 锚 + 增量重编 | 2026-09-12 |
| lan-mac 编译 | 编译中 | 同上（曾到 58%+）；protobuf 预防覆盖已做 | 2026-09-12 |
| 双机 43 锚同步 | 待办 | 把新 apply-auto-allow.py 分发到双机,`git checkout` 回滚 19 锚文件,重打 43,增量编译；双机 protobuf 修复法已实证（树内 runtime 覆盖 venv+pyproto） | 2026-09-12 |
| 双机行为验收 + D03 收口 | 待办 | 各自无参数 9222、tabs about:blank、grep 开关入二进制；GOAL 历史行 + proven 回填 | 2026-09-12 |
| bh 附着冒烟（部署版） | 待办 | BH_CDP_URL=http://127.0.0.1:9222 附着 C:\browse-rs 版；Google 搜索屏蔽已在 43 锚中（suggest off） | 2026-09-12 |
