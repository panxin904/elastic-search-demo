<template>
  <div class="api-container">
    <div class="api-toolbar">
      <select v-model="category" class="alg-toolbar__btn">
        <option value="list">list 列表</option>
        <option value="dict">dict 字典</option>
        <option value="str">str 字符串</option>
        <option value="json">json JSON</option>
        <option value="file">file 文件</option>
        <option value="os">os 操作系统</option>
      </select>
      <input v-model="keyword" placeholder="搜索 API（append、get、open...）" class="alg-toolbar__btn" style="flex:1;min-width:200px;" />
    </div>
    <div style="padding: 16px; max-height: 600px; overflow-y: auto;">
      <div v-for="api in filtered" :key="api.name" class="api-call">
        <div class="api-call__name">{{ api.name }}<span style="color: var(--vp-c-text-2); font-weight: normal; margin-left: 8px;">{{ api.label }}</span></div>
        <div class="api-call__sig">{{ api.sig }}</div>
        <div class="api-call__desc">{{ api.desc }}</div>
      </div>
      <div v-if="!filtered.length" class="ch-empty">😢 没有匹配的 API</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const category = ref('list')
const keyword = ref('')

const apis = [
  // list
  { cat: 'list', name: 'list.append', label: '追加元素', sig: 'list.append(x)', desc: '在列表末尾添加元素 x' },
  { cat: 'list', name: 'list.extend', label: '扩展列表', sig: 'list.extend(iterable)', desc: '用可迭代对象扩展列表' },
  { cat: 'list', name: 'list.insert', label: '插入元素', sig: 'list.insert(i, x)', desc: '在索引 i 处插入元素 x' },
  { cat: 'list', name: 'list.remove', label: '移除元素', sig: 'list.remove(x)', desc: '移除第一个值为 x 的元素' },
  { cat: 'list', name: 'list.pop', label: '弹出元素', sig: 'list.pop([i])', desc: '移除并返回索引 i 处元素（默认末尾）' },
  { cat: 'list', name: 'list.sort', label: '排序', sig: 'list.sort(key=None, reverse=False)', desc: '原地排序列表' },
  { cat: 'list', name: 'list.reverse', label: '反转', sig: 'list.reverse()', desc: '原地反转列表' },
  { cat: 'list', name: 'len(list)', label: '长度', sig: 'len(list)', desc: '返回列表元素数量' },
  { cat: 'list', name: 'list[0]', label: '索引访问', sig: 'list[i]', desc: '访问索引 i 处的元素' },
  { cat: 'list', name: 'list[1:3]', label: '切片', sig: 'list[start:stop:step]', desc: '列表切片' },
  { cat: 'list', name: 'for x in list', label: '遍历', sig: 'for x in list:', desc: '遍历列表元素' },
  { cat: 'list', name: 'list comprehension', label: '列表推导式', sig: '[x for x in iterable]', desc: '从一个可迭代对象创建列表' },
  { cat: 'list', name: 'sorted(list)', label: '返回新列表', sig: 'sorted(iterable)', desc: '返回新排序列表，不修改原列表' },
  { cat: 'list', name: 'list.count', label: '计数', sig: 'list.count(x)', desc: '统计 x 出现次数' },
  { cat: 'list', name: 'list.index', label: '查找', sig: 'list.index(x)', desc: '返回 x 第一次出现的索引' },

  // dict
  { cat: 'dict', name: 'dict[key]', label: '访问/设置', sig: 'dict[key] = value', desc: '访问或设置键值对' },
  { cat: 'dict', name: 'dict.get', label: '安全访问', sig: 'dict.get(key, default=None)', desc: '安全获取值，键不存在返回默认值' },
  { cat: 'dict', name: 'dict.keys', label: '所有键', sig: 'dict.keys()', desc: '返回所有键的视图' },
  { cat: 'dict', name: 'dict.values', label: '所有值', sig: 'dict.values()', desc: '返回所有值的视图' },
  { cat: 'dict', name: 'dict.items', label: '键值对', sig: 'dict.items()', desc: '返回所有 (key, value) 元组' },
  { cat: 'dict', name: 'for k,v in dict', label: '遍历', sig: 'for k, v in dict.items():', desc: '遍历字典' },
  { cat: 'dict', name: 'dict.pop', label: '移除', sig: 'dict.pop(key)', desc: '移除并返回 key 对应的值' },
  { cat: 'dict', name: 'dict.update', label: '合并', sig: 'dict.update(other)', desc: '用 other 字典更新当前字典' },
  { cat: 'dict', name: 'dict comprehension', label: '字典推导式', sig: '{k:v for k,v in iterable}', desc: '从一个可迭代对象创建字典' },
  { cat: 'dict', name: 'len(dict)', label: '长度', sig: 'len(dict)', desc: '返回键值对数量' },

  // str
  { cat: 'str', name: 'str.split', label: '分割', sig: 'str.split(sep, maxsplit=-1)', desc: '用 sep 分割字符串为列表' },
  { cat: 'str', name: 'str.join', label: '连接', sig: 'str.join(iterable)', desc: '用 str 连接可迭代对象' },
  { cat: 'str', name: 'str.replace', label: '替换', sig: 'str.replace(old, new, count=-1)', desc: '替换字符串中的子串' },
  { cat: 'str', name: 'str.strip', label: '去空白', sig: 'str.strip([chars])', desc: '去除两端空白字符' },
  { cat: 'str', name: 'str.upper', label: '转大写', sig: 'str.upper()', desc: '转换为大写' },
  { cat: 'str', name: 'str.lower', label: '转小写', sig: 'str.lower()', desc: '转换为小写' },
  { cat: 'str', name: 'str.startswith', label: '前缀', sig: 'str.startswith(prefix)', desc: '是否以 prefix 开头' },
  { cat: 'str', name: 'str.endswith', label: '后缀', sig: 'str.endswith(suffix)', desc: '是否以 suffix 结尾' },
  { cat: 'str', name: 'f-string', label: 'f-string', sig: 'f"Hello {name}"', desc: '格式化字符串（Python 3.6+）' },

  // json
  { cat: 'json', name: 'json.dumps', label: '转 JSON 字符串', sig: 'json.dumps(obj, ensure_ascii=False)', desc: 'Python 对象转 JSON 字符串' },
  { cat: 'json', name: 'json.loads', label: '解析 JSON', sig: 'json.loads(s)', desc: 'JSON 字符串转 Python 对象' },
  { cat: 'json', name: 'json.dump', label: '写入文件', sig: 'json.dump(obj, fp)', desc: '写入 JSON 到文件对象' },
  { cat: 'json', name: 'json.load', label: '读取文件', sig: 'json.load(fp)', desc: '从文件读取 JSON' },

  // file
  { cat: 'file', name: 'open', label: '打开文件', sig: 'open(path, mode="r")', desc: '打开文件（常用模式：r/w/a/rb/wb）' },
  { cat: 'file', name: 'file.read', label: '读取', sig: 'file.read(size=-1)', desc: '读取文件内容' },
  { cat: 'file', name: 'file.readline', label: '读一行', sig: 'file.readline()', desc: '读取一行' },
  { cat: 'file', name: 'file.readlines', label: '读所有行', sig: 'file.readlines()', desc: '返回所有行的列表' },
  { cat: 'file', name: 'file.write', label: '写入', sig: 'file.write(s)', desc: '写入字符串' },
  { cat: 'file', name: 'file.writelines', label: '写多行', sig: 'file.writelines(lines)', desc: '写入多行（不含换行符）' },
  { cat: 'file', name: 'with open()', label: '上下文管理', sig: 'with open(path) as f:', desc: '自动关闭文件（推荐）' },

  // os
  { cat: 'os', name: 'os.path.join', label: '路径拼接', sig: 'os.path.join(*paths)', desc: '拼接路径（跨平台）' },
  { cat: 'os', name: 'os.path.exists', label: '判断存在', sig: 'os.path.exists(path)', desc: '判断路径是否存在' },
  { cat: 'os', name: 'os.path.isfile', label: '判断文件', sig: 'os.path.isfile(path)', desc: '判断是否为文件' },
  { cat: 'os', name: 'os.path.isdir', label: '判断目录', sig: 'os.path.isdir(path)', desc: '判断是否为目录' },
  { cat: 'os', name: 'os.listdir', label: '列目录', sig: 'os.listdir(path)', desc: '列出目录下的文件和子目录' },
  { cat: 'os', name: 'os.makedirs', label: '创建目录', sig: 'os.makedirs(path, exist_ok=False)', desc: '递归创建目录' },
  { cat: 'os', name: 'os.environ', label: '环境变量', sig: 'os.environ["KEY"]', desc: '获取环境变量' }
]

const filtered = computed(() => {
  return apis.filter(a => {
    const kw = keyword.value.toLowerCase().trim()
    const catMatch = category.value === 'all' || a.cat === category.value
    const kwMatch = !kw || a.name.toLowerCase().includes(kw) || a.desc.toLowerCase().includes(kw)
    return catMatch && kwMatch
  })
})
</script>
