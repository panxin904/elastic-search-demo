<template>
  <div class="es-deploy">
    <div class="es-deploy__intro">
      ⚙️ 按 <strong>6 大主题</strong>组织 ES 7 部署与生产调优配置参考。
      每个主题含场景说明、推荐配置、完整 yaml/命令。「📋 复制」直接拷贝到生产环境使用。
    </div>

    <div class="es-deploy__subtabs">
      <button
        v-for="cat in categories"
        :key="cat.id"
        :class="['es-deploy__subtab', { 'es-deploy__subtab--active': activeTab === cat.id }]"
        @click="activeTab = cat.id"
      >
        {{ cat.icon }} {{ cat.label }}
        <span class="es-deploy__subtab-count">
          ({{ topics.filter(t => t.category === cat.id).length }})
        </span>
      </button>
    </div>

    <div class="es-deploy__cat-title">
      {{ currentCat.icon }} {{ currentCat.label }}
    </div>

    <div
      v-for="topic in filteredTopics"
      :key="topic.id"
      class="es-deploy__topic"
    >
      <div class="es-deploy__topic-head">
        <strong>{{ topic.title }}</strong>
        <div class="es-deploy__topic-tags">
          <span
            v-for="tag in topic.tags"
            :key="tag"
            class="es-deploy__tag"
          >{{ tag }}</span>
        </div>
      </div>
      <div class="es-deploy__desc">{{ topic.desc }}</div>
      <details class="es-deploy__details" open>
        <summary>{{ topic.configLabel || '完整配置' }}</summary>
        <pre class="es-deploy__pre">{{ topic.config }}</pre>
        <div class="es-deploy__actions">
          <button class="es-deploy__btn es-deploy__btn--sm" @click="copy(topic.config, topic.id)">
            {{ copiedId === topic.id ? '已复制 ✓' : '📋 复制' }}
          </button>
        </div>
      </details>
      <div v-if="topic.notes && topic.notes.length" class="es-deploy__notes">
        <div class="es-deploy__notes-title">📌 关键说明</div>
        <ul>
          <li v-for="(note, i) in topic.notes" :key="i">{{ note }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const categories = [
  { id: 'install', label: '安装方式', icon: '🛠️' },
  { id: 'cluster', label: '集群配置', icon: '🏗️' },
  { id: 'node', label: '节点角色', icon: '🧩' },
  { id: 'jvm', label: '内存与 GC', icon: '💾' },
  { id: 'security', label: '安全与 TLS', icon: '🔐' },
  { id: 'monitor', label: '监控配置', icon: '📊' }
]

const topics = [
  // ====== 安装方式 ======
  {
    id: 'install-tar',
    category: 'install',
    title: 'Tar 包单机部署（生产推荐）',
    tags: ['Tar', 'Linux'],
    desc: '从官网下载 7.17.10 tar 包，适合生产裸机/虚拟机部署。',
    configLabel: '完整部署命令',
    config: `# 1. 下载（7.17.10 与本项目配套版本）
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.17.10-linux-x86_64.tar.gz
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.17.10-linux-x86_64.tar.gz.sha512
shasum -a 512 -c elasticsearch-7.17.10-linux-x86_64.tar.gz.sha512

# 2. 解压
tar -xzf elasticsearch-7.17.10-linux-x86_64.tar.gz
cd elasticsearch-7.17.10

# 3. 创建专用用户（不能用 root 启动）
useradd -m -s /bin/bash esuser
chown -R esuser:esuser /opt/elasticsearch-7.17.10

# 4. 修改系统限制
cat >> /etc/security/limits.conf <<EOF
esuser  -  nofile  65536
esuser  -  nproc   4096
esuser  -  memlock unlimited
EOF

# 5. 禁用 swap（必须）
swapoff -a
# 永久：/etc/fstab 中注释掉 swap 行

# 6. 调整 vm.max_map_count
sysctl -w vm.max_map_count=262144
echo 'vm.max_map_count=262144' >> /etc/sysctl.conf

# 7. 编辑配置（详见"集群配置"主题）
vi config/elasticsearch.yml

# 8. 启动（后台模式）
su esuser -c "./bin/elasticsearch -d -p pid"

# 9. 验证
curl http://localhost:9200/_cluster/health?pretty`,
    notes: [
      '**不能用 root 启动**：ES 启动时会主动检查 UID，root 启动会报错并退出',
      '**vm.max_map_count ≥ 262144**：ES 用 mmap 大量文件，不足会导致 out of memory errors',
      '**关闭 swap**：JVM 在内存压力下可能换出堆，导致 GC 抖动甚至节点失联',
      '**kernel 参数**：THP (transparent_hugepage) 建议关闭，避免与 G1GC 冲突：`echo never > /sys/kernel/mm/transparent_hugepage/enabled`'
    ]
  },
  {
    id: 'install-docker',
    category: 'install',
    title: 'Docker 单机部署（开发测试）',
    tags: ['Docker', '单机'],
    desc: 'Docker 单容器部署，适合本地开发或 CI 测试。生产不推荐。',
    configLabel: 'docker run 命令',
    config: `# 单节点 + 启用安全 + 内存锁定
docker run -d --name es \\
  -p 9200:9200 -p 9300:9300 \\
  -e "discovery.type=single-node" \\
  -e "ES_JAVA_OPTS=-Xms2g -Xmx2g" \\
  -e "bootstrap.memory_lock=true" \\
  -e "xpack.security.enabled=true" \\
  -e "ELASTIC_PASSWORD=changeme" \\
  -v es_data:/usr/share/elasticsearch/data \\
  --ulimit memlock=-1:-1 \\
  docker.elastic.co/elasticsearch/elasticsearch:7.17.10

# 验证（生产模式需要 https + 密码）
curl -k -u elastic:changeme https://localhost:9200/_cluster/health?pretty`,
    notes: [
      '**版本一致性**：必须使用 7.17.10 镜像，与 Java Client 版本一致',
      '**生产慎用**：Docker 在 Linux 上有 ulimit/内存限制，难以配置节点角色',
      '**开发推荐**：docker-compose 一键起 ES + Kibana + Cerebro 全套',
      '**Mac/Windows 性能差**：docker desktop 的虚拟化层带来 30%+ 性能损耗'
    ]
  },
  {
    id: 'install-compose',
    category: 'install',
    title: 'Docker Compose 3 节点集群（推荐开发）',
    tags: ['Docker Compose', '集群'],
    desc: '本地用 Docker Compose 启动 3 节点 ES 集群，适合学习集群行为、调优测试。',
    configLabel: 'docker-compose.yml',
    config: `# docker-compose.yml
version: '3.8'
services:
  es01:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.17.10
    environment:
      - node.name=es01
      - cluster.name=es-dev-cluster
      - discovery.seed_hosts=es02,es03
      - cluster.initial_master_nodes=es01,es02,es03
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
      - bootstrap.memory_lock=true
      - xpack.security.enabled=true
      - ELASTIC_PASSWORD=changeme
    ulimits:
      memlock: { soft: -1, hard: -1 }
    volumes: ['./data/es01:/usr/share/elasticsearch/data']
    ports: ['9200:9200']
    networks: ['esnet']
  es02:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.17.10
    environment:
      - node.name=es02
      - cluster.name=es-dev-cluster
      - discovery.seed_hosts=es01,es03
      - cluster.initial_master_nodes=es01,es02,es03
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
    ulimits:
      memlock: { soft: -1, hard: -1 }
    volumes: ['./data/es02:/usr/share/elasticsearch/data']
    networks: ['esnet']
  es03:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.17.10
    environment:
      - node.name=es03
      - cluster.name=es-dev-cluster
      - discovery.seed_hosts=es01,es02
      - cluster.initial_master_nodes=es01,es02,es03
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
    ulimits:
      memlock: { soft: -1, hard: -1 }
    volumes: ['./data/es03:/usr/share/elasticsearch/data']
    networks: ['esnet']

networks:
  esnet:
    driver: bridge

# 启动
docker-compose up -d
# 查看状态
docker-compose ps
# 查看节点
curl -k -u elastic:changeme https://localhost:9200/_cat/nodes?v`,
    notes: [
      '**奇数节点**：3 / 5 / 7 节点（避免脑裂，master 需要 majority）',
      '**内存配置**：生产环境每个节点堆内存至少 8G，推荐 16-32G',
      '**data 目录**：挂载到宿主机，避免容器删除时数据丢失',
      '**network mode**：单机可以省略，跨机部署需要 overlay'
    ]
  },
  {
    id: 'install-rpm',
    category: 'install',
    title: 'RPM 包安装（CentOS/RHEL）',
    tags: ['RPM', 'Systemd'],
    desc: 'CentOS/RHEL 用 RPM 包安装，自动注册 systemd 服务。',
    configLabel: 'RPM 安装步骤',
    config: `# 1. 导入 GPG key
rpm --import https://artifacts.elastic.co/GPG-KEY-elasticsearch

# 2. 添加 yum repo
cat > /etc/yum.repos.d/elasticsearch.repo <<EOF
[elasticsearch-7.x]
name=Elasticsearch repository for 7.x packages
baseurl=https://artifacts.elastic.co/packages/7.x/yum
gpgcheck=1
gpgkey=https://artifacts.elastic.co/GPG-KEY-elasticsearch
enabled=1
autorefresh=1
type=rpm-md
EOF

# 3. 安装
yum install -y elasticsearch-7.17.10

# 4. 配置
vim /etc/elasticsearch/elasticsearch.yml
vim /etc/elasticsearch/jvm.options

# 5. 启动（systemd）
systemctl daemon-reload
systemctl enable elasticsearch.service
systemctl start elasticsearch.service
systemctl status elasticsearch.service

# 6. 查看日志
journalctl -u elasticsearch -f

# 7. 验证
curl http://localhost:9200/_cluster/health?pretty`,
    notes: [
      '**安装位置**：/usr/share/elasticsearch（程序）、/etc/elasticsearch（配置）、/var/lib/elasticsearch（数据）',
      '**systemd 集成**：service 文件位于 /usr/lib/systemd/system/elasticsearch.service',
      '**权限问题**：RPM 安装的文件属于 root:elasticsearch，需要保证数据目录权限正确',
      '**升级**：直接 yum update，旧数据可复用（仅 minor 版本）'
    ]
  },
  // ====== 集群配置 ======
  {
    id: 'config-cluster-basic',
    category: 'cluster',
    title: 'elasticsearch.yml 基础集群配置',
    tags: ['核心配置', '生产'],
    desc: '3 节点集群最简生产配置，含集群名、网络、发现。',
    configLabel: 'elasticsearch.yml 完整示例',
    config: `# ===================================
# elasticsearch.yml - 生产基础配置
# ===================================

# ---- 集群标识 ----
cluster.name: production-cluster

# ---- 节点标识（每节点唯一）----
node.name: \${HOSTNAME}
# 也可用 node.attr.rack: rack1 配合分片分配

# ---- 网络 ----
network.host: 0.0.0.0
http.port: 9200
transport.port: 9300

# ---- 节点发现 ----
discovery.seed_hosts:
  - 10.0.1.10:9300
  - 10.0.1.11:9300
  - 10.0.1.12:9300

# 首次启动时用于选主，**生产环境必须严格配置 3/5/7 个 master-eligible**
cluster.initial_master_nodes:
  - es-master-01
  - es-master-02
  - es-master-03

# ---- 集群规模参数 ----
# 最小主节点数（防止脑裂，默认 1）
discovery.zen.minimum_master_nodes: 2

# ping 超时（默认 3s，集群大或跨网可调大）
discovery.zen.ping.timeout: 5s
discovery.zen.ping.retries: 3

# ---- 恢复期防护（7.x 改名为 cluster.blocks）----
# 节点因网络抖动离开集群后，重启时不要立刻让分片全量重分配
cluster.routing.allocation.enable: all

# ---- 跨集群发现（可选）----
# cluster.remote.seeding_hosts:
#   - remote-cluster-host:9300`,
    notes: [
      '**initial_master_nodes 仅首次启动使用**：集群形成后该参数失效，由节点配置和 Zen discovery 接管',
      '**minimum_master_nodes = N/2 + 1**：3 节点设 2，5 节点设 3',
      '**network.host 不能用 127.0.0.1**：会进入开发模式自动生成 cluster.name',
      '**生产环境用 FQDN**：节点名加域名后缀，避免 DNS 解析问题'
    ]
  },
  {
    id: 'config-cluster-shard',
    category: 'cluster',
    title: '分片分配与均衡配置',
    tags: ['分片', 'allocation'],
    desc: '生产环境分片分配策略、磁盘水位、平衡阈值。',
    configLabel: '分片与磁盘配置',
    config: `# ---- 分片平衡权重 ----
# 同一节点上 shard 数与索引数据量权重比 (默认 0.45 : 0.55)
cluster.routing.allocation.balance.shard: 0.45
cluster.routing.allocation.balance.index: 0.55
cluster.routing.allocation.balance.threshold: 1.0

# ---- 磁盘水位（关键）----
# 当磁盘使用率超过 low，新分片不分配到此节点
cluster.routing.allocation.disk.threshold_enabled: true
cluster.routing.allocation.disk.watermark.low:  85%
cluster.routing.allocation.disk.watermark.high: 90%
# flood_stage: 超过 95% 时索引强制设为 read-only
cluster.routing.allocation.disk.watermark.flood_stage: 95%

# ---- 并发恢复控制（避免节点重启时 IO 打满）----
cluster.routing.allocation.node_concurrent_recoveries: 2
cluster.routing.allocation.cluster_concurrent_rebalance: 2

# ---- 感知（机架 / 可用区）----
# 让主分片和副本分到不同的 zone
cluster.routing.allocation.awareness.attributes: zone
node.attr.zone: us-east-1a   # 每节点配置不同的 zone

# ---- 平衡调度 ----
# 节点脱离集群多久后才重新分片（避免抖动）
cluster.routing.allocation.exclude._name: ""    # 主动排除某个节点

# 慢磁盘保护（IO 超过 100MB/s 阈值触发）
cluster.routing.allocation.disk.threshold_enabled: true
indices.store.throttle.type: merge
indices.store.throttle.max_bytes_per_sec: 50mb`,
    notes: [
      '**水位含义**：low=开始拦截新分片；high=主动搬出；flood_stage=索引只读',
      '**AWS/GCP 上**建议把 low 调到 80%，留出 buffer 防突发 IO',
      '**Awareness**：3 AZ 部署时主副本严格分布，可抗单 AZ 故障',
      '**节点并发恢复**：值不要太大，重启节点后恢复会抢资源影响业务'
    ]
  },
  {
    id: 'config-cluster-recovery',
    category: 'cluster',
    title: '恢复与慢日志配置',
    tags: ['恢复', '慢日志', '调试'],
    desc: '故障恢复阈值与慢查询/慢索引阈值。',
    configLabel: '恢复 + 慢日志',
    config: `# ---- 慢搜索日志 ----
index.search.slowlog.threshold.query.warn: 10s
index.search.slowlog.threshold.query.info:  5s
index.search.slowlog.threshold.query.debug: 2s
index.search.slowlog.threshold.query.trace: 500ms
index.search.slowlog.threshold.fetch.warn: 1s
index.search.slowlog.threshold.fetch.info:  800ms

# ---- 慢索引日志 ----
index.indexing.slowlog.threshold.index.warn: 10s
index.indexing.slowlog.threshold.index.info:  5s

# ---- 恢复控制（防止重启时 cluster yellow 太久）----
indices.recovery.max_bytes_per_sec: 100mb
indices.recovery.max_file_per_sec:   50

# ---- 写入限流（防止过载）----
indices.breaker.request.limit:        60%
indices.breaker.inflight_requests.limit: 100%
indices.breaker.accounting.limit:      100%
indices.breaker.fielddata.limit:       30%`,
    notes: [
      '**慢日志阈值**：先从 10s warn 开始，逐步调到业务可接受的 P99',
      '**写入限流**：默认足够，OOM 时才需调小 fielddata limit',
      '**恢复带宽**：生产环境 100mb/s 起步，避免影响业务 IO'
    ]
  },
  // ====== 节点角色 ======
  {
    id: 'node-role-master',
    category: 'node',
    title: 'Master-eligible 节点（管理集群）',
    tags: ['master', '集群状态'],
    desc: '负责集群状态管理、节点加入/离开、分片分配决策。生产 3/5 个奇数。',
    configLabel: 'Master 节点配置',
    config: `# elasticsearch.yml
# 仅启用 master 角色
node.master: true
node.data: false
node.ingest: false
node.ml: false
node.transform: false

# 数量与发现
discovery.seed_hosts:
  - 10.0.1.10:9300
  - 10.0.1.11:9300
  - 10.0.1.12:9300
cluster.initial_master_nodes:
  - master-01
  - master-02
  - master-03

# JVM（master 节点通常 4-8G 即可）
# -Xms4g -Xmx4g

# Master 节点数：3 / 5 / 7（奇数）
# Master CPU/内存：建议 2-4 core，4-8G heap`,
    notes: [
      '**3 节点 vs 5 节点**：3 节点抗 1 节点故障，5 节点抗 2 节点',
      '**Master 节点 CPU**：选举瞬间有 spike，分配 2-4 core',
      '**Master 节点磁盘**：数据量小，普通 SSD 即可',
      '**不要用 Master 节点兼做 data**：避免 GC 抖动影响集群稳定性'
    ]
  },
  {
    id: 'node-role-data',
    category: 'node',
    title: 'Data 节点（存储与查询）',
    tags: ['data', '存储'],
    desc: '存储数据并执行 CRUD/搜索。生产集群主力，按数据量扩容。',
    configLabel: 'Data 节点配置',
    config: `# elasticsearch.yml
node.master: false
node.data: true
node.ingest: true   # 默认 true，可改为 false 分离 ingest 到独立节点

# 关键磁盘路径
path.data:
  - /data1/es
  - /data2/es
path.logs: /var/log/elasticsearch

# 大内存（数据节点通常是 master 的 4-8 倍）
# -Xms31g -Xmx31g

# 数据节点数：3+ 个（按数据量扩展）
# 数据节点 CPU：8-32 core（搜索密集型需要更多）
# 数据节点内存：16-64G heap + 同等或 2 倍 heap 的 OS cache`,
    notes: [
      '**多个 data.path**：JBOD 模式（just a bunch of disks），一个盘故障不影响其他',
      '**OS Cache 越大越好**：文件系统缓存对搜索性能影响极大（>50% 文件系统缓存给 ES）',
      '**Disk IO 优先**：使用 NVMe SSD 或 高 IOPS 云盘（>3000 IOPS）',
      '**CPU 选择**：查询密集型选高主频（3GHz+），写入密集型选多核'
    ]
  },
  {
    id: 'node-role-coord',
    category: 'node',
    title: 'Coordinating-only 节点（负载均衡）',
    tags: ['协调', '负载均衡'],
    desc: '只做请求路由和结果聚合，不存数据。适合大规模集群前端。',
    configLabel: '协调节点配置',
    config: `# elasticsearch.yml
node.master: false
node.data: false
node.ingest: false
node.ml: false

# 中等内存（不存数据但需要缓存聚合结果）
# -Xms8g -Xmx8g

# 协调节点数：通常 2-3 个即可
# 放在 Nginx / SLB 后端，做请求入口`,
    notes: [
      '**作用**：减少 data 节点的 CPU 消耗（聚合返回结果在 coord 节点完成）',
      '**部署位置**：通常与 Kibana / 业务服务同一内网，离客户端最近',
      '**何时用**：集群规模 >10 data 节点，或聚合查询 P99 高',
      '**配合 SLB**：Kibana → SLB → 多个 coord 节点 → data 节点'
    ]
  },
  {
    id: 'node-role-warm-cold',
    category: 'node',
    title: 'Hot/Warm/Cold 架构（分层存储）',
    tags: ['分层', '存储成本'],
    desc: '用节点属性 + 分片过滤实现 hot/warm/cold 分层，平衡成本与性能。',
    configLabel: '分层节点配置',
    config: `# ---- Hot 节点（SSD，存最近数据）----
node.attr.box_type: hot
node.master: false
node.data: true

# ---- Warm 节点（HDD，存历史数据）----
node.attr.box_type: warm
node.master: false
node.data: true

# ---- Cold 节点（低 IOPS，存冷数据）----
node.attr.box_type: cold
node.master: false
node.data: true

# ---- 在索引模板中指定 ----
# PUT _index_template/logs-template
# {
#   "index_patterns": ["logs-*"],
#   "template": {
#     "settings": {
#       "number_of_shards": 1,
#       "number_of_replicas": 1,
#       "index.routing.allocation.require.box_type": "hot"
#     }
#   }
# }

# ---- ILM 自动迁移 ----
# hot → warm（30 天后） → cold（90 天后）→ delete（365 天后）
# 通过 ILM 策略自动执行，无需人工干预`,
    notes: [
      '**节点属性自定义**：用 node.attr.X 而非固定角色，更灵活',
      '**ILM 必须配置**：分层架构依赖 ILM 自动迁移数据',
      '**副本数**：hot 设 1-2，warm 设 0-1，cold 设 0',
      '**总节点数**：奇数 master + 多个 data（hot/warm/cold）'
    ]
  },
  // ====== 内存与 GC ======
  {
    id: 'jvm-heap',
    category: 'jvm',
    title: 'JVM Heap 大小计算',
    tags: ['Heap', '性能'],
    desc: 'Heap 设置是 ES 性能的头号参数。错误的 heap 直接导致 OOM。',
    configLabel: 'jvm.options.d/heap.options',
    config: `# ---- jvm.options（推荐放 -Xms 和 -Xmx 到独立文件）----
# 推荐最大 heap：31G（保留 compressed oops）
-Xms16g
-Xmx16g

# ---- heap 计算公式 ----
# 推荐 heap ≤ 物理内存的 50%，剩余给 OS 文件系统缓存
# 物理 64G：heap = 31G，OS cache = 33G（用于 Lucene segments）
# 物理 32G：heap = 16G，OS cache = 16G
# 物理 16G：heap = 8G，OS cache = 8G

# ---- 监控指标 ----
# GET /_nodes/stats/jvm
# 关注 jvm.mem.heap_used_percent：
#   > 75% 警告（频繁 GC）
#   > 85% 严重（接近 OOM）
#   长期 > 60% 考虑扩容`,
    notes: [
      '**Xms = Xmx**：避免运行时扩容带来的性能抖动',
      '**不要超过 32G**：超过 32G 会失去 CompressedOops，指针变 8 字节，性能下降',
      '**不要小于 1G**：太小会导致 Lucene segments 频繁被驱逐，搜索变慢',
      '**不要超过物理内存的 50%**：OS 需要文件系统缓存给 Lucene segments'
    ]
  },
  {
    id: 'jvm-gc',
    category: 'jvm',
    title: 'G1GC 参数调优',
    tags: ['GC', 'G1'],
    desc: 'ES 7 默认使用 G1GC，针对大堆优化。GC 停顿是 ES 性能的关键指标。',
    configLabel: 'jvm.options.d/gc.options',
    config: `# ---- jvm.options (GC 部分) ----
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200        # 最大 GC 停顿时间（ms）
-XX:G1HeapRegionSize=16m       # Region 大小（推荐 16-32m）
-XX:InitiatingHeapOccupancyPercent=45   # 触发并发标记的堆占用

# ---- 新生代（eden + survivor）----
-XX:G1NewSizePercent=30        # 新生代最小占比
-XX:G1MaxNewSizePercent=40     # 新生代最大占比（默认 60）

# ---- 字符串去重（JDK 8u20+）----
-XX:+UseStringDeduplication
-XX:+PrintStringDeduplicationStatistics

# ---- 大页面（huge pages）----
# 需要 OS 已配置 huge pages
-XX:+UseLargePages

# ---- GC 日志 ----
-Xlog:gc*,gc+age=trace,safepoint:file=logs/gc.log:utctime,pid,tags:filecount=32,filesize=64m

# ---- 监控命令 ----
# 1. GC 次数与时间
# GET /_nodes/stats/jvm
#   jvm.gc.collectors.young.collection_count / collection_time_in_millis
#   jvm.gc.collectors.old.collection_count / collection_time_in_millis
#
# 2. 强制 GC（慎用！）
# POST /_nodes/_local/_flush
# POST _cluster/_gc  # 仅老版本`,
    notes: [
      '**MaxGCPauseMillis=200**：默认目标停顿 200ms，搜索场景建议 100ms',
      '**G1NewSizePercent=40**：ES 数据节点新生代较大（Lucene segments cache）',
      '**GC 时间占比**：young GC < 10% 正常；old GC 频繁需要调大 heap 或减少索引',
      '**避免 Full GC**：出现 Full GC 时节点可能卡顿 30 秒+ 触发集群超时'
    ]
  },
  {
    id: 'jvm-memory-lock',
    category: 'jvm',
    title: '内存锁定 (memory_lock)',
    tags: ['内存', 'swap'],
    desc: '禁止 JVM 堆被 swap 到磁盘，避免节点响应慢导致集群超时。',
    configLabel: '内存锁定配置',
    config: `# ---- elasticsearch.yml ----
bootstrap.memory_lock: true   # 锁定堆内存（关键）

# ---- /etc/security/limits.conf ----
esuser  -  memlock  unlimited

# ---- systemd 服务文件 /etc/systemd/system/elasticsearch.service.d/override.conf ----
[Service]
LimitMEMLOCK=infinity

# ---- Docker ----
--ulimit memlock=-1:-1

# ---- 验证是否生效 ----
GET /_nodes?filter_path=nodes.*.jvm.mem.heap_init_in_bytes

# 或直接查进程
cat /proc/<ES_PID>/smaps | grep -i locked | head
# 应该看到 Locked: 16GB 左右

# ---- 启动失败排查 ----
# 如果启动失败看到 "memory locking requested for elasticsearch process
# but failed because the user has insufficient privileges"
# 1. 检查 limits.conf 是否生效（esuser 重新登录）
# 2. systemd 服务需要重启：systemctl daemon-reload && systemctl restart elasticsearch`,
    notes: [
      '**必须配置**：生产环境一定要开，否则 GC 后 swap 让响应时间变成秒级',
      '**ES 启动时验证**：日志会打印 "JVM arguments [...] -Xms16g ... -Xmx16g"',
      '**Docker 特殊**：必须用 --ulimit memlock=-1:-1，否则无法锁定',
      '**ulimit 设置后必须重连**：改 limits.conf 后 SSH 重连或重新 su 才生效'
    ]
  },
  {
    id: 'jvm-circuit-breakers',
    category: 'jvm',
    title: '熔断器 (Circuit Breakers)',
    tags: ['熔断', 'OOM 防护'],
    desc: '熔断器防止单个查询导致 OOM。理解每个熔断器避免误调。',
    configLabel: '熔断器配置',
    config: `# ---- 熔断器类型 ----
# 1. request 熔断器：限制单个请求的内存使用（默认 60% heap）
indices.breaker.request.limit: 60%

# 2. fielddata 熔断器：限制 fielddata 缓存（默认 30% heap）
indices.breaker.fielddata.limit: 30%

# 3. in-flight 请求熔断器（默认 100% heap）
# 限制请求数（不限制内存）
indices.breaker.inflight_requests.limit: 100%

# 4. accounting 熔断器（默认 100% heap）
# 限制父子请求聚合内存
indices.breaker.accounting.limit: 100%

# 5. 父级熔断器（默认 95% heap）
# 所有子熔断器总和不能超过
indices.breaker.total.use_real_memory: true  # 7.x 新增，更精确

# ---- 监控 ----
GET /_nodes/stats/breaker

# 触发熔断会返回 CircuitBreakingException
# 客户端应捕获并退避重试`,
    notes: [
      '**request 是最常触发**：高基数聚合或模糊查询导致内存爆涨',
      '**fielddata**：text 字段聚合时加载到内存，超限触发熔断',
      '**退避策略**：触发熔断后等待 1s/2s/4s 重试，不要立即重试',
      '**生产建议**：先用默认值（60%/30%），观察是否频繁触发再调整'
    ]
  },
  // ====== 安全与 TLS ======
  {
    id: 'security-enable',
    category: 'security',
    title: '启用 xpack.security',
    tags: ['xpack', '认证'],
    desc: 'ES 7.x 默认关闭安全，生产必须启用。涉及证书生成、密码设置、HTTPS。',
    configLabel: '启用安全 + 证书生成',
    config: `# ---- elasticsearch.yml ----
xpack.security.enabled: true
xpack.security.enrollment.enabled: true

# ---- TLS 配置（推荐生产用自签证书）----
xpack.security.http.ssl:
  enabled: true
  keystore.path: certs/http.p12
  # keystore.password: changeit（生产改复杂）
xpack.security.transport.ssl:
  enabled: true
  verification_mode: certificate
  keystore.path: certs/transport.p12
  truststore.path: certs/transport.p12

# ---- 生成证书（生产环境）----
# 1. 创建 CA
./bin/elasticsearch-certutil ca
# 输出文件：elastic-stack-ca.p12

# 2. 用 CA 签发证书
./bin/elasticsearch-certutil cert \\
  --ca elastic-stack-ca.p12 \\
  --name elasticsearch \\
  --dns <node1>,<node2>,<node3> \\
  --ip 10.0.1.10,10.0.1.11,10.0.1.12

# 3. 转换 keystore
./bin/elasticsearch-keystore add xpack.security.transport.ssl.keystore.secure_password
./bin/elasticsearch-keystore add xpack.security.transport.ssl.truststore.secure_password
./bin/elasticsearch-keystore add xpack.security.http.ssl.keystore.secure_password

# 4. 设置内置用户密码
./bin/elasticsearch-setup-passwords interactive`,
    notes: [
      '**生产必须启用**：未启用等于裸奔，任何能访问 9200 端口的人都能删除所有数据',
      '**证书分发**：所有节点共享同一份证书（http.p12 / transport.p12）',
      '**DNS 和 IP 都要**：客户端可能用 hostname 或 IP 访问，证书必须同时包含',
      '**密码复杂度**：elastic 用户至少 12 字符，包含大小写数字特殊字符'
    ]
  },
  {
    id: 'security-users',
    category: 'security',
    title: '内置用户与角色管理',
    tags: ['RBAC', '用户'],
    desc: 'ES 内置 6 个用户（elastic/kibana/logstash_system 等），按角色授权。',
    configLabel: '用户与角色配置',
    config: `# ---- 内置用户 ----
# elastic       超级管理员（生产慎用，建议创建专用用户）
# kibana        Kibana 专用（仅访问 .kibana 索引）
# logstash_system  Logstash 专用（写入权限）
# beats_system   Beats 专用
# apm_system     APM 专用
# remote_monitoring_user 监控代理（xpack.monitoring 使用）

# ---- 创建只读用户 ----
POST /_security/user/readonly_user
{
  "password": "ReadOnly2026!",
  "roles": ["readonly_role"],
  "full_name": "Read Only User"
}

# ---- 创建开发者用户 ----
POST /_security/user/developer
{
  "password": "DevPass2026!",
  "roles": ["developer_role"],
  "full_name": "App Developer"
}

# ---- 创建应用专用用户（最小权限）----
POST /_security/user/orders_app
{
  "password": "AppPass2026!",
  "roles": ["orders_writer"]
}

# ---- 创建角色 ----
POST /_security/role/orders_writer
{
  "cluster": ["monitor"],
  "indices": [
    {
      "names": ["orders", "orders-*"],
      "privileges": ["create", "read", "write", "delete", "manage"],
      "field_security": {
        "grant": ["order_id", "customer_id", "amount", "status"]
      }
    }
  ]
}

# ---- 创建 readonly 角色 ----
POST /_security/role/developer_role
{
  "cluster": ["monitor"],
  "indices": [
    {
      "names": ["*"],
      "privileges": ["read", "monitor"]
    }
  ]
}

# ---- 应用代码连接（推荐用应用专用用户）----
# 而不是用 elastic 超级用户`,
    notes: [
      '**最小权限原则**：应用代码绝不用 elastic，应用应有自己的专用账号',
      '**field_security 字段级控制**：限制应用只能读特定字段（敏感字段隐藏）',
      '**定期轮换密码**：用 Kibana 的安全功能或外部 secret manager 管理',
      '**不要在代码里硬编码密码**：用环境变量或密钥管理服务'
    ]
  },
  {
    id: 'security-network',
    category: 'security',
    title: '网络安全（防火墙 + CORS）',
    tags: ['firewall', 'CORS'],
    desc: '生产环境必须限制 9200/9300 端口访问范围，避免暴露公网。',
    configLabel: '网络隔离 + CORS',
    config: `# ---- iptables 仅允许内网访问 9200/9300 ----
# 9200 (REST API) 仅允许业务网段
iptables -A INPUT -p tcp --dport 9200 -s 10.0.0.0/8 -j ACCEPT
iptables -A INPUT -p tcp --dport 9200 -j DROP

# 9300 (节点间通信) 仅允许 ES 节点网段
iptables -A INPUT -p tcp --dport 9300 -s 10.0.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 9300 -j DROP

# ---- CORS 配置（仅当浏览器访问时启用）----
# elasticsearch.yml
http.cors.enabled: true
http.cors.allow-origin: "https://kibana.example.com"
http.cors.allow-methods: "OPTIONS, HEAD, GET, POST, PUT, DELETE"
http.cors.allow-headers: "Authorization, Content-Type, X-Requested-With"
http.cors.allow-credentials: true
http.cors.max-age: 3600

# ---- 公网暴露方案（生产不要直接暴露）----
# 方案 1: VPN / WireGuard（推荐）
# 方案 2: SSH 跳板机
#   ssh -L 9200:es-node:9200 user@jump-host
# 方案 3: Nginx 反向代理 + Basic Auth
#   location / { proxy_pass http://es-backend; auth_basic "ES"; }
# 方案 4: CloudFront / ALB + Cognito / IAM`,
    notes: [
      '**9200 vs 9300 都要保护**：9200 是 REST API，9300 是节点二进制协议',
      '**不要把 9200 暴露公网**：会立即被全网扫描攻击',
      '**CORS 仅对浏览器有效**：服务端到服务端调用不受 CORS 限制',
      '**生产推荐 VPN**：AWS PrivateLink / Azure Private Endpoint / GCP Private Service Connect'
    ]
  },
  // ====== 监控配置 ======
  {
    id: 'monitor-self',
    category: 'monitor',
    title: 'ES 自监控 (xpack.monitoring)',
    tags: ['monitoring', '监控'],
    desc: '开启 xpack.monitoring，把 ES 自身指标推到 Kibana 展示。生产必备。',
    configLabel: 'xpack.monitoring 配置',
    config: `# ---- elasticsearch.yml ----
xpack.monitoring.collection.enabled: true

# monitoring 数据存到哪里（两种模式）----
# 模式 1：自监控（ES 自身存储，默认）
xpack.monitoring.collection.interval: 10s   # 采集间隔（默认 10s）

# 模式 2：推到独立 ES 集群（生产推荐）
# xpack.monitoring.exporters:
#   my_remote:
#     type: http
#     host: ["http://monitoring-cluster:9200"]
#     auth:
#       username: remote_monitor
#       password: monitor_pass

# ---- Kibana 配置（让 Kibana 接收 monitoring）----
# kibana.yml
xpack.monitoring.enabled: true
# xpack.monitoring.kibana.collection.enabled: true

# ---- 查看 monitoring 状态 ----
GET /_monitoring/stats`,
    notes: [
      '**采集间隔**：默认 10s 足够，1s 会给集群带来 1-2% 性能损耗',
      '**生产推荐独立监控集群**：避免监控数据占用生产集群空间',
      '**需启用 Basic License**：xpack.monitoring 在基础许可证下免费',
      '**采集器类型**：ES 节点、索引、shard 三类指标'
    ]
  },
  {
    id: 'monitor-cerebro',
    category: 'monitor',
    title: 'Cerebro 集群可视化',
    tags: ['Cerebro', '开源 UI'],
    desc: 'Cerebro 是 ES 集群管理开源 UI，类似简化版 Kibana。强烈推荐运维部署。',
    configLabel: 'Cerebro Docker 部署',
    config: `# ---- Docker 一键启动 ----
docker run -d --name cerebro \\
  -p 9000:9000 \\
  -e CEREBRO_PORT=9000 \\
  -e CEREBRO_SECRET=your-secret-here \\
  lmenezes/cerebro

# 访问 http://localhost:9000
# 输入 ES 节点地址和认证信息

# ---- 连接 ES 集群示例 ----
# Node address: https://es-prod-01:9200
# Username: elastic
# Password: ****

# ---- Cerebro 主要功能 ----
# 1. 集群拓扑可视化（节点角色、分片分布）
# 2. 实时节点指标（heap、CPU、load、disk）
# 3. 索引管理（创建、删除、调整分片数）
# 4. SQL 查询界面（对 ES 跑 SQL）
# 5. REST API 控制台（带语法高亮）
# 6. 快照与恢复入口
# 7. 节点维护（exclude / include 分片）`,
    notes: [
      '**轻量级**：Java 启动内存约 200MB，比 Kibana 轻得多',
      '**无需 license**：完全开源免费',
      '**生产慎用 Basic Auth**：建议在反向代理上加认证',
      '**可对接 LDAP/AD**：通过 reverse proxy 实现统一认证'
    ]
  },
  {
    id: 'monitor-alerts',
    category: 'monitor',
    title: '关键监控指标与告警阈值',
    tags: ['告警', '指标'],
    desc: '生产环境需要监控的核心指标与推荐告警阈值。',
    configLabel: '关键指标清单',
    config: `# ===================================
# 生产 ES 关键监控指标与告警阈值
# ===================================

# 1. 集群状态（最重要）
#    GET /_cluster/health
#    status: green/yellow/red
#    ⚠️ 持续 yellow(>5min) P3
#    ⚠️ red(>1min) P0

# 2. 未分配分片数
#    unassigned_shards
#    ⚠️ > 0 P2
#    ⚠️ 持续 > 0 (10min) P1

# 3. JVM Heap 使用率
#    GET /_nodes/stats/jvm
#    jvm.mem.heap_used_percent
#    ⚠️ > 75% P3
#    ⚠️ > 85% P1
#    ⚠️ 持续 > 60% (1h) 考虑扩容

# 4. Full GC 频率
#    jvm.gc.collectors.old.collection_count
#    ⚠️ 1 分钟内多次 Full GC P0

# 5. CPU 使用率
#    os.cpu.percent
#    ⚠️ > 80% (持续 5min) P2

# 6. 磁盘使用率
#    fs.total.total_in_bytes vs fs.total.available_in_bytes
#    ⚠️ > 80% P3
#    ⚠️ > 90% P1（接近 flood_stage）

# 7. 主分片初始化中
#    initializing_shards
#    ⚠️ 持续 > 10 P2（节点恢复卡住）

# 8. 搜索延迟（重要业务指标）
#    GET /_nodes/stats/indices/search
#    search.query_time_in_millis / search.query_total
#    P99 < 200ms (业务相关)
#    ⚠️ P99 > 1s P2

# 9. 索引延迟
#    indexing.index_time_in_millis / indexing.index_total
#    ⚠️ 平均 > 100ms P2

# 10. 写入拒绝数
#     thread_pool.write.rejected
#     ⚠️ > 0 P0（写入过载）

# 11. 搜索拒绝数
#     thread_pool.search.rejected
#     ⚠️ > 0 P0（查询过载）

# 12. 节点数量
#     GET /_cluster/health
#     number_of_nodes
#     ⚠️ < expected P0

# 13. Master 节点
#     GET /_cat/master
#     ⚠️ master 频繁切换 P0（脑裂风险）

# ---- 推荐告警频率 ----
# 紧急告警：实时（1 分钟）
# 重要告警：5 分钟
# 一般告警：30 分钟`,
    notes: [
      '**heap > 60% 持续 1h**：通常意味着需要扩容或减少索引',
      '**Full GC 频繁**：节点可能即将假死，触发集群 yellow/red',
      '**rejected > 0**：写入/查询过载，要么扩容要么限流',
      '**master 切换**：网络分区或负载过高，立即排查'
    ]
  }
]

const activeTab = ref('install')
const copiedId = ref('')

const currentCat = computed(() =>
  categories.find((c) => c.id === activeTab.value) || categories[0]
)

const filteredTopics = computed(() =>
  topics.filter((t) => t.category === activeTab.value)
)

async function copy(text, id) {
  try {
    await navigator.clipboard.writeText(text)
    copiedId.value = id
    setTimeout(() => (copiedId.value = ''), 1500)
  } catch (_) {
    alert('复制失败，请手动复制')
  }
}
</script>

<style scoped>
.es-deploy {
  margin: 16px 0;
}

.es-deploy__intro {
  margin-bottom: 16px;
  padding: 10px 12px;
  background: var(--vp-c-bg-mute);
  border-radius: 6px;
  font-size: 13px;
  color: var(--vp-c-text-2);
}

.es-deploy__subtabs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 16px;
  padding: 8px 0;
  border-bottom: 1px dashed var(--vp-c-divider);
}

