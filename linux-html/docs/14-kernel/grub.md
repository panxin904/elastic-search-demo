---
title: GRUB 引导
date: 2026-08-15  # date-auto-injected
---

# GRUB 引导加载

> GRUB = **GR**and **U**nified **B**ootloader。Linux 开机第一阶段。

## 🏗️ 启动顺序

```
  按电源
    ↓
  BIOS / UEFI 初始化硬件
    ↓
  读 MBR / EFI 分区 → 加载 GRUB
    ↓
  GRUB 显示菜单 / 自动引导
    ↓
  加载内核 (vmlinuz) + initramfs
    ↓
  内核初始化硬件 → 切换到根文件系统
    ↓
  启动 systemd (PID 1)
    ↓
  各 service 启动
```

## 📂 文件位置

```
BIOS / Legacy:
  /boot/grub/grub.cfg         配置文件（不要手改！）
  /boot/grub/i386-pc/         BIOS 启动镜像

UEFI:
  /boot/efi/EFI/ubuntu/grubx64.efi  (Ubuntu)
  /boot/efi/EFI/centos/grubx64.efi  (CentOS)
  /boot/efi/EFI/BOOT/fbx64.efi
  /efi/EFI/...
```

> 配置**不要直接编辑** `/boot/grub/grub.cfg`，改 `/etc/default/grub` + `/etc/grub.d/` 然后 `update-grub`。

## 🛠 配置

```bash
sudo vim /etc/default/grub
```

```bash
GRUB_DEFAULT=0               # 默认启动第 0 项
GRUB_TIMEOUT=5               # 菜单 5 秒（生产建议 0）
GRUB_TIMEOUT_STYLE=hidden    # hidden / menu / countdown
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
GRUB_CMDLINE_LINUX="net.ifnames=0 biosdevname=0"   # 额外参数

# 应用
sudo update-grub              # Debian / Ubuntu
sudo grub2-mkconfig -o /boot/grub2/grub.cfg    # RHEL / CentOS
```

## 🔧 单次启动参数

启动时按 `e` 编辑菜单条目。在 `linux` 行末尾加参数。

| 参数 | 作用 |
|------|------|
| `single` | 单用户模式（救援） |
| `init=/bin/bash` | 跳过 systemd 直进 bash |
| `systemd.unit=rescue.target` | 进救援模式 |
| `nomodeset` | 跳过显卡驱动（卡黑屏时） |
| `quiet splash` | 隐藏启动信息 |
| `ro` / `rw` | 根挂载为只读 / 读写 |

按 `Ctrl+X` 或 `F10` 启动。

### 救援模式（忘 root 密码时）

```
1. 启动时长 Shift（或按 ESC）进 GRUB 菜单
2. 选默认内核，按 e
3. 找 linux 行，删 "ro quiet splash"
4. 末尾加 "rw init=/bin/bash"
5. Ctrl+X 启动
6. 获得 root shell
7. mount -o remount,rw /         # 根分区可能仍是 ro
8. passwd root                  # 改密码
9. exec /sbin/init              # 切回 systemd（或 reboot -f）
```

## 🪵 改默认启动顺序

```bash
# 看启动项
grep menuentry /boot/grub/grub.cfg

# 临时切换（下次启动）
sudo grub-reboot 'Advanced options for Ubuntu > Ubuntu, with Linux 5.15.0-91-generic'
sudo reboot

# 永久改默认
sudo grub-set-default 0
```

## 🪛 更新 GRUB

```bash
# 加 / 删内核后自动运行（一般 apt 会触发）
sudo update-grub

# 手动
sudo update-grub              # Debian / Ubuntu
sudo grub2-mkconfig -o /boot/grub/grub.cfg  # RHEL
```

## 🔐 密码保护 GRUB

```bash
# 给 GRUB 编辑菜单加密码（防修改）
grub-mkpasswd-pbkdf2           # 生成 hash
# 输出 grub.pbkdf2 ...

sudo vim /etc/grub.d/40_custom
```

```bash
# 加到 40_custom
set superusers="admin"
password_pbkdf2 admin grub.pbkdf2.sha512.10000.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# 应用
sudo update-grub

# 现在按 e 编辑要 admin 密码
```

⚠️ 密码别忘，否则自己也进不去。

## 🪤 UEFI / Secure Boot

```bash
# 看是否启用 Secure Boot
mokutil --sb-state

# 关（部分发行版需要）
# 进 BIOS 关闭 Secure Boot

# 装自定义内核签名
sudo apt install shim-signed
mokutil --import /path/to/key.cer
# 重启后走 MOK 管理（按提示 enroll）
```

## 🛠 实战

```bash
# 加 console=ttyS0（云主机串口调试）
GRUB_CMDLINE_LINUX="console=ttyS0,115200"
sudo update-grub

# 默认进入文本模式（关图形）
sudo systemctl set-default multi-user.target

# 启动时显示菜单（debug 用）
# /etc/default/grub
GRUB_TIMEOUT_STYLE=menu
GRUB_TIMEOUT=10
sudo update-grub

# 完全隐藏菜单（生产）
GRUB_TIMEOUT_STYLE=hidden
GRUB_TIMEOUT=0
sudo update-grub
```

## ⚠️ 故障

```bash
# "grub>" 提示符（grub rescue）
ls                             # 看分区
ls (hd0,msdos1)/
set root=(hd0,msdos1)
linux /boot/vmlinuz-...
initrd /boot/initrd.img-...
boot

# 正常进入后修复
sudo update-grub
sudo grub-install /dev/sda

# UEFI 系统下
sudo grub-install --target=x86_64-efi --efi-directory=/boot/efi
sudo update-grub

# 完全重装 GRUB
sudo apt install --reinstall grub
```

## 🔗 下一步

- [initramfs](/14-kernel/initramfs)
- [内核模块](/14-kernel/modules)
- [sysctl 调参](/14-kernel/sysctl)