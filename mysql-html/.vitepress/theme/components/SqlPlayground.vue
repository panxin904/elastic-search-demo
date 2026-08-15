<template>
  <div class="sql-playground">
    <div class="pg-header">
      <span class="pg-title">🛢️ MySQL SQL Playground</span>
      <select v-model="dialect" class="pg-select">
        <option value="mysql">MySQL 8.0</option>
        <option value="mysql57">MySQL 5.7</option>
      </select>
      <button class="pg-btn pg-btn--primary" @click="runSql">▶ 执行</button>
      <button class="pg-btn" @click="runExplain">📊 EXPLAIN</button>
      <button class="pg-btn" @click="formatSql">✨ 格式化</button>
      <button class="pg-btn" @click="resetSql">🔄 重置</button>
    </div>
    <textarea
      v-model="sql"
      class="sql-editor"
      spellcheck="false"
      placeholder="-- 输入 SQL，例如：&#10;SELECT * FROM products WHERE category = 'electronics' LIMIT 10;"
    />
    <div class="pg-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        :class="['pg-tab', { 'pg-tab--active': activeTab === tab.key }]"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>
    <div class="sql-output" v-if="output">{{ output }}</div>
    <div class="sql-output" v-else>执行 SQL 后在此查看结果</div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const dialect = ref('mysql')
const sql = ref(`-- MySQL Playground 示例

-- 示例 1: 简单查询
SELECT id, name, price
FROM products
WHERE category = 'electronics'
  AND price BETWEEN 100 AND 1000
ORDER BY price DESC
LIMIT 10;

-- 示例 2: 聚合查询
SELECT
  category,
  COUNT(*) AS cnt,
  AVG(price) AS avg_price,
  MAX(price) AS max_price
FROM products
GROUP BY category
HAVING cnt > 10
ORDER BY avg_price DESC;`)

const output = ref('')
const activeTab = ref('result')
const tabs = [
  { key: 'result', label: '📋 执行结果' },
  { key: 'explain', label: '📊 EXPLAIN' },
  { key: 'history', label: '🕐 历史' }
]

const history = ref([])

// 模拟 SQL 解析和执行结果
function parseSql(s) {
  const cleaned = s.trim().replace(/;$/, '').replace(/--.*$/gm, '').trim()
  if (!cleaned) return null
  const upper = cleaned.toUpperCase()
  const firstKeyword = upper.split(/\s+/)[0]
  return { type: firstKeyword, raw: cleaned, display: s.trim() }
}

function runSql() {
  const parsed = parseSql(sql.value)
  if (!parsed) {
    output.value = '⚠️ 请输入有效的 SQL 语句'
    return
  }
  activeTab.value = 'result'
  history.value.unshift({ ts: new Date(), sql: sql.value.trim(), type: parsed.type })
  if (history.value.length > 10) history.value = history.value.slice(0, 10)
  output.value = simulateExecution(parsed)
}

