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
- Defender 排除 `C:\clean-chrome`（否则链接阶段被扫描拖到极慢；实证 2026-09-11：未排除时 `git add` 40 万文件仅 21 文件/秒，排除后正常）[实证: M008 同日]
- pip 全局配置 `C:\Users\<u>\AppData\Roaming\pip\pip.ini` 必须无 BOM：带 BOM 则 vpython venv 构建每轮必炸（M008）
- 磁盘：源码 + 构建按 200GB 准备；2026-09-11 平移到 C: 内置 NVMe（724GB 空闲），E: 弃用 [实证: 当日 Get-Volume]
- 布局价值主张：本目录的存在意义是**稳定增量编译 + 环境快速稳定重建**，一切布局决策（内置 NTFS、Defender 排除、双 out 目录、文档化的替代路线）都为这两条服务；换机/重装时按本手册应可在半天内从零恢复到可编译状态

## 二、工具链安装（仅 Windows）

| 组件 | 版本 | 备注 |
| --- | --- | --- |
| Visual Studio 2026 | >=18.0.0 | 勾 Desktop development with C++ 与 MFC/ATL 子组件 |
| Windows 11 SDK | 10.0.28000.2270 | VS 安装器内勾选或单独安装 |
| SDK Debugging Tools | 10.0.26100.3323+ | 2026-09 实测 VS 组件图已无 `Windows11SDK.DebuggingTools` 包 ID、`msiexec ADDREMOVE` 对 VS 装的 SDK 也无效（缓存 MSI 不在标准位置）；正确姿势是下载对应版本 winsdksetup.exe 后 `& "$env:TEMP\winsdksetup-26100.exe" /features OptionId.WindowsDesktopDebuggers /q /norestart`（installer 直链见 learn.microsoft.com/windows/apps/windows-sdk/downloads），装完验 `Windows Kits\10\Debuggers\x64\cdb.exe` [实证: 2026-09-11] |

环境变量（系统级）：

```text
DEPOT_TOOLS_WIN_TOOLCHAIN = 0      # 外部开发者必设,否则 gclient 找 Google 内部工具链失败
vs2026_install = C:\Program Files\Microsoft Visual Studio\2026\<Edition>   # 仅 VS 装非默认位置时
```

## 三、源码检出

depot_tools 与 fetch（首跑 `gclient` 必须在 cmd.exe，官方明确 PowerShell 会装坏 msysgit/python）：

