---
title: Nginx
---

# Nginx

Nginx 是高性能的 HTTP 服务器和反向代理，常用于负载均衡、静态资源、HTTPS 终端。

## 🛠️ Nginx 关键配置

**反向代理**：`proxy_pass http://backend;` + `proxy_set_header X-Real-IP $remote_addr;`

**负载均衡策略**：
- `round-robin`（默认，轮询）
- `least_conn`（最少连接，适合长连接）
- `ip_hash`（会话保持，按客户端 IP hash）
- `weight=`（权重，可与上面策略组合）

**gzip 压缩**：`gzip on; gzip_types text/plain application/json; gzip_min_length 1024;`

**HTTPS**：`ssl_certificate /etc/nginx/ssl/cert.pem; ssl_certificate_key /etc/nginx/ssl/key.pem;`
（用 Let's Encrypt + certbot 自动续期）。

## 反向代理

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 负载均衡

```nginx
upstream backend {
    # 默认轮询
    server 192.168.1.101:8080 weight=3;  # 权重
    server 192.168.1.102:8080 weight=1;
    server 192.168.1.103:8080 backup;     # 备用
}

server {
    location /api/ {
        proxy_pass http://backend;
    }
}
```

## 静态资源

```nginx
server {
    listen 80;
    server_name www.example.com;

    # 前端静态文件
    location / {
        root /var/www/html;
        index index.html;
        try_files $uri $uri/ /index.html;  # SPA 路由
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|svg)$ {
        root /var/www/html;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # API 代理
    location /api/ {
        proxy_pass http://localhost:8080;
    }
}
```

## HTTPS 配置

```nginx
server {
    listen 443 ssl;
    server_name api.example.com;

    ssl_certificate     /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;

    location / {
        proxy_pass http://localhost:8080;
    }
}

# HTTP 自动跳转 HTTPS
server {
    listen 80;
    server_name api.example.com;
    return 301 https://$server_name$request_uri;
}
```

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="nginx" :height="400" />


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->

<!-- svg-injected:do-not-edit -->

## 图示：Nginx upstream 负载均衡

![Nginx upstream 负载均衡](/load-balancer-detail.svg)
