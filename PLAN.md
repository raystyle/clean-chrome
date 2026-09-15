# PLAN：当前目标实施计划

> 角色：当前目标方案文档：基于 research（为什么）与 references（怎么做）的执行计划；每条挂依据来源，不存历史目标。

## 当前目标

D02-8 console 参数预览抑制（第 2 轮裁定后语义）：console.* 与未捕获异常经 CDP 上报（ConsoleAPICalled / exceptionThrown）不再急切序列化对象数据进协议 payload（`generatePreview=false`,objectId 保留按需可取）;`Runtime.evaluate` 预览路径不动;文本通道保持 stock 一致（非差分,不修）（机制与实测通道图见 `docs\research\S006`）

## 步骤

| # | 步骤 | 依据 | 状态 |
| --- | --- | --- | --- |
| 1 | S006 机制研究定稿（数据流/收口点/保留面三清单 + 实测通道矩阵,152 树源码实读） | 本轮源码实读;S005 范式 | 完成 |
| 2 | 改锚：v8-console-message.cc reportToFrontend 两分支（kConsole wrapArguments 传 false;kException wrapException 传 false）,写入 apply-auto-allow.py（锚 48 至 50,文件 33 至 34,首入 v8/ 树） | S006 设计节;M017 marker 纪律 | 完成 |
| 3 | 双形态等价验证：仓库外沙盒 git apply 34 文件字节比对;脚本幂等（本机/mac/ubuntu 重跑 ok=0/skip=50） | AGENTS 编码节;M026 | 完成 |
| 4 | 本机增量重编 Dev + Release（v8 单文件,v8 库 + 一次链） | R001 五节 | 完成 |
| 5 | 验收：裸 CDP 探针（A/B 双脚本 + payload preview 字段 + exceptionThrown + evaluate 两态）;部署 browse-rs 复验（沙箱态,M027 ACE 修复后） | 用户验收规格第 2 轮修正;S006 四节 | 完成 |
| 6 | 三机同步：lan-mac / lan-ubuntu 脚本重打 + 增量重编 + 行为验收（树内 node 跑同探针） | D02-7 三台纪律 | 完成 |
| 7 | 文档同步：README/R001/CHANGELOG/INDEX/S006 回填/PRD/GOAL/diary/TODO;收官一笔 feat: 提交推送 | AGENTS 文档节;用户裁定③ | 完成 |

## 完成的定义

- [x] Runtime.enable 已开,console.debug(e)（stack getter 陷阱）后 `a === false`（152 本就过,记录性）
- [x] console.debug(Object.create(proxy))：`b === true` 记录在案（文本通道,stock 一致非 CDP 差分,第 2 轮裁定不修）
- [x] 未捕获 throw：exceptionThrown 的 exception `hasPreview=false`,objectId 保留（补丁前数据会进 payload）
- [x] ConsoleAPICalled（debug/table）args 全部无 preview、objectId 保留
- [x] `Runtime.evaluate({expression:'1+1'})`=2;evaluate({generatePreview:true}) 行为不变
- [x] 两补丁形态等价（34 文件字节比对）;脚本幂等（三机 ok=0/skip=50）
- [x] 本机 Dev/Release/browse-rs（沙箱态）+ lan-mac/lan-ubuntu 同步增量全过,四端验收矩阵逐项一致;README/R001 同步,CHANGELOG 记条
