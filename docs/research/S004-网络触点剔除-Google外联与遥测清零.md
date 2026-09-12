# S004:网络触点剔除(Google 外联与遥测清零)

> 目标:自编 Chromium 启动与运行全程零 Google 域外联、零遥测打点。核实日期 2026-09-12,源码基准 tag 152.0.7977.84。承接 S003(浏览器静默化)之后的网络层主题,同日项目更名 clean-chrome。

## 一、需求与实证(用户裁定连发)【知】

| # | 需求 | 实证来源 |
| --- | --- | --- |
| 1 | 初始访问 accounts.google.com 剔除 | 用户防火墙观察 + netlog `ListAccounts?source=ChromiumBrowser` |
| 2 | 访问 Google 与遥测打点全部剔除 | net-audit 30 秒空 profile 清单(19 个 google 域触点) |
| 3 | 集成 Google 翻译服务与右键 Google 服务剔除 | 用户裁定(feature 关闭 + 端点无效化) |
| 4 | Google AI 相关剔除 | 用户裁定(Optimization Guide 端点 + Lens feature) |
| 5 | Google 安全打点与 URL 扫描剔除 | 用户裁定(Safe Browsing 全家:v4/v5/realtime/上报) |
| 6 | 文件安全扫描剔除或关闭 | 用户裁定(下载保护 verdict 端点) |

**测量工具**:`tools/net-audit.py`(uv 运行;net-log 全进程覆盖含 browser 后台服务,CDP Network 域看不到这些;必须优雅退出才落盘,硬杀得 0 字节文件)。

## 二、原始触点清单(26 锚前的 30 秒实测)【知】

| 域名 | 用途 | 触发机制 |
| --- | --- | --- |
| accounts.google.com | Gaia 账号探测(ListAccounts) | signin 系统启动即查 |
| android.clients.google.com | GCM 注册(c2dm/register3)+ checkin | 推送通道 |
| mtalk.google.com:5228 | GCM XMPP 长连接 | 推送通道 |
| update.googleapis.com | 组件更新(update2/json) | component updater |
| clients2.google.com | CUP 时间校准(time/1/current) | network_time_tracker |
| dl.google.com | 组件差分下载(diffgen-puffin) | component updater 下载段 |
| redirector.gvt1.com / gvt1-cn | 拼写词典下载(zh-cn bdic) | 中文系统启动自动拉 |
| www.google.com | zero-suggest 预取(complete/search?client=chrome-omni&q=) | omnibox 启动预取 + SearchEnginePreconnector |

## 三、剔除方案定档【行】

**统一手法:RFC 6761 保留 `.invalid` TLD**。DNS 层永不解析,服务发起即快速失败,零外联、零本机误连(不用 127.0.0.1 防止误连本机服务)。用户手动导航 google.com 不受影响(导航不走这些常量)。

**三层组合**:
1. **端点常量无效化**(URL 锚):Gaia/GCM×3/组件更新×2/CUP 时间/拼写词典/翻译×2/OG×2/SB×5/文件扫描 = 18 锚
2. **feature 默认反转**:Lens overlay/Lens standalone/zero-suggest prefetch/AI(前期锚 17/18)= 4 锚
3. **pref 注册默认值**:OfferTranslate=false(翻译含右键)/SafeBrowsingEnabled=false(SB 全家含文件扫描)/SearchSuggestEnabled=false(suggest+preconnector)= 3 锚

S004 合计 24 锚(第 20 至 43 锚),加上 S001-S003 的 19 锚,补丁终态 **43 锚 32 文件**。

## 四、验证记录【行】

- 2026-09-12 三批锚渐进验证:26 锚版残余 www.google.com+clients2;34 锚版残余 www.google.com;43 锚版 **GOOGLE/TELEMETRY touchpoints: 0 hosts**(30 秒空 profile net-audit,残余全为 .invalid 快速失败)
- zero-suggest 定位法:netlog `--net-log-capture-mode=Everything` 的 traffic_annotation 指认 `client=chrome-omni&q=`(空查询)= 地址栏零键建议预取
- `kSearchSuggestEnabled=false` 一石三鸟:zero-suggest、typed suggest、SearchEnginePreconnector 启动预连全灭
- clean-chrome 更名后 43 锚以新 marker 全量重打重验(patch 31KB)

## 五、边界与已知取舍【知】

- **功能取舍**(全部为本机自动化浏览器不需要的):Google 登录/同步/推送/组件更新/拼写词典下载/翻译/Lens/AI 后台/Safe Browsing/下载扫描/CUP 时间
- **保留闸门**不变:端口仅 127.0.0.1、RemoteDebuggingAllowed 策略、Host header 校验(S002 第四节)
- 页面内手动访问 google.com 不受影响(S003 边界延续);企业策略通道若显式配置 SB/翻译仍可能重开(本地无策略源,不构成实际路径)
- 首跑后 profile 持久化的旧 pref 会覆盖默认值:现役 profile 需重建
