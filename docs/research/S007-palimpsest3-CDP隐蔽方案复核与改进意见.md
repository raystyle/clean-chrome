# S007：palimpsest#3 CDP 隐蔽方案复核与改进意见

> 编号：S007 ｜ 类型：research ｜ 日期：2026-09-15 ｜ 关联：S002（检测特征）,S006（console 通道图）;外部对象 [palimpsest#3](https://github.com/copyleftdev/palimpsest/issues/3)
> 六态：复测与结论**知+行**（stock Chrome Dev 155.0.8048.0 裸 CDP 复测 + S006 在 152.0.7977.84 的通道矩阵互证）;对 issue 的改进意见**已知**（意见本身未经对方采纳验证）

## 一、问题

外部 issue 提出 CDP stealth 三层方案（传输层封 `Runtime.enable` + 17 项 JS 补丁 + 二进制加固），其 **#1 CRITICAL 检测向量**断言："`console.groupEnd(obj)`（obj 原型为 Proxy）在 `Runtime.enable` 激活时序列化参数、走原型链触发 Proxy 陷阱（current, March 2026）"。该断言与本项目 S006 通道矩阵（2026-09-15,152.0.7977.84）直接冲突：152 的 preview 序列化不调 accessor/不碰 Proxy 陷阱;真正开火的是文本构建通道且 stock 零 CDP 同样开火。用户指令：研究改进该 issue。

## 二、复测（行）

探针：裸 CDP（fetch /json + 原生 WebSocket + Runtime.evaluate,与 S006 同范式）,复刻 issue 原始代码形态（`Object.create(new Proxy({}, {get…}))` 传给 console 调用,页内记录陷阱开火）;A=零域开启基线,B=`Runtime.enable` 后。对象：**stock Chrome Dev 155.0.8048.0**（日常浏览器二进制,临时 profile 隔离实例,测毕即杀,2026-09-15）。

| 探针形态 | A：未开 Runtime.enable | B：开 Runtime.enable 后 | CDP 差分 |
| --- | --- | --- | --- |
| groupEnd: 原型链 Proxy | `get:Symbol(Symbol.toStringTag)` 开火 | **同样开火,逐项一致** | **无** |
| debug / log: 原型链 Proxy | 同上开火 | 同上 | 无 |
| debug: Proxy 本体 | 静默 | 静默 | 无 |
| debug: accessor 对象 | 静默（getter 不调用） | 静默 | 无 |

附证：B 态 `ConsoleAPICalled` args[0] 含 `preview` 字段（YES）但陷阱/ getter 全程静默,即 preview 生成不跑用户代码,只把数据值序列化进协议 payload。

## 三、结论与改进意见

### 结论（对 issue 的更正）

| 结论 | 态 |
| --- | --- |
| issue #1 CRITICAL 向量在当前 Chrome 已死：Proxy get 陷阱（@@toStringTag）由文本构建通道（V8ValueStringBuilder,v8-console-message.cc:476-484,无条件执行）触发,与 Runtime.enable 无关;该检测代码会误报全部真实用户,不能区分 CDP 自动化 | 知+行（155 实测 + 152 的 S006 互证） |
| preview 序列化（Runtime.enable 独有通道）不调 accessor/不碰 Proxy 陷阱（152/155 一致）;其残余面是对象数据急切进 payload（数据卫生）,非页面可观测检测通道 | 知+行 |
| issue 引用的 rebrowser 检测技术断代:其"6/6 验收"标准须在当前 Chrome 重新基线化,否则验收意义不明;eoka 6/6 通过可能恰因向量已死 | 知（向量死）+推断（6/6 归因未实测） |

### 改进意见（对 issue 的修补清单）

1. **向量清单全部重基线**：每个"检测向量"先做 stock 对照差分实验（stock headful / stock headless / CDP 附着三方同探针）再决定修不修;2021-2023 时代的 stealth 清单（plugins/mimeTypes/window.chrome 形状等）大量已被 `--headless=new` 上游收敛,照抄会修不存在的差分
2. **反差分纪律**：无差分通道不修,修了反而制造新指纹（S006 第 2 轮裁定同理）;典型如 navigator.webdriver:CDP 启动（不传 --enable-automation）本就不置 true,JS 补丁的 descriptor 形状本身反而可检测
3. Layer 1 成本清单补全：封 `Runtime.enable` 会断 executionContextCreated 跟踪与 Runtime.bindingCalled（expose_function 依赖）与 ConsoleAPICalled 采集;`Runtime.evaluate` 零域开启即可用（本次 A 态即证）
4. Layer 3 剔除无的放矢项：`$cdc_` 是 ChromeDriver 注入物,chromiumoxide 路线无关;`--disable-blink-features=AutomationControlled` 仅在 --enable-automation 存在时有意义
5. 验收标准改为 stock 对照差分（零差分才绿）,替代/叠加 rebrowser-bot-detector 6/6
6. 备选层：crawler 控制二进制时,浏览器侧源头补丁比客户端 JS 补丁稳定（无 descriptor 形状问题、不随上游库行为漂移）;本项目 clean-chrome（50 锚,preview-off 属同族收口）为参考实现

## 四、验证记录

- [x] 155.0.8048.0 复测矩阵如二节,探针 `%TEMP%\cc-probe\palimpsest3-probe.mjs`（临时产物不入仓,范式已沉淀本文）
- [x] 与 S006 通道矩阵（152,48 锚=preview 通道为 stock 行为）逐行互证一致
- [x] 探针实例测毕 taskkill /T 清理,临时 profile 删除

## 五、遗留

- 交付形态已裁定（2026-09-15 用户）：**仅内部留存,不外发**;如日后改为外发,裁定为附 clean-chrome 仓库引用作为浏览器侧补丁路线参考实现
