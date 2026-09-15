# GOAL：任务目标管理

> 角色：工作任务管理，四个部分：起点、锚点、进程、历史。随工作实时更新。

## 起点

- **日期**：2026-09-11
- **起点**：agent 自动化附着本机浏览器时，被 DevTools 远程调试确认对话框打断；上游无此开关、企业策略不能免对话框，编译自定义 Chromium 是唯一路径 [实证: S001 结论表]，据此立项 D02/D03

## 锚点

- **锚定的目标**：D02-8 console 参数预览抑制（收官 2026-09-15）：console.* 与未捕获异常经 CDP 上报不再急切序列化对象数据进协议 payload（50 锚 34 文件,首入 v8/ 树,objectId 保留按需可取）;evaluate 预览与文本通道保持原样（实测通道图定档,载体 S006）

### 推进时间线

| 日期 | 进展 |
| --- | --- |
| 2026-09-11 | 研究核实完成（S001）；补丁双形态产出并回环验证；文档骨架建立 |
| 2026-09-11 | 环境铺路：git 六条全局配置、depot_tools 就位（用户 PATH 前插 + DEPOT_TOOLS_WIN_TOOLCHAIN=0）、VS 2026 安装与 chromium fetch 双线启动、增量编译双目录策略定档（Dev 迭代 + Release 分发） |

## 进程

- 当前目标：D02-8 **console 参数预览抑制收官（2026-09-15）**：50 锚 34 文件（首入 v8/ 树 v8-console-message.cc 收口 reportToFrontend 两分支）,四端验收矩阵全绿（本机 Dev/browse-rs 部署沙箱态/lan-mac/lan-ubuntu 逐项一致：preview 消失、objectId 保留、evaluate 两态不变）
- 前提修正两轮裁定定档（S006 通道图）：152 的 preview 不调 accessor/Proxy 陷阱（原验收 A 本就过）;文本通道 stock 一致非 CDP 差分,保持原样防反造差分;preview-off 实效=数据卫生+上游回归免疫
- 三机同步：mac/ubuntu 脚本重打 ok=0/skip=50,增量 13 步 40.3s / 50 步 20.8s,树内 node v24.12.0 跑同探针验收
- 顺带修复：M027 browse-rs AppContainer ACE（部署目录重建抹 ACE 致沙箱态 0x5 崩,deploy-release.py 已内置 icacls 自愈）;M024-M026（bh eval Node 环境/PS 管道换行污染/git apply 子目录 skip）入库
- 前一里程碑：D02/D03 三平台完美产物（2026-09-13,43 锚全编）,D02-2 至 D02-7 子项全交付（历史行见下）

## 历史

| 日期 | 目标 | 结果 |
| --- | --- | --- |
| 2026-09-11 | D02 Windows 构建（Dev 验收） | 全绿：自编 chrome.exe/dll 带开关零弹窗,bh 端到端附着通;Release 分发产物待编 |
| 2026-09-12 | D02 深化（Release 部署 + 43 锚网络清零 + 更名 clean-chrome） | Release 部署 C:\browse-rs 全绿;43 锚 32 文件净测 Google 域 0 外联（S004）;GitHub/本地全量更名;改名双坑 M018/M019 当日修复 |
| 2026-09-13 | D02/D03 收官（三平台原子化重编 + 逐台验收） | **三平台完美产物**：预检矩阵过全部历史坑,三台全清从起点重编（Win 3h/mac 3h42m/linux 6h30m）,逐台四条全绿;本机另过 net-audit 0 外联/部署刷新/bh 冒烟;M020-M022 入库 |
| 2026-09-14 | D02-6 调试通道环境变量化 | 全绿：CLEAN_CHROME_DEBUG 三态（port/pipe/both）,47 锚;管道走 io-pipes 句柄契约,范本 tools\pipe-smoke.py;三态矩阵+双形态等价全过;M023 入库;双机同步留后续 |
| 2026-09-15 | D02-7 bad-flags 黄条剔除 + linux 换机 lan-ubuntu | 全绿：48 锚 33 文件三台对齐,--no-sandbox 无黄条（截图目检）;lan-ubuntu rsync 全量分发（含 out/ 保增量态）,迁移+增量 4 步 21.6s+首跑验收全过;browse-rs 部署仍 47 锚,下次部署带 48 |
| 2026-09-15 | D02-8 console 参数预览抑制 | 全绿：50 锚 34 文件（首入 v8/ 树）;两轮裁定（范围三推荐+前提修正照规格落 preview-off）;四端验收矩阵一致（preview 消失/objectId 保留/evaluate 不变/A 过/B 文本通道记录性）;三机 ok=0/skip=50 同步增量;M024-M027 入库 |
