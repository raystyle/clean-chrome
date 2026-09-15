# S006：console 参数预览抑制（通道图与收口设计）

> 编号：S006 ｜ 类型：research ｜ 日期：2026-09-15 ｜ 关联：D02-8,S002（CDP 摩擦族）,R001 六节
> 六态：全表**已知已行**（152 树源码实读 + 裸 CDP 页内探针 + 50 锚三平台构建实证,2026-09-15 验收矩阵全绿）

## 一、问题

D02-8 原始规格（用户）：console.* 传参经 CDP 上报（ConsoleAPICalled）时 preview 会读对象属性,触发页面探针的 getter/Proxy 陷阱;要求 console API 路径 wrapObject 第四参强制 `generatePreview=false`,不动 `Runtime.evaluate`。验收 A（Error stack getter）/B（Proxy ownKeys 链）双脚本期望 a/b 均 false。

**前提修正（2026-09-15 第 2 轮裁定,实测驱动）**：152.0.7977.84 上 preview 不调 accessor、不碰 Proxy 陷阱,原始验收的 A 本就过、B 的开火通道是文本构建而非 preview,且文本通道 stock 同样开火（非 CDP 差分）。用户裁定照规格落 preview-off,验收语义随之修正（见四节）。

## 二、上游机制实读与通道图（152.0.7977.84,知+行）

### 数据流

1. 页面 `console.*` -> `V8Console`（v8-console.cc,Chromium 常驻安装,零 CDP 客户端也在）-> `ConsoleHelper::reportCall`（v8-console.cc:115）-> `V8ConsoleMessage::createForConsoleAPI`（v8-console-message.cc:451）
2. 消息创建时**无条件**构建文本 `m_message`（v8-console-message.cc:476-484,`V8ValueStringBuilder`）
3. Runtime 域开启的会话活消息走 `reportMessage(message, true)`（v8-runtime-agent-impl.cc:1232）-> `reportToFrontend`（v8-console-message.cc:318）-> kConsole 分支 `wrapArguments(session, generatePreview)`（:374）-> 逐参 `session->wrapObject(context, v, "console", generatePreview)`（:304）;kTable 型且 generatePreview 时走 `wrapTable`（:293）
4. kException 分支（未捕获异常）`wrapException(session, generatePreview)`（:338）-> 同 `wrapObject`
5. `Runtime.enable` 重放存量消息走 `reportMessage(&message, false)`（v8-runtime-agent-impl.cc:1151）,即**上游重放本就不带 preview**
6. 用户点名的 `fromValue` 在 152 已不存在（grep 实证）;`v8-console.cc:780` 是 `inspect()` 的 `kIdOnly` 包装,不读属性

### 实测通道矩阵（裸 CDP 页内探针,当前 48 锚产物）

| 通道 | 触发条件 | 页面可观测行为 | stock（零 CDP）同样开火 | CDP 差分 |
| --- | --- | --- | --- | --- |
| preview 序列化（wrapArguments/wrapTable,仅 Runtime.enable） | attach+enable | **无**：accessor 列为 `type:"accessor"` 不取值,Proxy 陷阱不碰;数据值/Error 内部 stack 急切进 payload | 否（无客户端） | payload 内容有差（preview 字段）,但页面看不见自己的 payload |
| 文本构建（V8ValueStringBuilder,永远） | 任何 console 调用 | `@@toStringTag` Get（own accessor 或原型链 Proxy get 陷阱）、`toString/valueOf` 兜底、Error.prototype.toString 读 name/message、数组元素 `Get(i)`（含索引 accessor） | **是** | **否**（stock 一致） |
| console.table/dir/dirxml | 同上 | 同 preview/文本通道,无第三形态（table accessor 亦不触发,table proxy 走文本） | 同上 | 否 |

关键实证（.probe/console-ab.mjs 与 console-table.mjs,2026-09-15）：A=false、B=true（文本通道）、direct Proxy 全静默、`{get zz(){return 42}}` 的 preview 为 `[{"name":"zz","type":"accessor"}]` 不取值、数组 preview 取元素数据值。

### 排除项

