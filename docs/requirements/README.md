# REQ 索引

> 需求登记:新需求先立 REQ 再实现,禁止静默假设。新建拷 0000-template.md,编号三位接当前最大号,退役不复用。implemented 必填 trace;rejected 留档防复提。PRD 时代的 D 编号已全部迁入,D0x 与 REQ 的对应关系见各篇正文关联行。

| id | 状态 | 优先级 | 标题 | trace |
|---|---|---|---|---|
| REQ-001 | implemented | must | 文档体系建立（D01,后由 REQ-011 升级承接） | docs/research/S001-devtools-auto-allow-switch-上游核实与补丁设计.md |
| REQ-002 | implemented | must | auto-allow-devtools-connections 开关（D02 主线） | docs/research/S002-CDP调试-提示限制与检测特征全景.md |
| REQ-003 | implemented | must | 无参数启动默认开 9222（D02-2） | docs/research/S002-CDP调试-提示限制与检测特征全景.md |
| REQ-004 | implemented | must | 浏览器静默化（D02-3） | docs/research/S003-浏览器静默化定制清单.md |
| REQ-005 | implemented | must | 网络触点清零（D02-4） | docs/research/S004-网络触点剔除-Google外联与遥测清零.md |
| REQ-006 | implemented | must | 项目更名 clean-chrome（D02-5） | CHANGELOG.md |
| REQ-007 | implemented | must | 调试通道三态环境变量（D02-6） | docs/research/S005-调试管道-remote-debugging-pipe机制与通道环境变量.md |
| REQ-008 | implemented | must | bad-flags 黄条剔除（D02-7） | docs/research/S003-浏览器静默化定制清单.md |
| REQ-009 | implemented | must | console 参数预览抑制（D02-8） | docs/research/S006-console参数预览抑制-通道图与收口设计.md |
| REQ-010 | implemented | must | 三平台构建对齐（D03） | docs/diary/2026-09-13-三平台收官验收.md |
| REQ-011 | implemented | must | 文档体系迁移 dev-evo 五节合同 | tools/check.py |
| REQ-012 | draft | must | 升 tag 155 三平台实战（待 155 stable,约 2026-09-23 触发） | |
