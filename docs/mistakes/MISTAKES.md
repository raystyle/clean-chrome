# MISTAKES：错误库

> 单文件起步（合法起点，错误族多了再拆 M1xx 分类文件）。一行一事，当场追加。

| 编号 | 现象 | 根因 | 正确处理 | 首踩日期 |
| --- | --- | --- | --- | --- |
| M001 | PowerShell here-string 拼补丁文本，插入内容与锚行粘连、末尾空行丢失，diff 出现重复函数签名 | here-string 收尾换行是闭引号终止符不属内容，首行空行才算真换行 | 多行插入块用显式 `` `n `` 拼接，不用 here-string；产出必须先 diff 再采用 [实证: 2026-09-11 补丁脚本两次返工] | 2026-09-11 |
| M002 | `$t.Replace([char]0x2192,'->')` 抛 MethodException 且非终止，后续语句带旧值继续跑，打印 done 假成功 | 字符串长度 2 匹配到了 char 重载 | 多字符替换写 `.Replace([string][char]0x2192,'->')` 或直接字面量；脚本加 `$ErrorActionPreference='Stop'` | 2026-09-11 |
| M003 | `git diff --no-index` 传 Windows 反斜杠路径，输出头带引号且路径含 `\`，后处理正则替换全部落空，patch 0 字节/脏头 | git 对含反斜杠路径按需加引号转义 | 传参一律用正斜杠；生成后 `Select-String '^diff --git'` 自检再落盘 | 2026-09-11 |
| M004 | `git apply` 后文件哈希与脚本输出不一致，疑补丁错误 | 本机全局 `core.autocrlf=true` 令 git apply 全文重写为 CRLF；内容实为等价 | Chromium 仓必须 `core.autocrlf false`；字节比对前先归一换行；真正判据是 `git apply --check` 通过 + 内容等价 [实证: 2026-09-11] | 2026-09-11 |
