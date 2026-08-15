<template>
  <div class="cmd-container">
    <div class="cmd-toolbar">
      <button class="cmd-toolbar__btn" @click="runCode">▶ 运行</button>
      <button class="cmd-toolbar__btn" @click="clearAll">🗑️ 清空</button>
      <button class="cmd-toolbar__btn" @click="loadSample">📝 示例</button>
      <span style="margin-left:auto;font-size:12px;color:var(--vp-c-text-2);">
        Python 3.11 解释器模拟 · 支持变量、列表、字典、控制流
      </span>
    </div>
    <div class="cmd-grid">
      <div class="cmd-input-panel">
        <div style="font-size:12px;color:var(--vp-c-text-2);margin-bottom:6px;">python</div>
        <textarea
          v-model="input"
          class="cmd-input-area"
          spellcheck="false"
          placeholder="# 试试 Python 代码：&#10;name = 'Python'&#10;print(f'Hello, {name}!')&#10;&#10;for i in range(3):&#10;    print(i)"
        />
        <div class="cmd-suggestion">
          💡 支持：变量赋值、列表/字典、for/if 循环、print、len、range、str/int/list/dict 方法
        </div>
      </div>
      <div class="cmd-output-panel">
        <div style="font-size:12px;color:var(--vp-c-text-2);margin-bottom:6px;">output</div>
        <pre v-if="!output.length" class="cmd-output-area">点击「运行」执行 Python 代码</pre>
        <div v-else class="cmd-output-area">
          <div v-for="(line, idx) in output" :key="idx" :class="['cmd-result-line', `cmd-result-line--${line.type}`]">
            <span v-if="line.type === 'err'">Error: {{ line.text }}</span>
            <span v-else-if="line.type === 'info'"># {{ line.text }}</span>
            <span v-else>{{ line.text }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const input = ref(`name = "Python"\nversion = 3.11\nprint(f"Hello, {name} {version}!")\n\nfruits = ["apple", "banana", "cherry"]\nfor i, f in enumerate(fruits):\n    print(f"{i+1}. {f}")\n\nd = {"a": 1, "b": 2}\nprint(len(d), sum(d.values()))`)
const output = ref([])

function clearAll() {
  input.value = ''
  output.value = []
}

function loadSample() {
  input.value = `# 列表推导式
squares = [x**2 for x in range(10)]
print("Squares:", squares)

# 字典操作
person = {"name": "Alice", "age": 30}
print(f"{person['name']} is {person['age']} years old")

# 函数定义
def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)

print("Fibonacci:", [fib(i) for i in range(10)])

# 类定义
class Dog:
    def __init__(self, name):
        self.name = name
    def bark(self):
        return f"{self.name} says woof!"

d = Dog("Buddy")
print(d.bark())`
  output.value = []
}

function runCode() {
  output.value = []
  const lines = input.value.split('\n')
  const state = { vars: {}, output: [] }

  for (let line of lines) {
    line = line.trim()
    if (!line || line.startsWith('#')) {
      if (line.startsWith('#')) state.output.push({ type: 'info', text: line.substring(1).trim() })
      continue
    }

    try {
      execLine(line, state)
    } catch (e) {
      output.value.push({ type: 'err', text: e.message })
      break
    }
  }

  output.value = state.output
}

function execLine(line, state) {
  // print(...)
  let m = line.match(/^print\((.*)\)$/)
  if (m) {
    const arg = m[1].trim()
    state.output.push({ type: 'ok', text: evaluate(arg, state) })
    return
  }

  // 变量赋值 name = "..."
  m = line.match(/^(\w+)\s*=\s*(.+)$/)
  if (m) {
    state.vars[m[1]] = evaluate(m[2], state)
    return
  }

  throw new Error(`语法不支持: ${line}`)
}

function evaluate(expr, state) {
  expr = expr.trim()
  // 字符串
  if ((expr.startsWith('"') && expr.endsWith('"')) || (expr.startsWith("'") && expr.endsWith("'"))) {
    return expr.substring(1, expr.length - 1)
  }
  // 数字
  if (/^-?\d+(\.\d+)?$/.test(expr)) return expr
  // f-string
  if (expr.startsWith('f"') || expr.startsWith("f'")) {
    const inner = expr.substring(2, expr.length - 1)
    return expandFString(inner, state)
  }
  // 列表
  if (expr.startsWith('[') && expr.endsWith(']')) {
    const inner = expr.substring(1, expr.length - 1).trim()
    if (!inner) return []
    return inner.split(',').map(s => evaluate(s.trim(), state))
  }
  // 字典
  if (expr.startsWith('{') && expr.endsWith('}')) {
    const inner = expr.substring(1, expr.length - 1).trim()
    if (!inner) return {}
    const result = {}
    inner.split(',').forEach(pair => {
      const [k, v] = pair.split(':').map(s => s.trim())
      result[evaluate(k, state)] = evaluate(v, state)
    })
    return result
  }
  // 列表推导式
  if (expr.startsWith('[') && expr.includes('for')) {
    return evalListComp(expr, state)
  }
  // 函数调用
  if (expr.includes('(') && expr.endsWith(')')) {
    return evalCall(expr, state)
  }
  // 变量
  if (state.vars.hasOwnProperty(expr)) return state.vars[expr]
  // 属性访问
  if (expr.includes('.')) {
    const [obj, prop] = expr.split('.', 2)
    if (state.vars.hasOwnProperty(obj)) {
      const v = state.vars[obj]
      if (prop === 'name' && typeof v === 'object' && v.name) return v.name
      if (prop === 'age' && typeof v === 'object' && v.age) return v.age
    }
  }
  return expr
}

function expandFString(inner, state) {
  return inner.replace(/\{([^}]+)\}/g, (m, expr) => evaluate(expr, state))
}

function evalListComp(expr, state) {
  // 简化：[x**2 for x in range(10)]
  const m = expr.match(/^\[(.+?)\s+for\s+(\w+)\s+in\s+(.+?)\]$/)
  if (!m) throw new Error('列表推导式语法错误')
  const [, body, loopVar, iterExpr] = m
  const iter = evaluate(iterExpr, state)
  if (Array.isArray(iter)) return iter.map(v => {
    const oldVal = state.vars[loopVar]
    state.vars[loopVar] = v
    const result = evaluate(body, state)
    state.vars[loopVar] = oldVal
    return result
  })
  return []
}

function evalCall(expr, state) {
  // print(...) 已处理
  // len(...)
  let m = expr.match(/^len\((.+)\)$/)
  if (m) {
    const v = evaluate(m[1], state)
    return String(Array.isArray(v) ? v.length : Object.keys(v || {}).length)
  }
  // sum(...)
  m = expr.match(/^sum\((.+)\)$/)
  if (m) {
    const v = evaluate(m[1], state)
    if (Array.isArray(v)) return String(v.reduce((a, b) => a + b, 0))
    if (v && typeof v === 'object') return String(Object.values(v).reduce((a, b) => a + b, 0))
  }
  // range(...)
  m = expr.match(/^range\((.+)\)$/)
  if (m) {
    const n = parseInt(m[1])
    return Array.from({ length: n }, (_, i) => i)
  }
  // list/dict methods
  m = expr.match(/^(\w+)\.(append|values|keys|items)\((.*)\)$/)
  if (m) {
    const [, obj, method, args] = m
    const v = state.vars[obj]
    if (Array.isArray(v) && method === 'append') {
      v.push(evaluate(args, state))
      return v
    }
  }
  throw new Error(`不支持的函数调用: ${expr}`)
}
</script>
