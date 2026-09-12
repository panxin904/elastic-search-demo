---
title: GRUB 引导
date: 2026-08-15  # date-auto-injected
---

# GRUB 引导加载
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600">Linux GRUB 启动顺序</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">BIOS/UEFI → GRUB → Kernel → init → 用户态</text>

  <!-- 6 阶段启动 -->
  <g>
    <text x="50" y="90" font-size="13" font-weight="700" fill="#1e293b">① Linux 启动 6 大阶段</text>

    <rect class="at-hover-card" x="40" y="105" width="80" height="55" rx="6" fill="#1e293b"/>
    <text x="80" y="125" text-anchor="middle" font-size="10" font-weight="700" fill="#10b981">1. 上电</text>
    <text x="80" y="143" text-anchor="middle" font-size="9" fill="#10b981">POST 自检</text>

    <path d="M120,133 L145,133" stroke="#64748b" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="145" y="105" width="90" height="55" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
    <text x="190" y="125" text-anchor="middle" font-size="10" font-weight="700" fill="#1e40af">2. BIOS/UEFI</text>
    <text x="190" y="143" text-anchor="middle" font-size="9" fill="#3b82f6">找启动盘</text>

    <path d="M235,133 L260,133" stroke="#64748b" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="260" y="105" width="100" height="55" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
    <text x="310" y="125" text-anchor="middle" font-size="10" font-weight="700" fill="#047857">3. GRUB</text>
    <text x="310" y="143" text-anchor="middle" font-size="9" fill="#10b981">选内核</text>

    <path d="M360,133 L385,133" stroke="#64748b" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="385" y="105" width="100" height="55" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="435" y="125" text-anchor="middle" font-size="10" font-weight="700" fill="#92400e">4. Kernel</text>
    <text x="435" y="143" text-anchor="middle" font-size="9" fill="#f59e0b">加载驱动</text>

    <path d="M485,133 L510,133" stroke="#64748b" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="510" y="105" width="50" height="55" rx="6" fill="#ede9fe" stroke="#8b5cf6" stroke-width="1.5"/>
    <text x="535" y="125" text-anchor="middle" font-size="10" font-weight="700" fill="#5b21b6">5. init</text>
    <text x="535" y="148" text-anchor="middle" font-size="8" fill="#8b5cf6">PID 1</text>

    <path d="M535,160 L535,180" stroke="#64748b" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="510" y="180" width="50" height="40" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
    <text x="535" y="203" text-anchor="middle" font-size="10" font-weight="700" fill="#047857">6. shell</text>
  </g>

  <!-- GRUB 阶段详解 -->
  <g>
    <text x="50" y="245" font-size="13" font-weight="700" fill="#1e293b">② GRUB 三阶段详解</text>

    <rect class="at-hover-card" x="40" y="255" width="160" height="100" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
    <text x="120" y="277" text-anchor="middle" font-size="11" font-weight="700" fill="#047857">Stage 1</text>
    <text x="120" y="297" text-anchor="middle" font-size="9" fill="#475569">MBR / GPT 前 446B</text>
    <text x="55" y="318" font-size="9" fill="#475569">· 引导到 Stage 1.5</text>
    <text x="55" y="334" font-size="9" fill="#475569">· 加载基本 FS 驱动</text>
    <text x="120" y="350" text-anchor="middle" font-size="9" fill="#10b981">极小空间</text>

    <rect class="at-hover-card" x="210" y="255" width="160" height="100" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="290" y="277" text-anchor="middle" font-size="11" font-weight="700" fill="#92400e">Stage 1.5</text>
    <text x="290" y="297" text-anchor="middle" font-size="9" fill="#475569">MBR 后 32KB</text>
    <text x="225" y="318" font-size="9" fill="#475569">· 识别 ext4/xfs FS</text>
    <text x="225" y="334" font-size="9" fill="#475569">· 加载 Stage 2 文件</text>
    <text x="290" y="350" text-anchor="middle" font-size="9" fill="#f59e0b">一般不可见</text>

    <rect class="at-hover-card" x="380" y="255" width="180" height="100" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
    <text x="470" y="277" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">Stage 2</text>
    <text x="470" y="297" text-anchor="middle" font-size="9" fill="#475569">/boot/grub/ 目录</text>
    <text x="395" y="318" font-size="9" fill="#475569">· 显示菜单 / 加载配置</text>
    <text x="395" y="334" font-size="9" fill="#475569">· 加载内核 + initramfs</text>
    <text x="470" y="350" text-anchor="middle" font-size="9" fill="#3b82f6">grub2-mkconfig 配置</text>
  </g>

  <!-- Init 阶段 -->
  <g>
    <text x="50" y="385" font-size="13" font-weight="700" fill="#1e293b">③ Init 阶段（PID 1）</text>

    <rect class="at-hover-card" x="40" y="395" width="510" height="60" rx="6" fill="#1e293b" stroke="#1e293b" stroke-width="1"/>
    <text x="55" y="418" font-size="10" font-weight="700" fill="#10b981">kernel 启动 init → 现代 Linux 默认 systemd</text>
    <text x="55" y="435" font-size="10" fill="#e2e8f0" font-family="monospace">systemd 启动 unit 链：local-fs.target → network.target → multi-user.target</text>
    <text x="55" y="452" font-size="9" fill="#94a3b8">查看启动耗时：systemd-analyze · 关键路径：systemd-analyze critical-chain</text>
  </g>
</svg>


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

<ClientOnly>
  <GiscusComment />
</ClientOnly>

<!-- giscus-injected:do-not-edit -->