function simulateExecution(parsed) {
  const lines = []
  lines.push('┌─ MySQL 8.0 - localhost:3306 ─────────────────┐')
  lines.push(`│ Query: ${parsed.type}                                    │`)
  lines.push(`│ Time:   ${new Date().toLocaleTimeString()}                              │`)
  lines.push('└────────────────────────────────────────────────┘')
  lines.push('')
  switch (parsed.type) {
    case 'SELECT':
      return lines.concat([
        '┌────────┬──────────────────────┬─────────┬────────┐',
        '│   id   │         name         │  price  │  stock │',
        '├────────┼──────────────────────┼─────────┼────────┤',
        '│     1  │ iPhone 15 Pro        │  8999.0 │    120 │',
        '│     2  │ MacBook Air M3       │  9499.0 │     45 │',
        '│     3  │ Sony WH-1000XM5      │  2399.0 │    200 │',
        '│     4  │ AirPods Pro 2        │  1899.0 │    350 │',
        '│     5  │ iPad Air 6           │  4799.0 │     80 │',
        '└────────┴──────────────────────┴─────────┴────────┘',
        '',
        '5 rows in set (0.0034 sec)'
      ]).join('\n')
    case 'INSERT':
      return lines.concat([
        'Query OK, 1 row affected (0.0012 sec)',
        '',
        'Records: 1  Duplicates: 0  Warnings: 0'
      ]).join('\n')
    case 'UPDATE':
      return lines.concat([
        'Query OK, 3 rows affected (0.0089 sec)',
        'Rows matched: 3  Changed: 3  Warnings: 0'
      ]).join('\n')
    case 'DELETE':
      return lines.concat([
        'Query OK, 2 rows affected (0.0045 sec)'
      ]).join('\n')
    case 'CREATE':
      return lines.concat([
        'Query OK, 0 rows affected (0.0234 sec)'
      ]).join('\n')
    case 'DROP':
      return lines.concat([
        'Query OK, 0 rows affected (0.0123 sec)',
        '',
        '⚠️ Warning: This action cannot be undone!'
      ]).join('\n')
    case 'EXPLAIN':
      return runExplainInternal(parsed.raw)
    default:
      return lines.concat([
        `✓ ${parsed.type} 语句解析成功`,
        '注：这是模拟执行结果，未连接真实数据库'
      ]).join('\n')
  }
}

function runExplain() {
  const parsed = parseSql(sql.value)
  if (!parsed) { output.value = '⚠️ 请输入有效的 SQL 语句'; return }
  activeTab.value = 'explain'
  history.value.unshift({ ts: new Date(), sql: 'EXPLAIN ' + sql.value.trim().substring(0, 50) + '...', type: 'EXPLAIN' })
  if (history.value.length > 10) history.value = history.value.slice(0, 10)
  output.value = runExplainInternal(parsed.raw)
}

function runExplainInternal(query) {
  const upper = query.toUpperCase()
  let usesIndex = 'idx_category_price'
  let hasWhere = upper.includes('WHERE')
  let hasJoin = upper.includes('JOIN')
  let hasOrderBy = upper.includes('ORDER BY')
  let hasGroupBy = upper.includes('GROUP BY')
  let hasLimit = upper.includes('LIMIT')

  const rows = []
  let id = 1

  if (hasJoin) {
    rows.push(['1', 'SIMPLE', 'orders o', '', '', 'NULL', `${(Math.random() * 1000 + 500).toFixed(0)}`, 'NULL', 'NULL', 'Using where'])
    rows.push(['1', 'SIMPLE', 'products p', 'eq_ref', 'PRIMARY', 'PRIMARY', '1', 'NULL', 'o.product_id', 'NULL'])
    rows.push(['NULL', 'NULL', 'NULL', 'ref', 'idx_orders_user', 'idx_orders_user', '1', 'const', 'NULL', 'Using where; Using temporary; Using filesort'])
  } else {
    rows.push(['1', 'SIMPLE', 'products', hasWhere ? 'range' : 'ALL', hasWhere ? usesIndex : 'NULL', hasWhere ? usesIndex : 'NULL', hasWhere ? '500' : '10000', hasWhere ? 'price' : 'NULL', '', hasWhere ? 'Using index condition' : 'NULL'])
  }

  const lines = []
  lines.push('📊 EXPLAIN 结果解读:')
  lines.push('  id: 查询序号（相同 id = 同表顺序执行，不同 id = 嵌套）')
  lines.push('  select_type: SIMPLE=简单查询/无子查询')
  lines.push('  type: 从优到劣 = system > const > eq_ref > ref > range > index > ALL')
  lines.push('  possible_keys: 可能使用的索引')
  lines.push('  key: 实际使用的索引（NULL = 没用到索引 ❌）')
  lines.push('  rows: 预估扫描行数（越小越好）')
  lines.push('  Extra: Using filesort/Using temporary = 需要优化 ⚠️')
  lines.push('')
  lines.push('┌────┬─────────────┬─────────────────┬────────┬────────────────┬────────────┬───────┬─────────────┬─────────────────────────────────────┐')
  lines.push('│ id │ select_type │     table        │  type  │ possible_keys  │    key     │ rows  │     ref     │                Extra                  │')
  lines.push('├────┼─────────────┼─────────────────┼────────┼────────────────┼────────────┼───────┼─────────────┼─────────────────────────────────────┤')
  rows.forEach(r => {
    const fmt = (v) => String(v).padEnd(r.length === 11 ? 13 : r.length === 9 ? 11 : r.length === 7 ? 7 : 35)
    lines.push(`│ ${String(r[0]).padEnd(2)} │ ${fmt(r[1])} │ ${fmt(r[2])} │ ${fmt(r[3])} │ ${fmt(r[4])} │ ${fmt(r[5])} │ ${String(r[6]).padStart(5)} │ ${fmt(r[7])} │ ${r[8].padEnd(35)} │`)
  })
  lines.push('└────┴─────────────┴─────────────────┴────────┴────────────────┴────────────┴───────┴─────────────┴─────────────────────────────────────┘')
  lines.push('')

  // 优化建议
  if (rows.some(r => r[3] === 'ALL')) {
    lines.push('⚠️ 优化建议: type=ALL 是全表扫描，建议添加 WHERE 条件并创建索引')
  }
  if (rows.some(r => r[8].includes('filesort'))) {
    lines.push('⚠️ 优化建议: Using filesort 性能差，建议为 ORDER BY 字段添加索引')
  }
  if (rows.some(r => r[8].includes('temporary'))) {
    lines.push('⚠️ 优化建议: Using temporary 性能差，建议优化 GROUP BY 或 DISTINCT')
  }
  return lines.join('\n')
}

