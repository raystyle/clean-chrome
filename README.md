# clean-chrome：自定义 Chromium 加 auto-allow 开关

> 自编译 Chromium，加命令行开关 `--auto-allow-devtools-connections`：每个远程调试连接不经确认对话框直接放行（`AcceptDebugging` 短路回 `kAllow`）。只用于本机自动化专用浏览器，绝不提交上游、不替换日常 Chrome。

## 快速开始

```powershell
# 1 构建全流程照操作手册执行(唯一权威)
docs\guides\R001-chromium-build-操作手册.md

# 2 打补丁(锚定式,幂等,uv 全平台)
uv run patches/apply-auto-allow.py --src-root C:/clean-chrome/chromium/src

# 3 运行:无需任何参数,双击即用
#    默认开 9222 调试端口、默认 User Data 零限制、零确认对话框、零提示条
out\Dev\chrome.exe

# 4 调试通道选择(环境变量,S005):CLEAN_CHROME_DEBUG=port|pipe|both
#    未设=port(默认 9222);pipe=只 CDP 管道不开端口(启动器传
#    --remote-debugging-io-pipes=<读句柄>,<写句柄>,范本 tools/pipe-smoke.py);
#    both=双通道;显式命令行开关永远优先于变量

# 5 不受支持的命令行标记黄条(--no-sandbox 等 bad-flags infobar)已剔除
#    (REQ-008,--no-sandbox 启动干干净净)

# 6 console 参数与未捕获异常经 CDP 上报不带 eager 预览
#    (REQ-009,S006):ConsoleAPICalled/exceptionThrown 的 RemoteObject 保留
#    objectId 供按需取,但不再急切序列化对象数据进协议 payload;
#    Runtime.evaluate 的 generatePreview 行为不变。实测 152 通道图:
#    preview 本就不调 getter/Proxy 陷阱,文本通道与 stock 一致(非差分,保持原样)
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
patches\    补丁双形态(apply-auto-allow.py 锚定式 uv 运行 + 钉 tag 的 .patch,两者字节等价,50 锚 34 文件含 v8/ 树)
args.gn     GN 参数唯一权威
tools\      uv 运行 PEP 723 全平台工具(含 check.py 文档合规门禁)
poc\        S001 验证参照树(152 原始与补丁后文件,只读)
docs\       adr(决策) requirements(需求) guides(操作手册与工作流) research(研究) diary(日记)
```

## 当前状态

- 2026-09-15 D02-8 console 参数预览抑制收官：50 锚 34 文件（首入 v8/ 树）,四端验收矩阵全绿（本机 Dev/browse-rs 部署沙箱态/lan-mac/lan-ubuntu）;三机同补丁同 tag,browse-rs 已刷新至 50 锚
- 历史里程碑：三平台全编收官（09-13）、网络触点清零 43 锚（09-12）、调试通道三态 47 锚（09-14）、bad-flags 黄条剔除 48 锚（09-15）

决策记录见 `docs\adr`,需求与验收见 `docs\requirements`,状态交接见 diary 最新篇与 `ROADMAP.md`。

## 安全注意

开关一开，能连上调试端口的本地进程都拿到完整 CDP 控制权且无任何提示：只给自动化专用实例用；端口默认仅听 127.0.0.1；禁止配 `--remote-debugging-address` 暴露外网；调试实例必须另开 `--user-data-dir`（M136 起默认 profile 拒绝调试端口）。
