# PLAN：当前目标实施计划

> 角色：当前目标方案文档：基于 research（为什么）与 references（怎么做）的执行计划；每条挂依据来源，不存历史目标。

## 当前目标

D02 Windows 侧：本机编出带开关的 `chrome.exe` 并验证生效（方案全文见 `docs\proven\P0001`）

## 步骤

| # | 步骤 | 依据 |
| --- | --- | --- |
| 0 | 预检：git 全局配置（autocrlf false 等）、App execution aliases、Defender 排除 | R001 预检节 |
| 1 | 装 VS 2026 (>=18.0.0) + Desktop C++ + MFC/ATL；Win11 SDK 10.0.28000.2270；Debugging Tools 10.0.26100.3323+；设 `DEPOT_TOOLS_WIN_TOOLCHAIN=0` | R001 3.1 节 |
| 2 | clone depot_tools 到 PATH 最前；cmd.exe 首跑 `gclient` | R001 3.2 节 |
| 3 | `fetch --nohooks --no-history chromium`；checkout tag `152.0.7977.84`；`gclient sync --with_branch_heads --with_tags` | R001 3.2 节 |
| 4 | 打补丁：`patches\apply-auto-allow.ps1`（或钉 tag 的 .patch，二者等价） | S001 补丁设计节 |
| 5 | `gn gen out\Release`（参数照根 `args.gn`，注意 `enable_nacl` 已删不能写） | R001 3.3 节 |
| 6 | `autoninja -C out\Release chrome`（首次 2 至 8 小时） | R001 3.3 节 |
| 7 | 验收四条（见下） | R001 验证节 |
| 8 | Linux/macOS 复制（同 tag 同 patch），进 P0001 附录后另立目标 | R001 三台纪律节 |

## 完成的定义

- [ ] `out\Release\chrome.exe` 编译产出
- [ ] `findstr /m /c:"auto-allow-devtools-connections" out\Release\chrome.dll` 命中
- [ ] 带开关启动后 `curl http://127.0.0.1:9222/json/version` 返回 200 且全程无确认对话框
- [ ] bh 附着该实例不弹 `DevToolsConnectionDialog` 即连即通

达成后：P0001 回填实施过程、GOAL 移历史、CHANGELOG 记里程碑。
