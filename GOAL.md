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

- 当前目标：D02 Windows 构建：**Dev 验收全绿达成（2026-09-11 晚）**；余项 Release 分发产物（args 照 R001 五节全编一次）
- 网络受阻全程破局：googlesource/git-https/SSH 大流量均被间歇掐断（M007），改道 aria2x16 codeload tarball（1.4GB,103Mbps）+ GitHub SSH 归化官方 tag 对象 + gclient 循环与陪跑自愈拉齐 300+ 依赖仓（20.5GB）+ insteadOf 镜像注入（skia/devtools-frontend/quiche）
- 环境坑当日全修：pip.ini BOM（M008）、系统 GOROOT 污染 dawn 内置 go（M009）、Defender 排除、-j32 OOM 降 j16
- 验收四条全绿：findstr 开关入 chrome.dll；CDP HTTP 端点 152；WS 握手 10ms 零对话框（auto-allow 短路生效直接证据）；bh 附着（BH_CDP_URL）js() 页面执行通
- 新工具：tools\net-probe.py（uv 全平台网络评估）；R001 增替代路线节与坑表 11-15

## 历史

| 日期 | 目标 | 结果 |
| --- | --- | --- |
| 2026-09-11 | D02 Windows 构建（Dev 验收） | 全绿：自编 chrome.exe/dll 带开关零弹窗,bh 端到端附着通;Release 分发产物待编 |
