# Oxford Hover Vocab

Windows 全局划词、Oxford 英英释义、简体中文辅助解释和本地间隔复习工具。

本项目 fork 自 [AFA7777/hover-translate](https://github.com/AFA7777/hover-translate)，保留其屏幕 OCR、鼠标定位、离线词典和语音能力，并增加可选 Oxford 官方 API、生词自动保存、复习文档与卡片界面。

## 可以做什么

- 在 PDF、网页、图片、视频字幕等任意电脑界面取词；
- 显示音标、简体中文释义和当前原句；
- 可选显示 Oxford 英英释义、同义词、反义词与例句；
- 使用 Windows 本地语音朗读英文和简体中文；
- 按原形自动去重并保存生词；
- 生成 Markdown 复习文档和 Excel 可打开的 CSV；
- 使用“不认识 / 困难 / 认识 / 简单”进行间隔复习；
- Oxford 不可用时自动保留本地查询结果。

## 工作流程

```text
按住 Ctrl 并将鼠标停在英文单词上
        ↓
截取光标附近的小范围画面
        ↓
Windows OCR 定位英文单词
        ↓
本地 ECDICT 立即显示简体释义
        ↓
Oxford API 在后台补充英英释义（可选）
        ↓
保存到本地 vocabulary.db
        ↓
导出文档或进入卡片复习
```

## 安装

要求：Windows 10/11、Python 3.8 或更高版本。

1. 点击 GitHub 页面右上角绿色 **Code → Download ZIP**。
2. 解压 ZIP；不要直接在压缩包里运行。
3. 双击 `setup.bat`。
4. 等待依赖和本地词典安装完成。
5. 桌面会出现 `Oxford 划词助手` 和 `生词复习`。

安装器会在项目内创建 `.venv`，不会把依赖装进全局 Python。首次构建本地词典需要下载约 65 MB 数据。

如果提示找不到 Python，请从 [python.org](https://www.python.org/downloads/) 安装，并勾选 **Add Python to PATH**。

### 从 Git 克隆

```powershell
git clone https://github.com/ziqing0816/oxford-hover-vocab.git
cd oxford-hover-vocab
python install.py
```

## 使用

| 操作 | 功能 |
|---|---|
| 按住 `Ctrl` 并移动鼠标到英文上，停留约 0.4 秒 | 查词 |
| 连续按两次 `Esc` | 结束程序 |
| `Ctrl+Alt+H` | 暂停或恢复 |
| `Ctrl+Alt+Q` | 结束程序 |
| 双击 `review-vocab.bat` | 打开生词复习 |
| 双击 `export-vocab.bat` | 导出复习文档 |

程序先立即显示本地释义，再在后台补充 Oxford 内容。网络较慢不会阻塞屏幕取词；较旧的网络响应也不会覆盖后来查询的单词。

## Oxford API（可选）

没有 Oxford 凭据时，程序仍然可以作为本地简体中文划词词典使用。

Oxford 数据必须通过官方 API 获取。本项目不抓取 Oxford 网页，也不绕过安全验证。申请 Sandbox 后，将凭据保存为当前 Windows 用户环境变量：

- `OXFORD_APP_ID`
- `OXFORD_APP_KEY`

详细步骤见 [Oxford API 配置](docs/OXFORD_SETUP.zh-CN.md)。

Sandbox 通常只有 500 次调用，并且英文只支持以 `A` 开头的测试词。程序会自动跳过其他字母，并缓存已经查询过的词，避免浪费试用额度。

## 生词保存与复习

每次成功取词会保存到本机 `vocabulary.db`，并按规范化后的原形去重。例如 `apples`、`apple` 会归入同一条记录。

保存内容包括单词、原形、词性、音标、简体/英英释义、同义词、反义词、例句、当前原句、查询时间与次数，以及复习阶段。

双击 `review-vocab.bat` 打开复习卡片：

- 空格：显示答案；
- `1`：不认识；
- `2`：困难；
- `3`：认识；
- `4`：简单。

双击 `export-vocab.bat` 会在 `exports` 目录生成 `vocabulary-review.md` 和 `vocabulary.csv`。CSV 使用 Excel 兼容的 UTF-8 编码，并防止原句被误认为公式。

## 隐私与网络边界

| 数据 | 是否离开电脑 |
|---|---|
| 光标附近截图 | 否；只交给 Windows 本地 OCR，不保存 |
| 当前原句 | 否；可选保存到本地生词库 |
| 查询的英文单词 | 启用 Oxford 时发送给 Oxford 官方 API |
| App ID / App Key | 作为 HTTPS 请求头发给 Oxford；不写入项目和生词库 |
| 生词、复习记录和导出文件 | 否；只保存在本机 |

项目默认不录屏、不读取剪贴板、不记录键盘内容，也不设置开机启动。触发键只检查按下状态。

`debug: true` 会把 OCR 识别到的单词和部分原句写入 `hover_translate.log`。请勿在密码、个人信息或机密文件画面上开启；排错完成后关闭并删除日志。

## 配置

首次启动会生成 `config.json`。常用字段：

| 字段 | 默认值 | 说明 |
|---|---:|---|
| `modifier` | `ctrl` | 触发键：ctrl / alt / shift / none |
| `dwell_ms` | `400` | 鼠标停留时间 |
| `use_oxford` | `true` | 有凭据时启用 Oxford |
| `oxford_timeout_seconds` | `8` | Oxford 超时秒数 |
| `auto_save_vocabulary` | `true` | 自动保存生词 |
| `save_context_sentence` | `true` | 将原句保存到本机 |
| `max_senses` | `4` | 最多显示的简体义项 |
| `max_english_definitions` | `2` | 最多显示的英英释义 |
| `max_synonyms` | `8` | 最多显示的同义词 |
| `max_examples` | `1` | 最多显示的 Oxford 例句 |
| `speak_english` | `true` | 朗读英文单词 |
| `speak_chinese` | `true` | 朗读简体中文释义 |
| `show_sentence` | `true` | 显示本地原句 |
| `debug` | `false` | 调试日志，可能包含屏幕文字 |

修改配置后需要重启程序。

## 数据与许可证

- 项目源码采用 MIT License，并保留上游作者署名；
- 本仓库不包含或重新发布 ECDICT、Oxford 词典内容；
- `build_dict.py` 从锁定的 ECDICT commit 下载数据并验证 SHA-256；
- Oxford 内容由用户使用自己的官方凭据按需查询；
- `vocabulary.db`、`.env` 和 `exports` 已加入 `.gitignore`。

详情见 [NOTICE](NOTICE) 和 [架构说明](docs/ARCHITECTURE.zh-CN.md)。

## 开发与测试

```powershell
.\.venv\Scripts\python.exe -m unittest -v test_oxford_provider.py test_provider_chain.py test_vocabulary_store.py test_vocab_cli.py test_review_app.py
.\.venv\Scripts\python.exe selftest.py
```

`selftest.py` 会实际验证屏幕捕获、Windows OCR、语音、弹窗、简体释义、快捷键和单一实例。Oxford 单元测试使用模拟响应，不消耗 API 调用次数。

## 项目状态

目前处于首个公开版本发布前的开发阶段。建议在正式使用前查看分支与 Release 说明。
