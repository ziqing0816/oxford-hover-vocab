# Oxford Hover Vocab 架构草案

## 项目目标

在 Windows 任意界面中，通过快捷键加鼠标悬停识别光标附近的英文单词，并展示：

- 英文释义与词性；
- 简体中文辅助解释；
- 音标和发音；
- 同义词、反义词、搭配和例句；
- 当前阅读语境中的原句；
- 可复习的个人生词记录。

项目基于 `AFA7777/hover-translate` 二次开发。保留其 Windows 屏幕捕获、OCR、浮窗和离线回退能力，不复制或重新发布第三方词典的受版权保护数据。

## 组件

```text
全局快捷键与鼠标悬停
        ↓
屏幕局部截图（仅触发时）
        ↓
Windows OCR 与光标单词定位
        ↓
词形标准化
        ↓
DictionaryProvider 接口
   ├─ Oxford API（可选，用户自行配置凭据）
   └─ 本地离线词典（默认回退）
        ↓
统一 WordEntry
        ↓
浮窗显示 + 本地生词库 + 间隔复习
```

## 词典提供者

所有词典实现统一返回 `WordEntry`，上层界面不直接依赖具体供应商。

建议字段：

- `word`、`lemma`、`part_of_speech`；
- `phonetic_uk`、`phonetic_us`、`audio_url`；
- `definitions_en`、`meaning_zh_cn`；
- `synonyms`、`antonyms`、`collocations`、`examples`；
- `provider`、`source_url`、`fetched_at`。

Oxford 提供者只调用官方授权接口，不抓取 Oxford 网页，不绕过安全验证。没有凭据、请求失败或离线时，程序自动回退到本地词典。

## 凭据与隐私

- Oxford App ID、App Key 等凭据只从环境变量或不纳入 Git 的本地配置读取。
- 不把凭据写入源码、日志、生词库、Issue、提交记录或错误报告。
- 默认只截取光标周围的小范围画面；不录屏，不保存截图。
- 发送给在线词典的默认内容只有规范化后的单词，不发送完整截图、窗口标题、其他屏幕文字或浏览历史。
- 原句默认仅保存在本机；未来如需交给在线 AI 补充解释，必须由用户主动启用。

## 简体中文策略

- ECDICT 原始简体中文释义直接入库，不再默认执行 `s2twp` 转换。
- 默认中文语音优先匹配简体中文 SAPI 语音，例如 `Huihui`。
- OCR 自动选择顺序优先英文，其次 `zh-Hans-CN`。
- 界面、配置示例、日志和主要文档使用简体中文。
- 上游繁体转换能力可作为可选兼容模式保留，但不作为默认路径。

## 生词与复习

生词库使用本地 SQLite 保存，按规范化 lemma 去重。每次查询更新：

- 首次/最近查询时间；
- 查询次数和来源原句；
- 词典提供者及来源链接；
- 复习阶段、下次复习日期和掌握状态。

导出层负责生成 CSV、Excel 或 Markdown 复习单。导出文件不应包含 API 凭据。

## 开发顺序

1. 将上游默认语言调整为简体中文，并保持原版自测可运行。
2. 抽象 `WordEntry` 与 `DictionaryProvider`。
3. 将现有离线词典迁移为 `LocalDictionaryProvider`。
4. 添加可选 `OxfordDictionaryProvider` 与凭据检查。
5. 添加本地生词库、去重、导出和间隔复习。
6. 完善隐私说明、测试、安装脚本和发布流程。
