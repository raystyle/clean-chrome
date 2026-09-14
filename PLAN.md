# PLAN：当前目标实施计划

> 角色：当前目标方案文档：基于 research（为什么）与 references（怎么做）的执行计划；每条挂依据来源，不存历史目标。

## 当前目标

D02-6 调试通道环境变量化：`CLEAN_CHROME_DEBUG=port|pipe|both`（默认 port 即现行为 9222;pipe 只管道不开端口;both 都开），管道句柄由启动方经 `--remote-debugging-io-pipes` 传入（机制见 `docs\research\S005`）

## 步骤

| # | 步骤 | 依据 |
| --- | --- | --- |
| 1 | S005 机制研究定稿（pipe handler/AdoptPipes/断线关闸/协议模式） | 本轮源码实读 |
| 2 | 改锚：remote_debugging_server.cc 通道选择块（env 读值 + pipe 启停 + 端口默认联动）,写入 apply-auto-allow.py（边界内文件,锚数 43 至 44） | S005 设计节;M017 marker 纪律 |
| 3 | 参照树等价验证：脚本形态与 .patch 形态产物字节一致 | AGENTS 编码节;S001 流程 |
| 4 | 增量重编 Release + Dev（单文件改动,分钟级/链一次 dll） | R001 五节 |
| 5 | 验收矩阵：unset 至 9222;pipe 至 管道通且 9222 不听;both 至 双通（Python 启动器传 io-pipes 实测） | S005 验证节 |
| 6 | 文档同步：README/R001/CHANGELOG/INDEX/diary/TODO;提交推送 | AGENTS 文档节 |

## 完成的定义

- [ ] 未设变量：无参数启动 9222 照旧,行为与 43 锚版一致
- [ ] `CLEAN_CHROME_DEBUG=pipe`：管道 CDP 双向通（Target.getBrowserVersion 往返）,9222 无监听
- [ ] `CLEAN_CHROME_DEBUG=both`：9222 与管道同时可用
- [ ] 两补丁形态等价（字节比对）;脚本幂等（重跑全 skip）
- [ ] README/R001 同步,CHANGELOG 记条
