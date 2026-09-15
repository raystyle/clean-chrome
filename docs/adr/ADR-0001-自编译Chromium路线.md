---
id: ADR-0001
title: 自编译 Chromium 路线
status: accepted
date: 2026-09-15
deciders: [ray]
supersedes: []
superseded_by: null
tags: [founding, cdp]
---

# ADR-0001:自编译 Chromium 路线

## Context

agent 自动化附着本机浏览器时被 DevTools 远程调试确认对话框打断。2026-09-11 上游核实:`--auto-allow-devtools-connections` 类开关上游不存在（`chrome_switches.cc@152.0.7977.84` 无相关常量,全网检索亦无）;企业策略 `RemoteDebuggingAllowed` 只管调试总闸,对话框照弹;无浏览器窗口时上游自动拒绝;向 Chromium 提交此类定制不在接受范围。备选:策略/启动参数/上游提交/现成第三方构建,全部不可行 [实证: S001 结论表,gitiles 逐文件核对]。

## Decision

以钉稳定 tag 的 Chromium 源码树自编译,补丁把 `AcceptDebugging()` 短路回 `kAllow`,只作为本机自动化（bh / CDP 工具链）专用浏览器,不替换日常 Chrome。

## Consequences

- 好:零对话框零提示;全链路可控,静默化、网络触点清零、通道三态等后续定制成为可能
- 坏:承担三平台构建与升 tag 维护成本;不承诺自动更新,需自己定期升 tag 重编;不进上游意味着每次升 tag 都要重验锚点（ADR-0002/0003 承接）
