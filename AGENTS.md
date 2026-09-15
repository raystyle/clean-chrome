# clean-chrome

> 自编译 Chromium 加命令行开关 `--auto-allow-devtools-connections`：每个远程调试连接不经确认对话框直接放行。作为本机自动化（bh / CDP 工具链）专用浏览器,公开契约以补丁双形态字节等价与根 args.gn 为准。边界:绝不提交上游、只钉稳定 tag 不跟 main、不替换日常 Chrome、不承诺自动更新。

## Commands

```powershell
# 打补丁(锚定式,幂等,uv 全平台;改锚点或升 tag 流程见 S001 第六节)
uv run patches/apply-auto-allow.py --src-root C:/clean-chrome/chromium/src
# 构建全流程唯一权威(预检/工具链/检出/补丁/构建/验证/分发),不即兴组合参数
# docs\guides\R001-chromium-build-操作手册.md
# 文档合规门禁 PE-01至13,提交前必跑,退出码 0 才过
uv run tools/check.py .
# 管道通道验收与启动器范本
uv run tools/pipe-smoke.py --mode pipe
```

## Must

- 新需求先立 REQ（docs\requirements）,不可逆选择先立 ADR（docs\adr）;禁止静默假设
- 改锚点或升 tag:先在 poc\S001 参照树验证补丁双形态等价,再更新补丁文件
- 短路整段逻辑一律替换式锚定;行为抑制优先 feature/pref 默认值（工作流照 docs\guides\G002）
- 写改补丁与脚本:R001 对应节与 README 同步;版本级成果进 CHANGELOG
- 出验证产物:poc\README.md 登记 + S 文档结论回填;研究完成落 S 文档（六态）并登记 research\README
- 踩坑当场处置:diary 当日记,M 号按 R001 十节或 G002 四节落位;同型二犯起配机器可执行约束
- 一次只推进一个目标;提交一事一提交（docs:/feat:/fix:/chore: 前缀）,提交后 diary 记钩子
- 立项拷问整轮齐问附推荐答案;答必六态,先读文档再答

## Must not

- `enable_nacl` 出现在任何 args（上游已删）
- 短路逻辑用提前 return（-Wunreachable-code）;幂等 marker 用上游已有字节
- 提交上游;改动 poc\ 参照文件（上游原始字节只读）;替换或影响日常 Chrome
- 未经指示做 commit/push/reset 等变更操作
- 把 why 写进函数注释或本合同（进 ADR）;手改生成物或另写第二份真相
- 把没验证的写成已验证（六态红线）

## Read first

- 构建操作:docs\guides\R001;补丁机制与升 tag:docs\research\S001
- 决策取舍:docs\adr\README.md;需求与验收:docs\requirements\README.md
- 写作规范:docs\guides\G001;补丁脚本与字节产物工作流:docs\guides\G002
- 研究档案:docs\research\README.md;项目日记:docs\diary\README.md
- 检索:rg -n "关键词" docs 逐目录全搜;状态交接看 diary 最新篇与 CHANGELOG.md

## 环境

- Windows 11 + pwsh 7 主战场;lan-mac / lan-ubuntu 为辅助编译机;文档与源码 UTF-8
- 版本基准:tag `152.0.7977.84`;产物 out\Dev（迭代）与 out\Release（分发）;部署 C:\browse-rs\chromium-152.0.7977.84
- 调试通道:`CLEAN_CHROME_DEBUG=port|pipe|both`,默认 port（9222）,显式开关永远优先（ADR-0006）
- GN 参数唯一权威:根 args.gn;Chromium 官方 git 全局配置见 R001 一节,任何构建动作前逐条核对
- 字节产物（diff/patch）不用 PowerShell 管道落盘,用 Git Bash 重定向（G002 二节）