- `Runtime.evaluate`/`callFunctionOn`/`awaitPromise` 的 preview 走 injected-script.cc:981 等独立路径,与收口点无交集,即 **evaluate({generatePreview:true}) 行为保持**
- `custom-preview.cc:123` 仅客户端显式开自定义格式器时激活,bh 不开,出边界
- `EstimatedValueSize`（debug-interface.cc:1133）纯堆对象 Size(),不跑用户代码
- Blink `consoleAPIMessage`（main_thread_debugger.cc:335）只收文本串,不碰对象

## 三、设计（行）

两锚,全落 v8-console-message.cc（首入 v8/ 树,锚 48 至 50,文件 33 至 34）：

1. **kConsole 分支**：`wrapArguments(session, generatePreview)` 改传 `false`（替换式锚）。console.* 全家族参数不再急切序列化;RemoteObject 保留 objectId,客户端可按需 getProperties;kTable 因 generatePreview 门（:277-278）自然失活,退普通 wrap
2. **kException 分支**：`wrapException(session, generatePreview)` 改传 `false`（第 1 轮裁定范围,同函数同手法）

**明确不动**（反差分纪律,与 stock 行为对齐）：

- 文本通道（V8ValueStringBuilder）**保持原样**：stock 同样开火,关掉反而制造可探针差分（第 2 轮裁定否决"双杀"方案的原因）
- evaluate/异常的 evaluate 侧包装、inspect kIdOnly、自定义格式器照旧
- 保留面（S002 第四节）与本补丁无交集

## 四、验证节（2026-09-15 实证回填,四端一致：本机 Dev / 本机 browse-rs 部署版（沙箱态）/ lan-mac / lan-ubuntu）

- [x] ConsoleAPICalled payload：console.debug 与 console.table 两事件 args 全部 `hasPreview=false` 且 `objectId` 保留（补丁前 preview 携带 real:1 / 数组元素 / err stack 串）
- [x] A 脚本（Error stack getter）：a=false（与补丁前一致,记录性;152 的 preview 本就不调 accessor）
- [x] B 脚本（Object.create(proxy)）：b=true（文本通道 @@toStringTag,stock 一致非差分,记录性;第 2 轮裁定不修）
- [x] 未捕获 throw `{secret:'leak'}`：exceptionThrown 的 exception `hasPreview=false`、objectId 保留（补丁前 wrapException preview=true 会把对象数据序列化进 payload）
- [x] `Runtime.evaluate({expression:'1+1'})`=2;`generatePreview:true` 照常返回 `[{name:'q',value:'1'}]`
- [x] 双形态等价（仓库外沙盒 git apply,34 文件字节一致）;脚本幂等（本机 ok=0/skip=50,mac/ubuntu 同）
- [x] 三机同步：mac ok=0/skip=50 增量 13 步 40.3s;ubuntu ok=0/skip=50 增量 50 步 20.8s;双机行为验收矩阵与本机逐项一致（树内 node v24.12.0 跑同探针）
- [x] 验收工具沉淀：裸 CDP 探针范本四脚本（attribution/AB/table/accept）;部署版顺带修复 M027（browse-rs AppContainer ACE,deploy 脚本已内置自愈）

## 五、结论

| 结论 | 态 |
| --- | --- |
| 152 的 console preview 不调 accessor/Proxy 陷阱,原始验收 A 本就过、B 挂在文本通道 | 知+行 |
| 文本通道 stock 同样开火（V8Console 常驻）,非 CDP 差分;关它反造差分,裁定保持原样 | 知+行 |
| preview-off 的实效=console 参数/未捕获异常不再急切序列化进协议 payload（数据卫生+上游回归免疫）,页面可观测行为零变化 | 知+行 |
| 收口点唯一：reportToFrontend kConsole/kException 两分支,evaluate 路径天然无交集 | 知+行 |
| 50 锚落地后四端验收矩阵全绿（preview 消失/objectId 保留/evaluate 两态不变） | 知+行 |
| M024:bh eval 执行环境是 Node daemon,console.* 在其中是 Node 的 console（util.inspect 读 stack）,页面行为探针必须走裸 CDP/页内执行 | 知+行 |
