<template>
  <div class="cmd-container">
    <div class="cmd-toolbar">
      <button class="cmd-toolbar__btn" @click="runCommands">▶ 执行</button>
      <button class="cmd-toolbar__btn" @click="clearAll">🗑️ 清空</button>
      <button class="cmd-toolbar__btn" @click="loadSample">📝 示例</button>
      <span style="margin-left:auto;font-size:12px;color:var(--vp-c-text-2);">
        模拟 Redis 7 · 字符串 / Hash / List / Set / ZSet / Stream
      </span>
    </div>
    <div class="cmd-grid">
      <div class="cmd-input-panel">
        <div style="font-size:12px;color:var(--vp-c-text-2);margin-bottom:6px;">
          redis-cli
        </div>
        <textarea
          v-model="input"
          class="cmd-input-area"
          spellcheck="false"
          placeholder="例如：&#10;SET user:1 &quot;tom&quot;&#10;EXPIRE user:1 60&#10;GET user:1"
        />
        <div class="cmd-suggestion">
          💡 支持命令：SET / GET / DEL / EXISTS / EXPIRE / TTL / INCR / HSET / HGET / HGETALL / LPUSH / RPUSH / LRANGE / SADD / SMEMBERS / ZADD / ZRANGE / XADD / XLEN
        </div>
      </div>
      <div class="cmd-output-panel">
        <div style="font-size:12px;color:var(--vp-c-text-2);margin-bottom:6px;">
          output
        </div>
        <pre v-if="!output.length" class="cmd-output-area">点击「执行」运行命令</pre>
        <div v-else class="cmd-output-area">
          <div v-for="(line, idx) in output" :key="idx" :class="['cmd-result-line', `cmd-result-line--${line.type}`]">
            <span v-if="line.type === 'err'">ERR {{ line.text }}</span>
            <span v-else-if="line.type === 'info'">({{ line.text }})</span>
            <span v-else>{{ line.text }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const input = ref('SET greeting "Hello Redis"\nGET greeting\nEXPIRE greeting 60\nTTL greeting')
const output = ref([])
const store = ref({})

function clearAll() {
  input.value = ''
  output.value = []
  store.value = {}
}

function loadSample() {
  input.value = [
    'SET user:1:name "Alice"',
    'SET user:2:name "Bob"',
    'HSET user:1 profile age 28 city "Beijing"',
    'HGETALL user:1',
    'LPUSH tasks "task1"',
    'LPUSH tasks "task2"',
    'LRANGE tasks 0 -1',
    'ZADD scores 95 "alice" 87 "bob"',
    'ZRANGE scores 0 -1 WITHSCORES',
    'XADD events * type "click" page "home"',
    'XLEN events'
  ].join('\n')
  output.value = []
}

function tokenize(line) {
  // 简单的 token 解析（支持双引号字符串）
  const tokens = []
  let cur = ''
  let inStr = false
  for (let i = 0; i < line.length; i++) {
    const ch = line[i]
    if (ch === '"' && !inStr) {
      inStr = true
    } else if (ch === '"' && inStr) {
      inStr = false
    } else if (ch === ' ' && !inStr) {
      if (cur.length > 0) {
        tokens.push(cur)
        cur = ''
      }
    } else {
      cur += ch
    }
  }
  if (cur.length > 0) tokens.push(cur)
  return tokens
}

function isExpired(key) {
  const entry = store.value[key]
  if (!entry) return true
  if (entry.expireAt && Date.now() > entry.expireAt) {
    delete store.value[key]
    return true
  }
  return false
}

function cmdSet(tokens) {
  if (tokens.length < 3) return { type: 'err', text: 'wrong number of arguments for SET' }
  const key = tokens[1]
  const value = tokens.slice(2).join(' ')
  store.value[key] = { type: 'string', value, expireAt: null }
  return { type: 'ok', text: 'OK' }
}

function cmdGet(tokens) {
  if (tokens.length < 2) return { type: 'err', text: 'wrong number of arguments for GET' }
  const key = tokens[1]
  if (isExpired(key)) return { type: 'ok', text: '(nil)' }
  const entry = store.value[key]
  if (!entry || entry.type !== 'string') return { type: 'ok', text: '(nil)' }
  return { type: 'ok', text: `"${entry.value}"` }
}

function cmdDel(tokens) {
  let count = 0
  for (let i = 1; i < tokens.length; i++) {
    if (store.value[tokens[i]]) {
      delete store.value[tokens[i]]
      count++
    }
  }
  return { type: 'ok', text: `(integer) ${count}` }
}

function cmdExists(tokens) {
  let count = 0
  for (let i = 1; i < tokens.length; i++) {
    if (!isExpired(tokens[i])) count++
  }
  return { type: 'ok', text: `(integer) ${count}` }
}

function cmdExpire(tokens) {
  if (tokens.length < 3) return { type: 'err', text: 'wrong number of arguments' }
  const key = tokens[1]
  const ttl = parseInt(tokens[2])
  if (!store.value[key]) return { type: 'ok', text: '(integer) 0' }
  store.value[key].expireAt = Date.now() + ttl * 1000
  return { type: 'ok', text: '(integer) 1' }
}

function cmdTtl(tokens) {
  if (tokens.length < 2) return { type: 'err', text: 'wrong number of arguments' }
  const key = tokens[1]
  if (isExpired(key)) return { type: 'ok', text: '(integer) -2' }
  const entry = store.value[key]
  if (!entry || !entry.expireAt) return { type: 'ok', text: '(integer) -1' }
  const ttl = Math.ceil((entry.expireAt - Date.now()) / 1000)
  return { type: 'ok', text: `(integer) ${ttl}` }
}

function cmdIncr(tokens) {
  if (tokens.length < 2) return { type: 'err', text: 'wrong number of arguments' }
  const key = tokens[1]
  if (!store.value[key]) {
    store.value[key] = { type: 'string', value: '1', expireAt: null }
    return { type: 'ok', text: '(integer) 1' }
  }
  const cur = parseInt(store.value[key].value)
  store.value[key].value = String(cur + 1)
  return { type: 'ok', text: `(integer) ${cur + 1}` }
}

function cmdHset(tokens) {
  if (tokens.length < 4) return { type: 'err', text: 'wrong number of arguments' }
  const key = tokens[1]
  if (!store.value[key] || store.value[key].type !== 'hash') {
    store.value[key] = { type: 'hash', value: {}, expireAt: null }
  }
  for (let i = 2; i < tokens.length; i += 2) {
    if (i + 1 < tokens.length) {
      store.value[key].value[tokens[i]] = tokens[i + 1]
    }
  }
  return { type: 'ok', text: '(integer) 1' }
}

function cmdHget(tokens) {
  if (tokens.length < 3) return { type: 'err', text: 'wrong number of arguments' }
  const key = tokens[1]
  if (!store.value[key] || store.value[key].type !== 'hash') return { type: 'ok', text: '(nil)' }
  const v = store.value[key].value[tokens[2]]
  return { type: 'ok', text: v !== undefined ? `"${v}"` : '(nil)' }
}

function cmdHgetall(tokens) {
  if (tokens.length < 2) return { type: 'err', text: 'wrong number of arguments' }
  const key = tokens[1]
  if (!store.value[key] || store.value[key].type !== 'hash') return { type: 'ok', text: '(empty array)' }
  const lines = []
  for (const [k, v] of Object.entries(store.value[key].value)) {
    lines.push(`1) "${k}"`)
    lines.push(`2) "${v}"`)
  }
  output.value.push({ type: 'ok', text: lines.length ? lines.join('\n') : '(empty array)' })
  return null
}

function cmdLpush(tokens) {
  if (tokens.length < 3) return { type: 'err', text: 'wrong number of arguments' }
  const key = tokens[1]
  if (!store.value[key] || store.value[key].type !== 'list') {
    store.value[key] = { type: 'list', value: [], expireAt: null }
  }
  for (let i = 2; i < tokens.length; i++) {
    store.value[key].value.unshift(tokens[i])
  }
  return { type: 'ok', text: `(integer) ${store.value[key].value.length}` }
}

function cmdRpush(tokens) {
  if (tokens.length < 3) return { type: 'err', text: 'wrong number of arguments' }
  const key = tokens[1]
  if (!store.value[key] || store.value[key].type !== 'list') {
    store.value[key] = { type: 'list', value: [], expireAt: null }
  }
  for (let i = 2; i < tokens.length; i++) {
    store.value[key].value.push(tokens[i])
  }
  return { type: 'ok', text: `(integer) ${store.value[key].value.length}` }
}

function cmdLrange(tokens) {
  if (tokens.length < 4) return { type: 'err', text: 'wrong number of arguments' }
  const key = tokens[1]
  const start = parseInt(tokens[2])
  const stop = parseInt(tokens[3])
  if (!store.value[key] || store.value[key].type !== 'list') return { type: 'ok', text: '(empty array)' }
  const arr = store.value[key].value
  const len = arr.length
  const s = start < 0 ? Math.max(0, len + start) : start
  const e = stop < 0 ? len + stop : stop
  const slice = arr.slice(s, e + 1)
  const lines = []
  for (let i = 0; i < slice.length; i++) {
    lines.push(`${i + 1}) "${slice[i]}"`)
  }
  output.value.push({ type: 'ok', text: lines.length ? lines.join('\n') : '(empty array)' })
  return null
}

function cmdSadd(tokens) {
  if (tokens.length < 3) return { type: 'err', text: 'wrong number of arguments' }
  const key = tokens[1]
  if (!store.value[key] || store.value[key].type !== 'set') {
    store.value[key] = { type: 'set', value: new Set(), expireAt: null }
  }
  let added = 0
  for (let i = 2; i < tokens.length; i++) {
    if (!store.value[key].value.has(tokens[i])) added++
    store.value[key].value.add(tokens[i])
  }
  return { type: 'ok', text: `(integer) ${added}` }
}

function cmdSmembers(tokens) {
  if (tokens.length < 2) return { type: 'err', text: 'wrong number of arguments' }
  const key = tokens[1]
  if (!store.value[key] || store.value[key].type !== 'set') return { type: 'ok', text: '(empty array)' }
  const lines = []
  let i = 1
  for (const v of store.value[key].value) {
    lines.push(`${i++}) "${v}"`)
  }
  output.value.push({ type: 'ok', text: lines.length ? lines.join('\n') : '(empty array)' })
  return null
}

function cmdZadd(tokens) {
  if (tokens.length < 4) return { type: 'err', text: 'wrong number of arguments' }
  const key = tokens[1]
  if (!store.value[key] || store.value[key].type !== 'zset') {
    store.value[key] = { type: 'zset', value: new Map(), expireAt: null }
  }
  let added = 0
  for (let i = 2; i < tokens.length; i += 2) {
    if (i + 1 < tokens.length) {
      const score = parseFloat(tokens[i])
      const member = tokens[i + 1]
      if (!store.value[key].value.has(member)) added++
      store.value[key].value.set(member, score)
    }
  }
  return { type: 'ok', text: `(integer) ${added}` }
}

function cmdZrange(tokens) {
  if (tokens.length < 4) return { type: 'err', text: 'wrong number of arguments' }
  const key = tokens[1]
  const start = parseInt(tokens[2])
  const stop = parseInt(tokens[3])
  const withScores = tokens.includes('WITHSCORES')
  if (!store.value[key] || store.value[key].type !== 'zset') return { type: 'ok', text: '(empty array)' }
  const arr = [...store.value[key].value.entries()].sort((a, b) => a[1] - b[1])
  const len = arr.length
  const s = start < 0 ? Math.max(0, len + start) : start
  const e = stop < 0 ? len + stop : stop
  const slice = arr.slice(s, e + 1)
  const lines = []
  for (let i = 0; i < slice.length; i++) {
    lines.push(`${i + 1}) "${slice[i][0]}"`)
    if (withScores) lines.push(`2) "${slice[i][1]}"`)
  }
  output.value.push({ type: 'ok', text: lines.length ? lines.join('\n') : '(empty array)' })
  return null
}

function cmdXadd(tokens) {
  if (tokens.length < 2 || tokens[1] !== '*') return { type: 'err', text: 'syntax error' }
  const key = tokens[2] || 'default-stream'
  if (!store.value[key] || store.value[key].type !== 'stream') {
    store.value[key] = { type: 'stream', value: [], expireAt: null }
  }
  const id = `${Date.now()}-0`
  const fields = []
  for (let i = 3; i < tokens.length; i += 2) {
    if (i + 1 < tokens.length) fields.push({ k: tokens[i], v: tokens[i + 1] })
  }
  store.value[key].value.push({ id, fields })
  return { type: 'ok', text: `"${id}"` }
}

function cmdXlen(tokens) {
  if (tokens.length < 2) return { type: 'err', text: 'wrong number of arguments' }
  const key = tokens[1]
  if (!store.value[key] || store.value[key].type !== 'stream') return { type: 'ok', text: '(integer) 0' }
  return { type: 'ok', text: `(integer) ${store.value[key].value.length}` }
}

const handlers = {
  SET: cmdSet, GET: cmdGet, DEL: cmdDel, EXISTS: cmdExists,
  EXPIRE: cmdExpire, TTL: cmdTtl, INCR: cmdIncr,
  HSET: cmdHset, HGET: cmdHget, HGETALL: cmdHgetall,
  LPUSH: cmdLpush, RPUSH: cmdRpush, LRANGE: cmdLrange,
  SADD: cmdSadd, SMEMBERS: cmdSmembers,
  ZADD: cmdZadd, ZRANGE: cmdZrange,
  XADD: cmdXadd, XLEN: cmdXlen
}

function runCommands() {
  output.value = []
  const lines = input.value.split('\n').filter(l => l.trim().length > 0)
  for (const line of lines) {
    const tokens = tokenize(line)
    if (!tokens.length) continue
    const cmd = tokens[0].toUpperCase()
    output.value.push({ type: 'info', text: `${line} ➜` })
    const handler = handlers[cmd]
    if (!handler) {
      output.value.push({ type: 'err', text: `unknown command '${cmd}'` })
      continue
    }
    const result = handler(tokens)
    if (result) output.value.push(result)
  }
}
</script>
