# TODO：当前目标任务进度清单

> 角色：当前目标的任务进度清单。目标完成后回填 docs/proven 对应方案，起新清单。

## 任务进度清单

| 任务项 | 进度 | 说明 | 日期 |
| --- | --- | --- | --- |
| git 全局配置预检（autocrlf false 等） | 未开始 | R001 预检节命令 | |
| 装 VS 2026 + 两 SDK 组件 | 未开始 | Debugging Tools 别漏 | |
| 设 DEPOT_TOOLS_WIN_TOOLCHAIN=0 | 未开始 | 外部开发者必设 | |
| depot_tools clone + PATH + cmd 首跑 gclient | 未开始 | 必须 cmd.exe | |
| fetch --nohooks --no-history chromium | 未开始 | 千兆网约 1 至 3 小时 | |
| checkout 152.0.7977.84 + gclient sync | 未开始 | 钉 tag 建 local-152 分支 | |
| 打补丁 apply-auto-allow.ps1 | 未开始 | 已在参照树验证过 | |
| gn gen out\Release | 未开始 | 参数照 args.gn | |
| autoninja -C out\Release chrome | 未开始 | 首次 2 至 8 小时 | |
| 验收四条（PLAN 完成的定义） | 未开始 | findstr/curl/bh 三面验证 | |
| Linux 侧复制构建 | 未开始 | D03，Windows 验收后另立目标 | |
| macOS 侧复制构建 | 未开始 | D03，同上 | |