```bat
cd /d C:\clean-chrome
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
:: 把 C:\clean-chrome\depot_tools 加到 PATH 最前(系统或用户变量,须在任何 python/git 之前)
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

### 网络受阻环境的替代路线（2026-09-11 全程实战）

先量化再选路（全平台,uv 运行,零依赖）：

```bash
uv run tools/net-probe.py            # 7 通道 x 多轮采样,输出成功率/延迟/判级与路线建议
uv run tools/net-probe.py --repo google/skia   # 探指定镜像仓的 codeload 通道
```

当 git 协议对 googlesource/GitHub 大流量传输被掐（现象：clone/fetch 传一截后 `early EOF` / `expected 'packfile'` / SSH `Bad packet length`，或干脆 0 字节挂死）时，通道实况与对策：

| 通道 | 实况 | 用途 |
| --- | --- | --- |
| `codeload.github.com`（纯 HTTP GET tarball） | 稳定，aria2 x16 实测 103Mbps | 主仓源码树落地 |
| `git@github.com` SSH（22/443 均可） | 认证通，大流量可能被掐但死点随机，重试可成 | 主仓 git 对象归化 |
| CIPD（chrome-infra-packages） | 时通时断 | 二进制包，gclient 自动重试 |
| googlesource git 协议 | 强干扰，ls-remote 都超时 | 只能等窗口 |
| Gitee `mirrors/chromium` | 已 404 | 不可用，网传教程过时 |

主仓替代（tarball 落地 + SSH 归化）：

```powershell
# 1 tarball 落地（aria2 多连接分段+断点续传，专治传输掐断）
aria2c -x16 -s16 -c -m 20 --retry-wait=5 -d C:\clean-chrome\chromium -o chromium-152.tar.gz https://codeload.github.com/chromium/chromium/tar.gz/refs/tags/152.0.7977.84
# 2 解压改名（bsdtar 会报约 7 个 symlink 失败，属预期，后续 git checkout 按Windows语义补齐）
tar -xzf chromium-152.tar.gz; Move-Item chromium-152.0.7977.84 src
# 3 建仓并归化到官方 tag 对象（fetch 走 SSH；被掐就重试，已传对象入库不浪费）
cd src; git init; git config core.symlinks false
git fetch --depth=1 git@github.com:chromium/chromium.git refs/tags/152.0.7977.84
git checkout -f -b local-152 FETCH_HEAD
# 4 .gclient 的 solution url 记得 pin：.../src.git@refs/tags/152.0.7977.84（防 sync 把 src 拽回 main）
```

依赖拉取加速（insteadOf 镜像注入，仅影响注入进程树）：对 GitHub 有官方镜像且体量大的仓，用 `GIT_CONFIG_COUNT` 环境变量注入 `url.<ssh-url>.insteadOf=<googlesource-url>`（2026-09-11 实测有效映射：skia -> git@github.com:google/skia.git、devtools-frontend -> ChromeDevTools/devtools-frontend、quiche -> google/quiche；v8/angle/pdfium/boringssl/dawn/catapult/ffmpeg/webrtc 在窗口期可直接拉，未必须映射）。注意 `GIT_CONFIG_COUNT` 的数值必须严格等于 KEY/VALUE 对数。

依赖拉取的自愈模式（gclient 循环 + 陪跑）：

- gclient sync 挂后台重试循环：每轮先 `Stop-Process git,git-remote-https` 清残骸进程，注入低速超时（`http.lowSpeedLimit=2000` + `http.lowSpeedTime=90`）让卡死自曝；已拉的仓下轮自动跳过，进度单调递增
- 陪跑脚本盯循环输出：gclient 死于某仓 `git rebase --onto ... could not detach HEAD`（半成品仓缺对象，不可续传）时自动删该仓目录，下轮重 clone
- 杀 fetch/gclient 任务后必须清场（M006 全套）：git 残留进程、`src\.git\shallow.lock`、`_gclient_*` 临时目录

## 四、打补丁

```powershell
# 锚定式(默认用,幂等,uv 全平台,五文件六锚,before/after/replace 三模式)
uv run C:\clean-chrome\patches\apply-auto-allow.py --src-root C:/clean-chrome/chromium/src
```

或钉 tag 标准补丁（在 `chromium\src` 下）：

```bat
git apply C:\clean-chrome\patches\auto-allow-devtools-connections-152.0.7977.84.patch
```

两者等价（S001/S002 验证记录）；锚点失配报错是保护，照 S001 第六节升 tag 流程处理。短路整段逻辑必须用 replace 模式,禁止提前 return（-Wunreachable-code-aggressive + -Werror,M011）。效果清单见 S002 第二节（默认端口 9222、零对话框、零 infobar、默认 User Data 零限制）。

## 五、构建

双目录策略（后期要改功能，增量迭代为主）：

| 目录 | 定位 | args 要点 | 用途 |
| --- | --- | --- | --- |
| `out\Dev` | 迭代主力 | `is_component_build=true` `symbol_level=1` `blink_symbol_level=0` `v8_symbol_level=0` | component 把 chrome 拆多个小 DLL，改 chrome/ 内文件只重链对应 DLL，增量为分钟级；symbol_level=1 留行号可调源码 |
| `out\Release` | 分发产物 | `is_component_build=false` `symbol_level=0` | 验收后全编一次的干净产物 |

```bat
:: 先 Dev 走通验收
gn gen out\Dev --args="is_debug=false is_component_build=true is_official_build=false symbol_level=1 blink_symbol_level=0 v8_symbol_level=0"
autoninja -C out\Dev chrome

