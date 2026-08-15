<template>
  <div class="ch-container">
    <div class="ch-search">
      <input v-model="keyword" placeholder="搜索（print、for、list、dict...）" class="ch-input" />
      <select v-model="category" class="ch-filter" style="padding: 8px 12px; border: 1px solid var(--vp-c-divider); border-radius: 6px; background: var(--vp-c-bg);">
        <option value="all">全部分类</option>
        <option value="basic">基础语法</option>
        <option value="control">控制流</option>
        <option value="data">数据结构</option>
        <option value="func">函数</option>
        <option value="class">类与面向对象</option>
        <option value="file">文件与异常</option>
        <option value="lib">常用库</option>
      </select>
    </div>
    <div v-if="!filtered.length" class="ch-empty">😢 没有匹配的内容</div>
    <div v-else class="ch-grid">
      <div v-for="item in filtered" :key="item.name" class="ch-card">
        <div class="ch-card__cat">{{ categoryLabel(item.category) }}</div>
        <div class="ch-card__title">{{ item.name }}</div>
        <div class="ch-card__syntax">{{ item.syntax }}</div>
        <div class="ch-card__desc">{{ item.desc }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const keyword = ref('')
const category = ref('all')

const items = [
  // 基础语法
  { cat: 'basic', name: '变量赋值', syntax: 'name = value\nx, y = 1, 2', desc: 'Python 动态类型，无需声明' },
  { cat: 'basic', name: '打印输出', syntax: 'print(value, end="\\n")', desc: '标准输出，默认换行' },
  { cat: 'basic', name: 'f-string 格式化', syntax: 'f"Hello {name}, age {age}"', desc: 'Python 3.6+ 推荐' },
  { cat: 'basic', name: '类型转换', syntax: 'int(s)\nfloat(s)\nstr(x)', desc: '字符串与数字互转' },
  { cat: 'basic', name: '类型检查', syntax: 'isinstance(obj, type)\ntype(obj)', desc: '检查对象类型' },
  { cat: 'basic', name: '多变量赋值', syntax: 'a, b, c = 1, 2, 3', desc: '元组解包' },
  { cat: 'basic', name: '注释', syntax: '# 单行注释\n"""多行字符串（可作文档）"""', desc: '注释代码' },

  // 控制流
  { cat: 'control', name: 'if 条件', syntax: 'if condition:\n    ...\nelif ...:\n    ...\nelse:\n    ...', desc: '条件分支' },
  { cat: 'control', name: 'for 循环', syntax: 'for item in iterable:\n    ...', desc: '遍历可迭代对象' },
  { cat: 'control', name: 'while 循环', syntax: 'while condition:\n    ...', desc: '条件循环' },
  { cat: 'control', name: 'break/continue', syntax: 'break  # 跳出循环\ncontinue  # 跳过本次', desc: '循环控制' },
  { cat: 'control', name: '三元表达式', syntax: 'x if condition else y', desc: '简化版 if-else' },
  { cat: 'control', name: 'match-case', syntax: 'match value:\n    case 1: ...\n    case _: ...', desc: 'Python 3.10+ 模式匹配' },

  // 数据结构
  { cat: 'data', name: 'list 列表', syntax: '[1, 2, 3]\nlist.append(x)\nlist[i]', desc: '可变有序序列' },
  { cat: 'data', name: 'tuple 元组', syntax: '(1, 2, 3)\n(1,)  # 单元素元组', desc: '不可变有序序列' },
  { cat: 'data', name: 'dict 字典', syntax: '{"a": 1, "b": 2}\ndict[key] = value', desc: '键值对映射' },
  { cat: 'data', name: 'set 集合', syntax: '{1, 2, 3}\nset.add(x)\nset & set2  # 交集', desc: '无序不重复元素' },
  { cat: 'data', name: 'list 切片', syntax: 'lst[start:stop:step]\nlst[::-1]  # 反转', desc: '高效切片操作' },
  { cat: 'data', name: '列表推导式', syntax: '[x*2 for x in range(10) if x > 5]', desc: '简洁创建列表' },
  { cat: 'data', name: '字典推导式', syntax: '{k: v for k, v in items}', desc: '简洁创建字典' },
  { cat: 'data', name: '解包', syntax: 'a, *b, c = [1, 2, 3, 4, 5]', desc: '解包到多个变量' },

  // 函数
  { cat: 'func', name: '函数定义', syntax: 'def func(a, b=10, *args, **kwargs):\n    """docstring"""\n    return result', desc: '使用 def 关键字' },
  { cat: 'func', name: 'lambda 匿名函数', syntax: 'lambda x: x * 2', desc: '单行函数' },
  { cat: 'func', name: '装饰器', syntax: '@decorator\ndef func():\n    ...', desc: '修改函数行为' },
  { cat: 'func', name: '生成器', syntax: 'def gen():\n    yield value', desc: '惰性求值迭代器' },
  { cat: 'func', name: '类型注解', syntax: 'def func(x: int) -> str:', desc: 'Python 3.5+ 类型提示' },

  // 类
  { cat: 'class', name: '类定义', syntax: 'class MyClass:\n    def __init__(self, x):\n        self.x = x', desc: '面向对象基础' },
  { cat: 'class', name: '继承', syntax: 'class Child(Parent):\n    def method(self):\n        super().method()', desc: '子类继承父类' },
  { cat: 'class', name: '魔术方法', syntax: '__init__\n__str__\n__repr__\n__len__', desc: 'Python 内置方法' },
  { cat: 'class', name: '类装饰器', syntax: '@dataclass\nclass Point:\n    x: int\n    y: int', desc: 'Python 3.7+ 数据类' },
  { cat: 'class', name: 'property', syntax: '@property\ndef name(self):\n    return self._name', desc: '属性访问控制' },

  // 文件与异常
  { cat: 'file', name: '读取文件', syntax: 'with open("file.txt") as f:\n    content = f.read()', desc: '推荐用 with 自动关闭' },
  { cat: 'file', name: '写入文件', syntax: 'with open("out.txt", "w") as f:\n    f.write(text)', desc: '"w" 覆盖，"a" 追加' },
  { cat: 'file', name: 'try-except', syntax: 'try:\n    ...\nexcept Exception as e:\n    ...\nfinally:\n    ...', desc: '异常处理' },
  { cat: 'file', name: 'with 语句', syntax: 'with open(path) as f:\n    # 自动关闭', desc: '上下文管理器' },

  // 常用库
  { cat: 'lib', name: 'os 模块', syntax: 'import os\nos.listdir(path)\nos.path.join(a, b)', desc: '操作系统接口' },
  { cat: 'lib', name: 'sys 模块', syntax: 'import sys\nsys.argv\nsys.exit()', desc: 'Python 运行时环境' },
  { cat: 'lib', name: 'json 模块', syntax: 'import json\njson.dumps(obj)\njson.loads(s)', desc: 'JSON 序列化' },
  { cat: 'lib', name: 'requests', syntax: 'import requests\nr = requests.get(url)', desc: 'HTTP 客户端（需 pip install）' },
  { cat: 'lib', name: 'pandas', syntax: 'import pandas as pd\ndf = pd.read_csv(file)', desc: '数据分析库' },
  { cat: 'lib', name: 'numpy', syntax: 'import numpy as np\narr = np.array([1, 2, 3])', desc: '数值计算库' },
  { cat: 'lib', name: 'pytest', syntax: 'def test_func():\n    assert func() == 1', desc: '测试框架' },
  { cat: 'lib', name: 'logging', syntax: 'import logging\nlog = logging.getLogger(__name__)\nlog.info("msg")', desc: '日志记录' }
]

const filtered = computed(() => {
  return items.filter(i => {
    const kw = keyword.value.toLowerCase().trim()
    const catMatch = category.value === 'all' || i.cat === category.value
    const kwMatch = !kw || i.name.toLowerCase().includes(kw) || i.syntax.toLowerCase().includes(kw) || i.desc.toLowerCase().includes(kw)
    return catMatch && kwMatch
  })
})

function categoryLabel(c) {
  const map = { basic: '基础语法', control: '控制流', data: '数据结构', func: '函数', class: '面向对象', file: '文件/异常', lib: '常用库' }
  return map[c] || c
}
</script>
