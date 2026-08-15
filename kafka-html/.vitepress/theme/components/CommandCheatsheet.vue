<template>
  <div class="ch-container">
    <div class="ch-search">
      <input v-model="keyword" placeholder="搜索命令（CREATE / PRODUCE / CONSUMER ...）" class="ch-input" />
      <select v-model="category" class="ch-filter">
        <option value="all">全部分类</option>
        <option value="topic">Topic 管理</option>
        <option value="produce">生产</option>
        <option value="consume">消费</option>
        <option value="group">消费者组</option>
        <option value="config">配置</option>
        <option value="admin">集群管理</option>
      </select>
    </div>

    <div v-if="filtered.length === 0" class="ch-empty">😢 没有匹配的命令</div>
    <div v-else class="ch-grid">
      <div v-for="cmd in filtered" :key="cmd.name" class="ch-card">
        <div class="ch-card__cat">{{ categoryLabel(cmd.category) }}</div>
        <div class="ch-card__title">{{ cmd.name }}</div>
        <div class="ch-card__syntax">{{ cmd.syntax }}</div>
        <div class="ch-card__desc">{{ cmd.desc }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const keyword = ref('')
const category = ref('all')

const commands = [
  // Topic 管理
  { name: 'kafka-topics.sh --create', category: 'topic', syntax: 'kafka-topics.sh --create --topic <name> --partitions <n> --replication-factor <n>', desc: '创建 Topic，指定分区数和副本数' },
  { name: 'kafka-topics.sh --list', category: 'topic', syntax: 'kafka-topics.sh --list --bootstrap-server <host:port>', desc: '列出所有 Topic' },
  { name: 'kafka-topics.sh --describe', category: 'topic', syntax: 'kafka-topics.sh --describe --topic <name>', desc: '查看 Topic 详情（分区、Leader、副本）' },
  { name: 'kafka-topics.sh --alter', category: 'topic', syntax: 'kafka-topics.sh --alter --topic <name> --partitions <new-n>', desc: '增加分区数（不可减少）' },
  { name: 'kafka-topics.sh --delete', category: 'topic', syntax: 'kafka-topics.sh --delete --topic <name>', desc: '删除 Topic' },
  { name: 'kafka-topics.sh --config', category: 'topic', syntax: 'kafka-topics.sh --alter --topic <name> --config <key>=<value>', desc: '修改 Topic 配置（如 retention.ms）' },

  // 生产
  { name: 'kafka-console-producer', category: 'produce', syntax: 'kafka-console-producer.sh --broker-list <host:port> --topic <name>', desc: '命令行生产者（控制台输入消息）' },
  { name: 'kafka-console-producer --property', category: 'produce', syntax: '--property parse.key=true --property key.separator=:', desc: '带 Key 的消息生产' },
  { name: 'kafka-verifiable-producer', category: 'produce', syntax: 'kafka-verifiable-producer.sh --topic <name> --max-messages <n>', desc: '可验证的生产者（测试用）' },

  // 消费
  { name: 'kafka-console-consumer', category: 'consume', syntax: 'kafka-console-consumer.sh --bootstrap-server <host:port> --topic <name> --from-beginning', desc: '命令行消费者（控制台打印消息）' },
  { name: 'kafka-console-consumer --group', category: 'consume', syntax: '--group <group-name> --topic <name>', desc: '指定消费者组消费' },
  { name: 'kafka-console-consumer --property', category: 'consume', syntax: '--property print.timestamp=true --property print.key=true', desc: '打印时间戳和 Key' },

  // 消费者组
  { name: 'kafka-consumer-groups --list', category: 'group', syntax: 'kafka-consumer-groups.sh --bootstrap-server <host:port> --list', desc: '列出所有消费者组' },
  { name: 'kafka-consumer-groups --describe', category: 'group', syntax: 'kafka-consumer-groups.sh --bootstrap-server <host:port> --describe --group <name>', desc: '查看消费者组详情（LAG 等）' },
  { name: 'kafka-consumer-groups --reset-offsets', category: 'group', syntax: '--reset-offsets --to-earliest --topic <name> --execute', desc: '重置消费者组偏移量' },
  { name: 'kafka-consumer-groups --delete', category: 'group', syntax: '--delete --group <name>', desc: '删除消费者组' },

  // 配置
  { name: 'kafka-configs --describe', category: 'config', syntax: 'kafka-configs.sh --bootstrap-server <host:port> --describe --entity-type brokers --entity-name <id>', desc: '查看 Broker 配置' },
  { name: 'kafka-configs --alter', category: 'config', syntax: '--alter --add-config <key>=<value> --entity-type brokers --entity-name <id>', desc: '动态修改 Broker 配置' },
  { name: 'kafka-log-dirs --describe', category: 'config', syntax: 'kafka-log-dirs.sh --bootstrap-server <host:port> --describe --broker-list <id>', desc: '查看 Broker 日志目录' },

  // 集群管理
  { name: 'kafka-broker-api-versions', category: 'admin', syntax: 'kafka-broker-api-versions.sh --bootstrap-server <host:port>', desc: '查看 Broker 支持的 API 版本' },
  { name: 'kafka-reassign-partitions', category: 'admin', syntax: 'kafka-reassign-partitions.sh --bootstrap-server <host:port> --reassignment-json-file <file> --execute', desc: '分区重新分配（扩容/缩容）' },
  { name: 'kafka-preferred-replica-election', category: 'admin', syntax: 'kafka-preferred-replica-election.sh --bootstrap-server <host:port>', desc: '触发 Preferred Replica Leader 选举' },
  { name: 'kafka-leader-election', category: 'admin', syntax: 'kafka-leader-election.sh --bootstrap-server <host:port> --topic <name> --election-type <type> --all-topic-partitions', desc: '强制 Leader 选举' },
  { name: 'kafka-storage', category: 'admin', syntax: 'kafka-storage.sh --bootstrap-server <host:port> random-assign --topics-to-move-json-file <file>', desc: '随机分配存储' },
  { name: 'kafka-acls --list', category: 'admin', syntax: 'kafka-acls.sh --bootstrap-server <host:port> --list', desc: '列出所有 ACL 权限规则' },
  { name: 'kafka-metadata-quorum', category: 'admin', syntax: 'kafka-metadata-quorum.sh --bootstrap-server <host:port> describe --status', desc: '查看 KRaft 集群元数据状态' }
]

const filtered = computed(() => {
  return commands.filter(c => {
    const kw = keyword.value.toLowerCase().trim()
    const catMatch = category.value === 'all' || c.category === category.value
    const kwMatch = !kw || c.name.toLowerCase().includes(kw) || c.desc.toLowerCase().includes(kw)
    return catMatch && kwMatch
  })
})

function categoryLabel(c) {
  const map = {
    topic: 'Topic', produce: '生产', consume: '消费',
    group: '消费者组', config: '配置', admin: '集群管理'
  }
  return map[c] || c
}
</script>