.es-deploy__subtab {
  padding: 6px 12px;
  border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg);
  color: var(--vp-c-text-2);
  border-radius: 16px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.15s;
  white-space: nowrap;
}

.es-deploy__subtab:hover {
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-text-1);
}

.es-deploy__subtab--active {
  background: var(--vp-c-brand-1);
  color: white;
  border-color: var(--vp-c-brand-1);
  font-weight: 600;
}

.es-deploy__subtab-count {
  opacity: 0.75;
  font-weight: 400;
}

.es-deploy__cat-title {
  margin: 0 0 12px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--vp-c-divider);
  font-size: 15px;
  color: var(--vp-c-brand-1);
}

.es-deploy__topic {
  padding: 12px;
  margin-bottom: 12px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg);
}

.es-deploy__topic-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.es-deploy__topic-head strong {
  font-size: 14px;
  color: var(--vp-c-text-1);
}

.es-deploy__topic-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.es-deploy__tag {
  display: inline-block;
  padding: 1px 6px;
  font-size: 10px;
  border-radius: 8px;
  background: var(--vp-c-bg-mute);
  color: var(--vp-c-text-2);
}

.es-deploy__desc {
  font-size: 13px;
  line-height: 1.5;
  color: var(--vp-c-text-2);
  margin: 4px 0 8px;
}

