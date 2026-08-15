<template>
  <div class="ch-container">
    <div class="ch-search">
      <input v-model="keyword" placeholder="搜索命令（SET / GET / HSET / XADD ...）" class="ch-input" />
      <select v-model="category" class="ch-filter">
        <option value="all">全部分类</option>
        <option value="string">String 字符串</option>
        <option value="hash">Hash 哈希</option>
        <option value="list">List 列表</option>
        <option value="set">Set 集合</option>
        <option value="zset">ZSet 有序集合</option>
        <option value="stream">Stream 流</option>
        <option value="key">Key 通用</option>
        <option value="server">服务端</option>
      </select>
    </div>

    <div v-if="filtered.length === 0" class="ch-empty">
      😢 没有匹配的命令
    </div>
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
  // String
  { name: 'SET',  category: 'string', syntax: 'SET key value [EX seconds] [PX ms]', desc: '设置 key 的值，可选过期时间' },
  { name: 'GET',  category: 'string', syntax: 'GET key', desc: '获取 key 的值' },
  { name: 'DEL',  category: 'string', syntax: 'DEL key [key ...]', desc: '删除一个或多个 key' },
  { name: 'INCR', category: 'string', syntax: 'INCR key', desc: '将 key 中的值加 1（原子操作）' },
  { name: 'DECR', category: 'string', syntax: 'DECR key', desc: '将 key 中的值减 1（原子操作）' },
  { name: 'INCRBY', category: 'string', syntax: 'INCRBY key increment', desc: '将 key 中的值增加指定步长' },
  { name: 'MGET', category: 'string', syntax: 'MGET key [key ...]', desc: '批量获取多个 key' },
  { name: 'MSET', category: 'string', syntax: 'MSET key value [key value ...]', desc: '批量设置多个 key-value' },
  { name: 'APPEND', category: 'string', syntax: 'APPEND key value', desc: '向 key 追加字符串' },
  { name: 'STRLEN', category: 'string', syntax: 'STRLEN key', desc: '获取 key 字符串长度' },

  // Hash
  { name: 'HSET', category: 'hash', syntax: 'HSET key field value', desc: '设置 hash 字段值' },
  { name: 'HGET', category: 'hash', syntax: 'HGET key field', desc: '获取 hash 字段值' },
  { name: 'HMSET', category: 'hash', syntax: 'HMSET key f1 v1 f2 v2 ...', desc: '批量设置 hash 多个字段' },
  { name: 'HMGET', category: 'hash', syntax: 'HMGET key f1 f2 ...', desc: '批量获取 hash 多个字段' },
  { name: 'HGETALL', category: 'hash', syntax: 'HGETALL key', desc: '获取 hash 所有字段与值' },
  { name: 'HDEL', category: 'hash', syntax: 'HDEL key field', desc: '删除 hash 字段' },
  { name: 'HKEYS', category: 'hash', syntax: 'HKEYS key', desc: '获取 hash 所有字段名' },
  { name: 'HVALS', category: 'hash', syntax: 'HVALS key', desc: '获取 hash 所有字段值' },
  { name: 'HEXISTS', category: 'hash', syntax: 'HEXISTS key field', desc: '判断 hash 字段是否存在' },
  { name: 'HINCRBY', category: 'hash', syntax: 'HINCRBY key field increment', desc: 'hash 字段自增' },

  // List
  { name: 'LPUSH', category: 'list', syntax: 'LPUSH key element [element ...]', desc: '从左侧插入元素' },
  { name: 'RPUSH', category: 'list', syntax: 'RPUSH key element [element ...]', desc: '从右侧插入元素' },
  { name: 'LPOP', category: 'list', syntax: 'LPOP key [count]', desc: '从左侧弹出元素' },
  { name: 'RPOP', category: 'list', syntax: 'RPOP key [count]', desc: '从右侧弹出元素' },
  { name: 'LRANGE', category: 'list', syntax: 'LRANGE key start stop', desc: '获取区间内元素' },
  { name: 'LLEN', category: 'list', syntax: 'LLEN key', desc: '获取 list 长度' },
  { name: 'LINDEX', category: 'list', syntax: 'LINDEX key index', desc: '按下标获取元素' },
  { name: 'LSET', category: 'list', syntax: 'LSET key index element', desc: '按下标设置元素' },
  { name: 'BRPOP', category: 'list', syntax: 'BRPOP key timeout', desc: '阻塞式右侧弹出（消息队列）' },

  // Set
  { name: 'SADD', category: 'set', syntax: 'SADD key member [member ...]', desc: '添加集合元素' },
  { name: 'SREM', category: 'set', syntax: 'SREM key member [member ...]', desc: '删除集合元素' },
  { name: 'SMEMBERS', category: 'set', syntax: 'SMEMBERS key', desc: '获取所有元素' },
  { name: 'SISMEMBER', category: 'set', syntax: 'SISMEMBER key member', desc: '判断是否是成员' },
  { name: 'SCARD', category: 'set', syntax: 'SCARD key', desc: '获取集合大小' },
  { name: 'SINTER', category: 'set', syntax: 'SINTER key [key ...]', desc: '求多个集合交集' },
  { name: 'SUNION', category: 'set', syntax: 'SUNION key [key ...]', desc: '求多个集合并集' },
  { name: 'SDIFF', category: 'set', syntax: 'SDIFF key [key ...]', desc: '求多个集合差集' },
  { name: 'SPOP', category: 'set', syntax: 'SPOP key [count]', desc: '随机弹出元素' },

  // ZSet
  { name: 'ZADD', category: 'zset', syntax: 'ZADD key score member [score member ...]', desc: '添加有序集合元素' },
  { name: 'ZSCORE', category: 'zset', syntax: 'ZSCORE key member', desc: '获取元素分数' },
  { name: 'ZRANGE', category: 'zset', syntax: 'ZRANGE key start stop [WITHSCORES]', desc: '按排名获取元素' },
  { name: 'ZREVRANGE', category: 'zset', syntax: 'ZREVRANGE key start stop [WITHSCORES]', desc: '按排名倒序获取' },
  { name: 'ZRANGEBYSCORE', category: 'zset', syntax: 'ZRANGEBYSCORE key min max', desc: '按分数区间获取' },
  { name: 'ZINCRBY', category: 'zset', syntax: 'ZINCRBY key increment member', desc: '增加元素分数' },
  { name: 'ZCARD', category: 'zset', syntax: 'ZCARD key', desc: '获取 ZSet 元素数' },
  { name: 'ZREM', category: 'zset', syntax: 'ZREM key member', desc: '删除元素' },
  { name: 'ZRANK', category: 'zset', syntax: 'ZRANK key member', desc: '获取元素排名（从 0 开始）' },

  // Stream
  { name: 'XADD', category: 'stream', syntax: 'XADD key * field value [field value ...]', desc: '追加消息到流' },
  { name: 'XLEN', category: 'stream', syntax: 'XLEN key', desc: '获取流消息数' },
  { name: 'XRANGE', category: 'stream', syntax: 'XRANGE key start end', desc: '按 ID 范围获取消息' },
  { name: 'XREAD', category: 'stream', syntax: 'XREAD [COUNT count] STREAMS key id', desc: '阻塞式读取消息' },
  { name: 'XGROUP', category: 'stream', syntax: 'XGROUP CREATE key group id [MKSTREAM]', desc: '创建消费者组' },
  { name: 'XREADGROUP', category: 'stream', syntax: 'XREADGROUP GROUP g c COUNT n STREAMS k id', desc: '消费组内读取' },
  { name: 'XACK', category: 'stream', syntax: 'XACK key group id', desc: '确认消息已处理' },
  { name: 'XPENDING', category: 'stream', syntax: 'XPENDING key group', desc: '查看待确认消息' },

  // Key
  { name: 'EXISTS', category: 'key', syntax: 'EXISTS key [key ...]', desc: '判断 key 是否存在' },
  { name: 'EXPIRE', category: 'key', syntax: 'EXPIRE key seconds', desc: '设置 key 过期时间（秒）' },
  { name: 'PEXPIRE', category: 'key', syntax: 'PEXPIRE key milliseconds', desc: '设置 key 过期时间（毫秒）' },
  { name: 'TTL', category: 'key', syntax: 'TTL key', desc: '查看 key 剩余 TTL（秒）' },
  { name: 'PTTL', category: 'key', syntax: 'PTTL key', desc: '查看 key 剩余 TTL（毫秒）' },
  { name: 'PERSIST', category: 'key', syntax: 'PERSIST key', desc: '移除 key 过期时间' },
  { name: 'KEYS', category: 'key', syntax: 'KEYS pattern', desc: '查找匹配的 key（⚠️生产不要用）' },
  { name: 'SCAN', category: 'key', syntax: 'SCAN cursor [MATCH pattern] [COUNT n]', desc: '迭代式扫描 key（生产推荐）' },
  { name: 'TYPE', category: 'key', syntax: 'TYPE key', desc: '查看 key 类型' },
  { name: 'RENAME', category: 'key', syntax: 'RENAME key newkey', desc: '重命名 key' },

  // Server
  { name: 'PING', category: 'server', syntax: 'PING', desc: '测试连接是否存活' },
  { name: 'INFO', category: 'server', syntax: 'INFO [section]', desc: '查看服务器信息' },
  { name: 'DBSIZE', category: 'server', syntax: 'DBSIZE', desc: '当前数据库 key 总数' },
  { name: 'FLUSHDB', category: 'server', syntax: 'FLUSHDB', desc: '清空当前 DB（⚠️危险）' },
  { name: 'FLUSHALL', category: 'server', syntax: 'FLUSHALL', desc: '清空所有 DB（⚠️危险）' },
  { name: 'BGSAVE', category: 'server', syntax: 'BGSAVE', desc: '后台保存 RDB 快照' },
  { name: 'LASTSAVE', category: 'server', syntax: 'LASTSAVE', desc: '上次保存时间' },
  { name: 'MONITOR', category: 'server', syntax: 'MONITOR', desc: '实时监控所有命令' },
  { name: 'DEBUG SLEEP', category: 'server', syntax: 'DEBUG SLEEP seconds', desc: '让 Redis 阻塞 N 秒' },
  { name: 'SLOWLOG', category: 'server', syntax: 'SLOWLOG [GET|LEN|RESET]', desc: '慢查询日志' }
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
    string: 'String', hash: 'Hash', list: 'List', set: 'Set',
    zset: 'ZSet', stream: 'Stream', key: 'Key', server: 'Server'
  }
  return map[c] || c
}
</script>
