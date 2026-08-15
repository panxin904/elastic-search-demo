import { defineConfig } from 'vitepress'

export default defineConfig({
  base: '/filesystem/',
  title: '文件系统 / 文件服务 / 存储全栈 知识图谱',
  description: '系统化学习文件系统 - 本地盘 FS / 分布式 FS / 对象存储 / 网络协议 / 云原生存储 / 容器 FS / 性能调优 / 安全 / 备份 - 13 大类 · 76 节点 · 70+ 内容页',
  lang: 'zh-CN',
  lastUpdated: true,
  srcDir: 'docs',
  cleanUrls: false,
  ignoreDeadLinks: true,
  head: [
    ['link', { rel: 'apple-touch-icon', href: '/apple-touch-icon.png', sizes: '180x180' }],
    ['link', { rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' }],
    ['link', { rel: 'icon', href: '/favicon.ico', type: 'image/x-icon' }],
    ['meta', { name: 'theme-color', content: '#0f766e' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:locale', content: 'zh_CN' }]  ],
  themeConfig: {
    siteTitle: '文件全栈',
    nav: [
      
      { text: '🏠 门户', link: 'https://java-px.bot.cd/', target: '_blank' },
{ text: '首页', link: '/' },
      { text: '知识图谱', link: '/graph' },
      { text: '思维导图', link: '/mindmap' },
      { text: '学习路径', link: '/path' },
      { text: '速记卡', link: '/cheatsheet' },
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
          { text: 'Linux 服务器', link: 'https://java-px.bot.cd/linux/' },
          { text: 'MySQL', link: 'https://java-px.bot.cd/mysql/' },
          { text: 'Python', link: 'https://java-px.bot.cd/python/' },
          { text: 'Redis', link: 'https://java-px.bot.cd/redis/' },
          { text: '微服务 / Spring Cloud', link: 'https://java-px.bot.cd/cloud/' },
          { text: '计算机网络', link: 'https://java-px.bot.cd/network/' },
          { text: '在线工具', link: 'https://java-px.bot.cd/tools/' },
          { text: '视频处理', link: 'https://java-px.bot.cd/video/' },
          { text: '文件系统与存储', link: 'https://java-px.bot.cd/filesystem/' }
        ]
      }
    ],
    sidebar: {
      '/': [
        {
          text: '🎯 开始',
          items: [
            { text: '📖 学习路径', link: '/path' },
            { text: '🧠 知识图谱', link: '/graph' },
            { text: '🧭 思维导图', link: '/mindmap' },
            { text: '⚡ 速记卡', link: '/cheatsheet' }
          ]
        },
        {
          text: '📁 文件系统基础',
          items: [
            { text: 'inode 与 dentry', link: '/01-basics/inode-dentry' },
            { text: 'VFS 虚拟文件系统', link: '/01-basics/vfs' },
            { text: '文件描述符与 open', link: '/01-basics/file-descriptor' },
            { text: 'Page Cache 页缓存', link: '/01-basics/page-cache' },
            { text: '挂载与文件系统树', link: '/01-basics/mount' },
            { text: '日志与一致性', link: '/01-basics/journal' },
            { text: '目录与路径解析', link: '/01-basics/path-resolution' }
          ]
        },
        {
          text: '💾 本地盘文件系统',
          items: [
            { text: 'ext4 经典之选', link: '/02-disk-fs/ext4' },
            { text: 'XFS 高性能日志', link: '/02-disk-fs/xfs' },
            { text: 'Btrfs COW 与快照', link: '/02-disk-fs/btrfs' },
            { text: 'ZFS 企业级', link: '/02-disk-fs/zfs' },
            { text: 'NTFS / FAT / exFAT', link: '/02-disk-fs/windows-fs' },
            { text: 'APFS / HFS+', link: '/02-disk-fs/apple-fs' },
            { text: '横向对比与选型', link: '/02-disk-fs/compare' }
          ]
        },
        {
          text: '🌐 分布式文件系统',
          items: [
            { text: 'HDFS 大数据基石', link: '/03-distributed/hdfs' },
            { text: 'CephFS 统一存储', link: '/03-distributed/cephfs' },
            { text: 'GlusterFS 弹性卷', link: '/03-distributed/glusterfs' },
            { text: 'JuiceFS 云原生', link: '/03-distributed/juicefs' },
            { text: 'MooseFS 轻量级', link: '/03-distributed/moosefs' },
            { text: 'Lustre HPC 超算', link: '/03-distributed/lustre' },
            { text: '架构对比与选型', link: '/03-distributed/compare' }
          ]
        },
        {
          text: '📦 对象存储',
          items: [
            { text: 'S3 协议规范', link: '/04-object/s3-protocol' },
            { text: 'MinIO 自建对象存储', link: '/04-object/minio' },
            { text: '阿里云 OSS', link: '/04-object/oss' },
            { text: '腾讯云 COS', link: '/04-object/cos' },
            { text: '纠删码 vs 多副本', link: '/04-object/erasure-coding' },
            { text: '多版本与生命周期', link: '/04-object/lifecycle' },
            { text: '一致性模型', link: '/04-object/consistency' }
          ]
        },
        {
          text: '🔗 网络文件协议',
          items: [
            { text: 'NFS Unix 经典', link: '/05-network/nfs' },
            { text: 'SMB / CIFS Windows', link: '/05-network/smb' },
            { text: 'WebDAV HTTP 文件', link: '/05-network/webdav' },
            { text: 'FTP / SFTP / SCP', link: '/05-network/ftp-sftp' },
            { text: 'rsync 增量同步', link: '/05-network/rsync' }
          ]
        },
        {
          text: '☸️ 云原生存储',
          items: [
            { text: 'CSI 容器存储接口', link: '/06-cloud-native/csi' },
            { text: 'PV / PVC / StorageClass', link: '/06-cloud-native/pv-pvc' },
            { text: '动态配置 StorageClass', link: '/06-cloud-native/dynamic' },
            { text: 'Rook Ceph Operator', link: '/06-cloud-native/rook' },
            { text: 'Longhorn 分布式块', link: '/06-cloud-native/longhorn' },
            { text: 'OpenEBS 容器化存储', link: '/06-cloud-native/openebs' },
            { text: 'Volume Snapshot / Clone', link: '/06-cloud-native/snapshot' }
          ]
        },
        {
          text: '🐳 容器文件系统',
          items: [
            { text: 'OverlayFS 联合挂载', link: '/07-container/overlayfs' },
            { text: 'Docker 镜像分层', link: '/07-container/docker-layers' },
            { text: 'containerd 快照', link: '/07-container/containerd' },
            { text: 'BuildKit 缓存', link: '/07-container/buildkit' },
            { text: '存储驱动对比', link: '/07-container/storage-drivers' }
          ]
        },
        {
          text: '🛠️ 文件工具集',
          items: [
            { text: 'FUSE 用户态 FS', link: '/08-tools/fuse' },
            { text: 'debugfs 调试工具', link: '/08-tools/debugfs' },
            { text: 'rsync 同步备份', link: '/08-tools/rsync' },
            { text: 'find / fd / ripgrep', link: '/08-tools/find-fd' },
            { text: 'inotify / fanotify', link: '/08-tools/inotify' },
            { text: 'du / df / ncdu', link: '/08-tools/du-df' },
            { text: 'lsof / fuser', link: '/08-tools/lsof' }
          ]
        },
        {
          text: '⚡ 性能调优',
          items: [
            { text: 'IO 调度器选型', link: '/09-perf/io-scheduler' },
            { text: 'Page Cache 调优', link: '/09-perf/page-cache-tune' },
            { text: 'fsync 语义与坑', link: '/09-perf/fsync' },
            { text: 'readahead 预读', link: '/09-perf/readahead' },
            { text: 'Direct I/O 旁路缓存', link: '/09-perf/direct-io' },
            { text: '性能分析方法论', link: '/09-perf/methodology' }
          ]
        },
        {
          text: '🔒 安全与权限',
          items: [
            { text: 'POSIX 权限位', link: '/10-security/posix-perm' },
            { text: 'ACL 访问控制列表', link: '/10-security/acl' },
            { text: 'xattr 扩展属性', link: '/10-security/xattr' },
            { text: '加密静态 / 传输', link: '/10-security/encryption' },
            { text: 'auditd 审计', link: '/10-security/auditd' }
          ]
        },
        {
          text: '💼 备份与快照',
          items: [
            { text: '快照技术对比', link: '/11-backup/snapshot' },
            { text: 'Borg 增量备份', link: '/11-backup/borg' },
            { text: 'restic 云原生备份', link: '/11-backup/restic' },
            { text: '3-2-1 备份原则', link: '/11-backup/3-2-1' },
            { text: '灾难恢复 RPO/RTO', link: '/11-backup/dr' }
          ]
        },
        {
          text: '🏢 企业案例',
          items: [
            { text: 'Netflix S3 架构', link: '/12-cases/netflix-s3' },
            { text: 'ByteDance JuiceFS', link: '/12-cases/juicefs-bytedance' },
            { text: 'CERN EOS 物理存储', link: '/12-cases/cern-eos' },
            { text: 'Snowflake 存储层', link: '/12-cases/snowflake' },
            { text: 'Meta HDFS 演进', link: '/12-cases/meta-hdfs' }
          ]
        },
        {
          text: '🎯 面试 / 实战',
          items: [
            { text: '高频面试题', link: '/13-interview/questions' },
            { text: '系统设计题', link: '/13-interview/system-design' },
            { text: '技术对比表', link: '/13-interview/comparison' }
          ]
        }
      ]
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com' }
    ],
    search: {
      provider: 'local',
      options: {
        miniSearch: { searchOptions: { fuzzy: 0.2, prefix: true, boost: { title: 4, text: 2 } } }
      }
    },
    outline: { level: [2, 3], label: '本页目录' },
    docFooter: { prev: '上一篇', next: '下一篇' },
    footer: {
      message: '基于 VitePress 构建 · 文件系统 / 文件服务 / 存储全栈 · 🏠 <a href="https://java-px.bot.cd/" target="_blank">门户首页</a>',
      copyright: '文件全栈 · Filesystem Atlas'
    }
  }
})