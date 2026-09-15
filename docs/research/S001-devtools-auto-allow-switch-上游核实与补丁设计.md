# S001：devtools auto-allow 开关上游核实与补丁设计

> 研究文档：为什么 auto-allow-devtools-connections 必须自己编译、上游机制是什么、补丁怎么设计。核实日期 2026-09-11，信源为 chromium.googlesource.com main 分支与 `152.0.7977.84` tag 源码及官方文档原文。

## 一、背景与问题

用户指南声称「编译自定义 Chromium 加 `--auto-allow-devtools-connections`」可行；立项前需核实：开关是否已存在、企业策略能否免编译绕过、代码落点与版本漂移、Windows 工具链现状。

## 二、关键结论

| # | 结论 | 事实标记 |
| --- | --- | --- |
| 1 | `--auto-allow-devtools-connections` 上游不存在：`chrome_switches.cc@152.0.7977.84` 相关常量仅 `kDevToolsFlags` / `kDevToolsNavigationGatingRules` / `kRemoteDebuggingTargets`，全网检索亦无此开关 | [实证: 2026-09-11 gitiles 逐文件核对] |
| 2 | 企业策略 `RemoteDebuggingAllowed` 只管调试总闸（禁则 `--remote-debugging-port` 全失效），开着时确认对话框照弹，不能免编译 | [实证: 2026-09-11 chromeenterprise 策略页与多个下游 issue] |
| 3 | 2026-09 Stable 为 152.0.7977.84（153 rollout 中）；2026-09 起 Chrome 改两周发一版，tag 通胀加快，补丁更须钉死 tag | [实证: ChromiumDash 2026-09-11] |
| 4 | Windows 工具链（main 文档原文）：VS 2026 (>=18.0.0) + Desktop C++ + MFC/ATL；Win11 SDK 10.0.28000.2270；Debugging Tools 10.0.26100.3323+；外部开发者必设 `DEPOT_TOOLS_WIN_TOOLCHAIN=0` | [实证: 2026-09-11 windows_build_instructions.md] |
| 5 | `enable_nacl` GN 参数上游已删除（`build/config/features.gni` 与 `chrome/common/buildflags.gni` @152 均无），args 里写了 gn gen 报未知参数 | [实证: 2026-09-11 两文件逐行核对] |
| 6 | 构建系统为 Siso（autoninja 包装，用法不变）；Linux 基准仍 Ubuntu 22.04（文档移至 `docs/linux/build_instructions.md`）；macOS 不钉 Xcode 版本，以 `mac_sdk.gni` 的 `mac_sdk_official_version` 为准 | [实证: 2026-09-11 各平台文档] |
| 7 | M136 起默认 User Data 拒绝 `--remote-debugging-port`，调试实例必须另开 `--user-data-dir`；144+ 默认 profile 走 chrome://inspect#remote-debugging 开关，但每个连接仍弹确认对话框 | [经验: bh browser 技能口径 + S001 机制节] |

## 三、上游机制细节

确认对话框链路（2026-09-11 源码核实）：

1. 连接进来后 Chrome 层回调 `ChromeDevToolsManagerDelegate::AcceptDebugging(AcceptCallback callback)` [实证: @152 源码]
2. 该函数先把 callback 包一层 UMA 上报（`DevTools.RemoteDebugging.ConnectionPermission`），再取 last active browser 交给 `DevToolsConnectionDialog::Show()` [实证: @152 源码]
3. 对话框三种结局：Allow 按钮回 `kAllow`；Cancel/关闭/Disable 按钮均回 `kDeny`；**无浏览器窗口时构造函数直接自动 `kDeny`** [实证: `devtools_connection_dialog.cc`@main]
4. `AcceptConnectionResult` 枚举位于 `content::DevToolsManagerDelegate`，仅 kAllow/kDeny 两值 [实证: @152 源码]
5. 版本漂移实证：152 用 `GlobalBrowserCollection`，main 已重构为 `ProfileBrowserCollection`；即补丁必须钉 tag，跨版本要重打 [实证: 2026-09-11 两版源码对比]

另注：`SetActiveWebSocketConnections` 在有连接期间展示全局 infobar（纯提示），补丁不改它。

## 四、补丁设计

设计目标：最小改动、自包含、抗小版本漂移。共 3 文件 +14 行：

| 文件 | 改动 | 锚点与理由 |
| --- | --- | --- |
| `chrome/common/chrome_switches.h` | +1 行 extern 声明 | 插在 `kAutoOpenDevToolsForTabs` 前：同为「自动化免用户交互」开关族，字母序正确（Auth < AutoAllow < AutoOpen） |
| `chrome/common/chrome_switches.cc` | +4 行（注释 2 + 常量 + 空行） | 同上位置，锚定其注释行 |
| `chrome/browser/devtools/chrome_devtools_manager_delegate.cc` | +9 行守卫块 | 锚定 `AcceptDebugging` 签名行（签名跨版本稳定），在其后插入：有开关则 `std::move(callback).Run(kAllow); return;` |

自包含性：目标文件本就 include `base/command_line.h` 与 `chrome/common/chrome_switches.h`，无需新增 include [实证: @152 include 列表]。

双形态交付（必须等价）：

1. `patches\apply-auto-allow.ps1`：锚定式编辑，幂等（已含开关则跳过），锚点失配或重复时显式报错，供跨近似 tag 使用
2. `patches\auto-allow-devtools-connections-152.0.7977.84.patch`：标准 git patch，钉死该 tag

## 五、验证记录

- 脚本在 152 原始三文件副本上运行：三文件全部 patched，幂等重跑显示 skip [实证: 2026-09-11]
- `.patch` 以 `git apply --check` 通过并实际应用成功 [实证: 2026-09-11]
- 两种形态输出内容逐字节等价（归一换行后比对；差异仅源于当时本机 autocrlf=true 导致 git apply 全文 CRLF 重写，非内容差异） [实证: 2026-09-11]
- 真实构建验证（编译、链接、行为）尚未进行，属构建方案范围（现 REQ-002）[假设: 补丁在完整构建中无编译错误，验证路径为该方案步骤 6 至 7]

## 六、待验假设与升 tag 注意

- [假设: 根 args.gn 全套参数在 152 上 gn gen 通过] 验证：首次 gn gen 无 unknown argument 报错
- [假设: 签名行锚点在 153/154 仍不变] 验证：升 tag 时先跑 apply 脚本，失配则按新版源码更新锚点并在参照树重验
- 升 tag 流程：fetch 新 tag、checkout、跑 apply 脚本、锚点失配报错属预期保护，参照 `poc\S001-chromium152-auto-allow\` 树重做双形态
- 安全边界：开关一开，能连上调试端口的本地进程都拿到完整 CDP 控制权且无提示；端口默认仅听 127.0.0.1，禁止配 `--remote-debugging-address` 暴露外网
