<template>
  <div class="cheatsheet">
    <div class="cs-search">
      <input v-model="search" type="text" placeholder="🔍 搜索 SQL（输入关键字过滤）..." class="cs-input" />
      <select v-model="category" class="cs-select">
        <option value="all">全部</option>
        <option value="basic">基础 CRUD</option>
        <option value="ddl">DDL</option>
        <option value="query">查询</option>
        <option value="agg">聚合</option>
        <option value="join">JOIN</option>
        <option value="index">索引</option>
        <option value="transaction">事务</option>
        <option value="performance">性能</option>
        <option value="admin">运维</option>
      </select>
    </div>

    <div v-for="(item, i) in filtered" :key="i" class="cheatsheet__item">
      <div class="cheatsheet__title">
        <span class="cs-tag" :data-cat="item.category">{{ categoryLabel(item.category) }}</span>
        {{ item.title }}
        <button class="cs-copy" @click="copy(item.code)">{{ copied === i ? '✓ 已复制' : '📋 复制' }}</button>
      </div>
      <div v-if="item.desc" class="cheatsheet__desc">{{ item.desc }}</div>
      <pre class="cheatsheet__code">{{ item.code }}</pre>
    </div>

    <div v-if="filtered.length === 0" class="cs-empty">
      <p>😅 没有匹配「{{ search }}」的 SQL 模板</p>
      <p>试试搜索关键字：SELECT、索引、JOIN、事务、EXPLAIN、备份...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const search = ref('')
const category = ref('all')
const copied = ref(-1)

