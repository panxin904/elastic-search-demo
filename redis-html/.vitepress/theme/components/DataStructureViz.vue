<template>
  <div class="ds-container">
    <div class="ds-tabs">
      <button
        v-for="t in tabs" :key="t.id"
        :class="['ds-tab', { 'ds-tab--active': active === t.id }]"
        @click="active = t.id"
      >{{ t.label }}</button>
    </div>
    <div ref="canvasRef" class="ds-canvas">
      <template v-if="active === 'sds'">
        <div class="ds-canvas-cell" :style="{ top: '30px', left: '20px' }">len: 5</div>
        <div class="ds-canvas-cell" :style="{ top: '30px', left: '110px' }">alloc: 6</div>
        <div class="ds-canvas-cell" :style="{ top: '30px', left: '210px' }">flags: 0</div>
        <div class="ds-canvas-cell" :style="{ top: '30px', left: '310px' }">'H'</div>
        <div class="ds-canvas-cell" :style="{ top: '30px', left: '400px' }">'e'</div>
        <div class="ds-canvas-cell" :style="{ top: '30px', left: '480px' }">'l'</div>
        <div class="ds-canvas-cell" :style="{ top: '30px', left: '560px' }">'l'</div>
        <div class="ds-canvas-cell" :style="{ top: '30px', left: '640px' }">'o'</div>
        <div class="ds-canvas-cell ds-canvas-cell--array" :style="{ top: '30px', left: '720px' }">'\0'</div>
        <div style="position:absolute;top:80px;left:20px;font-size:13px;color:#666;">
          ← header（5 字节） →&nbsp;&nbsp;&nbsp;&nbsp;← 字符缓冲（6 字节含 \0）→
        </div>
        <div style="position:absolute;top:120px;left:20px;font-size:12px;color:#888;">
          预分配空间 alloc=6 &gt; len=5，下次追加无需重新分配内存
        </div>
      </template>

      <template v-else-if="active === 'dict'">
        <div style="position:absolute;top:20px;left:20px;font-size:13px;font-weight:600;color:#1e40af;">
          ht[0] (rehash 后将迁移)
        </div>
        <div v-for="(b, i) in 4" :key="`a${i}`" :style="{
          position:'absolute', top: `${60 + i * 70}px`, left: '20px',
          width:'40px',height:'40px',background:'#dbeafe',border:'2px solid #1e40af',
          display:'flex',alignItems:'center',justifyContent:'center',fontWeight:600
        }">slot{{ b - 1 }}</div>
        <div :style="{ position:'absolute', top:'70px',  left:'100px', color:'#1e40af' }">name → "Alice"</div>
        <div :style="{ position:'absolute', top:'140px', left:'100px', color:'#1e40af' }">age → 28</div>
        <div :style="{ position:'absolute', top:'210px', left:'100px', color:'#1e40af' }">city → "Beijing"</div>
        <div :style="{ position:'absolute', top:'280px', left:'100px', color:'#1e40afe' }">null</div>

        <div style="position:absolute;top:20px;left:380px;font-size:13px;font-weight:600;color:#166534;">
          ht[1]（扩容后的新表，渐进式 rehash 中）
        </div>
        <div v-for="(b, i) in 8" :key="`b${i}`" :style="{
          position:'absolute', top: `${60 + i * 38}px`, left: '380px',
          width:'40px',height:'30px',background:i < 4 ? '#dcfce7' : '#fee2e2',
          border: '2px solid ' + (i < 4 ? '#166534' : '#aaa'),
          display:'flex',alignItems:'center',justifyContent:'center',fontSize:'11px'
        }">slot{{ b - 1 }}</div>
        <div :style="{ position:'absolute', top:'67px',  left:'460px', fontSize:'11px' }">name</div>
        <div :style="{ position:'absolute', top:'105px', left:'460px', fontSize:'11px' }">city</div>
        <div :style="{ position:'absolute', top:'143px', left:'460px', fontSize:'11px' }">age</div>
      </template>

      <template v-else-if="active === 'skiplist'">
        <div v-for="(n, i) in skiplistNodes" :key="`n${i}`">
          <div
            v-for="lvl in n.levels"
            :key="`n${i}l${lvl}`"
            class="ds-canvas-cell ds-canvas-cell--level"
            :style="{
              top: `${40 + (5 - lvl) * 60}px`,
              left: `${40 + i * 130}px`
            }"
          >{{ n.value }}</div>
          <div v-if="n.pointer"
            class="ds-canvas-cell ds-canvas-cell--pointer"
            :style="{ top: `${40 + (5 - 0) * 60}px`, left: `${40 + i * 130 + 90}px`, fontSize: '10px' }"
          >L{{ n.levels.length }}→</div>
        </div>
        <div style="position:absolute;top:340px;left:20px;font-size:12px;color:#888;">
          平均 O(log N) 查找 · 多级索引加速 · Redis ZSet 内部使用
        </div>
      </template>

      <template v-else-if="active === 'quicklist'">
        <div style="position:absolute;top:20px;left:20px;font-size:13px;font-weight:600;color:#166534;">
          quicklistNode → listpack → listpack → ...
        </div>
        <div v-for="i in 3" :key="i" class="ds-canvas-cell ds-canvas-cell--array" :style="{
          top: '60px', left: `${20 + i * 180}px`, width: '150px'
        }">
          listpack#{{ i }}
        </div>
        <div v-for="i in 3" :key="`b${i}`" :style="{
          position:'absolute', top: '110px', left: `${20 + i * 180 + 20}px`,
          width: '110px', height: '40px', background: '#fff',
          border: '1px solid #166534', display:'flex', alignItems:'center', justifyContent:'space-around',
          fontSize:'11px'
        }">
          <span>v1</span><span>v2</span><span>v3</span>
        </div>
        <div style="position:absolute;top:180px;left:20px;font-size:12px;color:#888;">
          quicklist = 双向链表 + 节点内 listpack（双向链表 + 压缩列表的混合结构）
        </div>
      </template>
    </div>

    <div class="ds-info-panel">
      <div v-if="active === 'sds'">
        <b>SDS（Simple Dynamic String）</b>：Redis 自实现的字符串结构。相比 C 字符串：<br/>
        ✅ O(1) 取长度（len 字段） · ✅ 杜绝缓冲区溢出 · ✅ 减少内存重分配次数（alloc 预分配 + 惰性释放） · ✅ 二进制安全（len 控制边界）
      </div>
      <div v-else-if="active === 'dict'">
        <b>Dict 哈希表</b>：Redis 所有 key-value 的底层存储。<br/>
        ✅ 自动扩容缩容（负载因子 0.1/1/5 触发） · ✅ 渐进式 rehash（不阻塞主线程，分批迁移） · ✅ 链地址法解决哈希冲突
      </div>
      <div v-else-if="active === 'skiplist'">
        <b>SkipList 跳表</b>：Redis ZSet 的底层实现之一。<br/>
        ✅ 平均 O(log N) 查找 / 插入 / 删除 · ✅ 实现简单（相比红黑树） · ✅ 支持范围查询 ZRANGEBYSCORE
      </div>
      <div v-else-if="active === 'quicklist'">
        <b>QuickList</b>：Redis List 的底层实现。<br/>
        ✅ 双向链表 + listpack 节点 · ✅ 平衡了内存占用和访问性能 · ✅ 替代了老的 linkedlist + ziplist
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const tabs = [
  { id: 'sds', label: '📝 SDS 字符串' },
  { id: 'dict', label: '🗂️ Dict 哈希表' },
  { id: 'skiplist', label: '🦘 SkipList 跳表' },
  { id: 'quicklist', label: '🔗 QuickList' }
]

const active = ref('sds')

const skiplistNodes = [
  { value: 'L1', levels: [5, 4, 3, 2, 1], pointer: true },
  { value: 'L3', levels: [5, 4, 2, 1], pointer: true },
  { value: 'L5', levels: [5, 4, 3, 1], pointer: true },
  { value: 'L8', levels: [5, 3, 1], pointer: true },
  { value: 'L12', levels: [5, 2, 1], pointer: false }
]
</script>
