# INDEX：项目总索引

> 角色：全仓唯一索引：只做定位。规则权威源见 AGENTS.md。

## 一、编号体系

前缀：`P`（proven，已完成方案归档，4 位）；`S`（research，研究，3 位）；`R`（references，现役流程，3 位）；`G`（guide，规范禁令，3 位）；`M`（mistakes，M1xx 分类文件、M0xx 行级）。退役编号不复用。

## 二、目录结构

| 类别 | 路径 | 说明 |
| --- | --- | --- |
| 入口 | `README.md` | 项目概貌、结论表、快速开始指针 |
| 根原语 | `PRD.md` `GOAL.md` `PLAN.md` `TODO.md` | 需求/目标/计划/进度 |
| 协作规则 | `AGENTS.md`（`CLAUDE.md` 一行桥接） | 唯一权威源 |
| 补丁 | `patches\apply-auto-allow.py` | 锚定式补丁脚本（uv 运行,43 锚 32 文件,三模式,默认用,幂等;2026-09-11 起替代 ps1） |
| 补丁 | `patches\auto-allow-devtools-connections-152.0.7977.84.patch` | 钉 tag 标准补丁（与脚本等价,43 锚） |
| 工具 | `tools\net-probe.py` | 网络通道稳定性评估（uv 运行 PEP 723,全平台,见 R001 替代路线） |
| 工具 | `tools\net-audit.py` | 产物网络行为审计（net-log 全进程 Google 域外联统计,S004 实证工具） |
| 工具 | `tools\deploy-release.py` | Release 产物部署自包含目录至 C:\browse-rs（SxS manifest 必带） |
| 工具 | `tools\pack-tree.py` | 构建树打包分发（双机同步用,配 R001 分发节） |
| 构建 | `args.gn` | GN 参数唯一权威（enable_nacl 已删勿写） |
| 验证产物 | `poc\S001-chromium152-auto-allow\` | 152 原始/补丁后参照树（orig/base/patched，只读） |
| 文档 | `docs\`（proven/diary/research/references/guide/mistakes） | 六目录 |
| 源码检出 | `chromium\`（未来，gitignore） | fetch 产物不入仓 |

> 迁移注记：2026-09-11 顶层 `research\` 并入体系，参照文件移至 `poc\S001-chromium152-auto-allow\`（用户裁定）。

## 三、方案归档

| 编号 | 文件 | 主题 |
| --- | --- | --- |
| P0001 | `docs\proven\P0001-chromium152-auto-allow-windows-build.md` | Windows 侧编译与验收（进行中） |

## 四、项目日记

| 日期 | 文件 | 主题 |
| --- | --- | --- |
| 2026-09-11 | `docs\diary\2026-09-11-项目启动研究与立项.md` | 研究核实、补丁就绪、骨架立项 |
| 2026-09-12 | `docs\diary\2026-09-12-双机部署与网络触点清零.md` | 双机分发攻坚、网络触点清零 43 锚、项目更名 clean-chrome |
| 2026-09-13 | `docs\diary\2026-09-13-三平台收官验收.md` | 三平台原子化重编收官、逐台验收全绿 |

## 五、研究文档

| 编号 | 文件 | 主题 |
| --- | --- | --- |
| S001 | `docs\research\S001-devtools-auto-allow-switch-上游核实与补丁设计.md` | 开关不存在/策略不能绕/机制/补丁设计/验证记录 |
| S002 | `docs\research\S002-CDP调试-提示限制与检测特征全景.md` | 提示/限制/检测特征逐项移除层与保留建议(五文件六锚定档) |
| S003 | `docs\research\S003-浏览器静默化定制清单.md` | 启动静默与 Google 触点 UI 剔除(19 锚定档与验证全绿) |
| S004 | `docs\research\S004-网络触点剔除-Google外联与遥测清零.md` | 网络层 Google 域外联与遥测清零(.invalid 端点+feature/pref,43 锚净测 0 外联) |

## 六、references 现役流程

| 编号 | 文件 | 用途 |
| --- | --- | --- |
| R001 | `docs\references\R001-chromium-build-操作手册.md` | 三平台构建唯一权威命令（预检/工具链/检出/补丁/构建/验证/纪律/坑表） |

## 七、guide 规范

| 编号 | 文件 | 用途 |
| --- | --- | --- |
| G001 | `docs\guide\G001-文档标准细则.md` | 命名/写作/六态/门禁 |

## 八、错误速查

| 编号 | 分类文件 | 覆盖关键词 | 行级编号段 |
| --- | --- | --- | --- |
| M001-M004 | `docs\mistakes\MISTAKES.md`（单文件） | PowerShell here-string、char Replace、git diff --no-index、autocrlf | M001 至 M004 |
| M005-M008 | `docs\mistakes\MISTAKES.md`（单文件） | 外置盘掉线、停 fetch 残留清场、直连间歇阻断与低速超时、pip.ini BOM 与 GIT_CONFIG_COUNT | M005 至 M008 |
| M009-M013 | `docs\mistakes\MISTAKES.md`（单文件） | 项目内工具链优先（GOROOT 污染）、singleton 误杀、-Wunreachable-code 替换式锚定、窗口成员不可空、幽灵锚 | M009 至 M013 |
| M014-M015 | `docs\mistakes\MISTAKES.md`（单文件） | 跨平台 tar 分发丢执行位、平台 CIPD 与 npm 资产缺失须目标机 sync 重装 | M014 至 M015 |
| M016-M017 | `docs\mistakes\MISTAKES.md`（单文件） | protobuf 同版本号树内带兼容补丁与 wheel 混搭、幂等 marker 误用上游字节致锚永久 skip | M016 至 M017 |
| M018-M019 | `docs\mistakes\MISTAKES.md`（单文件） | 根目录改名后 ninja 生成物旧绝对路径须重 gn gen、PYTHONUTF8 混入构建 shell 致 icacls 本地化 ACL 解码崩 | M018 至 M019 |
| M020 | `docs\mistakes\MISTAKES.md`（单文件） | 跨平台脚本用了 py3.10+ 的 write_text(newline=),mac CLT 3.9.6 崩于半打状态 | M020 |
| M021 | `docs\mistakes\MISTAKES.md`（单文件） | Dev(symbol_level=1) 全编内存高于 Release,叠加常驻浏览器触发低水位杀任务,降 j 并收浏览器 | M021 |
| M022 | `docs\mistakes\MISTAKES.md`（单文件） | ssh compound 里 pkill -f 同串文本自杀外壳（exit 255）,远端杀进程用 pkill -x | M022 |

## 九、阶段与版本

- `ROADMAP.md`：阶段路线
- `CHANGELOG.md`：版本里程碑
