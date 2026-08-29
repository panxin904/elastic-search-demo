---
title: swap 交换分区
---

# swap 交换分区

> Linux "虚拟内存"：把磁盘当内存用。**慢但救命**。

## 🤔 swap 在干嘛

内存不够时，kernel 把不活跃的内存页换到 swap（磁盘）上。

```
            ┌──────────┐
            │   RAM    │  ← 快
            │  (内存)  │
            └──────────┘
                ↕ 页面交换
            ┌──────────┐
            │  swap   │  ← 慢（但容量大）
            │ (磁盘)  │
            └──────────┘
```

何时用 swap：
- 内存不足（OOM 杀手介入前的缓冲）
- 休眠（hibernate）需要写入 swap
- 大内存但程序有小 bug 内存泄漏

## 📊 要不要 / 要多大？

老经验（2010s）：
```
RAM < 2GB:   swap = 2×RAM
2-8GB:       swap = RAM
8-64GB:      swap = 4-8GB（够用）
> 64GB:      swap = 4-8GB 或不要
```

现代（2020s+）：
- 服务器 **不需要 swap**（足够内存 + OOM killer）
- 桌面 **需要 swap**（休眠需要）
- 云主机看工作负载

## 🔍 看现有 swap

```bash
free -h                          # 看 swap 大小
swapon --show                    # 看哪个设备
swapon -s                        # 旧式（cat /proc/swaps）
cat /proc/swaps

# 看 swap 活动
vmstat 1 5                       # si / so 列就是 swap in / out
```

## ➕ 加 swap 文件（推荐）

不需要重新分区，文件系统任意位置都行。

```bash
# 1. 创建文件
sudo fallocate -l 4G /swapfile     # 快速创建（不实际写 4G）
# 或
sudo dd if=/dev/zero of=/swapfile bs=1M count=4096

# 2. 限权
sudo chmod 600 /swapfile

# 3. 格式化为 swap
sudo mkswap /swapfile

# 4. 启用
sudo swapon /swapfile

# 5. 永久（fstab）
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 6. 验证
free -h
swapon --show
```

## ➕ 加 swap 分区

```bash
# 创建专用分区
sudo fdisk /dev/sdc
# n → p → 1 → 回车 → +4G → t → 82 (Linux swap)

sudo mkswap /dev/sdc1
sudo swapon /dev/sdc1

# fstab
UUID=xxx none swap sw 0 0 | sudo tee -a /etc/fstab
```

## 🛠 管理

```bash
# 禁用
sudo swapoff /swapfile
sudo swapoff /dev/sdc1

# 优先级（多个 swap 时）
sudo swapon -p 10 /swapfile1       # 优先级 0-32767，越高越优先
sudo swapon -p 5 /swapfile2

# /etc/fstab
/swapfile1 none swap sw,pri=10 0 0
/swapfile2 none swap sw,pri=5  0 0
```

## 🎛 swappiness - swap 倾向

```
sysctl vm.swappiness
```

- 0-100（Linux 5.8+ 范围改为 0-200）
- **默认 60** — 中等偏好
- 0 = 几乎不用 swap（直到内存压力极大）
- 100 = 积极用 swap

```bash
# 临时
sudo sysctl vm.swappiness=10

# 永久
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

**经验**：
- 数据库服务器：`vm.swappiness=1` 或 `10`（避免 swap 让响应变慢）
- 桌面：默认值 `60`
- 内存告急的机器：可以提高

## 🧹 监控 / 性能

```bash
# 看 swap IO
iostat -x 1                # 看 sda / dm-X 的 await

# 大压力：swap 用满
# 意味着真实内存不够（物理加内存 / 限制进程 / 优化程序）

# 找谁在用 swap（按进程）
for f in /proc/*/smaps; do
  pid=$(echo $f | cut -d/ -f3)
  if [ -r "$f" ]; then
    swap=$(grep '^Swap:' "$f" 2>/dev/null | awk '{sum+=$2} END {print sum}')
    [ "$swap" -gt 0 ] && echo "PID $pid: ${swap} KB"
  fi
done | sort -k2 -n -r | head
```

## 🩺 故障

```bash
# "swapon failed: Device or resource busy"
# 已经在用了。先 swapoff

# "fallocate failed"
# 文件系统不支持 fallocate（如 xfs 在某些版本）
sudo dd if=/dev/zero of=/swapfile bs=1M count=4096

# "swap 不够用"
# 加 swap：swapon 更多文件
# 或调 vm.swappiness 让其更积极使用
sudo sysctl vm.swappiness=80

# 紧急：禁用 swap（不要给 OOM killer 兜底）
sudo swapoff -a
```

## 🎯 实战

### 数据库服务器 swap 策略

```bash
# 数据库：低 swap 倾向
echo 'vm.swappiness=1' | sudo tee -a /etc/sysctl.conf

# 预留 4G（避免 OOM）
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 桌面休眠

```bash
# 休眠需要 swap >= RAM
# 16GB RAM → swap 至少 16GB
sudo fallocate -l 16G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 测试休眠
sudo systemctl hibernate
```

### 关闭 swap（容器 / 云主机）

```bash
# Kubernetes / Docker 节点
sudo swapoff -a
# 注释 /etc/fstab 中的 swap 行
```

## 🔗 下一步

- [mount / umount](/09-storage/mount)
- [LVM 逻辑卷](/09-storage/lvm)
- [内核模块](/14-kernel/modules)


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [devops](https://java-px.bot.cd/devops/):DevOps 自动化
- [cloud-native](https://java-px.bot.cd/cloud-native/):云原生
- [network](https://java-px.bot.cd/network/):Linux 网络
