# §8.79 intra-site dups 治理建议
基于 audit-content.py (2026-08-28) 检测到的 58 处同站重复标题分析：
## 总览
- P0 真重复（需合并/删除）: **2** 组
- P1 模板词（建议扩展白名单豁免）: **10** 组
- P2 cheatsheet 设计模式（不动）: **5** 组
- 其他（同话题两页各写角度）: **13** 组

---

## P0 · 真重复（需手动修）

### '为什么需要读写分离？'（2 处）

- `mysql/read-write-split.md`
- `mysql/read-write-split.md`

### '创建 DataFrame'（2 处）

- `python/pandas.md`
- `python/pandas.md`

---

## P1 · 模板词（建议豁免白名单）

- '🆚 vs LangGraph'
- '🆚 替代品'
- '🆚 vs Deployment'
- '与 Decorator 区别'
- '🆚 三者对比'
- 'Saga 模式详解'
- '实战案例：定位锁竞争'
- '三大指标详解'
- 'COPY 协议（最快）'
- '实战：登录 + 爬取'

建议加入 TEMPLATE_TITLES 白名单：

```python
TEMPLATE_TITLES.add(
    'COPY 协议（最快）',
    'Saga 模式详解',
    '三大指标详解',
    '与 Decorator 区别',
    '实战案例：定位锁竞争',
    '实战：登录 + 爬取',
    '🆚 vs Deployment',
    '🆚 vs LangGraph',
    '🆚 三者对比',
    '🆚 替代品',
)
```
---

## P2 · cheatsheet 设计模式（不动）

- 'OTel Collector 详解'（2 处）
- 'Hugging Face'（2 处）
- '计算机视觉'（2 处）
- 'LLM 应用开发'（2 处）
- '自然语言处理'（2 处）

---

## 其他：同话题多页面

- 'OTel Collector 详解' (2处) - observability, observability
- 'Hugging Face' (2处) - python, python
- '计算机视觉' (2处) - python, python
- 'LLM 应用开发' (2处) - python, python
- '自然语言处理' (2处) - python, python
- 'KafkaTemplate' (2处) - kafka, kafka
- 'htop - top 的升级版' (2处) - linux, linux
- '关联数组（map）' (2处) - linux, linux
- '开启慢查询日志' (2处) - mysql, mysql
- '慢查询日志格式' (2处) - mysql, mysql
- '性能提升数据' (2处) - mysql, mysql
- '自动填充（create_time / update_time）' (2处) - mysql, mysql
- 'ShardingSphere 是什么？' (2处) - mysql, mysql
- '何时选 PG' (2处) - postgresql, postgresql
- '数据分析实战' (2处) - python, python
- '第一个爬虫' (2处) - python, python
- 'Fixture（测试夹具）' (2处) - python, python
- '参数化测试' (2处) - python, python

---

## 治理建议

1. P0 真重复（合并/删除）：人工 review 后合并或拆分
2. P1 模板词：批量加入 `audit-content.py` TEMPLATE_TITLES 白名单
3. P2 cheatsheet：设计模式合理，不修
