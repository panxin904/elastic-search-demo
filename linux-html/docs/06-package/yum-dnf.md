---
title: yum / dnf (RHEL)
---

# yum / dnf - RHEL 系包管理

> dnf 是 yum 的现代替代（基于 libsolv）。CentOS 8+ / RHEL 8+ / Fedora 已默认 dnf。

## 🛠 高频命令

```bash
# 大部分命令与 apt 类似
sudo dnf check-update                 # 看可升级
sudo dnf update                        # 升级所有
sudo dnf install nginx               # 安装
sudo dnf install nginx-1:1.20.0      # 指定版本
sudo dnf remove nginx                # 卸载
sudo dnf autoremove                   # 清不再需要的依赖

# 搜索
dnf search nginx
dnf search "web server"

# 看包信息
dnf info nginx
dnf deplist nginx                    # 依赖

# 列出
dnf list installed                   # 已装
dnf list available                   # 可装
dnf list updates                     # 可升级

# 组（批量）
dnf group list                       # 列出组
dnf group install "Development Tools"
```

## 📦 源 / 仓库

```bash
ls /etc/yum.repos.d/
# epel.repo
# nginx.repo
```

```ini
# /etc/yum.repos.d/nginx.repo
[nginx-stable]
name=nginx stable repo
baseurl=http://nginx.org/packages/centos/$releasever/$basearch/
gpgcheck=1
enabled=1
gpgkey=https://nginx.org/keys/nginx_signing.key
module_hotfixes=true
```

```bash
sudo dnf config-manager --add-repo https://example.com/repo.repo
sudo dnf config-manager --enable nginx-stable
```

## 📊 仓库组

| 仓库 | 含义 |
|------|------|
| base | RHEL 基础（主发行版） |
| epel | Extra Packages for Enterprise Linux（社区） |
| rpmfusion | RPM Fusion（多媒体 / 非自由） |
| updates / security | 官方更新 / 安全 |
| extras | RHEL 额外（订阅） |

## 🪞 常见技巧

```bash
# 看某文件属于哪个包
dnf provides /etc/nginx/nginx.conf
rpm -qf /etc/nginx/nginx.conf

# 下载 rpm 不安装
dnf download nginx

# 看安装历史
dnf history list
dnf history info <id>                 # 看某次详情
dnf history undo <id>                 # 撤销
```

## 🆚 yum vs dnf vs rpm

| | yum | dnf | rpm |
|--|-----|-----|-----|
| 依赖 | 自动 | 自动 | 手动 |
| 仓库 | ✅ | ✅ | ❌ |
| 速度 | 慢 | 快（C 写的 libsolv） | - |
| 推荐 | CentOS 7 | CentOS 8+ / RHEL 8+ / Fedora | 查信息 |

## 🔐 EPEL（必装）

```bash
# CentOS 7
sudo yum install epel-release
sudo yum install nginx

# RHEL 8+ / Rocky
sudo dnf install epel-release
# 或
sudo dnf install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
```

## 🛠 实战

```bash
# 查系统版本
cat /etc/redhat-release
rpm -E %{rhel}

# 看已装内核（清理旧版本）
rpm -qa kernel
sudo dnf remove kernel-5.14.0-... 

# 仓库元数据重建
sudo dnf clean all
sudo dnf makecache

# 启用 modularity（dnf 独家）
dnf module list
dnf module enable nodejs:18
dnf install nodejs

# 检查安全更新
dnf check-update --security
```

## 🧊 配置 /etc/dnf/dnf.conf

```ini
[main]
gpgcheck=1
installonly_limit=3
clean_requirements_on_remove=True
fastestmirror=True
max_parallel_downloads=4
```

## 🔗 下一步

- [apt (Debian/Ubuntu)](/06-package/apt)
- [源码编译](/06-package/source)
- [容器化安装](/06-package/container)