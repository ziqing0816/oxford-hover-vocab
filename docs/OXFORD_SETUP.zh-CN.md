# Oxford API 配置

Oxford 数据是可选增强来源。没有凭据、断网或接口失败时，应用应继续使用本地离线词典。

## Sandbox 限制

- Sandbox 最多提供 500 次测试调用；
- 英文测试数据通常只允许查询以 `A` 开头的单词；
- Sandbox 返回的字段可能少于正式套餐，例如某些词条没有例句或同义词；
- 项目不抓取 Oxford Dictionary 网页，也不绕过网站安全验证。

## 保存凭据

凭据必须保存为当前 Windows 用户的环境变量：

- `OXFORD_APP_ID`
- `OXFORD_APP_KEY`

可选变量 `OXFORD_API_BASE_URL` 用于切换环境。未设置时默认使用：

```text
https://od-api-sandbox.oxforddictionaries.com/api/v2
```

切换到正式套餐时才设置为：

```text
https://od-api.oxforddictionaries.com/api/v2
```

不要把真实凭据写进源码、`.env`、截图、Issue、日志或 Git 提交。项目的 `.gitignore` 会忽略 `.env`，但环境变量仍是推荐方式。

## 隐私边界

Oxford 提供者只发送规范化后的英文单词，例如 `apple`。它不会发送屏幕截图、窗口标题、原句、生词记录或浏览历史。认证信息只作为 HTTPS 请求头发送给 Oxford 官方 API，不会加入请求网址或返回的词条对象。

官方资料：

- https://developer.oxforddictionaries.com/documentation/getting_started
- https://developer.oxforddictionaries.com/dictionary-api
- https://developer.oxforddictionaries.com/documentation/making-requests-to-the-api
