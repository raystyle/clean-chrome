# R001：chromium build 操作手册

> 现役流程：三平台编译带 `--auto-allow-devtools-connections` 的 Chromium，从环境预检到验收。命令是唯一权威，构建一律照此执行。版本基准：tag `152.0.7977.84`，核实日期 2026-09-11（依据 S001）。

## 一、预检

git 全局配置（官方要求，一次性）：

```powershell
git config --global core.autocrlf false
git config --global core.filemode false
git config --global core.preloadindex true
git config --global core.fscache true
git config --global branch.autosetuprebase always
git config --global core.longpaths true
```

其余预检：

- 控制面板「App execution aliases」取消 `python.exe` / `python3.exe` 指向 App Installer 的别名（防与 depot_tools 自带 python 冲突）
- Defender 排除 `E:\unsafe-chrome`（否则链接阶段被扫描拖到极慢）
- 磁盘：源码 + 构建按 200GB 准备；本机 E 盘 2026-09-11 有 741GB 空闲 [实证: 当日 Get-Volume]

## 二、工具链安装（仅 Windows）

| 组件 | 版本 | 备注 |
| --- | --- | --- |
| Visual Studio 2026 | >=18.0.0 | 勾 Desktop development with C++ 与 MFC/ATL 子组件 |
| Windows 11 SDK | 10.0.28000.2270 | VS 安装器内勾选或单独安装 |
| SDK Debugging Tools | 10.0.26100.3323+ | 控制面板、程序和功能、Windows SDK、Change、Debugging Tools for Windows |

环境变量（系统级）：

```text
DEPOT_TOOLS_WIN_TOOLCHAIN = 0      # 外部开发者必设,否则 gclient 找 Google 内部工具链失败
vs2026_install = C:\Program Files\Microsoft Visual Studio\2026\<Edition>   # 仅 VS 装非默认位置时
```

## 三、源码检出

depot_tools 与 fetch（首跑 `gclient` 必须在 cmd.exe，官方明确 PowerShell 会装坏 msysgit/python）：

```bat
cd /d E:\unsafe-chrome
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
:: 把 E:\unsafe-chrome\depot_tools 加到 PATH 最前(系统或用户变量,须在任何 python/git 之前)
set DEPOT_TOOLS_WIN_TOOLCHAIN=0
gclient
fetch --nohooks --no-history chromium
cd chromium\src
git fetch origin tag 152.0.7977.84
git checkout -b local-152 152.0.7977.84
gclient sync --with_branch_heads --with_tags
```

要点：

- `--no-history` 浅克隆最省时；打断后续跑 `gclient sync` 即可
- 想留全历史可改用 `fetch --git-cache chromium`（共享对象缓存约 30GB）
- 千兆网约 1 至 3 小时；期间禁休眠

## 四、打补丁

```powershell
E:\unsafe-chrome\patches\apply-auto-allow.ps1 -SrcRoot E:\unsafe-chrome\chromium\src
```

或钉 tag 标准补丁（在 `chromium\src` 下）：

```bat
git apply E:\unsafe-chrome\patches\auto-allow-devtools-connections-152.0.7977.84.patch
```

两者等价（S001 验证记录）；锚点失配报错是保护，照 S001 第六节升 tag 流程处理。

## 五、构建

```bat
gn gen out\Release --args="is_debug=false is_component_build=false is_official_build=false symbol_level=0 blink_symbol_level=0 v8_symbol_level=0"
autoninja -C out\Release chrome
```

- 参数唯一权威是根 `args.gn`；`enable_nacl` 上游已删，禁止出现 [实证: S001 结论 5]
- 只编 `chrome` 目标，不编 all；首次 2 至 8 小时（核数差异大），之后改 delegate 的增量是分钟级
- 迭代期可临时 `is_component_build=true` 加速链接，分发构建用非 component
- 构建后端已是 Siso，autoninja 用法不变

## 六、验证

启动：

```bat
E:\unsafe-chrome\chromium\src\out\Release\chrome.exe --user-data-dir=E:\tmp\cdp-dev --remote-debugging-port=9222 --auto-allow-devtools-connections
```

验收四条（对应 PLAN 完成的定义）：

```powershell
# 1 开关编进产物(在 chrome.dll,不在 chrome.exe;--help 不列自定义开关,别用它验证)
findstr /m /c:"auto-allow-devtools-connections" E:\unsafe-chrome\chromium\src\out\Release\chrome.dll
# 2 HTTP 端点通
curl http://127.0.0.1:9222/json/version
```

3. 全程无确认对话框（对照：不带开关时每个新连接弹 `DevToolsConnectionDialog`）
4. bh 附着该实例即连即通

## 七、Linux 与 macOS 简表

Linux（Ubuntu 22.04 x64 为基准；非 Ubuntu 走官方 Docker 说明）：

```bash
sudo apt update && sudo apt install -y git python3 python3-pip curl
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git ~/depot_tools
echo 'export PATH="$HOME/depot_tools:$PATH"' >> ~/.bashrc && source ~/.bashrc
mkdir -p ~/chromium && cd ~/chromium
fetch --nohooks --no-history chromium && cd src
./build/install-build-deps.sh
git fetch origin tag 152.0.7977.84 && git checkout -b local-152 152.0.7977.84
gclient sync --with_branch_heads --with_tags
gn gen out/Release --args='is_debug=false is_component_build=false is_official_build=false symbol_level=0 blink_symbol_level=0 v8_symbol_level=0'
autoninja -C out/Release chrome
./out/Release/chrome --user-data-dir=/tmp/cdp-dev --remote-debugging-port=9222 --auto-allow-devtools-connections
```

macOS：最新 Xcode + CLT；`ls "$(xcode-select -p)/Platforms/MacOSX.platform/Developer/SDKs"` 确认 SDK（权威版本看 `mac_sdk.gni` 的 `mac_sdk_official_version`）；APFS 卷；长任务套 `caffeinate`；Apple Silicon 默认 arm64，编 Intel 加 `target_cpu="x64"`；其余同 Linux（无 install-build-deps）。

平台注意：16GB 内存机配至少 16GB swap；Windows 的 depot_tools 不与 WSL 共用。

## 八、三台机器纪律

- 三台用同一 tag、同一份补丁；日常只在一台改，另两台 checkout 同 tag 后 `git apply` 同一 patch
- 不维护三份源码分叉；升 tag 顺序：一台更新补丁双形态并在参照树验证，再分发

## 九、常见坑速查

| # | 坑 | 处置 |
| --- | --- | --- |
| 1 | 路径含空格 | 全程 `E:\unsafe-chrome` 无空格 |
| 2 | Windows 首跑 gclient 用了 PowerShell | msysgit/python 装坏，删掉重来，必须 cmd.exe |
| 3 | 没设 DEPOT_TOOLS_WIN_TOOLCHAIN=0 | 外部开发者直接失败 |
| 4 | autocrlf 没设 false | 行尾污染，patch 应用异常 |
| 5 | args 写了 enable_nacl=false | 上游已删，gn gen 报未知参数 |
| 6 | Linux 没跑 install-build-deps.sh | 依赖缺失编译失败 |
| 7 | 跟 main 不跟 tag | 补丁对不上（152 与 main 已实证漂移） |
| 8 | 杀毒扫描 out 目录 | 链接极慢，加 Defender 排除 |
| 9 | 默认 User Data 开调试端口 | M136 起被拒，必须另开 --user-data-dir |
| 10 | 把调试端口暴露外网 | 开关一开即全控制权，端口只听 127.0.0.1，禁配 --remote-debugging-address |
