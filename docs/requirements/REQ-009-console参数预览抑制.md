---
id: REQ-009
title: console 参数预览抑制
status: implemented
priority: must
trace: docs/research/S006-console参数预览抑制-通道图与收口设计.md
---

# REQ-009:console 参数预览抑制

关联:旧 PRD D02-8,2026-09-15 两轮裁定（范围三推荐 + 前提修正照规格落 preview-off）;纪律依据 ADR-0005。

## Scenario

console.* 传参与未捕获异常经 CDP 上报时不再急切序列化对象数据进协议 payload,objectId 保留按需可取;Runtime.evaluate 行为不变。

## Criteria

- [x] ConsoleAPICalled（console.debug/table 等）args 全部无 preview 且 objectId 保留
- [x] exceptionThrown 的 exception 无 preview、objectId 保留
- [x] Runtime.evaluate 两态（1+1 与 generatePreview:true）行为不变
- [x] 收口点唯一:reportToFrontend kConsole/kException 两分支（首入 v8/ 树,50 锚）
- [x] 四端验收矩阵全绿（本机 Dev/browse-rs 部署沙箱态/lan-mac/lan-ubuntu）
