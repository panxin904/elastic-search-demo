---
title: Nginx
---

# Nginx

Nginx 是高性能的 HTTP 服务器和反向代理，常用于负载均衡、静态资源、HTTPS 终端。

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
