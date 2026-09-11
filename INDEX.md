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
| 补丁 | `patches\apply-auto-allow.ps1` | 锚定式补丁脚本（默认用，幂等） |
| 补丁 | `patches\auto-allow-devtools-connections-152.0.7977.84.patch` | 钉 tag 标准补丁 |
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

## 五、研究文档

| 编号 | 文件 | 主题 |
| --- | --- | --- |
| S001 | `docs\research\S001-devtools-auto-allow-switch-上游核实与补丁设计.md` | 开关不存在/策略不能绕/机制/补丁设计/验证记录 |

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

## 九、阶段与版本

- `ROADMAP.md`：阶段路线
- `CHANGELOG.md`：版本里程碑
