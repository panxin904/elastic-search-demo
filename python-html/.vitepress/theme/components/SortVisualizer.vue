<template>
  <div class="alg-container">
    <div class="alg-controls">
      <select v-model="algorithm" class="alg-toolbar__btn">
        <option value="bubble">冒泡排序</option>
        <option value="selection">选择排序</option>
        <option value="insertion">插入排序</option>
        <option value="quick">快速排序</option>
        <option value="merge">归并排序</option>
      </select>
      <button class="alg-toolbar__btn" @click="reset">🔄 重新生成</button>
      <button class="alg-toolbar__btn" @click="step">▶ 单步</button>
      <button class="alg-toolbar__btn" @click="run">▶▶ 自动播放</button>
      <button class="alg-toolbar__btn" @click="pause">⏸ 暂停</button>
      <span style="margin-left:12px;font-size:12px;color:var(--vp-c-text-2);">
        速度: <input type="range" v-model.number="speed" min="50" max="1000" /> {{ speed }}ms
      </span>
    </div>
    <div class="sort-array">
      <div
        v-for="(val, idx) in array"
        :key="idx"
        :class="['sort-bar', highlightClass(idx)]"
        :style="{ height: (val * 4) + 'px' }"
      >
        {{ val }}
      </div>
    </div>
    <div class="sort-info">
      <span class="sort-info__status">{{ status }}</span>
      <span class="sort-info__stats">
        比较: {{ comparisons }} | 交换: {{ swaps }} | 步骤: {{ stepCount }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const algorithm = ref('bubble')
const speed = ref(300)
const array = ref([])
const status = ref('点击 ▶ 自动播放 开始排序')
const comparisons = ref(0)
const swaps = ref(0)
const stepCount = ref(0)
const highlight = ref({ comparing: [], swapping: [], sorted: [] })
let running = false
let stepFn = null
let intervalId = null

function generate() {
  const arr = []
  for (let i = 0; i < 15; i++) arr.push(Math.floor(Math.random() * 40) + 5)
  array.value = arr
  status.value = '点击 ▶ 自动播放 开始排序'
  comparisons.value = 0
  swaps.value = 0
  stepCount.value = 0
  highlight.value = { comparing: [], swapping: [], sorted: [] }
}

function highlightClass(idx) {
  if (highlight.value.swapping.includes(idx)) return 'sort-bar--swap'
  if (highlight.value.comparing.includes(idx)) return 'sort-bar--compare'
  if (highlight.value.sorted.includes(idx)) return 'sort-bar--sorted'
  if (highlight.value.active === idx) return 'sort-bar--active'
  return ''
}

function reset() {
  pause()
  generate()
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms))
}

async function bubbleSort() {
  const arr = [...array.value]
  const n = arr.length
  for (let i = 0; i < n - 1; i++) {
    for (let j = 0; j < n - i - 1; j++) {
      comparisons.value++
      highlight.value = { comparing: [j, j + 1], swapping: [], sorted: arr.slice(n - i).map((_, idx) => n - 1 - idx) }
      array.value = [...arr]
      stepCount.value++
      await sleep(speed.value)
      if (arr[j] > arr[j + 1]) {
        [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]]
        swaps.value++
        highlight.value = { comparing: [], swapping: [j, j + 1], sorted: arr.slice(n - i).map((_, idx) => n - 1 - idx) }
        array.value = [...arr]
        await sleep(speed.value)
      }
    }
  }
  highlight.value = { comparing: [], swapping: [], sorted: arr.map((_, idx) => idx) }
  array.value = [...arr]
  status.value = '✓ 排序完成'
}

async function selectionSort() {
  const arr = [...array.value]
  const n = arr.length
  for (let i = 0; i < n - 1; i++) {
    let minIdx = i
    for (let j = i + 1; j < n; j++) {
      comparisons.value++
      highlight.value = { comparing: [minIdx, j], swapping: [], active: i, sorted: arr.slice(0, i).map((_, idx) => idx) }
      array.value = [...arr]
      stepCount.value++
      await sleep(speed.value)
      if (arr[j] < arr[minIdx]) minIdx = j
    }
    if (minIdx !== i) {
      [arr[i], arr[minIdx]] = [arr[minIdx], arr[i]]
      swaps.value++
      highlight.value = { comparing: [], swapping: [i, minIdx], active: i, sorted: arr.slice(0, i + 1).map((_, idx) => idx) }
      array.value = [...arr]
      await sleep(speed.value)
    }
  }
  highlight.value = { comparing: [], swapping: [], sorted: arr.map((_, idx) => idx) }
  array.value = [...arr]
  status.value = '✓ 排序完成'
}

