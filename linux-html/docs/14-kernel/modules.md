---
title: 内核模块
date: 2026-08-15  # date-auto-injected
---

# 内核模块

> Linux 内核按需加载 / 卸载的能力（LKM = Loadable Kernel Module）。

## 📜 基础命令

```bash
lsmod                           # 当前加载的模块（= /proc/modules）
modinfo <module>                # 看模块信息
modprobe <module>               # 智能加载（自动解决依赖）
modprobe -r <module>             # 智能卸载
insmod <module.ko>              # 直接插入（不处理依赖）
rmmod <module>                  # 直接卸载
depmod                          # 生成 modules.dep
```

### 看模块

```bash
lsmod | head
Module                  Size  Used by
nvidia_drm             61440  0
nvidia_modeset        1228800  1 nvidia_drm
nvidia              33732608  91 nvidia_modeset,nvidia_drm
ahci                   40960  1
```

第一列：模块名
第二列：占内存大小
第三列：使用计数 + 谁在用

### 看模块详情

```bash
modinfo ext4
filename:       /lib/modules/5.15.0-91-generic/kernel/fs/ext4/ext4.ko
license:        GPL
description:    Fourth Extended Filesystem
author:         ...
depends:        mbcache,jbd2
vermagic:       5.15.0-91-generic SMP preempt mod_unload modversions

# 关键字段
# depends  - 依赖的其他模块
# vermagic - 模块的"魔数"（与内核版本必须匹配）
```

## 🔧 modprobe - 智能加载

```bash
# 自动处理依赖
sudo modprobe ext4

# 加参数
sudo modprobe thinkpad_acpi fan_control=1

# 临时禁加载（黑名单）
sudo modprobe -r usbcore
sudo modprobe -b usbcore        # 之后禁止自动加载

# 强制加载（覆盖版本检查）
sudo modprobe -f ext4.ko
```

## 🚫 黑名单（开机不加载）

```bash
# /etc/modprobe.d/blacklist.conf
blacklist nouveau              # 黑名单
blacklist nouveau              # 重复写以加强
install nouveau /bin/false     # 装=直接失败（更彻底）
install usb-storage /bin/true  # 装=直接成功但不做事

# 应用（不需要重启）
sudo modprobe -r nouveau
sudo modprobe nouveau            # 失败（被黑名单）

# 或
sudo update-initramfs -u        # 让 initramfs 也生效
sudo reboot
```

## 📂 模块位置

```
/lib/modules/$(uname -r)/kernel/
├── arch/                    # 架构特定
├── drivers/                 # 设备驱动
│   ├── net/                 # 网卡
│   ├── block/                # 块设备
│   ├── gpu/                  # GPU
│   └── ...
├── fs/                      # 文件系统
│   ├── ext4/
│   ├── xfs/
│   └── btrfs/
├── net/                     # 网络协议
└── sound/                   # 声卡
```

## 🪛 加载失败的常见原因

```bash
# 1. vermagic 不匹配（模块为其他内核编译的）
modinfo ext4 | grep vermagic    # 看 magic
uname -r                       # 当前内核
# 不匹配 → 重新编译对应内核的模块

# 2. 缺少依赖
sudo modprobe ext4
# modprobe: ERROR: could not insert 'ext4': Unknown symbol in module
# 看 dmesg
dmesg | tail -5
sudo depmod                     # 重新生成 dep
sudo modprobe ext4

# 3. 签名问题（Secure Boot / 内核 lockdown）
dmesg | grep "module verification"
# 关 Secure Boot 或用 kmod sign
```

## 🛠 实战：装新驱动

### 显卡驱动（NVIDIA）

```bash
# 1. 确认显卡
lspci | grep -i nvidia

# 2. 装 DKMS 工具
sudo apt install dkms build-essential

# 3. 装驱动
sudo apt install nvidia-driver-535

# 4. 验证
nvidia-smi
lsmod | grep nvidia
```

### DKMS（Dynamic Kernel Module Support）

驱动源码在**内核升级时自动重编译**：

```bash
ls /usr/src/
# nvidia-535.146.02  rtl8812au-5.13.6

# /usr/src/<module>/ 里有 DKMS 配置
ls /usr/src/nvidia-535.146.02/
# dkms.conf    Makefile
```

```bash
# 手动重编译（内核升级后）
sudo dkms status
sudo dkms build -m nvidia -v 535.146.02
sudo dkms install -m nvidia -v 535.146.02
```

## 🪵 加载参数（运行时调）

```bash
# 看当前模块参数
sudo modinfo -p ext4
# parm:           journal_checksum_bits
# parm:           nojumbfs

# 设参数（运行时）
sudo modprobe ext4 nojumbfs=1

# 或临时改已加载的
sudo sh -c 'echo 1 > /sys/module/ext4/parameters/nojumbfs'

# 永久（/etc/modprobe.d/ext4.conf）
options ext4 nojumbfs=1
```

## 🔧 编译自定义模块

```bash
# 装内核头
sudo apt install linux-headers-$(uname -r)

# 拿源码
git clone <module-repo>.git
cd module

# 编译
make -C /lib/modules/$(uname -r)/build M=$(pwd) modules

# 装到 /lib/modules
sudo make -C /lib/modules/$(uname -r)/build M=$(pwd) modules_install

# 更新 dep
sudo depmod

# 加载
sudo modprobe <module-name>
```

## 🩺 排查模块问题

```bash
# 看启动日志中失败
dmesg | grep -i "module\|firmware"

# 启动时模块失败 → blacklist + 重新生成 initramfs
sudo modprobe -b <module>
sudo update-initramfs -u

# /proc/modules 是真实的
cat /proc/modules | head

# /sys/module/<name>/ 是参数和状态
ls /sys/module/ext4/

# /sys/kernel/debug/ 调试信息（需要打开）
sudo mount -t debugfs debugfs /sys/kernel/debug
ls /sys/kernel/debug/
```

## 🆚 编译进内核 vs 模块

| | 模块（默认） | 编译进内核（CONFIG_Y=y） |
|--|------------|------------------------|
| 灵活性 | 高，可动态加 | 启动即用 |
| 启动时间 | 略慢（要 modprobe） | 略快 |
| 调试 | 容易替换 | 改完要重编内核 |

## 🔗 下一步

- [GRUB 引导](/14-kernel/grub)
- [initramfs](/14-kernel/initramfs)
- [sysctl 调参](/14-kernel/sysctl)

<!-- svg-injected:do-not-edit -->

## 图示：Linux Kernel 子系统全景

![Linux Kernel 子系统全景](/linux-kernel-arch.svg)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [devops](https://java-px.bot.cd/devops/):DevOps 自动化
- [cloud-native](https://java-px.bot.cd/cloud-native/):云原生
- [network](https://java-px.bot.cd/network/):Linux 网络
