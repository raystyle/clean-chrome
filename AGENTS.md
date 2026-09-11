# unsafe-chrome：开发协作规则

> 唯一权威源。`CLAUDE.md` 仅一行 `@AGENTS.md` 桥接，不重复维护。

## 一、项目定位

> 本项目的本质与边界。根为定位，下分本质、边界、交互对象。

1. **本质**：维护一份 Chromium 补丁与三平台构建流程，产出带 `--auto-allow-devtools-connections` 的自编译 Chromium，作为本机自动化（bh / CDP 工具链）的专用浏览器
2. **边界**：补丁只动 `chrome_switches.h` / `chrome_switches.cc` / `chrome_devtools_manager_delegate.cc` 三文件；钉稳定 tag 不跟 main；绝不提交上游；不替换、不影响日常 Chrome；不做官方 branding，不承诺自动更新（自己定期升 tag 重编）
3. **交互对象**：用户本人与 coding agent（Windows 主战场，Linux 与 macOS 为辅助机）；产物由 CDP 客户端消费

## 二、工作规则

> 四类场景：对话、操作、编码、文档。先列动作清单，再定规则（可以/禁止/参考）。

### 对话

- 每轮先核对四原语（PRD/GOAL/PLAN/TODO）；新需求先入 PRD 走追问链，禁止静默假设
- 对话分两式：立项拷问走你问我答（整轮齐问、附推荐答案）；咨询答疑走我问你答（先读文档再答、答必六态）
- 一次只推进一个目标；踩坑当场落 `docs\mistakes\`

### 操作

- Windows 用 PowerShell 7(`pwsh`)；Linux/macOS/WSL 用该平台常规 shell；文档与源码 UTF-8
- Chromium 官方 git 全局配置（`core.autocrlf false` 等）见 R001 预检节；任何构建动作前逐条核对
- 未经指示不做 commit/push/reset 等变更操作；提交一事一提交（`docs:`/`feat:`/`fix:`/`chore:` 前缀）
- 构建与打补丁命令一律照 R001 执行，不即兴组合参数

### 编码

- 补丁只有两种交付形态：`patches\apply-auto-allow.py`（锚定式 uv 运行，默认用，三模式 before/after/replace）与 `patches\auto-allow-devtools-connections-<tag>.patch`（钉 tag 标准补丁）；两者必须等价（2026-09-11 起替代 ps1 版）
- 补丁边界 19 锚 12 文件（2026-09-11 深夜定档,清单与机制见 S002/S003）：CDP 摩擦（对话框/端口 9222/默认目录/调试 infobar）、启动静默（API 密钥/过时系统/OSCrypt/默认浏览器与会话恢复 infobar/crash 气泡两处/首跑向导）、Google 触点剔除（NTP 工厂 about:blank/默认搜索关/AI Mode 关/启动型恒 DEFAULT）
- 改锚点或升 tag：先在 `poc\S001-chromium152-auto-allow\` 参照树上验证两种形态等价，再更新补丁文件
- 开关语义：`AcceptDebugging()` 开头短路回 `kAllow`；`SetActiveWebSocketConnections` 的 infobar 已裁定移除（2026-09-11 用户裁定，S002 第二节）；短路整段逻辑一律用替换式锚定，禁止提前 return（-Wunreachable-code，M011）
- 明确保留的本机安全闸门：端口仅 127.0.0.1、RemoteDebuggingAllowed 策略 gate、Host header 校验（S002 第四节）
- GN 参数唯一权威是根 `args.gn`；`enable_nacl` 上游已删除，任何 args 里禁止出现 [实证: S001 结论表]
- `poc\` 内参照文件是上游原始字节，只读不改

### 文档

| 动作 | 时机 | 义务 |
| --- | --- | --- |
| 新需求提出 | 提出时 | PRD 登记新行 |
| 目标立项 | 开工前 | GOAL 起点/锚点、PNNNN 方案、PLAN、TODO 清单 |
| 选型与调研 | 研究完成 | S 文档（六态）+ INDEX 研究节 |
| 写改补丁与脚本 | 改动完成 | README 同步；R001 对应节同步；版本级成果进 CHANGELOG |
| 出验证产物 | 验证完成 | `poc\README.md` 登记表 + S 文档结论回填 |
| 踩坑 | 当场 | MISTAKES.md 接编一行；INDEX 错误节同步 |
| 方案达成 | 验收全绿 | proven 回填、GOAL 历史行、INDEX 归档节 |
| 每次提交 | 提交后 | diary 当天记钩子 |
| 发布 | tag 后 | CHANGELOG 封版、ROADMAP 阶段状态 |
| 文档结构变更 | 改名移目录后 | INDEX 同步 |

## 三、意图路由

> 需求意图到文档/命令的映射摘要层；细则唯一权威见对应 R 文档。

- 构建/环境预检/平台差异 到 `docs\references\R001-chromium-build-操作手册.md`
- 补丁锚点、升 tag、上游代码漂移 到 `docs\research\S001` 与 `patches\`
- 开关行为与上游确认对话框机制 到 `docs\research\S001`
- 文档命名与写作规范 到 `docs\guide\G001`
- 踩坑与历史错误 到 `docs\mistakes\MISTAKES.md`
- 项目状态交接到 GOAL 进程段与 diary 最新篇

## 四、资源索引

> 配合 INDEX 的搜索方法与分析路径。

```powershell
rg -n "关键词" INDEX.md                        # 1 先搜总索引
rg --files docs | rg 关键词                     # 2 按文件名搜
rg -n "关键词" docs\research docs\references    # 3 全文搜研究参考
rg -n "关键词" docs\mistakes\                   # 4 搜错误处理
```

分析路径：改补丁行为先读 S001 再动手；构建操作先读 R001；规范禁令查 G001；踩坑查 MISTAKES.md。
