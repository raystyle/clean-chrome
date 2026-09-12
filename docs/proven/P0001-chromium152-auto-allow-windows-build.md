# P0001：chromium 152 auto-allow Windows 构建

> 本机（Windows）编译带 `--auto-allow-devtools-connections` 的 Chromium 并验证生效。落点：本文件。进行中与否以 TODO.md 为准。

- 状态：完成（2026-09-12）：Dev 与 Release 双产物验收全绿（Release 无参数 9222 + about:blank 首页 + WS 13ms 零对话框 + findstr 开关入 dll）
- 日期：2026-09-11
- 关联：PRD D02；S001（研究与补丁）；R001（操作手册）；PLAN/TODO

## 背景与问题

agent 自动化附着本机浏览器时被 DevTools 确认对话框打断；上游无开关、策略不能免对话框（S001 结论 1、2），需自编译。本方案覆盖 Windows 主战场；Linux/macOS 属后续目标（D03）。

## 目标与非目标

- 目标：tag `152.0.7977.84` 上编出 `out\Release\chrome.exe`，开关生效且免对话框
- 非目标：不进上游；不做安装包（mini_installer）；不改 infobar；不支持默认 profile 直开调试端口

## 方案

补丁双形态（S001 第四节）+ R001 全流程；GN 参数照根 `args.gn`。

## 备选方案

- 模拟点击对话框（UI 自动化）：脆弱且无窗口场景自动 Deny，弃 [实证: S001 机制节第 3 条]
- 企业策略：只管总闸，弃 [实证: S001 结论 2]
- 跟 main 而非 tag：补丁漂移不可控，弃 [实证: S001 机制节第 5 条]

## 实施步骤

见 PLAN 步骤表（0 至 7），依据全部挂 R001 对应节。

## 风险与回滚

- 首次编译 2 至 8 小时且可能因工具链版本踩坑：严格照 R001 版本号安装
- 补丁锚点失配：apply 脚本显式报错保护，照 S001 第六节处理
- 回滚：删 `chromium\src\out\Release` 重编即可；补丁本身 `git checkout` 三文件即撤

## 验收记录（Release,2026-09-12）

无参数启动 out\Release\chrome.exe:9222 自动开;/json/version 152;首 tab about:blank(19 锚全入产物);WS 握手 13ms 零对话框;findstr 开关命中 chrome.dll。

## 实施过程与经验

> 完成时回填。

- 研究与补丁阶段（S001 验证记录）
- 2026-09-11：E 盘故障（M005）项目平移 C:；fetch 因直连强干扰（M007）12 轮全灭,改道替代路线（aria2 x16 codeload tarball 1.4GB + GitHub SSH 归化官方 tag 对象,详见 R001 三节）;依赖 gclient sync 循环+陪跑自愈拉齐（20.5GB）
- 三大环境坑当日全踩当日全修：pip.ini BOM 炸 venv（M008）、系统 GOROOT 污染 dawn 项目内 go（M009）、Defender 未排除致 git add 21 文件/秒（R001 预检实证）
- 首编：`-j 32` 在 64GB RAM 机器 OOM 被杀,降 `-j 16` 稳定跑完;净编译约 4.5 小时（含 blink/v8 巨型 obj 段）,产物 `out\Dev` 约 20GB
- 验收四条全绿（out\Dev）:findstr 开关入 chrome.dll;`/json/version` 返回 Chrome/152.0.7977.84;**WS 握手 10ms 秒通（无确认对话框,auto-allow 短路生效的直接证据）**;WS 会话 JSON-RPC 双向响应
- 经验沉淀:tools\net-probe.py（uv 运行全平台网络评估）;R001 新增替代路线节;坑表 11-15

## 验收标准

PLAN「完成的定义」四条全勾；达成后在 diary 补一笔。

## 附录：三平台收官（2026-09-13,D03 同步达成）

- **原子化同步**：三台同 tag（152.0.7977.84）同补丁（43 锚 clean-chrome）,打补丁后三台 `git status` 32 个改动文件清单**逐字节一致**;mac `[ok]×43` / linux `[skip]×43` 幂等等价核验
- **全清从起点重编**：三台 out 全删、各自全新 gn gen、同时起编（Win -j16 / linux -j8 / mac -j6 caffeinate）;Build Succeeded 全零 FAILED（mac 3h42m / Win 约 4h / linux 6h30m）
- **逐台验收全绿**：开关入二进制（Win chrome.dll / mac Chromium Framework / linux chrome,各 grep=1）、无参数默认 9222、WS 握手即时 101 零对话框、首页 about:blank;Windows 另过 net-audit（真实 Google 域 0 外联,触点全 `.invalid`）、deploy-release 刷新 C:\browse-rs、bh 附着端到端
- **跨平台注意**：mac 开关串在 Chromium Framework 二进制（MacOS/Chromium 只是启动器）;Ubuntu 23.10+ 需 --no-sandbox 或开 userns（R001 坑 18）;无显示器验收用 --headless=new（坑 19）;远端杀进程 pkill -x（坑 20/M022）
- 过程新坑 M020-M022 全部当日入库,历史坑 M001-M019 经预检矩阵无一重犯