const items = [
  // 基础 CRUD
  { category: 'basic', title: '插入单条数据', desc: 'INSERT 单行', code: `INSERT INTO users (name, email, age)\nVALUES ('张三', 'zhangsan@example.com', 25);` },
  { category: 'basic', title: '批量插入', desc: 'INSERT 多行（性能远高于循环单条插入）', code: `INSERT INTO users (name, email, age) VALUES\n  ('李四', 'lisi@example.com', 30),\n  ('王五', 'wangwu@example.com', 28),\n  ('赵六', 'zhaoliu@example.com', 35);` },
  { category: 'basic', title: '根据 ID 查询', desc: '最常用查询', code: `SELECT * FROM users WHERE id = 100;\n-- 或查询多个字段\nSELECT id, name, email FROM users WHERE id IN (1, 2, 3);` },
  { category: 'basic', title: '更新数据', desc: 'UPDATE 务必带 WHERE', code: `-- ⚠️ 危险：会更新所有行\nUPDATE users SET status = 1;\n\n-- ✅ 安全：带 WHERE 条件\nUPDATE users SET status = 1, updated_at = NOW()\nWHERE id = 100 AND status = 0;` },
  { category: 'basic', title: '删除数据', desc: 'DELETE 也务必带 WHERE', code: `-- ✅ 删除指定记录\nDELETE FROM users WHERE id = 100;\n\n-- ⚠️ 更安全：软删除（推荐）\nUPDATE users SET deleted_at = NOW() WHERE id = 100;\n\n-- 物理删除整表（慎用！）\nTRUNCATE TABLE users;` },

  // DDL
  { category: 'ddl', title: '创建表（含索引）', desc: '建表时同步加索引', code: `CREATE TABLE products (\n  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',\n  name VARCHAR(200) NOT NULL COMMENT '商品名称',\n  category_id INT NOT NULL COMMENT '类目ID',\n  price DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT '价格',\n  stock INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '库存',\n  status TINYINT NOT NULL DEFAULT 1 COMMENT '1=上架 0=下架',\n  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,\n  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,\n  PRIMARY KEY (id),\n  KEY idx_category (category_id),\n  KEY idx_category_status (category_id, status),\n  KEY idx_created (created_at)\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品表';` },
  { category: 'ddl', title: '修改表结构', desc: 'ALTER TABLE 常用操作', code: `-- 添加列\nALTER TABLE users ADD COLUMN phone VARCHAR(20) AFTER email;\n\n-- 修改列类型\nALTER TABLE users MODIFY COLUMN age SMALLINT;\n\n-- 删除列\nALTER TABLE users DROP COLUMN phone;\n\n-- 添加索引\nALTER TABLE users ADD INDEX idx_phone (phone);\n\n-- 重命名表\nRENAME TABLE old_name TO new_name;` },
  { category: 'ddl', title: '创建视图', desc: '虚拟表（不存数据）', code: `CREATE OR REPLACE VIEW v_active_users AS\nSELECT id, name, email, created_at\nFROM users\nWHERE status = 1 AND deleted_at IS NULL;\n\n-- 使用视图\nSELECT * FROM v_active_users WHERE created_at > '2025-01-01';` },

  // 查询
  { category: 'query', title: '分页查询', desc: 'LIMIT + OFFSET 分页', code: `-- 基础分页（深分页性能差）\nSELECT id, name FROM products\nORDER BY id LIMIT 20 OFFSET 100;\n\n-- ✅ 推荐：基于主键的\"游标分页\"\nSELECT id, name FROM products\nWHERE id > 100  -- 上次最后一条的 id\nORDER BY id LIMIT 20;` },
  { category: 'query', title: '模糊查询', desc: 'LIKE 与全文索引', code: `-- 前缀匹配（可用索引）\nSELECT * FROM products WHERE name LIKE 'iPhone%';\n\n-- 中间包含（不能用索引 ⚠️）\nSELECT * FROM products WHERE name LIKE '%手机%';\n\n-- ✅ 推荐：全文索引\nSELECT * FROM products\nWHERE MATCH(name, description) AGAINST('iPhone 手机' IN NATURAL LANGUAGE MODE);` },
  { category: 'query', title: '去重查询', desc: 'DISTINCT 与 GROUP BY', code: `-- DISTINCT 去重\nSELECT DISTINCT category_id FROM products;\n\n-- GROUP BY 去重（更灵活，可加聚合）\nSELECT category_id, COUNT(*) AS cnt\nFROM products\nGROUP BY category_id\nORDER BY cnt DESC;` },

  // 聚合
  { category: 'agg', title: '常用聚合函数', desc: 'COUNT/SUM/AVG/MAX/MIN', code: `SELECT\n  COUNT(*) AS total,\n  COUNT(DISTINCT user_id) AS active_users,\n  SUM(amount) AS total_amount,\n  AVG(amount) AS avg_amount,\n  MAX(amount) AS max_amount,\n  MIN(amount) AS min_amount\nFROM orders\nWHERE created_at >= '2025-01-01';` },
  { category: 'agg', title: 'GROUP BY 分组', desc: '按维度统计', code: `SELECT\n  DATE(created_at) AS date,\n  category_id,\n  COUNT(*) AS order_cnt,\n  SUM(amount) AS total\nFROM orders\nWHERE created_at >= '2025-01-01'\nGROUP BY date, category_id\nHAVING order_cnt > 10\nORDER BY date DESC, total DESC;` },
  { category: 'agg', title: '窗口函数', desc: 'MySQL 8.0+ 强大功能', code: `-- 每个用户按消费金额排名\nSELECT\n  user_id,\n  order_date,\n  amount,\n  RANK() OVER (PARTITION BY user_id ORDER BY amount DESC) AS rk,\n  SUM(amount) OVER (PARTITION BY user_id ORDER BY order_date) AS running_total\nFROM orders;\n\n-- 取每个分类 TOP 3\nSELECT * FROM (\n  SELECT\n    *, ROW_NUMBER() OVER (PARTITION BY category_id ORDER BY sales DESC) AS rn\n  FROM products\n) t WHERE rn <= 3;` },

  // JOIN
  { category: 'join', title: 'INNER JOIN 内连接', desc: '只保留两表都有匹配的', code: `SELECT\n  o.id AS order_id,\n  u.name AS user_name,\n  o.amount,\n  o.created_at\nFROM orders o\nINNER JOIN users u ON o.user_id = u.id\nWHERE o.created_at >= '2025-01-01'\nORDER BY o.created_at DESC;` },
  { category: 'join', title: 'LEFT JOIN 左连接', desc: '保留左表全部，右表无匹配为 NULL', code: `SELECT\n  u.id,\n  u.name,\n  COUNT(o.id) AS order_count,\n  IFNULL(SUM(o.amount), 0) AS total_spent\nFROM users u\nLEFT JOIN orders o ON u.id = o.user_id\nGROUP BY u.id, u.name\nORDER BY total_spent DESC\nLIMIT 100;` },
  { category: 'join', title: '子查询 vs JOIN', desc: '推荐用 JOIN（性能更好）', code: `-- 子查询（可读但可能慢）\nSELECT * FROM products\nWHERE category_id IN (SELECT id FROM categories WHERE status = 1);\n\n-- ✅ 改写为 JOIN（通常更快）\nSELECT p.*\nFROM products p\nINNER JOIN categories c ON p.category_id = c.id\nWHERE c.status = 1;` },

  // 索引
  { category: 'index', title: '创建索引', desc: '最常用索引操作', code: `-- 普通索引\nCREATE INDEX idx_user_email ON users(email);\n\n-- 唯一索引\nCREATE UNIQUE INDEX uk_user_phone ON users(phone);\n\n-- 复合索引（注意字段顺序！）\nCREATE INDEX idx_order_user_date ON orders(user_id, created_at DESC);\n\n-- 前缀索引（节省空间）\nCREATE INDEX idx_url_prefix ON logs(url(20));` },
  { category: 'index', title: '查看索引', desc: '查看表的索引信息', code: `SHOW INDEX FROM products;\n-- 或\nSHOW KEYS FROM products;` },
  { category: 'index', title: '删除索引', desc: 'DROP INDEX', code: `DROP INDEX idx_user_email ON users;\n\n-- MySQL 5.7 也支持\nALTER TABLE users DROP INDEX idx_user_email;` },
  { category: 'index', title: '强制使用/忽略索引', desc: '优化器调试用', code: `SELECT * FROM products\nUSE INDEX (idx_category_status)\nWHERE category_id = 1 AND status = 1;\n\n-- 强制忽略某个索引\nSELECT * FROM products\nIGNORE INDEX (idx_name)\nWHERE name = 'iPhone';` },

  // 事务
  { category: 'transaction', title: '事务基础', desc: 'BEGIN / COMMIT / ROLLBACK', code: `START TRANSACTION;\n-- 或 BEGIN;\n\nUPDATE accounts SET balance = balance - 100 WHERE id = 1;\nUPDATE accounts SET balance = balance + 100 WHERE id = 2;\n\n-- 检查无误后提交\nCOMMIT;\n\n-- 出错回滚\n-- ROLLBACK;` },
  { category: 'transaction', title: '设置隔离级别', desc: 'MySQL 默认为 REPEATABLE READ', code: `-- 会话级（推荐）\nSET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;\n\n-- 全局级\nSET GLOBAL TRANSACTION ISOLATION LEVEL REPEATABLE READ;\n\n-- 查看当前隔离级别\nSELECT @@transaction_isolation;` },
  { category: 'transaction', title: '保存点', desc: '部分回滚', code: `START TRANSACTION;\n\nINSERT INTO orders (user_id, amount) VALUES (1, 100);\nSAVEPOINT sp1;\n\nINSERT INTO order_items (order_id, product_id) VALUES (LAST_INSERT_ID(), 101);\n-- 假设这步出错\nROLLBACK TO sp1;  -- 回滚到保存点，但保留 orders\n\nCOMMIT;  -- 提交 orders` },

  // 性能
  { category: 'performance', title: 'EXPLAIN 分析', desc: '看懂查询计划', code: `EXPLAIN SELECT * FROM products\nWHERE category_id = 1 AND status = 1\nORDER BY created_at DESC LIMIT 20;\n\n-- 详细分析（8.0.18+）\nEXPLAIN ANALYZE SELECT ...;` },
  { category: 'performance', title: 'PROFILE 追踪', desc: 'MySQL 8.0 详细耗时', code: `SET profiling = 1;\n\nSELECT COUNT(*) FROM products WHERE category_id = 1;\n\nSHOW PROFILES;\nSHOW PROFILE FOR QUERY 1;` },
  { category: 'performance', title: '优化器提示', desc: '影响执行计划', code: `-- 强制 JOIN 顺序\nSELECT /*+ JOIN_ORDER(orders, users) */ *\nFROM orders STRAIGHT_JOIN users ON orders.user_id = users.id;\n\n-- 强制使用某索引\nSELECT /*+ INDEX(products idx_category) */ *\nFROM products WHERE category_id = 1;\n\n-- 直方图提示（8.0+）\nANALYZE TABLE products UPDATE HISTOGRAM ON price;` },

  // 运维
  { category: 'admin', title: '查看进程', desc: '排查慢查询', code: `-- 查看所有连接\nSHOW PROCESSLIST;\n-- 或详细版（带完整 SQL）\nSHOW FULL PROCESSLIST;\n\n-- 查看正在执行的语句\nSELECT * FROM information_schema.PROCESSLIST\nWHERE COMMAND != 'Sleep'\nORDER BY TIME DESC;` },
  { category: 'admin', title: '杀死慢查询', desc: 'KILL PROCESS', code: `-- 先查看进程 ID\nSHOW PROCESSLIST;\n\n-- 杀掉指定 ID 的查询\nKILL 12345;\n-- KILL QUERY 12345; -- 只杀查询，不断连接\n-- KILL CONNECTION 12345; -- 杀连接` },
  { category: 'admin', title: '查看表大小', desc: '库表空间占用', code: `SELECT\n  table_schema AS '数据库',\n  table_name AS '表名',\n  ROUND(data_length / 1024 / 1024, 2) AS '数据MB',\n  ROUND(index_length / 1024 / 1024, 2) AS '索引MB',\n  ROUND((data_length + index_length) / 1024 / 1024, 2) AS '总MB',\n  table_rows AS '行数'\nFROM information_schema.tables\nWHERE table_schema NOT IN ('mysql', 'information_schema', 'performance_schema')\nORDER BY (data_length + index_length) DESC\nLIMIT 20;` },
  { category: 'admin', title: '查看锁等待', desc: '排查锁阻塞', code: `SELECT * FROM performance_schema.data_locks LIMIT 10;\n\n-- 谁在等谁\nSELECT\n  blocking_pid AS blocker,\n  waiting_pid AS waiter,\n  waiting_query AS sql_text\nFROM performance_schema.events_statements_history\nWHERE waiting_pid IS NOT NULL;` }
]

