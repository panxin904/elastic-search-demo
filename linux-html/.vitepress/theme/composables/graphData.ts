// linux-html graph data
// 节点分类：foundation / filesystem / text / process / user / package / network / firewall / storage / perf / shell / systemd / security / kernel

export const graphData = {
  nodes: [
    // 入门
    { name: 'Linux 是什么', category: 'foundation', link: '/01-foundation/intro', value: 5 },
    { name: '发行版选择', category: 'foundation', link: '/01-foundation/distros', value: 5 },
    { name: 'Shell 与终端', category: 'foundation', link: '/01-foundation/shell', value: 5 },
    { name: '文件系统树', category: 'foundation', link: '/01-foundation/fs-tree', value: 5 },

    // 文件与目录
    { name: 'ls / cp / mv', category: 'filesystem', link: '/02-filesystem/ls', value: 6 },
    { name: 'find 查找', category: 'filesystem', link: '/02-filesystem/find', value: 6 },
    { name: '软链与硬链', category: 'filesystem', link: '/02-filesystem/ln', value: 5 },
    { name: '权限 rwx', category: 'filesystem', link: '/02-filesystem/permissions', value: 6 },
    { name: '压缩归档', category: 'filesystem', link: '/02-filesystem/archive', value: 4 },

    // 文本处理
    { name: 'grep', category: 'text', link: '/03-text/grep', value: 7 },
    { name: 'awk', category: 'text', link: '/03-text/awk', value: 7 },
    { name: 'sed', category: 'text', link: '/03-text/sed', value: 7 },
    { name: 'sort / uniq', category: 'text', link: '/03-text/sort-uniq', value: 4 },
    { name: 'xargs', category: 'text', link: '/03-text/xargs', value: 5 },

    // 进程
    { name: 'ps / top / htop', category: 'process', link: '/04-process/ps-top', value: 7 },
    { name: '信号 (kill)', category: 'process', link: '/04-process/signals', value: 5 },
    { name: 'systemd', category: 'process', link: '/04-process/systemd', value: 6 },
    { name: 'cron 定时任务', category: 'process', link: '/04-process/cron', value: 5 },
    { name: '前台后台 jobs', category: 'process', link: '/04-process/jobs', value: 4 },

    // 用户与权限
    { name: '用户 / 用户组', category: 'user', link: '/05-user/users-groups', value: 5 },
    { name: 'chmod 权限', category: 'user', link: '/05-user/chmod', value: 6 },
    { name: 'chown / chgrp', category: 'user', link: '/05-user/chown', value: 5 },
    { name: 'sudo 提权', category: 'user', link: '/05-user/sudo', value: 6 },
    { name: 'ACL 细粒度', category: 'user', link: '/05-user/acl', value: 4 },

    // 软件包
    { name: 'apt', category: 'package', link: '/06-package/apt', value: 6 },
    { name: 'yum / dnf', category: 'package', link: '/06-package/yum-dnf', value: 5 },
    { name: '源码编译', category: 'package', link: '/06-package/source', value: 4 },
    { name: '容器化安装', category: 'package', link: '/06-package/container', value: 5 },

    // 网络
    { name: 'ip / ifconfig', category: 'network', link: '/07-network/ip', value: 5 },
    { name: 'ping / traceroute', category: 'network', link: '/07-network/ping', value: 4 },
    { name: 'curl / wget', category: 'network', link: '/07-network/curl', value: 5 },
    { name: 'DNS 解析', category: 'network', link: '/07-network/dns', value: 5 },
    { name: 'ss / netstat', category: 'network', link: '/07-network/ss', value: 5 },

    // 防火墙 / SSH
    { name: 'iptables', category: 'firewall', link: '/08-firewall-ssh/iptables', value: 6 },
    { name: 'ufw / firewalld', category: 'firewall', link: '/08-firewall-ssh/ufw-firewalld', value: 5 },
    { name: 'OpenSSH', category: 'firewall', link: '/08-firewall-ssh/openssh', value: 6 },
    { name: 'ssh-keygen', category: 'firewall', link: '/08-firewall-ssh/ssh-keys', value: 5 },
    { name: 'SSH 隧道', category: 'firewall', link: '/08-firewall-ssh/ssh-tunnel', value: 5 },

    // 存储
    { name: 'mount / umount', category: 'storage', link: '/09-storage/mount', value: 5 },
    { name: 'fstab', category: 'storage', link: '/09-storage/fstab', value: 5 },
    { name: 'LVM', category: 'storage', link: '/09-storage/lvm', value: 5 },
    { name: 'ext4 / xfs / btrfs', category: 'storage', link: '/09-storage/fs-types', value: 5 },
    { name: 'swap', category: 'storage', link: '/09-storage/swap', value: 4 },

    // 性能监控
    { name: 'top / htop', category: 'perf', link: '/10-perf/top-htop', value: 6 },
    { name: 'vmstat / mpstat', category: 'perf', link: '/10-perf/vmstat', value: 5 },
    { name: 'iostat / iotop', category: 'perf', link: '/10-perf/iostat', value: 5 },
    { name: 'sar', category: 'perf', link: '/10-perf/sar', value: 5 },
    { name: 'perf / strace', category: 'perf', link: '/10-perf/perf-strace', value: 6 },

    // Shell 脚本
    { name: 'bash 基础语法', category: 'shell', link: '/11-shell/bash-syntax', value: 5 },
    { name: '变量与参数', category: 'shell', link: '/11-shell/variables', value: 5 },
    { name: '数组与字符串', category: 'shell', link: '/11-shell/arrays', value: 4 },
    { name: '函数与组织', category: 'shell', link: '/11-shell/functions', value: 5 },
    { name: '调试与陷阱', category: 'shell', link: '/11-shell/debug', value: 5 },

    // systemd
    { name: 'systemctl', category: 'systemd', link: '/12-systemd/systemctl', value: 6 },
    { name: 'Unit 文件', category: 'systemd', link: '/12-systemd/unit', value: 5 },
    { name: 'journald', category: 'systemd', link: '/12-systemd/journald', value: 5 },
    { name: 'Timer', category: 'systemd', link: '/12-systemd/timer', value: 4 },

    // 安全加固
    { name: 'SELinux', category: 'security', link: '/13-security/selinux', value: 6 },
    { name: 'AppArmor', category: 'security', link: '/13-security/apparmor', value: 4 },
    { name: 'sshd_config 加固', category: 'security', link: '/13-security/sshd-config', value: 5 },
    { name: 'auditd', category: 'security', link: '/13-security/auditd', value: 5 },
    { name: 'lynis 合规', category: 'security', link: '/13-security/lynis', value: 4 },

    // 内核
    { name: 'GRUB 引导', category: 'kernel', link: '/14-kernel/grub', value: 4 },
    { name: 'initramfs', category: 'kernel', link: '/14-kernel/initramfs', value: 4 },
    { name: '内核模块', category: 'kernel', link: '/14-kernel/modules', value: 5 },
    { name: 'sysctl', category: 'kernel', link: '/14-kernel/sysctl', value: 6 }
  ],

  links: [
    // 入门 → 文件
    { source: 'Linux 是什么', target: '文件系统树' },
    { source: 'Linux 是什么', target: 'Shell 与终端' },
    { source: 'Shell 与终端', target: 'grep' },
    { source: 'Shell 与终端', target: 'awk' },

    // 文件 → 文本
    { source: '文件系统树', target: 'ls / cp / mv' },
    { source: 'ls / cp / mv', target: 'find 查找' },
    { source: 'find 查找', target: 'grep' },
    { source: 'find 查找', target: 'xargs' },
    { source: 'ls / cp / mv', target: '权限 rwx' },
    { source: '权限 rwx', target: 'chmod 权限' },

    // 文本 → 进程 / 脚本
    { source: 'grep', target: 'awk' },
    { source: 'awk', target: 'sed' },
    { source: 'grep', target: 'sort / uniq' },
    { source: 'awk', target: 'bash 基础语法' },
    { source: 'sed', target: 'bash 基础语法' },
    { source: 'xargs', target: 'bash 基础语法' },

    // 文件 → 用户
    { source: 'ls / cp / mv', target: '用户 / 用户组' },
    { source: '权限 rwx', target: 'chown / chgrp' },
    { source: '用户 / 用户组', target: 'sudo 提权' },
    { source: 'chmod 权限', target: 'ACL 细粒度' },

    // 用户 → 安全
    { source: 'sudo 提权', target: 'sshd_config 加固' },
    { source: '用户 / 用户组', target: 'auditd' },

    // 进程
    { source: 'Shell 与终端', target: 'ps / top / htop' },
    { source: 'ps / top / htop', target: '信号 (kill)' },
    { source: '信号 (kill)', target: 'systemd' },
    { source: 'systemd', target: 'cron 定时任务' },
    { source: '前台后台 jobs', target: 'bash 基础语法' },

    // systemd
    { source: 'systemd', target: 'systemctl' },
    { source: 'systemctl', target: 'Unit 文件' },
    { source: 'Unit 文件', target: 'journald' },
    { source: 'Unit 文件', target: 'Timer' },
    { source: 'Timer', target: 'cron 定时任务' },

    // 软件包
    { source: '发行版选择', target: 'apt' },
    { source: '发行版选择', target: 'yum / dnf' },
    { source: 'apt', target: '源码编译' },
    { source: 'yum / dnf', target: '源码编译' },
    { source: '源码编译', target: '容器化安装' },

    // 网络
    { source: 'Shell 与终端', target: 'ip / ifconfig' },
    { source: 'ip / ifconfig', target: 'ping / traceroute' },
    { source: 'ip / ifconfig', target: 'ss / netstat' },
    { source: 'ip / ifconfig', target: 'DNS 解析' },
    { source: 'curl / wget', target: 'DNS 解析' },

    // 防火墙 / SSH
    { source: 'ip / ifconfig', target: 'iptables' },
    { source: 'iptables', target: 'ufw / firewalld' },
    { source: 'sshd_config 加固', target: 'iptables' },
    { source: 'OpenSSH', target: 'ssh-keygen' },
    { source: 'ssh-keygen', target: 'SSH 隧道' },
    { source: 'OpenSSH', target: 'sshd_config 加固' },

    // 存储
    { source: 'Linux 是什么', target: 'mount / umount' },
    { source: 'mount / umount', target: 'fstab' },
    { source: 'fstab', target: 'LVM' },
    { source: 'LVM', target: 'ext4 / xfs / btrfs' },
    { source: 'ext4 / xfs / btrfs', target: 'swap' },

    // 性能
    { source: 'ps / top / htop', target: 'top / htop' },
    { source: 'top / htop', target: 'vmstat / mpstat' },
    { source: 'top / htop', target: 'iostat / iotop' },
    { source: 'iostat / iotop', target: 'sar' },
    { source: 'sar', target: 'perf / strace' },

    // 安全加固
    { source: 'iptables', target: 'SELinux' },
    { source: 'iptables', target: 'AppArmor' },
    { source: 'SSH 隧道', target: 'SELinux' },
    { source: 'sshd_config 加固', target: 'auditd' },
    { source: 'auditd', target: 'lynis 合规' },

    // 内核
    { source: 'Linux 是什么', target: 'GRUB 引导' },
    { source: 'GRUB 引导', target: 'initramfs' },
    { source: 'GRUB 引导', target: '内核模块' },
    { source: '内核模块', target: 'sysctl' },
    { source: 'sysctl', target: 'vmstat / mpstat' },

    // 脚本 → 网络
    { source: 'bash 基础语法', target: 'curl / wget' },
    { source: '变量与参数', target: 'curl / wget' },

    // 用户 → systemd
    { source: '用户 / 用户组', target: 'systemctl' },

    // cron → 定时任务
    { source: 'cron 定时任务', target: 'Timer' },

    // 系统状态
    { source: 'journald', target: 'auditd' },
    { source: 'journald', target: 'sar' }
  ]
}