# TODO：当前目标任务进度清单

> 角色：当前目标的任务进度清单。目标完成后回填 docs/proven 对应方案，起新清单。
> 2026-09-12 深夜快照：项目已更名 clean-chrome（GitHub 已改 raystyle/clean-chrome；本地目录改名由用户重启后执行 `Rename-Item C:\unsafe-chrome clean-chrome`，项目文件与脚本默认路径均已写为 C:\clean-chrome）。

## 任务进度清单

| 任务项 | 进行中 | 说明 | 日期 |
| --- | --- | --- | --- |
| Release 全编 + 部署 C:\browse-rs | 部署待刷新 | 19 锚版已部署验收过（9222+about:blank 全绿）；43 锚 clean-chrome 版编译完成后需 `uv run tools/deploy-release.py` 刷新 | 2026-09-12 |
| 43 锚增量编译（clean-chrome marker 版） | 编译中 | 改名双坑当日修复（M018 重 gn gen + M019 剥 PYTHONUTF8）后续编中（后台 bihxut21o）；再被打断直接重跑同命令 | 2026-09-12 |
| 43 锚产物 net-audit 复测 | 待编译 | `uv run tools/net-audit.py`（默认指 out\Release）；19/26/34 锚版实测 Google 触点分别为 19/5/3 域，43 锚版目标 0（此前 43 锚 unsafe-chrome 版已实测 0） | 2026-09-12 |
| 项目文件 clean-chrome 更名 | 已完成 | 11 文件 86 处替换；GitHub repo 已 rename；remote URL 已更新；chromium 树 43 锚已回滚重打（clean-chrome marker） | 2026-09-12 |
| 本地目录改名 C:\clean-chrome | 已完成 | 用户重启 session 后执行 `Rename-Item C:\unsafe-chrome clean-chrome`（2026-09-12 夜）；改名连带 M018/M019 当场修复入库 | 2026-09-12 |
| 提交推送（更名 + S004 + 43 锚 + M014-M017） | 已完成 | 359781b/6038d88 等已推,main 与 origin/main 同步（本 session 核实）；M018/M019 文档批次另行提交 | 2026-09-12 |
| CHANGELOG / diary / GOAL / README 回填 | 已完成 | CHANGELOG 三条/README 更名/diary 当日篇此前已就；GOAL 进程段与 INDEX（补丁 43 锚描述/tools 三脚本/diary 行/错误节）本 session 补齐 | 2026-09-12 |
| R001 补充分发节 | 已完成 | 新八节：git archive 干净 depot_tools、pack-tree.py、双机落地三连修法（M014/M015）、protobuf 覆盖（M016）、deploy-release.py（SxS manifest 必带）；坑表补 16/17 | 2026-09-12 |
| M018/M019 文档批次提交 | 待办 | docs: 前缀一笔（MISTAKES/INDEX/R001/TODO/GOAL/diary）；编译验收后再 feat 收口 | 2026-09-12 |
| lan-linux 编译 | 编译中 | 2026-09-12 夜核实：autoninja -j8 活跃,resume.log 2975/47442（v8 段,load 8.26）；产物为 19 锚版,完成后需重打 43 锚 + 增量重编 | 2026-09-12 |
| lan-mac 编译 | 编译中 | 2026-09-12 夜核实：autoninja -j6 活跃,obj 21:12 仍更新（helper 链接段,曾到 58%+ 后重启续编）；protobuf 预防覆盖已做 | 2026-09-12 |
| 双机 43 锚同步 | 待办 | 把新 apply-auto-allow.py 分发到双机,`git checkout` 回滚 19 锚文件,重打 43,增量编译；双机 protobuf 修复法已实证（树内 runtime 覆盖 venv+pyproto） | 2026-09-12 |
| 双机行为验收 + D03 收口 | 待办 | 各自无参数 9222、tabs about:blank、grep 开关入二进制；GOAL 历史行 + proven 回填 | 2026-09-12 |
| bh 附着冒烟（部署版） | 待办 | BH_CDP_URL=http://127.0.0.1:9222 附着 C:\browse-rs 版；Google 搜索屏蔽已在 43 锚中（suggest off） | 2026-09-12 |
