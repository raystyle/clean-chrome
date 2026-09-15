---
id: ADR-0002
title: 钉稳定 tag 不跟 main,绝不提交上游
status: accepted
date: 2026-09-15
deciders: [ray]
supersedes: []
superseded_by: null
tags: [versioning]
---

# ADR-0002:钉稳定 tag 不跟 main,绝不提交上游

## Context

2026-09 起 Chrome 改两周发一版,tag 通胀加快;152 稳定 tag 与 main 之间已有代码漂移;补丁锚定对字节级敏感,上游一动锚点即失效 [实证: S001 结论 3,ChromiumDash 2026-09-11]。

## Decision

补丁钉稳定 tag（基准 `152.0.7977.84`）,不跟 main;任何情况下不向上游提交;标准补丁文件名带 tag（`auto-allow-devtools-connections-<tag>.patch`）;升 tag 走 R001 流程并在 poc 参照树重验。

## Consequences

- 好:锚点字节稳定,双形态等价可验;不背上游评审与下线风险
- 坏:升 tag 是周期性人工流程,上游漂移可能迫使锚点重写;安全更新需自行跟进;`enable_nacl` 等上游已删参数禁止出现在任何 args