.es-deploy__details {
  font-size: 13px;
  margin: 8px 0;
}

.es-deploy__details summary {
  cursor: pointer;
  color: var(--vp-c-brand-1);
  padding: 4px 0;
  user-select: none;
  font-weight: 600;
}

.es-deploy__pre {
  background: #0f172a;
  color: #e2e8f0;
  padding: 16px;
  margin: 8px 0;
  border-radius: 6px;
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
  font-size: 12px;
  line-height: 1.6;
  overflow-x: auto;
  max-height: 600px;
  overflow-y: auto;
  white-space: pre;
  word-break: normal;
}

.es-deploy__actions {
  display: flex;
  gap: 6px;
  margin-top: 4px;
}

.es-deploy__btn {
  padding: 4px 10px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
}

.es-deploy__btn:hover {
  background: var(--vp-c-bg-mute);
  border-color: var(--vp-c-brand-1);
}

.es-deploy__btn--sm {
  padding: 4px 10px;
  font-size: 12px;
}

.es-deploy__notes {
  margin-top: 12px;
  padding: 10px 14px;
  border-left: 3px solid var(--vp-c-brand-1);
  background: var(--vp-c-bg-mute);
  border-radius: 4px;
  font-size: 13px;
}

.es-deploy__notes-title {
  font-weight: 600;
  margin-bottom: 6px;
  color: var(--vp-c-brand-1);
}

.es-deploy__notes ul {
  margin: 0;
  padding-left: 20px;
  color: var(--vp-c-text-2);
}

.es-deploy__notes li {
  margin: 4px 0;
  line-height: 1.6;
}

.es-deploy__notes li :deep(strong) {
  color: var(--vp-c-text-1);
}

.es-deploy__notes li :deep(code) {
  background: var(--vp-c-bg-mute);
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 12px;
}
</style>
