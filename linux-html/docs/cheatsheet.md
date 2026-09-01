---
title: 命令速查
date: 2026-08-15  # date-auto-injected
---

# 📋 Linux 高频命令速查

> 30+ 高频命令，分组速查。每条带常用示例，可以直接复制运行。

## 🗂️ 文件与目录

```bash
# 查看
ls -lah                    # 详细列表 + 人类可读大小
ls -lt                     # 按时间排序
ls -lS                     # 按大小排序
pwd                        # 当前路径

# 切换
cd -                       # 回到上一次目录
cd ~                       # HOME
cd ~user                   # user 的 HOME

# 创建
mkdir -p a/b/c             # 递归创建
touch file.txt             # 创建空文件 / 更新时间戳

# 复制 / 移动 / 删除
cp -r src/ dst/            # 递归复制
mv old new                 # 改名 / 移动
rm -rf dir                 # 递归强制删除（慎用）
shred -n 3 -z file         # 安全删除（覆写）

# 查看
cat file                   # 全部打印
less file                  # 分页浏览（q 退出）
head -n 20 file            # 前 20 行
tail -n 50 -f log          # 末尾 50 行 + 跟踪
```

## 🔍 查找

```bash
find . -name '*.log'                  # 按名
find . -type f -size +100M           # 大于 100MB
find . -mtime -7                       # 7 天内修改
find / -user alice                    # 按用户
find . -name '*.tmp' -delete           # 找并删
find . -name '*.js' -exec wc -l {} +  # 对结果执行命令
which node                            # 查可执行路径
locate nginx.conf                     # 走 updatedb
```

## 🔤 grep / 文本

```bash
grep -rn 'TODO' src/                  # 递归 + 行号
grep -E 'err|warn' log                # 扩展正则
grep -v '^$' file                    # 反选（去掉空行）
grep -A2 -B2 'error' log             # 上下文前后 2 行

sort file | uniq -c | sort -rn        # 出现次数倒序
sed -i 's/old/new/g' file             # 全局替换
sed -n '1,10p' file                   # 打印 1-10 行
awk -F: '$3==0 {print $1}' /etc/passwd  # 打印 root 用户
awk '{sum+=$1} END {print sum}' f      # 求和
xargs -I {} cp {} /backup/            # 把 stdin 当参数
```

## ⚙️ 进程与系统

```bash
ps aux | grep nginx              # 找进程
ps -ef --forest                  # 进程树
top -p <pid>                      # 监控某个 PID
htop                              # 更友好的 top（需装）
kill -15 <pid>                    # 优雅退出（SIGTERM）
kill -9 <pid>                     # 强制（SIGKILL）
pkill -f 'node app.js'            # 按命令名杀
pgrep -f 'sshd'                   # 查 PID

systemctl status nginx           # 服务状态
systemctl restart nginx          # 重启
systemctl enable nginx           # 开机启动
journalctl -u nginx -f            # 服务日志
```

## 📅 定时任务

```bash
crontab -e                        # 编辑当前用户
crontab -l                        # 列出

# 格式: 分 时 日 月 周 命令
0 2 * * * /opt/backup.sh          # 每天 02:00
*/5 * * * * /opt/check.sh         # 每 5 分钟
0 9 * * 1-5 /opt/work.sh          # 工作日 09:00
```

## 🌐 网络

```bash
ip a                              # 查看 IP（替代 ifconfig）
ip r                              # 路由表
ip link                           # 网卡

ping -c 4 host                    # 4 次后停
traceroute host                   # 路由追踪
mtr host                          # 持续追踪

curl -I https://example.com      # 仅 headers
curl -X POST -d 'a=1' url          # POST
curl -L -o file url               # 跟随 302 下载

nslookup domain                   # DNS 查询
dig domain                        # 详细 DNS
ss -tulnp                         # 监听端口
nc -zv host 80                    # 探测端口
tcpdump -i eth0 port 80           # 抓包
```

