---
id: REQ-011
title: 文档体系迁移 dev-evo 五节合同
status: implemented
priority: must
trace: tools/check.py
---

# REQ-011:文档体系迁移 dev-evo 五节合同

关联:2026-09-15 用户裁定（激进标准化/REQ 细粒度 11 篇/门禁拷入 tools/两笔提交）;决策记录 ADR-0007;承接 REQ-001。

## Scenario

现行上一代骨架（根四原语 + INDEX + docs 六目录）按 dev-evo 标准迁移为五节合同 + ADR/REQ 体系,不留双轨。

## Criteria

- [x] AGENTS.md 五节合同（Commands/Must/Must not/Read first/环境）
- [x] docs\adr 与 docs\requirements 运转,PRD 十一条目全部迁入且 trace 回填
- [x] MISTAKES 27 条按错误链分流进 guides（R001 坑表与 G002）,M0xx 行号保留
- [x] proven/references/guide/mistakes 目录与根四原语、INDEX 退役,全仓引用替换归零
- [x] tools\check.py 加 mdrules.py 入仓,PE-01至13 全绿（提交前必跑）
