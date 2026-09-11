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

- 当前目标：D02 Windows 构建（进行中）
- 研究与补丁已就绪；构建未开始
- 环境待办：VS 2026 (>=18.0.0) + Win11 SDK 10.0.28000.2270 + Debugging Tools 10.0.26100.3323+；`DEPOT_TOOLS_WIN_TOOLCHAIN=0`；本机全局 `git core.autocrlf` 2026-09-11 时仍为 true，须按 R001 预检改 false（改后复核） [记忆: 改没改以下次会话 `git config --global core.autocrlf` 输出为准]

## 历史

| 日期 | 目标 | 结果 |
| --- | --- | --- |
