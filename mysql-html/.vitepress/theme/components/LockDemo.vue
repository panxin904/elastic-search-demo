<template>
  <div class="lock-demo">
    <div class="ld-header">
      <h4>🔒 {{ demos[active].title }}</h4>
      <select v-model="active" class="ld-select">
        <option v-for="(d, i) in demos" :key="i" :value="i">{{ d.title }}</option>
      </select>
    </div>
    <p class="ld-desc">{{ demos[active].desc }}</p>

    <div class="ld-scenario">
      <div
        v-for="(tx, i) in state"
        :key="i"
        :class="['ld-tx', { 'ld-tx--active': tx.active, 'ld-tx--blocked': tx.blocked, 'ld-tx--error': tx.error }]"
      >
        <div class="ld-tx__head">
          <span class="ld-tx__name">事务 {{ tx.name }}</span>
          <span :class="['ld-tx__status', `ld-tx__status--${tx.status}`]">{{ statusText(tx.status) }}</span>
        </div>
        <div class="ld-tx__op">{{ tx.op }}</div>
        <div v-if="tx.lock" class="ld-tx__lock">🔒 持有: {{ tx.lock }}</div>
        <div v-if="tx.wait" class="ld-tx__wait">⏳ 等待: {{ tx.wait }}</div>
      </div>
    </div>

    <div class="ld-actions">
      <button class="ld-btn" @click="step" :disabled="state.some(t => t.active && !t.blocked && !t.error) || finished">
        ▶ 下一步
      </button>
      <button class="ld-btn" @click="reset">🔄 重置</button>
      <span class="ld-step">步骤: {{ stepIdx }} / {{ demos[active].steps.length }}</span>
    </div>

    <div class="ld-explain">
      <strong>💡 解读:</strong>
      <p v-for="(line, i) in currentExplain" :key="i">{{ line }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const demos = [
  {
    title: '共享锁 vs 排他锁',
    desc: '演示 SELECT...LOCK IN SHARE MODE 与 SELECT...FOR UPDATE 的兼容性',
    steps: [
      { tx: 0, status: 'idle', op: '准备读取 products WHERE id=1' },
      { tx: 0, status: 'running', op: 'BEGIN; SELECT ... LOCK IN SHARE MODE', lock: 'S-lock(id=1)' },
      { tx: 1, status: 'running', op: 'BEGIN; SELECT ... LOCK IN SHARE MODE', lock: 'S-lock(id=1)' },
      { tx: 1, status: 'done', op: '读取成功（共享锁兼容）' },
      { tx: 0, status: 'done', op: '事务 0 提交' },
      { tx: 1, status: 'done', op: '事务 1 提交' }
    ],
    explain: [
      '✓ 多个事务可以同时持有同一行的共享锁（S-lock）',
      '✓ 共享锁之间兼容，读读不阻塞',
      '⚠️ 但排他锁（X-lock）与任何锁都不兼容',
      '⚠️ SELECT...LOCK IN SHARE MODE 会阻塞 UPDATE/DELETE 同一行'
    ]
  },
  {
    title: '死锁演示',
    desc: '两个事务互相等待对方持有的锁，InnoDB 自动检测并回滚其中一个',
    steps: [
      { tx: 0, status: 'running', op: 'UPDATE accounts SET balance=balance-100 WHERE id=1', lock: 'X-lock(id=1)' },
      { tx: 1, status: 'running', op: 'UPDATE accounts SET balance=balance+100 WHERE id=2', lock: 'X-lock(id=2)' },
      { tx: 0, status: 'blocked', op: 'UPDATE accounts SET balance=balance+100 WHERE id=2', wait: 'X-lock(id=2)' },
      { tx: 1, status: 'blocked', op: 'UPDATE accounts SET balance=balance-100 WHERE id=1', wait: 'X-lock(id=1)' },
      { tx: 0, status: 'error', op: '❌ 检测到死锁！事务 0 被回滚', error: true },
      { tx: 1, status: 'running', op: '事务 1 获得锁，继续执行' },
      { tx: 1, status: 'done', op: '事务 1 提交' }
    ],
    explain: [
      '⚠️ 死锁 = 循环等待：A 等 B 的锁，B 等 A 的锁',
      '✓ InnoDB 自动检测死锁（innodb_deadlock_detect=on）',
      '✓ 选择回滚代价最小的事务（undo log 量少）',
      '✓ 另一事务继续执行，返回 ER_LOCK_DEADLOCK 错误',
      '💡 应用层应捕获 1213 错误并重试事务'
    ]
  },
  {
    title: '脏读（READ UNCOMMITTED）',
    desc: '事务 A 读取到事务 B 未提交的数据',
    steps: [
      { tx: 0, status: 'running', op: 'BEGIN; UPDATE accounts SET balance=999 WHERE id=1', lock: 'X-lock(id=1)' },
      { tx: 1, status: 'running', op: 'BEGIN; SELECT balance FROM accounts WHERE id=1' },
      { tx: 1, status: 'done', op: '读到 balance=999 ⚠️ 这是脏数据！' },
      { tx: 0, status: 'error', op: '事务 0 ROLLBACK', error: true },
      { tx: 1, status: 'error', op: '事务 1 读到的数据不存在 ❌ 脏读' }
    ],
    explain: [
      '⚠️ 脏读 = 读到其他事务未提交的数据',
      '⚠️ 该数据可能永远不会被提交（回滚），读到的就是错的',
      '✓ READ COMMITTED 隔离级别可以防止脏读',
      '✓ READ UNCOMMITTED 几乎不用（性能提升有限，破坏一致性）'
    ]
  },
  {
    title: '不可重复读 vs 幻读',
    desc: '同一事务内多次读取，结果不一致',
    steps: [
      { tx: 0, status: 'running', op: 'BEGIN; SELECT * FROM products WHERE category=1' },
      { tx: 0, status: 'done', op: '读到 5 条记录' },
      { tx: 1, status: 'running', op: 'INSERT INTO products (category) VALUES (1)' },
      { tx: 1, status: 'done', op: '插入成功并提交' },
      { tx: 0, status: 'running', op: '再次 SELECT * FROM products WHERE category=1' },
      { tx: 0, status: 'done', op: '⚠️ 读到 6 条！幻读发生' }
    ],
    explain: [
      '⚠️ 不可重复读 = 同一行，两次读结果不同（UPDATE 导致）',
      '⚠️ 幻读 = 同一范围，两次读记录数不同（INSERT/DELETE 导致）',
      '✓ REPEATABLE READ（MySQL 默认）解决不可重复读',
      '⚠️ REPEATABLE READ 在 MySQL 通过 MVCC 解决幻读（读快照）',
      '⚠️ 但当前读（FOR UPDATE）仍可能幻读，需要 SERIALIZABLE'
    ]
  }
]

const active = ref(0)
const stepIdx = ref(0)
const state = ref([
  { name: 'A', status: 'idle', op: '—', lock: '', wait: '', active: false, blocked: false, error: false },
  { name: 'B', status: 'idle', op: '—', lock: '', wait: '', active: false, blocked: false, error: false }
])

const finished = computed(() => stepIdx.value >= demos[active.value].steps.length)
const currentExplain = computed(() => demos[active.value].explain)

function statusText(s) {
  const map = { idle: '空闲', running: '执行中', blocked: '阻塞', done: '已提交', error: '已回滚' }
  return map[s] || s
}

function step() {
  if (finished.value) return
  const steps = demos[active.value].steps
  const s = steps[stepIdx.value]
  const tx = state.value[s.tx]
  Object.assign(tx, {
    status: s.status,
    op: s.op,
    lock: s.lock || '',
    wait: s.wait || '',
    active: s.status === 'running',
    blocked: s.status === 'blocked',
    error: s.error || false
  })
  stepIdx.value++
}

function reset() {
  stepIdx.value = 0
  state.value.forEach(tx => Object.assign(tx, {
    status: 'idle', op: '—', lock: '', wait: '',
    active: false, blocked: false, error: false
  }))
}

watch(active, reset)
</script>

<style scoped>
.ld-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.ld-header h4 { margin: 0; }
.ld-select {
  padding: 4px 10px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 13px;
}
.ld-desc {
  font-size: 13px;
  color: var(--vp-c-text-2);
  margin: 0 0 12px 0;
}
.ld-scenario {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 12px;
}
.ld-tx {
  padding: 12px;
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  transition: all 0.2s;
}
.ld-tx--active {
  border-color: var(--mysql-blue, #00758F);
  box-shadow: 0 0 0 2px rgba(0, 117, 143, 0.1);
}
.ld-tx--blocked {
  border-color: #f59e0b;
  background: #fef3c7;
  animation: pulse 1.5s infinite;
}
.ld-tx--error {
  border-color: #ef4444;
  background: #fee2e2;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
.ld-tx__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.ld-tx__name {
  font-weight: 600;
  font-size: 14px;
}
.ld-tx__status {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  background: var(--vp-c-bg-mute);
}
.ld-tx__status--running { background: #dbeafe; color: #1e40af; }
.ld-tx__status--blocked { background: #fef3c7; color: #92400e; }
.ld-tx__status--done { background: #dcfce7; color: #166534; }
.ld-tx__status--error { background: #fee2e2; color: #991b1b; }
.ld-tx__op {
  font-family: monospace;
  font-size: 12px;
  color: var(--vp-c-text-1);
  margin-bottom: 4px;
}
.ld-tx__lock,
.ld-tx__wait {
  font-size: 12px;
  margin-top: 4px;
}
.ld-tx__lock { color: #00758F; }
.ld-tx__wait { color: #92400e; }
.ld-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.ld-btn {
  padding: 5px 14px;
  background: var(--mysql-blue, #00758F);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}
.ld-btn:hover { opacity: 0.85; }
.ld-btn:disabled { background: #ccc; cursor: not-allowed; }
.ld-step {
  margin-left: auto;
  font-size: 12px;
  color: var(--vp-c-text-2);
}
.ld-explain {
  padding: 10px 12px;
  background: var(--vp-c-bg-mute);
  border-radius: 6px;
  font-size: 13px;
  line-height: 1.7;
}
.ld-explain strong { color: var(--mysql-blue, #00758F); }
.ld-explain p { margin: 4px 0; }
</style>