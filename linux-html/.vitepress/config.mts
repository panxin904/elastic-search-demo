import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'
import { fileURLToPath, URL } from 'node:url'

// P0: VitePress/rollup 默认 fs.allow 限制 cwd 外 import。用 vite alias 解决相对路径。
const SHARED_ASSETS = fileURLToPath(new URL('../../shared-assets', import.meta.url))

export default withMermaid(defineConfig({
  vite: {
    resolve: {
      alias: [
        { find: '@shared', replacement: SHARED_ASSETS },
      ],
    },
  },
    mermaid: {
    theme: 'default'
  },
  base: '/linux/',
  title: 'Linux 服务器 知识图谱',
  description: '系统化学习 Linux 服务器与常用命令 - 知识图谱、思维导图、命令速查',
  lang: 'zh-CN',
  lastUpdated: true,
  srcDir: 'docs',
  cleanUrls: true,
  head: [
    ['link', { rel: 'apple-touch-icon', href: '/apple-touch-icon.png', sizes: '180x180' }],
    ['link', { rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' }],
    ['link', { rel: 'icon', href: '/favicon.ico', type: 'image/x-icon' }],
    ['meta', { name: 'theme-color', content: '#f97316' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:locale', content: 'zh_CN' }]  ],
  themeConfig: {
    siteTitle: 'Linux 服务器',
    nav: [

      { text: '🏠 门户', link: 'https://java-px.bot.cd/', target: '_blank' },
{ text: '首页', link: '/' },
      { text: '知识图谱', link: '/graph' },
      { text: '思维导图', link: '/mindmap' },
      { text: '命令速查', link: '/cheatsheet' },
      { text: '学习路径', link: '/path' },
      {
        text: '更多站点',
        items: [
        { text: 'AI 工具 / 大模型', link: 'https://java-px.bot.cd/ai/' },
        { text: '企业级架构', link: 'https://java-px.bot.cd/architecture/' },
        { text: '大数据', link: 'https://java-px.bot.cd/bigdata/' },
        { text: '云原生 / Docker / K8s', link: 'https://java-px.bot.cd/cloud-native/' },
        { text: 'ElasticSearch', link: 'https://java-px.bot.cd/es/' },
        { text: '前端 & Node', link: 'https://java-px.bot.cd/frontend/' },
        { text: 'Java 语言', link: 'https://java-px.bot.cd/java-language/' },
        { text: 'Java Web 开发', link: 'https://java-px.bot.cd/java/' },
        { text: 'Kafka', link: 'https://java-px.bot.cd/kafka/' },
        { text: 'MySQL', link: 'https://java-px.bot.cd/mysql/' },
        { text: 'Python', link: 'https://java-px.bot.cd/python/' },
        { text: 'Redis', link: 'https://java-px.bot.cd/redis/' },
        { text: '微服务 / Spring Cloud', link: 'https://java-px.bot.cd/cloud/' },
        { text: '计算机网络', link: 'https://java-px.bot.cd/network/' },
        { text: '文件系统与存储', link: 'https://java-px.bot.cd/filesystem/' },
        { text: '在线工具', link: 'https://java-px.bot.cd/tools/' },
        { text: '视频处理', link: 'https://java-px.bot.cd/video/' }
      ]
      }
    ],
    sidebar: {
      '/': [
        { text: '🎯 开始', items: [{ text: '📖 学习路径', link: '/path' }] },
        {
          text: '🌐 入门基础',
          items: [
            { text: 'Linux 是什么', link: '/01-foundation/intro' },
            { text: '发行版选择', link: '/01-foundation/distros' },
            { text: 'Shell 与终端', link: '/01-foundation/shell' },
            { text: '文件系统树', link: '/01-foundation/fs-tree' }
          ]
        },
        {
          text: '📁 文件与目录',
          items: [
            { text: 'ls / cp / mv', link: '/02-filesystem/ls' },
            { text: 'find 查找', link: '/02-filesystem/find' },
            { text: '软链与硬链', link: '/02-filesystem/ln' },
            { text: '权限 (rwx)', link: '/02-filesystem/permissions' },
            { text: '压缩与归档', link: '/02-filesystem/archive' }
          ]
        },
        {
          text: '📦 文本处理三剑客',
          items: [
            { text: 'grep', link: '/03-text/grep' },
            { text: 'awk', link: '/03-text/awk' },
            { text: 'sed', link: '/03-text/sed' },
            { text: 'sort / uniq', link: '/03-text/sort-uniq' },
            { text: 'xargs', link: '/03-text/xargs' }
          ]
        },
        {
          text: '⚙️ 进程与任务',
          items: [
            { text: 'ps / top / htop', link: '/04-process/ps-top' },
            { text: '信号 (kill)', link: '/04-process/signals' },
            { text: 'systemd', link: '/04-process/systemd' },
            { text: 'cron 定时任务', link: '/04-process/cron' },
            { text: '前台后台 (jobs)', link: '/04-process/jobs' }
          ]
        },
        {
          text: '🛠️ 用户与权限',
          items: [
            { text: '用户 / 用户组', link: '/05-user/users-groups' },
            { text: 'chmod 权限', link: '/05-user/chmod' },
            { text: 'chown / chgrp', link: '/05-user/chown' },
            { text: 'sudo 提权', link: '/05-user/sudo' },
            { text: 'ACL 细粒度权限', link: '/05-user/acl' }
          ]
        },
        {
          text: '📦 软件与包管理',
          items: [
            { text: 'apt (Debian/Ubuntu)', link: '/06-package/apt' },
            { text: 'yum / dnf (RHEL)', link: '/06-package/yum-dnf' },
            { text: '源码编译', link: '/06-package/source' },
            { text: '容器化安装', link: '/06-package/container' }
          ]
        },
        {
          text: '🌐 网络',
          items: [
            { text: 'ip / ifconfig', link: '/07-network/ip' },
            { text: 'ping / traceroute', link: '/07-network/ping' },
            { text: 'curl / wget', link: '/07-network/curl' },
            { text: 'DNS 解析', link: '/07-network/dns' },
            { text: 'ss / netstat', link: '/07-network/ss' }
          ]
        },
        {
          text: '🔥 防火墙 / SSH',
          items: [
            { text: 'iptables', link: '/08-firewall-ssh/iptables' },
            { text: 'ufw / firewalld', link: '/08-firewall-ssh/ufw-firewalld' },
            { text: 'OpenSSH 配置', link: '/08-firewall-ssh/openssh' },
            { text: 'ssh-keygen / ssh-copy-id', link: '/08-firewall-ssh/ssh-keys' },
            { text: 'SSH 隧道 / 代理', link: '/08-firewall-ssh/ssh-tunnel' }
          ]
        },
        {
          text: '🗄️ 存储',
          items: [
            { text: 'mount / umount', link: '/09-storage/mount' },
            { text: 'fstab 自动挂载', link: '/09-storage/fstab' },
            { text: 'LVM 逻辑卷', link: '/09-storage/lvm' },
            { text: 'ext4 / xfs / btrfs', link: '/09-storage/fs-types' },
            { text: 'swap 交换分区', link: '/09-storage/swap' }
          ]
        },
        {
          text: '⚡ 性能监控',
          items: [
            { text: 'top / htop', link: '/10-perf/top-htop' },
            { text: 'vmstat / mpstat', link: '/10-perf/vmstat' },
            { text: 'iostat / iotop', link: '/10-perf/iostat' },
            { text: 'sar 持续监控', link: '/10-perf/sar' },
            { text: 'perf / strace', link: '/10-perf/perf-strace' }
          ]
        },
        {
          text: '📜 Shell 脚本',
          items: [
            { text: 'bash 基础语法', link: '/11-shell/bash-syntax' },
            { text: '变量与参数', link: '/11-shell/variables' },
            { text: '数组与字符串', link: '/11-shell/arrays' },
            { text: '函数与脚本组织', link: '/11-shell/functions' },
            { text: '调试与陷阱', link: '/11-shell/debug' }
          ]
        },
        {
          text: '🛠️ systemd 服务',
          items: [
            { text: 'systemctl 命令', link: '/12-systemd/systemctl' },
            { text: 'Unit 文件', link: '/12-systemd/unit' },
            { text: 'journald 日志', link: '/12-systemd/journald' },
            { text: 'systemd Timer', link: '/12-systemd/timer' }
          ]
        },
        {
          text: '🔒 安全加固',
          items: [
            { text: 'SELinux', link: '/13-security/selinux' },
            { text: 'AppArmor', link: '/13-security/apparmor' },
            { text: 'sshd_config 加固', link: '/13-security/sshd-config' },
            { text: 'auditd 审计', link: '/13-security/auditd' },
            { text: '合规检查 (lynis)', link: '/13-security/lynis' }
          ]
        },
        {
          text: '🏗️ 内核与启动',
          items: [
            { text: 'GRUB 引导', link: '/14-kernel/grub' },
            { text: 'initramfs', link: '/14-kernel/initramfs' },
            { text: '内核模块', link: '/14-kernel/modules' },
            { text: 'sysctl 调参', link: '/14-kernel/sysctl' }
          ]
        }
      ],
      '/graph': [{ text: '🌐 知识图谱', items: [{ text: '全局知识图谱', link: '/graph' }] }],
      '/mindmap': [{ text: '🧭 思维导图', items: [{ text: 'Linux 思维导图', link: '/mindmap' }] }],
      '/cheatsheet': [{ text: '📋 命令速查', items: [{ text: '高频命令速查', link: '/cheatsheet' }] }],
      '/path': [{ text: '🎯 学习路径', items: [{ text: 'Linux 学习路径', link: '/path' }] }]
    },
    socialLinks: [{ icon: 'github', link: 'https://github.com' }],
    footer: {
      message: 'Linux 服务器 - 系统化学习 Linux 命令与运维 · 🏠 <a href="https://java-px.bot.cd/" target="_blank">门户首页</a>',
      copyright: 'MIT License'
    },
    outline: { level: [2, 3], label: '页面大纲' },
    docFooter: { prev: '上一篇', next: '下一篇' },

    search: { provider: 'local' },
  }
}))