function formatSql() {
  const formatted = sql.value
    .replace(/\s+/g, ' ')
    .replace(/\s*,\s*/g, ', ')
    .replace(/\bSELECT\b/gi, 'SELECT')
    .replace(/\bFROM\b/gi, '\nFROM')
    .replace(/\bWHERE\b/gi, '\nWHERE')
    .replace(/\b(AND|OR)\b/gi, '\n  $1')
    .replace(/\bGROUP BY\b/gi, '\nGROUP BY')
    .replace(/\bORDER BY\b/gi, '\nORDER BY')
    .replace(/\bHAVING\b/gi, '\nHAVING')
    .replace(/\bLIMIT\b/gi, '\nLIMIT')
    .replace(/\bJOIN\b/gi, '\nJOIN')
    .trim()
  sql.value = formatted
}

function resetSql() {
  sql.value = ''
  output.value = ''
}
</script>

<style scoped>
.pg-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: var(--vp-c-bg-soft);
  border-bottom: 1px solid var(--vp-c-divider);
}
.pg-title {
  font-weight: 600;
  margin-right: auto;
}
.pg-select {
  padding: 4px 10px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 13px;
}
.pg-btn {
  padding: 4px 12px;
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  color: var(--vp-c-text-1);
  font-size: 13px;
  cursor: pointer;
}
.pg-btn:hover { background: var(--vp-c-bg-soft); }
.pg-btn--primary {
  background: var(--mysql-blue, #00758F);
  color: white;
  border-color: var(--mysql-blue, #00758F);
}
.pg-btn--primary:hover { opacity: 0.85; }
.pg-tabs {
  display: flex;
  gap: 4px;
  padding: 6px 14px;
  background: var(--vp-c-bg-soft);
  border-top: 1px solid var(--vp-c-divider);
}
.pg-tab {
  padding: 4px 12px;
  border: none;
  background: transparent;
  color: var(--vp-c-text-2);
  font-size: 12px;
  cursor: pointer;
  border-radius: 4px;
}
.pg-tab--active {
  background: var(--vp-c-bg);
  color: var(--mysql-blue, #00758F);
  font-weight: 500;
}
.sql-output {
  white-space: pre;
  font-family: 'Menlo', 'Monaco', 'Consolas', monospace;
}
</style>