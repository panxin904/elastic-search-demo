<template>
  <div class="lock-container">
    <div class="lock-toolbar">
      <button class="lock-toolbar__btn" @click="startSimulation">▶ 模拟抢锁</button>
      <button class="lock-toolbar__btn" @click="reset">🔄 重置</button>
      <select v-model="lockType" style="padding:5px 10px;border-radius:4px;border:1px solid var(--vp-c-divider);">
        <option value="setnx">SETNX + EXPIRE（基础）</option>
        <option value="setnx-correct">SET NX EX（正确）</option>
        <option value="redisson">Redisson（含看门狗）</option>
      </select>
      <span style="margin-left:auto;font-size:12px;color:var(--vp-c-text-2);">
        {{ lockType === 'setnx' ? '❌ 有问题：原子性破坏' : lockType === 'setnx-correct' ? '✅ 原子但无续期' : '✅✅ 含续期 + Lua 脚本' }}
      </span>
    </div>

    <div class="lock-scenario">
      <div style="background:var(--vp-c-bg-soft);padding:12px;border-radius:6px;margin-bottom:12px;font-size:13px;">
        <b>场景：</b> 5 个客户端同时抢锁 <code>lock:order:1001</code>，持锁 2 秒后自动释放。
      </div>
      <div v-for="client in clients" :key="client.id" :class="['lock-row', `lock-row--${client.status}`]">
        <div class="lock-row__id">{{ client.id }}</div>
        <div class="lock-row__msg">{{ client.message }}</div>
        <div :class="['lock-row__status', `lock-row__status--${client.status}`]">
          {{ client.status === 'running' ? '运行中' : client.status === 'waiting' ? '等待中' : client.status === 'done' ? '已完成' : '失败' }}
        </div>
      </div>
    </div>

    <div class="ds-info-panel">
      <div v-if="lockType === 'setnx'">
        <b>问题：</b>SETNX 和 EXPIRE 不是原子操作。<br/>
        ❌ SETNX 成功后，客户端崩溃，锁永远不会释放（无 EXPIRE）<br/>
        ❌ 即使两个都执行成功，中间崩溃也会导致锁永久失效
      </div>
      <div v-else-if="lockType === 'setnx-correct'">
        <b>改进：</b>SET NX EX 单一原子命令。<br/>
        ✅ 持锁 / 设置过期原子完成<br/>
        ⚠️ 但如果持锁业务超过 TTL，锁会被自动释放，业务未结束锁已失效
      </div>
      <div v-else>
        <b>Redisson：</b>看门狗机制 + Lua 脚本。<br/>
        ✅ 默认锁 30s，watchdog 每 10s 自动续期（续到 30s）<br/>
        ✅ 解锁用 Lua 脚本判断 value（避免误删别人的锁）<br/>
        ✅ 完美解决以上两个问题
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const lockType = ref('setnx-correct')
const clients = reactive([
  { id: 'client-A', status: 'waiting', message: '' },
  { id: 'client-B', status: 'waiting', message: '' },
  { id: 'client-C', status: 'waiting', message: '' },
  { id: 'client-D', status: 'waiting', message: '' },
  { id: 'client-E', status: 'waiting', message: '' }
])
let lockHolder = null

function delay(ms) {
  return new Promise(r => setTimeout(r, ms))
}

async function tryAcquireLock(client) {
  // 模拟加锁
  if (lockHolder) {
    client.status = 'waiting'
    client.message = `锁被 ${lockHolder.id} 持有，等待中...`
    return false
  }
  // SETNX (模拟：if 锁不存在则设置成功)
  lockHolder = client
  client.status = 'running'
  client.message = `${client.id} 获得锁，执行业务逻辑...`
  return true
}

async function releaseLock(client) {
  if (lockHolder === client) {
    lockHolder = null
    client.status = 'done'
    client.message = `${client.id} 释放锁，完成任务`
  }
}

async function runClient(client) {
  const acquired = await tryAcquireLock(client)
  if (!acquired) {
    // 等待直到锁释放
    while (lockHolder) {
      await delay(300)
    }
    return runClient(client)
  }
  // 持锁执行
  await delay(2000)
  await releaseLock(client)
}

async function startSimulation() {
  reset()
  await delay(200)
  // 顺序启动 5 个客户端（模拟并发）
  await Promise.all(clients.map(c => runClient(c)))
}

function reset() {
  lockHolder = null
  clients.forEach(c => {
    c.status = 'waiting'
    c.message = ''
  })
}
</script>
