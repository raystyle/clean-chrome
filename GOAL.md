# GOAL：任务目标管理

> 角色：工作任务管理，四个部分：起点、锚点、进程、历史。随工作实时更新。

## 起点

- **日期**：2026-09-11
- **起点**：agent 自动化附着本机浏览器时，被 DevTools 远程调试确认对话框打断；上游无此开关、企业策略不能免对话框，编译自定义 Chromium 是唯一路径 [实证: S001 结论表]，据此立项 D02/D03

## 锚点

- **锚定的目标**：D02 Windows 侧：在本机编出 `chrome.exe` 且 `--auto-allow-devtools-connections` 生效（方案载体 P0001）

### 推进时间线

| 日期 | 进展 |
| --- | --- |
| 2026-09-11 | 研究核实完成（S001）；补丁双形态产出并回环验证；文档骨架建立 |
| 2026-09-11 | 环境铺路：git 六条全局配置、depot_tools 就位（用户 PATH 前插 + DEPOT_TOOLS_WIN_TOOLCHAIN=0）、VS 2026 安装与 chromium fetch 双线启动、增量编译双目录策略定档（Dev 迭代 + Release 分发） |

## 进程

- 当前目标：D02/D03 **三平台完美产物全部达成（2026-09-13）**：43 锚 clean-chrome 原子化同步（三台 32 文件清单逐字节一致）后各自全新全编,逐台验收全绿；余项仅本机 out\Dev 迭代目录全编收口
- 本机 Windows：四条 + net-audit（真实 Google 域 0 外联,触点全 .invalid）+ deploy 刷新 C:\browse-rs（499 文件 652MB SxS manifest）+ bh 附着端到端（goto_url+js）
- lan-mac：全编 3h42m,四条全绿（开关在 Chromium Framework 二进制,MacOS/Chromium 只是启动器）
- lan-linux：全编 6h30m,headless 验收四条全绿（Ubuntu userns 限制用 --no-sandbox 过验,R001 坑表 18-20 沉淀：sandbox/headless 验收法/pkill 自匹配）
- 网络受阻全程破局：googlesource/git-https/SSH 大流量均被间歇掐断（M007），改道 aria2x16 codeload tarball + GitHub SSH 归化官方 tag 对象 + gclient 循环与陪跑自愈拉齐 300+ 依赖仓 + insteadOf 镜像注入（skia/devtools-frontend/quiche）
- 环境坑当日全修：pip.ini BOM（M008）、GOROOT 污染（M009）、-j32 OOM 降 j16、改名双坑（M018/M019）、Dev 低内存（M021）、pkill 自匹配（M022）
- 工具链：tools\net-probe.py / net-audit.py（S004 实证）/ deploy-release.py（SxS manifest 部署）/ pack-tree.py（跨机分发）

## 历史

| 日期 | 目标 | 结果 |
| --- | --- | --- |
| 2026-09-11 | D02 Windows 构建（Dev 验收） | 全绿：自编 chrome.exe/dll 带开关零弹窗,bh 端到端附着通;Release 分发产物待编 |
| 2026-09-12 | D02 深化（Release 部署 + 43 锚网络清零 + 更名 clean-chrome） | Release 部署 C:\browse-rs 全绿;43 锚 32 文件净测 Google 域 0 外联（S004）;GitHub/本地全量更名;改名双坑 M018/M019 当日修复 |
| 2026-09-13 | D02/D03 收官（三平台原子化重编 + 逐台验收） | **三平台完美产物**：预检矩阵过全部历史坑,三台全清从起点重编（Win 3h/mac 3h42m/linux 6h30m）,逐台四条全绿;本机另过 net-audit 0 外联/部署刷新/bh 冒烟;M020-M022 入库 |
