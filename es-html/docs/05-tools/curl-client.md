---
title: ES 调试器
---

<span class="kg-badge kg-badge-storage">调试</span>

# ES 请求调试器

> 在线构造并发送 ES 请求，附带 **JSON 格式化**、**请求头编辑**、**认证**、**自动生成 curl 命令**。

## 🎯 功能

- ✏️ 自定义 HTTP 方法 + URL 路径
- 📦 Body 编辑器 + **一键 JSON 格式化**
- 📑 自定义请求头（多 header）
- 🔐 Basic Auth 自动注入
- 📨 实时显示状态码/耗时/响应大小
- 🖥️ 等效 curl 命令生成（一键复制）

<EsRequestDebugger />

## 🚀 使用流程

1. **配置 endpoint**：第一次访问在顶部 `服务端地址` 中输入 ES 地址（如 `http://localhost:9200`），自动保存到浏览器
2. **如启用了 xpack.security**：填入用户名密码
3. **选择方法**：GET / POST / PUT / DELETE / HEAD
4. **输入路径**：如 `/products/_search`、`/_cluster/health`
5. **Body**：多行 JSON 输入，点击 **✨ 格式化 JSON** 缩进美化
6. **点击「发送请求」**：查看响应

## 🖥️ 等效 curl

切到「🖥️ 等效 curl」标签页可看到自动生成的 curl 命令，复制到本地终端可绕开 CORS 限制。

## ⚠️ CORS 配置

工具箱通过浏览器直接调用 ES，需要 ES 开启 CORS：

```yaml
# elasticsearch.yml
http.cors.enabled: true
http.cors.allow-origin: "*"
http.cors.allow-methods: "OPTIONS, HEAD, GET, POST, PUT, DELETE"
http.cors.allow-headers: "Authorization, Content-Type, X-Requested-With"
http.cors.allow-credentials: true
```

修改后**重启 ES 节点**生效。

## 🛠️ 错误排查

| 现象 | 原因 | 解决 |
|---|---|---|
| CORS 错误 | ES 未开启 CORS | 配置 `http.cors.enabled` 或用 curl 命令 |
| 401 Unauthorized | 未提供凭据 | 输入用户名密码 |
| 连接被拒绝 | ES 未启动 / 端口错 | 检查 endpoint 与端口 |
| Body 不是合法 JSON | JSON 语法错 | 用「格式化 JSON」按钮检测 |

## 📚 关联工具

- 📚 **[DSL 速查](/05-tools/dsl)** — 21 个常用 Query DSL 模板，可在调试器一键预填
- ☕ **[Java SDK 速查](/05-tools/java)** — 20+ 个 Java Client 代码片段
- 📊 **[集群监控仪表板](/05-tools/dashboard)** — 实时监控集群

## 📚 关联文档

- [安装部署](/04-ops/installation)
- [集群健康](/04-ops/cluster-health)
- [Query DSL](/02-query/query-dsl)
- [聚合 Aggregation](/02-query/aggregation)
- [Java Client 官方文档](https://www.elastic.co/guide/en/elasticsearch/client/java-api-client/current/introduction.html)