const filtered = computed(() => {
  return items.filter(item => {
    const matchCat = category.value === 'all' || item.category === category.value
    const matchSearch = !search.value ||
      item.title.toLowerCase().includes(search.value.toLowerCase()) ||
      item.code.toLowerCase().includes(search.value.toLowerCase()) ||
      (item.desc && item.desc.toLowerCase().includes(search.value.toLowerCase()))
    return matchCat && matchSearch
  })
})

function categoryLabel(c) {
  const map = { basic: 'CRUD', ddl: 'DDL', query: '查询', agg: '聚合', join: 'JOIN', index: '索引', transaction: '事务', performance: '性能', admin: '运维' }
  return map[c] || c
}

function copy(code) {
  navigator.clipboard.writeText(code)
  copied.value = items.findIndex(i => i.code === code)
  setTimeout(() => copied.value = -1, 1500)
}
</script>

<style scoped>
.cs-search {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}
.cs-input {
  flex: 1;
  padding: 8px 14px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 14px;
}
.cs-select {
  padding: 8px 12px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 14px;
}
.cs-tag {
  display: inline-block;
  padding: 2px 8px;
  margin-right: 8px;
  background: var(--mysql-blue, #00758F);
  color: white;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
  vertical-align: middle;
}
.cheatsheet__title {
  display: flex;
  align-items: center;
  gap: 8px;
}
.cs-copy {
  margin-left: auto;
  padding: 2px 10px;
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  font-size: 12px;
  color: var(--vp-c-text-2);
  cursor: pointer;
}
.cs-copy:hover { background: var(--vp-c-bg-soft); }
.cs-empty {
  padding: 40px;
  text-align: center;
  color: var(--vp-c-text-2);
  background: var(--vp-c-bg-soft);
  border-radius: 8px;
}
</style>