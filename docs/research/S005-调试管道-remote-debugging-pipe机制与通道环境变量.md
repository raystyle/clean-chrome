# S005：调试管道（remote-debugging-pipe）机制与通道环境变量化

> 编号：S005 ｜ 类型：research ｜ 日期：2026-09-14 ｜ 关联：D02-6,S002（同闸门）,R001 六节
> 六态：机制与设计**已知已行**（源码实读 + 43 锚构建上实证）;三态验收矩阵**已知未行**（待补丁落地后实证,回填验证节）

## 一、问题

调试通道现只有 TCP 端口形态（43 锚默认 9222）。需求：启动时以环境变量选择通道形态,`port`（默认,现行为）/`pipe`（只管道不开端口）/`both`（都开）,管道句柄由启动方传入。

## 二、上游机制实读（152.0.7977.84,知）

1. **pipe handler 入口**（chrome/browser/devtools/remote_debugging_server.cc:346-354）：`--remote-debugging-pipe` 开关触发 `StartPipeHandler()`;与端口段是**两个独立 if**,天然可并存（both 合法）
2. **闸门**：pipe 与 port 走同一个 `IsRemoteDebuggingAllowed`（S002 已被 43 锚解锁）,无新增拦截
3. **无对话框路径**：pipe 客户端直接 `AttachClient` 到 browser target（devtools_pipe_handler.cc:404）,不经 WS accept,DevToolsConnectionDialog 对管道**根本不存在**;auto-allow 补丁与管道互不相扰
4. **句柄传递两形态**（devtools_agent_host_impl.cc:224-239）：
   - 默认 fd 3（读）/fd 4（写）（devtools_agent_host.h:74-75）,POSIX 惯例
   - Windows 专属 `--remote-debugging-io-pipes=<读句柄>,<写句柄>`（十进制逗号串,`AdoptPipes` :112 经 `_open_osfhandle` 收养）,**启动器首选**,免碰 CRT fd 编号
5. **协议两模式**（devtools_pipe_handler.cc:396-427）：ASCIIZ（NUL 分隔 JSON,默认）/CBOR（`--remote-debugging-pipe=cbor`,信封定长帧）
6. **断线关闸**：`on_disconnect = CloseBrowserSoon`（remote_debugging_server.cc:319-321）,启动方退出管道,浏览器**随之关闭**（自动化生命周期绑定,符合"启动器拥有浏览器"模型）
7. **无效句柄安全**：Windows 下 `_get_osfhandle` 失败被 ScopedInvalidParameterHandlerOverride 拦住不崩（:99-131）,ReadFile 失败走 OnDisconnect 即自退,**双击误设 pipe 态的表现是闪退,不是挂死/崩溃对话框**

## 三、设计（行）

- 变量名 `CLEAN_CHROME_DEBUG`,值 `port|pipe|both`（大小写不敏感,未设=port）
- 落点：remote_debugging_server.cc `GetInstance()` 通道选择块（43 锚补丁边界内文件,锚 43 至 44）
- 语义（显式开关永远优先于变量）：
  - pipe 启停：`HasSwitch(kRemoteDebuggingPipe) || 值∈{pipe,both}` 则 StartPipeHandler
  - 端口段：显式 `--remote-debugging-port` 照用;否则值=pipe 时**跳过 9222 默认注入**（不开端口）;port/both 照旧 9222
  - 读变量用 `base::Environment::Create()->GetVar`（跨平台正道）
- 启动器契约：Windows 传 `--remote-debugging-io-pipes=<in>,<out>` + 可继承句柄;POSIX 传 fd 3/4

## 四、验证节（2026-09-14 实证回填）

- [x] 未设变量:9222 照旧（无参启动监听即证,回归过）
- [x] pipe:管道 CDP 双向通（`Target.getTargets` 经管道返回真实 target 列表,JSON-RPC id 回环）,9222 无监听
- [x] both:管道往返 + 9222 同时监听
- [x] 双补丁形态等价（沙盒 git apply 后 32 文件字节比对全一致）;脚本幂等（迁移重打 ok=6/skip=41）
- [x] 启动器范本 `tools\pipe-smoke.py`（Windows io-pipes 契约实现,uv 运行）

## 五、结论

| 结论 | 态 |
| --- | --- |
| pipe 上游原生支持,无对话框,与 auto-allow 互不相扰 | 知+行 |
| Windows 句柄传递走 io-pipes 开关,启动器无需碰 fd 编号 | 知+行 |
| 断线关闸与无效句柄自退,pipe 态安全模型成立 | 知+行 |
| 环境变量三态（port/pipe/both）落地,47 锚,增量重编后三态矩阵全绿 | 知+行 |
| 踩坑 M023:写锚前先读目标 tag 实际 API 签名（GetVar 152 已改单参 optional） | 知+行 |
