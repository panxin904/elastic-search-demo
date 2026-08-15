---
title: curl / wget
---

# curl / wget

> 命令行 HTTP 工具，调试 API / 下载文件必备。

## 🆚 curl vs wget

| | curl | wget |
|--|------|------|
| HTTP 方法 | GET / POST / PUT / DELETE / PATCH … | 仅 GET / POST |
| 输出 | 默认 stdout | 默认下载到文件 |
| 协议 | HTTP / FTP / SMTP / LDAP / 等 | HTTP / FTP / SFTP |
| 递归下载 | ❌ | ✅（爬站） |
| 管道 | ✅ | ⚠ |
| 现代 API 调试 | ✅ | ❌ |

## 📡 curl 基础

```bash
curl url                        # GET 请求（输出到 stdout）
curl -I url                    # 只看 headers
curl -L url                    # 跟随 302 重定向
curl -o file url               # 保存到文件
curl -O url                    # 保存为 url 的 basename
curl -s url                    # silent（不显示进度）
curl -v url                    # verbose（看请求详情）

# POST
curl -X POST url               # 显式 POST
curl -X POST -d 'a=1&b=2' url
curl -X POST -H 'Content-Type: application/json' \
  -d '{"name":"alice"}' url

# 自动 JSON / form
curl -X POST -F 'name=alice' -F 'age=30' url   # multipart form
curl --data-urlencode 'msg=hello world' url
```

## 📋 headers / cookies

```bash
# 看响应头
curl -I url                    # 仅 headers
curl -v url                    # 完整请求 / 响应

# 自定义 headers
curl -H 'Authorization: Bearer xxx' url
curl -H 'User-Agent: Mozilla/5.0' url

# Cookie
curl -c cookies.txt url       # 存
curl -b cookies.txt url       # 用
curl -b 'session=xxx' url     # 内联
```

## 🔐 认证

```bash
# Basic
curl -u user:pass url
curl -u user url               # 会提示输入密码

# Bearer Token
curl -H 'Authorization: Bearer xxx' url

# 自定义 header
curl -H 'X-API-Key: xxx' url
```

## 🪝 高级用法

```bash
# 文件上传
curl -F 'file=@/path/to/file' url

# 跟随 redirect 但保留 cookies
curl -L -c cookies.txt url

# 设超时
curl --connect-timeout 5 --max-time 30 url

# 限速（调试大文件）
curl --limit-rate 100k url

# 看响应时间
curl -w '\n%{time_total}\n' url

# 指定 DNS
curl --resolve example.com:443:1.2.3.4 https://example.com/

# 模拟浏览器
curl -A 'Mozilla/5.0' \
  -H 'Accept: text/html' \
  -b cookies.txt url

# POST JSON 自动加 Content-Type
curl -X POST -H 'Content-Type: application/json' \
  -d '{"x":1}' url
```

## 🛠 实战

```bash
# 健康检查
curl -I -m 5 http://localhost:8080/health

# API 测试
curl -X POST http://api.example.com/v1/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"secret"}'

# 看 nginx 是否正常
curl -I -L https://example.com
# HTTP/2 200 / server: nginx / content-type: text/html

# 看 API 完整时间
curl -w '%{time_total} / %{http_code}\n' -o /dev/null -s url

# 下载大文件（断点续传）
curl -C - -O url

# 模拟表单
curl -X POST -F 'username=alice' -F 'password=p@ss' \
  https://example.com/login

# Webhook 测试
curl -X POST -H 'X-Hub-Signature: xxx' \
  -d '{"event":"push"}' \
  http://localhost:8080/webhook
```

## 📥 wget 基础

```bash
wget url                       # 下载到当前目录
wget -O name url               # 指定文件名
wget -c url                   # 断点续传
wget -b url                   # 后台（输出 wget-log）
wget -q url                   # 安静模式
wget --limit-rate=500k url   # 限速
wget -i list.txt              # 批量下载（每行一个 URL）

# 递归下载（爬站）
wget -r -np -k https://example.com/
# -r recursive
# -np no-parent（不上溯）
# -k 把链接转本地
```

## 🔄 模拟请求（调试后端）

```bash
# OPTIONS（看 CORS）
curl -X OPTIONS -I url

# 看完整 HTTP 交换
curl -v -X POST url -d 'a=1' 2>&1 | grep -E '^[<>]'

# 设置 User-Agent 防 403
curl -A 'curl/7.81' url

# 用 -I 测试 HTTP 头（不上 body）
curl -I -X DELETE url
```

## 📊 性能 / 调试

```bash
# 时间分解
curl -w '@-' <<EOF -o /dev/null -s url
time_namelookup:    %{time_namelookup}\n
time_connect:        %{time_connect}\n
time_appconnect:     %{time_appconnect}\n
time_pretransfer:    %{time_pretransfer}\n
time_redirect:       %{time_redirect}\n
time_starttransfer:  %{time_starttransfer}\n
time_total:          %{time_total}\n
EOF

# 多次请求看稳定性
for i in {1..10}; do
  curl -w '%{time_total}\n' -o /dev/null -s url
done
```

## 🔗 下一步

- [DNS 解析](/07-network/dns)
- [ss / netstat](/07-network/ss)
- [SSH 隧道 / 代理](/08-firewall-ssh/ssh-tunnel)