async function insertionSort() {
  const arr = [...array.value]
  const n = arr.length
  for (let i = 1; i < n; i++) {
    const key = arr[i]
    let j = i - 1
    while (j >= 0) {
      comparisons.value++
      highlight.value = { comparing: [j, j + 1], swapping: [], sorted: arr.slice(0, i).map((_, idx) => idx) }
      array.value = [...arr]
      stepCount.value++
      await sleep(speed.value)
      if (arr[j] > key) {
        arr[j + 1] = arr[j]
        swaps.value++
        highlight.value = { comparing: [], swapping: [j, j + 1], sorted: arr.slice(0, i).map((_, idx) => idx) }
        array.value = [...arr]
        await sleep(speed.value)
        j--
      } else break
    }
    arr[j + 1] = key
    array.value = [...arr]
  }
  highlight.value = { comparing: [], swapping: [], sorted: arr.map((_, idx) => idx) }
  array.value = [...arr]
  status.value = '✓ 排序完成'
}

async function quickSort() {
  const arr = [...array.value]
  await quickSortHelper(arr, 0, arr.length - 1)
  highlight.value = { comparing: [], swapping: [], sorted: arr.map((_, idx) => idx) }
  array.value = [...arr]
  status.value = '✓ 排序完成'
}

async function quickSortHelper(arr, lo, hi) {
  if (lo >= hi) return
  const pivot = arr[hi]
  let i = lo - 1
  for (let j = lo; j < hi; j++) {
    comparisons.value++
    highlight.value = { comparing: [j, hi], swapping: [], active: hi }
    array.value = [...arr]
    stepCount.value++
    await sleep(speed.value)
    if (arr[j] < pivot) {
      i++
      [arr[i], arr[j]] = [arr[j], arr[i]]
      swaps.value++
      highlight.value = { comparing: [], swapping: [i, j], active: hi }
      array.value = [...arr]
      await sleep(speed.value)
    }
  }
  [arr[i + 1], arr[hi]] = [arr[hi], arr[i + 1]]
  swaps.value++
  await quickSortHelper(arr, lo, i)
  await quickSortHelper(arr, i + 2, hi)
}

async function mergeSort() {
  const arr = [...array.value]
  await mergeSortHelper(arr, 0, arr.length - 1)
  highlight.value = { comparing: [], swapping: [], sorted: arr.map((_, idx) => idx) }
  array.value = [...arr]
  status.value = '✓ 排序完成'
}

async function mergeSortHelper(arr, lo, hi) {
  if (lo >= hi) return
  const mid = Math.floor((lo + hi) / 2)
  await mergeSortHelper(arr, lo, mid)
  await mergeSortHelper(arr, mid + 1, hi)
  await merge(arr, lo, mid, hi)
}

async function merge(arr, lo, mid, hi) {
  const left = arr.slice(lo, mid + 1)
  const right = arr.slice(mid + 1, hi + 1)
  let i = 0, j = 0, k = lo
  while (i < left.length && j < right.length) {
    comparisons.value++
    highlight.value = { comparing: [lo + i, mid + 1 + j], swapping: [], active: k }
    array.value = [...arr]
    stepCount.value++
    await sleep(speed.value)
    if (left[i] <= right[j]) {
      arr[k++] = left[i++]
    } else {
      arr[k++] = right[j++]
    }
    swaps.value++
    array.value = [...arr]
  }
  while (i < left.length) {
    arr[k++] = left[i++]
    swaps.value++
    array.value = [...arr]
  }
  while (j < right.length) {
    arr[k++] = right[j++]
    swaps.value++
    array.value = [...arr]
  }
}

async function step() {
  status.value = '单步模式暂未实现，请使用自动播放'
}

async function run() {
  if (running) return
  running = true
  status.value = '排序中...'
  highlight.value = { comparing: [], swapping: [], sorted: [] }
  comparisons.value = 0
  swaps.value = 0
  stepCount.value = 0

  const fns = { bubble: bubbleSort, selection: selectionSort, insertion: insertionSort, quick: quickSort, merge: mergeSort }
  const fn = fns[algorithm.value]
  if (fn) await fn()
  running = false
}

function pause() {
  running = false
  status.value = '已暂停'
}

generate()
</script>
