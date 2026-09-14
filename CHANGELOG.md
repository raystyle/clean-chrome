# Changelog

本文件记录可交付变更。粒度纪律：只留版本级里程碑（定位变更/发布/阶段完成/核心能力整体落地）。

## [Unreleased]

- 2026-09-11 项目启动：上游核实完成（S001），补丁双形态产出并回环验证，文档体系建立
- 2026-09-11 **D02 Dev 构建验收全绿**：Windows 自编 Chromium 152.0.7977.84 带 `--auto-allow-devtools-connections`,验收四条全过（开关入产物 / CDP 端点 / 零对话框 / bh 附着）；网络受阻替代路线与 tools\net-probe.py 沉淀进 R001;M005 至 M009 入错误库。Release 分发产物待编
- 2026-09-11 **浏览器静默化收官（D02-2/D02-3）**：补丁体系 uv Python 化并扩至 19 锚 12 文件：无参数启动默认开 9222、默认 User Data 零限制、启动零提示零横幅（API 密钥/过时系统/OSCrypt/默认浏览器/会话恢复/crash 气泡/首跑向导全灭）、NTP 全入口 about:blank、默认搜索与 AI Mode 关闭；S002/S003 研究定档,M011 至 M013 入库（幽灵锚教训：编译通过不等于锚生效）
- 2026-09-12 **P0001 完成:Release 分发产物落地并部署**：Release 全编验收全绿（无参数 9222 + about:blank 首页 + WS 零对话框 + 开关入 dll）,`tools\deploy-release.py` 部署自包含目录至 C:\browse-rs\chromium-152.0.7977.84（含 SxS manifest 与 initial_preferences）
- 2026-09-12 **网络触点清零（D02-4,S004）**：net-audit 实证驱动补丁扩至 **43 锚 32 文件**:Gaia/GCM/组件更新/CUP 时间/拼写词典端点 `.invalid` 化（RFC 6761 永不解析）、翻译与 Lens 与 zero-suggest prefetch feature 关、SB 全家（v4/v5/realtime/文件扫描）与翻译提议与 suggest pref 默认关;净测 30 秒空 profile **Google 域 0 外联**;M014 至 M017 入库（跨平台分发三连坑、protobuf 同号不同内容、marker 幽灵锚）
- 2026-09-12 **项目更名 clean-chrome（D02-5）**：GitHub 仓库 rename、remote 更新、项目文件 86 处更替、补丁 marker 全量换 clean-chrome 并重打重验（patch 31KB）
- 2026-09-13 **D02/D03 收官：三平台完美产物**：三台原子化同步 43 锚（改动清单逐字节一致）后全清从起点重编,逐台验收全绿（开关入二进制/无参 9222/WS 零对话框/about:blank,Windows 另过 net-audit 0 外联+部署刷新+bh 端到端）;全流程预检矩阵消化 M001-M019 无重犯,新坑 M020-M022 当场入库（脚本 py3.9 兼容/Dev 低内存降 j/pkill 自匹配）
- 2026-09-14 **调试通道环境变量化（D02-6,S005）**：`CLEAN_CHROME_DEBUG=port|pipe|both`（默认 port 即 9222 现行为;pipe 只 CDP 管道不开端口;both 双通道）,补丁扩至 **47 锚**;Windows 管道走 `--remote-debugging-io-pipes` 句柄契约,启动器范本 `tools\pipe-smoke.py`;三态矩阵全绿（getTargets 管道往返+端口态正确）,双形态字节等价;M023 入库
- 2026-09-15 **bad-flags 黄条剔除（D02-7）与 linux 编译机换机**：`--no-sandbox` 等不受支持标记警告 infobar 灭（48 锚 33 文件,三台同步+本机截图目检）;linux 编译机 lan-linux 换 **lan-ubuntu**（16 核/61G,linux 对 linux rsync 全量含 out/,同路径保增量态,分发+迁移+增量+验收一气呵成,增量仅 4 步 21 秒）