:: 后 Release 出分发产物
gn gen out\Release --args="is_debug=false is_component_build=false is_official_build=false symbol_level=0 blink_symbol_level=0 v8_symbol_level=0"
autoninja -C out\Release chrome
```

- 参数唯一权威是根 `args.gn`（模板与说明）；`enable_nacl` 上游已删，禁止出现 [实证: S001 结论 5]
- 只编 `chrome` 目标，不编 all；首编实测（64GB RAM、C: NVMe）：`-j 32` 会 OOM 被杀，`-j 16` 稳定约 4.5 小时（blink/v8 巨型 obj 段吃掉大头），扩页面文件至 32GB+ 后可试 `-j 24`；改 delegate/switches 的增量是分钟级 [实证: 2026-09-11]
- 增量由 autoninja(ninja) 天然保证，不手动清 out；目录参数定型后禁止再改（改 component/symbol 触发近全量重编）
- 构建后端已是 Siso，autoninja 用法不变

## 六、验证

启动（2026-09-11 起**无需任何参数**,补丁已默认开 9222）：

```bat
C:\clean-chrome\chromium\src\out\Release\chrome.exe
```

如需隔离实例或换端口,显式参数仍可叠加：`--user-data-dir=<dir>` / `--remote-debugging-port=<port>`。

验收四条（对应 PLAN 完成的定义）：

```powershell
# 1 开关编进产物(在 chrome.dll,不在 chrome.exe;--help 不列自定义开关,别用它验证)
findstr /m /c:"auto-allow-devtools-connections" C:\clean-chrome\chromium\src\out\Release\chrome.dll
# 2 HTTP 端点通
curl http://127.0.0.1:9222/json/version
```

3. 全程无确认对话框（对照：不带开关时每个新连接弹 `DevToolsConnectionDialog`）
4. bh 附着实战验收（优先方式,替代裸 WS 探针）：

```powershell
$env:BH_CDP_URL='http://127.0.0.1:9222'   # 直指端点,绕开 daemon discovery 的 UUID 缓存
bh --restart --yes                          # daemon 重连;--status 应见 connected:true
bh --new-tab 'goto_url("https://www.google.com/")'   # 专属 tab;先过首页建立 cookie
bh 'goto_url("https://www.google.com/search?q=chromium+152")'
bh 'js("JSON.stringify({url: location.href, title: document.title, n: document.querySelectorAll(\"#rso h3\").length})")'
```

   通过判据:connected:true、搜索结果 n>0、全程无弹窗。注意:新 profile 无 cookie 直链搜索会吃 Google `/sorry` 反机器人页,先访问一次首页即可 [实证: 2026-09-11]

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
| 1 | 路径含空格 | 全程 `C:\clean-chrome` 无空格 |
| 2 | Windows 首跑 gclient 用了 PowerShell | msysgit/python 装坏，删掉重来，必须 cmd.exe |
| 3 | 没设 DEPOT_TOOLS_WIN_TOOLCHAIN=0 | 外部开发者直接失败 |
| 4 | autocrlf 没设 false | 行尾污染，patch 应用异常 |
| 5 | args 写了 enable_nacl=false | 上游已删，gn gen 报未知参数 |
| 6 | Linux 没跑 install-build-deps.sh | 依赖缺失编译失败 |
| 7 | 跟 main 不跟 tag | 补丁对不上（152 与 main 已实证漂移） |
| 8 | 杀毒扫描 out 目录 | 链接极慢，加 Defender 排除 |
| 9 | 默认 User Data 开调试端口 | 仅锁官方品牌 Chrome（GOOGLE_CHROME_BRANDING 编译开关,remote_debugging_server.cc:169）；自编非 branded Chromium 默认目录也可直接开端口（2026-09-11 实测 9223 通）；--user-data-dir 仍推荐,作实例隔离与 profile 复用 |
| 10 | 把调试端口暴露外网 | 开关一开即全控制权，端口只听 127.0.0.1，禁配 --remote-debugging-address |
| 11 | pip.ini 带 BOM | vpython venv 构建必炸，无 BOM 重写（M008） |
| 12 | 停 fetch/gclient 任务后留残骸 | M006 全套清场再重启 |
| 13 | VS 组件图找不到 DebuggingTools 包 | 装 Debuggers 用 winsdksetup /features，见工具链节 |
| 14 | tar 解压报 symlink Invalid argument | 预期行为（约 7 个），git checkout 按 core.symlinks=false 补齐 |
| 15 | 系统装过 Go 且设了 GOROOT | dawn/tint 生成器 go 版本错配（M009），构建 shell 先 `GOROOT/GOPATH/GOCACHE` 置空；项目内工具链优先，勿让系统 go/python 环境变量外泄进构建 |
