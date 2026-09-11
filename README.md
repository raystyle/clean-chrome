# unsafe-chrome：自定义 Chromium 加 auto-allow 开关

> 自编译 Chromium，加命令行开关 `--auto-allow-devtools-connections`：每个远程调试连接不经确认对话框直接放行（`AcceptDebugging` 短路回 `kAllow`）。只用于本机自动化专用浏览器，绝不提交上游、不替换日常 Chrome。

## 快速开始

```powershell
# 1 构建全流程照操作手册执行(唯一权威)
docs\references\R001-chromium-build-操作手册.md

# 2 打补丁(锚定式,幂等,uv 全平台)
uv run patches/apply-auto-allow.py --src-root C:/unsafe-chrome/chromium/src

# 3 运行:无需任何参数,双击即用
#    默认开 9222 调试端口、默认 User Data 零限制、零确认对话框、零提示条
out\Dev\chrome.exe
```

## 研究结论速览

核实日期 2026-09-11，信源为当日 chromium.googlesource.com 源码与官方文档原文，全表见 `docs\research\S001`。

| 事实 | 结论 |
|---|---|
| `--auto-allow-devtools-connections` 上游是否存在 | 不存在，必须自己打补丁 |
| 企业策略能否绕过对话框 | 不能：`RemoteDebuggingAllowed` 只管调试总闸，对话框照弹 |
| 确认对话框机制 | 无浏览器窗口时自动拒绝；补丁须短路整个 `AcceptDebugging()` |
| 版本策略 | 钉稳定 tag（基准 152.0.7977.84）；152 与 main 之间已有代码漂移；2026-09 起 Chrome 两周发一版 |
| Windows 工具链 | VS 2026 (>=18.0.0) + Win11 SDK 10.0.28000.2270 + Debugging Tools 10.0.26100.3323+；外部开发者必设 `DEPOT_TOOLS_WIN_TOOLCHAIN=0` |
| `enable_nacl` | 上游已删该 GN 参数，args 里禁止出现 |
| Linux 与 macOS | 基准 Ubuntu 22.04；macOS 以 `mac_sdk.gni` 的 `mac_sdk_official_version` 为准 |

## 仓库结构

```
patches\    补丁双形态(apply-auto-allow.ps1 锚定式 + 钉 tag 的 .patch,两者等价)
args.gn     GN 参数唯一权威
tools\      uv 运行 PEP 723 全平台工具(net-probe.py 网络通道评估)
poc\        S001 验证参照树(152 原始与补丁后文件,只读)
docs\       proven(方案) research(研究) references(操作手册) guide(规范) mistakes(错误库) diary(日记)
```

## 当前状态

- 2026-09-11 Windows 侧 Dev 构建验收全绿：自编 152 带 `--auto-allow-devtools-connections` 零对话框,bh 端到端附着可用（`BH_CDP_URL=http://127.0.0.1:9222`）;Release 分发产物待编。进度详见 GOAL/TODO

项目状态与下一步见 `GOAL.md` 与 `TODO.md`；当前目标 P0001（Windows 构建，进行中）。

## 安全注意

开关一开，能连上调试端口的本地进程都拿到完整 CDP 控制权且无任何提示：只给自动化专用实例用；端口默认仅听 127.0.0.1；禁止配 `--remote-debugging-address` 暴露外网；调试实例必须另开 `--user-data-dir`（M136 起默认 profile 拒绝调试端口）。
