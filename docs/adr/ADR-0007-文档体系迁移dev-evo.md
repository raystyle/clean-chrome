---
id: ADR-0007
title: 文档体系迁移 dev-evo 五节合同
status: accepted
date: 2026-09-15
deciders: [ray]
supersedes: []
superseded_by: null
tags: [docs]
---

# ADR-0007:文档体系迁移 dev-evo 五节合同

## Context

现行文档体系是 project-evo 上一代骨架（根四原语 PRD/GOAL/PLAN/TODO + INDEX + docs 六目录）,运行五天无规则事故,但需求追溯与决策留案分散在四原语与 S 文档里。dev-evo 已演进为五节合同 + ADR/REQ 体系,其存量迁移映射与本仓旧体系一一对应。2026-09-15 用户裁定:激进标准化迁移（历史引用全量替换,不留双轨）、REQ 细粒度 11 篇、check.py 门禁拷入 tools\、两笔提交。

## Decision

AGENTS.md 重写为五节合同（Commands/Must/Must not/Read first/环境）;PRD 条目转 REQ 十一篇,PLAN/TODO 语义并入 Criteria 与 trace,GOAL 定位句并入 AGENTS 与 README,INDEX 职责由 Read first 加各目录 README 承接;proven 拆入 implemented REQ 与 ADR 后退役;MISTAKES 27 条按错误链分流进 guides（R001 坑表与 G002）,M0xx 行号保留;`tools\check.py` + `mdrules.py` 入仓为提交前门禁。

## Consequences

- 好:与 dev-evo 工具链（check/md-guard）同构;需求可追溯到验收,决策取舍有案可 supersede
- 坏:历史文档引用被改写,史料保真让位于体系一致性;S/R/G/M 旧编号保留为兼容层,新旧编号并存有学习成本
