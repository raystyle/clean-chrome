# tools 工具清单

> 全部 uv 运行 PEP 723 零依赖 Python,三平台同跑;新增或改动同步登记本表。补丁脚本 apply-auto-allow.py 归 patches\,不在此列。

| 脚本 | 用途 | 出处 |
| --- | --- | --- |
| check.py | 文档体系合规门禁 PE-01至13,提交前必跑,退出码 0 才过 | 自 ProjectEvo dev-evo scripts 拷入,ADR-0007 |
| mdrules.py | 四类禁字规则唯一权威,check.py 依赖,勿单独改 | 同上 |
| net-probe.py | 网络通道稳定性评估,全平台 | R001 替代路线节 |
| net-audit.py | 产物网络行为审计,net-log 全进程 Google 域外联统计 | S004 |
| deploy-release.py | Release 产物部署自包含目录至 C:\browse-rs,内置 ACE 自愈 | M027 |
| pack-tree.py | 构建树打包分发,双机同步用 | R001 分发节 |
| pipe-smoke.py | 管道通道验收与启动器范本,Windows io-pipes 契约活样例 | S005 |