## 📁 权限 / 用户

```bash
chmod 644 file                    # rw-r--r--
chmod 755 dir                     # rwxr-xr-x
chmod +x script.sh                # 加执行位
chown user:group file             # 改属主
chown -R user dir                 # 递归

sudo -i                           # 切 root（保持环境）
sudo -u alice cmd                 # 以 alice 身份跑
visudo                            # 安全编辑 sudoers
```

## 🗜 磁盘 / 存储

```bash
df -h                             # 磁盘使用
du -sh dir                        # 目录大小
du -h --max-depth=1 /             # 1 层深度
lsblk                             # 列出块设备

mount /dev/sdb1 /mnt              # 挂载
umount /mnt                       # 卸载

df -i                             # inode 使用
```

## ⚡ 性能排查

```bash
top                               # 实时
htop                              # 改进版
iostat -xm 2 5                    # 磁盘 IO
vmstat 2 5                        # 内存 / CPU / IO
sar -u 2 5                        # CPU 历史
sar -r 2 5                        # 内存历史
free -h                           # 内存概览

strace -p <pid>                   # 跟踪 syscalls
strace -e openat cmd              # 只看 open 类调用
lsof -p <pid>                     # 进程打开的文件
lsof -i :80                       # 谁占用 80
```

## 📜 文本工具

```bash
less +F file                      # 实时跟踪（类 tail -f）
sed -i.bak 's/a/b/' file          # 改之前备份
diff -u a b                       # unified diff
patch < file.patch                # 应用 patch

xargs                             # 把 stdin 转参数
xargs -n1                         # 一次一个
xargs -0                          # 用 null 分隔（防空格）
```

## 🔥 防火墙

```bash
# iptables（内核级）
iptables -L -n                    # 列出
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -j DROP          # 默认拒绝

# ufw（Ubuntu）
ufw status
ufw allow 22/tcp
ufw enable

# firewalld（RHEL）
firewall-cmd --list-all
firewall-cmd --add-port=80/tcp --permanent
firewall-cmd --reload
```

## 🛠 systemd 服务管理

```bash
systemctl status nginx            # 状态
systemctl restart nginx           # 重启
systemctl stop nginx              # 停
systemctl start nginx             # 启
systemctl enable nginx            # 开机启动
systemctl disable nginx           # 取消开机启动
systemctl daemon-reload           # 重读 unit
systemctl list-unit-files         # 列出所有 unit
systemctl list-units --type=service --state=running   # 运行中的服务
```

## 🔒 SSH 速查

```bash
ssh user@host                     # 登录
ssh -p 2222 user@host             # 自定义端口
ssh -L 8080:remote:80 host        # 本地端口转发
ssh -D 1080 host                  # SOCKS 代理

ssh-keygen -t ed25519             # 生成密钥
ssh-copy-id user@host             # 上传公钥
ssh -i ~/.ssh/key user@host       # 指定密钥

scp file user@host:/dest          # 上传
scp -r dir user@host:/dest        # 目录
rsync -avz dir/ user@host:/dest/  # 增量同步
```

## 📜 Shell 脚本片段

```bash
#!/usr/bin/env bash
set -euo pipefail              # 严格模式

# 遍历文件
for f in *.txt; do
  echo "处理 $f"
done

# 读 stdin
while IFS= read -r line; do
  echo "$line"
done

# 函数
log() { printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*"; }

# 判文件
[ -f "$1" ] && echo "是文件"
[ -d "$1" ] && echo "是目录"

# 错误退出
command || { echo "失败"; exit 1; }
```

## 🔗 下一步

- [入门基础](/01-foundation/intro) — 理解 Linux 全貌
- [文件与目录](/02-filesystem/ls) — 高频命令详解
- [学习路径](/path) — 系统化学习路线


## 📱 手机扫码继续阅读

<ClientOnly>
  <QrShare />
</ClientOnly>
