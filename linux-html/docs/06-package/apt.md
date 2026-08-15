---
title: apt (Debian/Ubuntu)
---

# apt - Debian/Ubuntu 包管理

> Advanced Package Tool。Ubuntu/Debian 默认包管理器。

## 🛠 高频命令

```bash
sudo apt update                          # 同步源索引
sudo apt upgrade                         # 升级已装包
sudo apt install nginx                  # 安装
sudo apt install nginx=1.18.0-1        # 指定版本
sudo apt remove nginx                   # 卸载（保留配置）
sudo apt purge nginx                     # 卸载 + 删配置
sudo apt autoremove                      # 删不再需要的依赖

# 搜索
apt search nginx
apt-cache search nginx                  # 更精确

# 看包信息
apt show nginx
apt-cache showpkg nginx
apt-cache depends nginx                 # 依赖
apt-cache rdepends nginx                # 谁依赖它

# 列出
apt list --installed                     # 已装
apt list --upgradable                    # 可升级

# 锁定版本（防自动升级）
sudo apt-mark hold nginx
sudo apt-mark unhold nginx
```

## 📦 源

```bash
cat /etc/apt/sources.list
# deb http://archive.ubuntu.com/ubuntu noble main restricted universe multiverse
# deb http://archive.ubuntu.com/ubuntu noble-updates main restricted universe multiverse
# deb http://security.ubuntu.com/ubuntu noble-security main restricted universe multiverse

# 第三方源（推荐 PPA）
sudo add-apt-repository ppa:nginx/stable
sudo apt update
sudo apt install nginx

# 自己加源
echo 'deb https://download.example.com/repo stable main' | sudo tee /etc/apt/sources.list.d/example.list
sudo apt-key add <key>
sudo apt update
```

## 🗃 本地 deb 包

```bash
sudo dpkg -i package.deb              # 安装
sudo apt install ./package.deb        # apt 处理依赖
sudo dpkg -l                          # 列出已装包
sudo dpkg -L nginx                    # 包安装的所有文件
sudo dpkg -S /usr/sbin/nginx          # 哪个包提供的
dpkg-deb -c package.deb              # 看 deb 内容（未安装）
```

## 🔍 看文件属于哪个包

```bash
apt-file search bin/nginx             # 全源文件搜索
sudo apt install -y apt-file
sudo apt-file update
apt-file search /etc/nginx/nginx.conf
```

## 🪤 锁定包 + 升级策略

```bash
# /etc/apt/apt.conf.d/50unattended-upgrades
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
    "${distro_id}:${distro_codename}-updates";
};

# 自动清理旧 kernel
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
```

## 🪞 sources.list 格式

```
deb http://site/ubuntu distro component1 component2
deb-src http://site/ubuntu distro component1 component2
```

| 部分 | 含义 |
|------|------|
| `deb` / `deb-src` | 二进制 / 源码 |
| URL | 仓库地址 |
| `distro` | 发行版代号（noble / jammy） |
| `component` | main / restricted / universe / multiverse |

## 🧊 缓存

```bash
ls /var/cache/apt/archives/            # 下载的 .deb 缓存
sudo apt clean                         # 全部清掉
sudo apt autoclean                     # 只清旧版本
```

## 🪛 实战

```bash
# 看大文件包
dpkg-query -W --showformat='${Installed-Size}\t${Package}\n' | sort -rn | head

# 装 .deb 并自动补依赖
sudo apt install ./pkg.deb

# 查某个命令是哪个包
dpkg -S $(which nginx)

# 完整重建包列表（迁移 / 审计）
dpkg --get-selections > pkglist.txt
# 恢复
sudo dpkg --set-selections < pkglist.txt && sudo apt-get dselect-upgrade

# 仅安全升级
sudo apt upgrade -s                  # 模拟
sudo unattended-upgrade -d          # dry-run

# 列出 apt 配置文件
ls /etc/apt/apt.conf.d/
```

## 🆚 apt vs apt-get

| | apt | apt-get |
|--|-----|---------|
| 用户体验 | 彩色输出 + 进度条 | 纯文本 |
| 默认适合 | 日常使用 | 脚本 |
| 进度条 | ✅ | ❌ |

`apt` 是 `apt-get` + `apt-cache` 的"前端封装"。新脚本建议用 apt。

## 🔗 下一步

- [yum / dnf (RHEL)](/06-package/yum-dnf)
- [源码编译](/06-package/source)
- [容器化安装](/06-package/container)