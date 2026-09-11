# S002：CDP 调试的提示、限制与检测特征全景

> 研究目标：枚举 Chromium 中围绕 CDP 远程调试的安全提示、安全限制与被检测特征,逐项给出移除层与保留建议,服务于本机自动化专用浏览器(unsafe-chrome)的「零摩擦、零提示」目标。核实日期 2026-09-11,源码基准 tag 152.0.7977.84(本地树逐行核实)。

## 一、范围与定位【知】

- 服务对象:本机自动化(bh / CDP 工具链)专用浏览器,自编树内做正当定制
- 不做:针对特定网站风控的规避操作;检测特征只列公开对抗面与缓解层
- 每项标注移除层:补丁(源码)、启动纪律(参数)、CDP 纪律(调用侧)、不建议(保留)

## 二、已移除项(本轮五锚,行级实证)【行】

| # | 项目 | 机制位置 | 移除方式 |
| --- | --- | --- | --- |
| 1 | DevTools 连接确认对话框 | chrome_devtools_manager_delegate.cc `AcceptDebugging()` | 开关短路回 kAllow(S001 原设计) |
| 2 | 「远程调试活动」infobar | 同文件 `SetActiveWebSocketConnections()` | 整块替换为注释(提前 return 会触发 -Wunreachable-code-aggressive + -Werror,实证 2026-09-11) |
| 3 | 无参数不开始口 | remote_debugging_server.cc `GetInstance()` 端口解析 | port_str 为空时默认 9222 |
| 4 | 默认 User Data 目录限制 | 同文件 `IsRemoteDebuggingAllowed()` | 上游 gate 块整块替换为注释 |
| 5 | 品牌编译开关 | 同函数 GOOGLE_CHROME_BRANDING 分支 | 非 branded 自编天然不启用,实证默认目录可开端口 |
| 6 | 启动期「缺少 Google API 密钥」与「系统过时」infobar | chrome/browser/ui/startup/infobar_utils.cc 185-198 | 整块替换为注释(含 infobar_manager 定义,防 unused 变量;2026-09-11 用户裁定「去掉这些干扰提示」) |

## 三、安全提示类(用户可见 UI)【知】

| 项目 | 结论 | 依据 |
| --- | --- | --- |
| bad-flags「不受支持的命令行」infobar | **无需处理** | 逐行核对 bad_flags_prompt.cc 的 kBadFlags 清单:--remote-debugging-port 与本项目开关均不在列,启动零警告 [实证: 2026-09-11 本地树] |
| DevTools 前端内远程调试横幅 | 低优先 | devtools_frontend 资源层,不影响 CDP 协议,收益低 |
| chrome://inspect 页面提示 | 零优先 | 非阻断提示 |

## 四、安全限制类(协议与端口 gate)【知】

| 项目 | 建议 | 理由 |
| --- | --- | --- |
| RemoteDebuggingAllowed 策略 gate | **保留** | 本机无策略时恒放行,不构成摩擦;留作紧急关闭后门 |
| 端口仅听 127.0.0.1 | **强烈保留** | R001 坑表 10:一旦暴露外网,开关全开即全控制权;这是保护本机不被他进程/他机利用的最后闸门,禁配 --remote-debugging-address |
| WS Origin gate(--remote-allow-origins) | 按需启动参数 | bh(Node ws)不发 Origin 头不受限;仅当网页内 WS 直连 CDP 时需要;默认放开会新增任意网页连本机 9222 的攻击面,不做默认 |
| Host header 校验(DNS rebinding 防护,devtools_http_handler.cc:465/520) | **保留** | 网络层安全闸门,与本地自动化零冲突 |

## 五、被检测特征类(网页可感知)【知】

| 特征 | 触发条件 | 缓解层 |
| --- | --- | --- |
| Navigator.webdriver=true | --enable-automation 或旧 headless 启动 | 启动纪律:不带这些参数,CDP attach 本身不置位,零改动天然 false |
| /json/version 返回 HeadlessChrome UA | headless 实例且 HTTP 端点被网页访问 | 端口仅 127.0.0.1 已挡外部探测;桌面实例返回 Chrome/152 无此特征 |
| Runtime.enable 的 console 行为差异 | 客户端 enable Runtime/Console 域 | CDP 纪律:能不 enable 则不 enable;bh 侧调用面控制 |
| debugger; 语句陷阱(页面主动下断点) | Debugger 域被 enable | CDP 纪律:bh 常规操作不 enable Debugger 域 |
| Runtime.addBinding 的 window 属性 | 客户端注入 binding | CDP 纪律:优先 evaluate + isolate world,少用 addBinding |
| 时序类检测(事件 isTrusted、CDP 命令往返抖动) | 合成输入 | 无完美移除;对抗属公开军备(puppeteer-stealth 生态),真需求另立研究(S003 候选) |

## 六、结论与动作清单【行】

- 本轮已闭环五项(第二节);零改动两项(bad-flags 核对、webdriver 天然 false)
- 明确保留三项:127.0.0.1 绑定、策略 gate、Host 校验(本机安全闸门,与自动化零冲突)
- 检测特征类:当前 bh 使用面(附着桌面实例、js 助手 evaluate)落在「天然无特征」区,无需补丁;激进出彻底 stealth 是独立课题
- 后续:若网页内直连 CDP 需求出现,再评估 Origin 放开的受控形态

## 七、验证记录【行】

- 2026-09-11:默认目录 + 9223 端口实测通过(自编非 branded 树);bad-flags 清单逐行核对;五锚补丁编译中(unreachable-code 坑已用替换式锚定绕过,实证见第二节 #2)
