---
title: WebDAV
---

# WebDAV — 把文件系统搬上 HTTP

> <span class="kg-badge kg-badge--network">网络协议</span>
> HTTP 扩展 · 跨互联网友好 · 协作场景

WebDAV（Web Distributed Authoring and Versioning）是一组 HTTP 方法扩展，让客户端能**在远端 web 服务器上读写文件**。它把 HTTP 当成"远程文件系统"，是云盘、协作工具的核心协议。

## 1. HTTP 方法扩展

| 方法 | 用途 |
|------|------|
| GET / HEAD | 取文件（HTTP 原生） |
| PUT | 上传文件 |
| DELETE | 删除文件 |
| MKCOL | 创建目录 |
| COPY | 服务端拷贝 |
| MOVE | 服务端移动/重命名 |
| PROPFIND | 查文件属性 |
| PROPPATCH | 改文件属性 |
| LOCK / UNLOCK | 文件锁（RFC 4918） |

## 2. 协议栈

```
┌────────────────┐
│  WebDAV Client │
└────────┬───────┘
         │ HTTP/HTTPS
┌────────▼───────┐
│  WebDAV Server │
│  (Apache/nginx + dav / Nextcloud / Seafile) │
└────────────────┘
```

走标准 80 / 443 端口 → 防火墙友好、跨互联网可用。

## 3. 服务端实现

### 3.1 Apache mod_dav

```bash
yum install -y httpd mod_dav_fs

cat > /etc/httpd/conf.d/dav.conf <<EOF
DavLockDB "/var/www/davlock"
<VirtualHost *:80>
    ServerName dav.example.com
    DocumentRoot /data/webdav

    <Directory /data/webdav>
        Options Indexes
        DAV On
        AuthType Basic
        AuthName "WebDAV"
        AuthUserFile /etc/httpd/.htpasswd
        Require valid-user
    </Directory>
</VirtualHost>
EOF

mkdir -p /data/webdav
chown -R apache:apache /data/webdav
htpasswd -c /etc/httpd/.htpasswd alice

systemctl start httpd
```

### 3.2 Nginx + nginx-dav-ext

```bash
# 需要 nginx-dav-ext 模块（nginx 自带的 dav 只支持 MKCOL 等基础方法）
apt install -y libnginx-mod-http-dav-ext

cat > /etc/nginx/sites-available/dav <<EOF
server {
    listen 80;
    server_name dav.example.com;

    location / {
        root /data/webdav;
        dav_methods PUT DELETE MKCOL COPY MOVE;
        dav_ext_methods PROPFIND OPTIONS LOCK UNLOCK;
        create_full_put_path on;
        client_max_body_size 0;
        auth_basic "WebDAV";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }
}
EOF

nginx -t && systemctl reload nginx
```

### 3.3 专用产品

| 产品 | 说明 |
|------|------|
| Nextcloud | 自托管网盘（WebDAV + 协作） |
| Seafile | 自托管云盘（自研协议 + WebDAV） |
| OwnCloud | 自托管云盘（WebDAV） |
| Apache Guacamole | 远程桌面 + 文件 |

## 4. 客户端使用

### 4.1 Windows

```cmd
net use Z: https://dav.example.com /user:alice password
```

资源管理器直接打开 Z 盘。

### 4.2 Linux

```bash
# cadaver（命令行）
yum install -y cadaver
cadaver https://dav.example.com

# 用 curl
curl -T file.txt https://alice:password@dav.example.com/upload.txt
curl -O https://alice:password@dav.example.com/file.txt

# 挂载（davfs2）
yum install -y davfs2
mount -t davfs https://dav.example.com /mnt/webdav
```

### 4.3 macOS

`Finder → 前往 → 连接服务器` → `https://dav.example.com`

## 5. WebDAV + 大文件

```bash
# 客户端：分片上传 + 断点续传
# WebDAV 协议层面没有分片，要靠客户端：
# - 客户端用 chunked transfer encoding
# - 或客户端分割文件后多次 PUT

# 服务端：允许大请求
# Apache
LimitXMLRequestBody 0
LimitRequestBody 0

# Nginx
client_max_body_size 0;
```

## 6. 性能

| 维度 | WebDAV | NFS |
|------|--------|-----|
| 延迟 | 高（HTTP） | 低 |
| 吞吐 | 中 | 高 |
| 跨网 | **优** | 差 |
| 加密 | TLS 内置 | 需 Kerberos |
| 大目录 list | 慢 | 快 |
| 文件锁 | RFC 4918（用得少） | 强 |

**经验**：WebDAV 适合"个人网盘、协作、远程办公"，不适合"高性能计算"。

## 7. 与 HTTP/REST API 对比

| 特性 | WebDAV | REST 对象存储 |
|------|--------|--------------|
| 文件接口 | 完整 | 完整 |
| 元数据 | 标准属性 | 自定义 |
| 权限 | HTTP 鉴权 | IAM |
| 生态 | 网盘 / 备份 | 通用 |

WebDAV = **HTTP + 文件系统**；S3 = **HTTP + 键值**。

## 8. 实战：Nextcloud 用 WebDAV

Nextcloud 暴露 WebDAV 接口 `/remote.php/dav/files/<user>/`：

```
URL: https://nc.example.com/remote.php/dav/files/alice/
```

可以挂在 macOS Finder、Linux mount.davfs，作为"个人云盘"使用。

## 9. 安全

```bash
# 强制 HTTPS
<VirtualHost *:443>
    SSLEngine on
    SSLCertificateFile /etc/ssl/cert.pem
    SSLCertificateKeyFile /etc/ssl/key.pem
    ...
</VirtualHost>

# 限流（Nginx）
limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s;

location / {
    limit_req zone=one burst=20;
    ...
}
```

防爆破、防 CC。

## 10. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| WebDAV = HTTP + 文件 | "WebDAV=HTTP-FS" |
| 端口 80/443 | "HTTP=过防火墙" |
| 自托管 = Nextcloud | "Nextcloud=自托管" |
| 性能不及 NFS | "性能≤NFS" |
| 协作场景的杀手锏 | "协作=WebDAV" |

## 参考

- RFC 4918（WebDAV）
- Apache mod_dav 文档
- nginx-dav-ext 仓库
- Nextcloud 用户手册（WebDAV 章节）