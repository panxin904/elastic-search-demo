---
title: initramfs
---

# initramfs - 初始内存文件系统

> 内核启动到挂载真实根目录之间的"小"Linux 运行环境。

## 🤔 为什么需要

```
内核启动 → 找 / 根分区
但找 / 需要：磁盘驱动 / 文件系统驱动 / LVM / mdadm ...
这些驱动在 /lib/modules/，但 / 还没挂！
```

**initramfs** = 把驱动 / 必要工具 / 启动脚本打包成 cpio 镜像，内核启动时**先解压到 tmpfs**运行，挂载真根后再 chroot 进去。

## 🪛 看 initramfs 内容

```bash
ls -lh /boot/initrd.img-$(uname -r)
# ~50-200MB

# 看里面
zcat /boot/initrd.img-$(uname -r) | cpio -idmv 2>/dev/null
# 解到当前目录！
ls -la

# 看用了什么模块
ls /lib/modules/$(uname -r)/kernel/drivers/

# 重要文件
# init                  - 主启动脚本
# init_functions       - 工具函数
# usr/lib/firmware/    - 固件
```

## 🏗️ 启动流程

```
GRUB 加载内核 + initramfs
  ↓
内核解压 initramfs 到 tmpfs（内存）
  ↓
内核执行 /init（initramfs 里的脚本）
  ↓
/init 做：
  - 加载必要驱动（lvm / mdadm / filesystem）
  - 解析 cmdline 中的 root=/dev/sda1
  - 找 / 分区并挂载
  - switch_root 到真根
  ↓
内核执行真根 /sbin/init（systemd）
```

## 🛠 配置

```bash
# Debian / Ubuntu
ls /etc/initramfs-tools/

# /etc/initramfs-tools/initramfs.conf
MODULES=most          # most / dep / netboot / list
BUSYBOX=auto          # busybox 内置工具（默认）
COMPRESS=gzip         # gzip / lz4 / xz / zstd
KEYMAP=n
```

```bash
# RHEL / CentOS
ls /etc/dracut.conf.d/
```

## 🔧 自定义 initramfs

### 加额外驱动

```bash
# /etc/initramfs-tools/modules（Debian）
# 加模块名（不带 .ko）
ext4
sd_mod
ahci

# 重新生成
sudo update-initramfs -u -k all
```

### 加自定义脚本

```bash
# /etc/initramfs-tools/scripts/init-bottom/PRE_NETWORK.sh
#!/bin/sh
PREREQ=""
. /scripts/functions
log_begin_msg "Custom step"
# ... 你的逻辑
log_end_msg

sudo chmod +x /etc/initramfs-tools/scripts/init-bottom/PRE_NETWORK.sh
sudo update-initramfs -u -k all
```

### 加文件

```bash
# /etc/initramfs-tools/hooks/myhook
#!/bin/sh
set -e
. /usr/share/initramfs-tools/hook-functions
copy_exec /usr/bin/mytool /bin
# 或
copy_files /etc/myapp.conf /etc

sudo chmod +x /etc/initramfs-tools/hooks/myhook
sudo update-initramfs -u -k all
```

## 🚀 重新生成

```bash
# Debian / Ubuntu
sudo update-initramfs -u              # 升级（保留）
sudo update-initramfs -u -k all      # 全部内核
sudo update-initramfs -c -k $(uname -r)  # 创建当前内核的

# RHEL / CentOS
sudo dracut -f                       # 强制重建当前内核
sudo dracut --kver <kernel-version>  # 指定内核
sudo dracut --add-drivers "ext4 nvme" # 加额外驱动
sudo dracut --add-firmware /lib/firmware/... # 加固件
```

## 🪤 调试

```bash
# 启动卡住？看 initramfs 的错误
# 内核参数加：rd.shell  rd.debug=log
GRUB_CMDLINE_LINUX="rd.shell rd.debug=log"
sudo update-grub

# 启动后进 initramfs shell（无 systemd）
# 在 GRUB 菜单按 e，linux 行加：
break=mount

# 手动修复
lvm vgscan
lvm vgchange -ay
mount /dev/vg0/root /mnt
# 修复后
exit
```

## 🛠 实战：LVM 根分区

如果根分区在 LVM 上，initramfs **必须**包含 lvm 模块：

```bash
# 检查
lsinitramfs /boot/initrd.img-$(uname -r) | grep lvm
# 应有 lvm / dm-snapshot 等

# 没有就加
# /etc/initramfs-tools/modules
dm-mod
dm-mirror
dm-snapshot
dm-thin-pool
dm-zero

sudo update-initramfs -u -k all
```

## 🪛 实战：磁盘迁移到新控制器

旧机器 initramfs 不带新驱动 → 启动不了：

```bash
# 1. 在新机器上装（同样内核版本）initramfs
# 2. 重新生成 initramfs（带新驱动）
sudo update-initramfs -u -k all

# 3. 验证含新驱动
lsinitramfs /boot/initrd.img-$(uname -r) | grep -i nvme
```

## ⚠️ 注意

- 升级内核时 initramfs 自动重建
- 改 `/etc/initramfs-tools/` 后**手动** `update-initramfs -u`
- initramfs 不一致是常见启动失败原因

## 🔗 下一步

- [GRUB 引导](/14-kernel/grub)
- [内核模块](/14-kernel/modules)
- [sysctl 调参](/14-kernel/sysctl)