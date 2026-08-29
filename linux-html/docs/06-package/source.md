---
title: 源码编译
date: 2026-08-15  # date-auto-injected
---

# 源码编译安装

> 多数情况用包管理器最简单，但有时确实需要编译（最新版本、自定义选项）。

## 🛠 三大步骤

```
configure  ->  make  ->  make install
```

```bash
# 1. configure：探测环境 + 生成 Makefile
./configure --prefix=/usr/local/myapp \
            --enable-feature \
            --disable-other

# 2. make：并行编译
make -j$(nproc)

# 3. make install：安装
sudo make install
```

## 📦 准备工具链

```bash
# Debian / Ubuntu
sudo apt install build-essential autoconf automake libtool pkg-config

# RHEL / CentOS
sudo dnf groupinstall "Development Tools"
sudo dnf install autoconf automake libtool pkgconfig
```

## 🔧 经典例子：编译 nginx / redis / nodejs

### Redis

```bash
wget https://download.redis.io/releases/redis-7.2.0.tar.gz
tar xzf redis-7.2.0.tar.gz
cd redis-7.2.0
make -j$(nproc)
sudo make install

# 或装到指定目录
make PREFIX=/opt/redis install
```

### Node.js

```bash
git clone https://github.com/nodejs/node.git
cd node
./configure --prefix=/usr/local/node
make -j$(nproc)
sudo make install
```

### 自定义编译选项

```bash
# 典型 autotools 项目
./configure --help                  # 看所有选项
./configure --prefix=/usr/local/myapp \
            --with-openssl          # 启用 openssl 支持
            --without-icu          # 禁用 ICU

# 典型 cmake 项目（CMake）
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release \
         -DCMAKE_INSTALL_PREFIX=/usr/local/myapp
make -j$(nproc)
sudo make install
```

## 📁 推荐安装位置

| 路径 | 用途 |
|------|------|
| `/usr/local/` | 自编译软件默认目录（不影响包管理器） |
| `/opt/<name>/` | 大型第三方（Oracle、IDE） |
| `/usr/local/bin/` | 可执行文件 |
| `/usr/local/lib/` | 库文件 |
| `/usr/local/share/` | 共享数据 |

**不要**装到 `/usr/`——会和系统包冲突。

## 🔧 ldconfig

```bash
# 装到 /usr/local/lib 后，需要让动态链接器找到
sudo ldconfig

# 或临时生效
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
```

## 🛠 checkinstall（推荐）

普通 `make install` 会让包管理器"看不到"自编译软件。

```bash
sudo apt install checkinstall    # Ubuntu

cd myapp-1.0
./configure --prefix=/usr/local/myapp
make
sudo checkinstall
# 自动打包成 .deb，下一次可以 dpkg -r 干净卸载
```

## 🪤 与系统包共存

```bash
# 自编译装到 /usr/local
# 系统包装到 /usr
# 优先用 /usr/local（PATH 顺序）
echo $PATH
# /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# 自编译 vs 系统包命令
which -a nginx                    # 列所有
```

## 🐳 优先考虑容器

```bash
# 多数情况，用 docker 比编译更省心
docker run -d -p 80:80 nginx:alpine

# 如果非要本地：编译到容器外的 volume
docker run -v /opt/myapp/dist:/dist ...
```

详见 [容器化安装](/06-package/container)。

## ⚠️ 源码编译的代价

| 代价 | 描述 |
|------|------|
| 升级麻烦 | 每次新版要重新编译 |
| 安全补丁 | 没有自动推送 |
| 依赖冲突 | 自带 lib 可能与系统 lib 版本冲突 |
| 卸载麻烦 | `make uninstall`（如果有）或手动清 |

## 🔧 实战：编译并打成包

```bash
# ./configure + make + checkinstall
./configure --prefix=/usr/local/myapp
make -j$(nproc)
sudo checkinstall --pkgname=myapp \
                 --pkgversion=1.0.0 \
                 --default
```

## 🔗 下一步

- [apt (Debian/Ubuntu)](/06-package/apt)
- [yum / dnf (RHEL)](/06-package/yum-dnf)
- [容器化安装](/06-package/container)