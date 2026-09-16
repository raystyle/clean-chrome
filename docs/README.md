# docs 文档地图

> docs 面总入口:活跃体系一表速览与裁定注记;细则归各目录 README 与 AGENTS 合同,本图是投影,不另立第二真相。

## 活跃体系表

| 体系 | 目录 | 职能 | 规模 | 索引 |
| --- | --- | --- | --- | --- |
| ADR 决策 | [adr](adr/README.md) | 不可逆技术选择,Context/Decision/Consequences,状态机 proposed 到 accepted 到 superseded | 7 篇 | 各 README 索引表 |
| REQ 需求 | [requirements](requirements/README.md) | 需求登记,Scenario/Criteria,implemented 回填 trace | 12 篇 | 各 README 索引表 |
| guides 指南 | [guides](guides/README.md) | 任务导向操作手册与工作流(R001 构建/G001 写作/G002 补丁) | 3 篇 | 各 README 索引表 |
| diary 日记 | [diary](diary/README.md) | 项目日记一天一篇,踩坑当场记,提交后记钩子 | 6 篇 | 各 README 索引表 |
| research 研究 | [research](research/README.md) | SNNN 研究档案,六态标注,结论可追溯 | 7 篇 | 各 README 索引表 |

> 检索:rg -n 关键词 docs 逐目录直搜;ADR/REQ 状态机与索引一致性、六态与禁字由 tools/check.py 门禁把守。

## 裁定与红线

- 三栈投影不适用:本仓为 Chromium 构建仓,无自有代码 API 面,Rust/Python/TypeScript 三栈契约注释与投影工具链(cargo doc/MkDocs/API Extractor)不适用;公开契约以补丁双形态字节等价为门禁(ADR-0003),构建门禁为 autoninja(R001 五节) [经验: ADR-0001 自编译路线的直接推论]
- diary 与 research 为不可裁撤体系,任何精简或迁移不得删除或合并 [实证: 用户裁定 2026-09-16]
