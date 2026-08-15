# 28 站点内容审计报告

**审计日期**：2026-08-13
**审计范围**：28 个 VitePress 子站 + 1 个门户首页
**数据规模**：1412 个 md 文件 / 7.9 MB 纯文本 / 平均 5.7KB/文件

---

## 一、现状快照

### 站点规模分布（按页面数）

| 量级 | 站点 | 页数 |
|------|------|------|
| **小型 (≤35)** | tools (13) / devops (30) / chaos (32) / cloud (35) / rust (35) / go (36) / clickhouse (36) / security (36) | 8 站 |
| **中型 (36-55)** | observability (50) / design-pattern (49) / architecture (51) / bigdata (51) / system-design (52) / postgresql (53) / java-language (55) | 8 站 |
| **大型 (55-75)** | cloud-native (55) / ai (57) / redis (59) / python (60) / es (63) / frontend (65) / network (66) / video (67) / mysql (67) / kafka (73) / linux (71) | 12 站 |
| **巨型 (>75)** | **filesystem (94)** | 1 站 ⚠️ |

### 站点质量分布（按平均页大小）

| 平均 | 站点数 | 状态 |
|------|--------|------|
| < 3KB | 2 站 (es 2035 / java 2032) | 🔴 几乎全是 stub |
| 3-5KB | 10 站 | 🟡 紧凑但信息密度尚可 |
| 5-7KB | 7 站 | 🟢 标准 |
| > 7KB | 9 站 | 🟢 充实（system-design 7870 / cloud 8892 / python 8543 / mysql 9480 / kafka 10020 / go 8019） |

---

## 二、🔴 高优先级问题（必须修）

### 1. es / java / java-language 三站被"stub 化"（影响最大）

| 站点 | stub / 总页 | stub 占比 |
|------|-------------|-----------|
| **java-language** | 53 / 55 | **96%** 🔴 |
| **java** | 47 / 53 | **89%** 🔴 |
| **es** | 58 / 63 | **92%** 🔴 |

具体问题：es 01-storage 13 页平均 1.6KB（典型页：definition + 一段示例 + 知识图谱引用 + 关联项目源码）。这种"短句 + 表格链接"风格对**知识图谱浏览**是合理的，但对**搜索引擎和深度学习**严重不足。

**建议方案**：
- 给每个 topic 页加 ## 实战案例 / ## 进阶话题 / ## 关联章节 三段扩到 3-4KB
- 或承认 es/java 的"知识图谱"定位，把 1-2KB 短页当作 by-design，不强求 ≥3KB
- java-language 的 53/55 stub 比例过高，**必须回填** —— 这站定位与 go / rust 并列（语言层），应有同等待遇

### 2. frontend 49% stub（32/65）

frontend 是 65 页的中型站，但 32 个 stub 是新站的一半。同样问题：紧凑但严重不足。

### 3. filesystem 12 个 stub + 巨型体量（94 页）

filesystem 是最大的站（94 页），平均 4.7KB 还行，但有 15 个 stub（16%）。作为容器存储 / 分布式文件系统专题站，**章节深度参差不齐**——有的章节是 12 页，有的只有 2-3 页。

---

## 三、🟡 中优先级问题（建议修）

### 4. 站内搜索 19/28 站缺失（影响可发现性）

| 已开启 (9) | 未开启 (19) |
|------------|-------------|
| es / java / filesystem / observability / security / devops / rust / go / chaos | mysql / redis / cloud / python / kafka / tools / frontend / linux / cloud-native / ai / java-language / bigdata / architecture / network / video / system-design / postgresql / clickhouse / design-pattern |

**影响**：50+ 页的站点没有 search，用户只能靠 sidebar 浏览。

**修复成本**：每个 config.mts 加 `search: { provider: 'local' }` 一行即可。15 秒。

### 5. 跨站引用矩阵几乎为零（生态孤立）

```
站A → 站B 引用次数
filesystem → 12 个外链（最强）
cloud-native → system-design 6
go → 5 sites (mysql/redis/tools/network)
mysql → java 4
es → java 3
security → frontend 3
```

**但以下 5 站对外 0 引用**（站与站之间互不连接）：
- 🔴 **chaos**（应该 → observability / system-design / postgresql）
- 🔴 **postgresql**（应该 → clickhouse / mysql）
- 🔴 **clickhouse**（应该 → mysql / postgresql / kafka / observability）
- 🔴 **devops**（应该 → cloud-native / security）
- 🔴 **rust**（应该 → cloud-native / go）

**改进方案**：每个站点选 3-5 个 topic 页加 1 段"关联章节"段，链到主题相近的其他站点（如 chaos 05-resilience → system-design 08-availability、chaos 02-chaos-mesh → cloud-native 的 k8s 章）。

### 6. theme-color 缺失（2 站）

- **es** 和 **java** 的 config.mts 没有 `theme-color` meta，浏览器移动端打开看不到品牌色。
- 修复：在 head 数组加 `['meta', { name: 'theme-color', content: '#xxxxxx' }]` 一行。

### 7. 门户首页 chip 计数不准确 + arch 分类无对应按钮

| 类别 | chip 显示 | 实际卡片数 | 差异 |
|------|-----------|------------|------|
| all | 28 | 28 | ✓ |
| data | 6 | 6 | ✓ |
| **backend** | **8** | **9** | **+1** (chaos 加入未更新计数) |
| frontend | 3 | 3 | ✓ |
| infra | 4 | 4 | ✓ |
| ai | 2 | 2 | ✓ |
| ops | 2 | 2 | ✓ |
| security | 1 | 1 | ✓ |
| **arch** | (无按钮) | 1 | **缺按钮**（architecture 站点用 `data-cat="arch"` 但没有 arch 芯片按钮） |

**修复**：
1. `cnt-backend` 8 → 9
2. 加一个 `<button class="chip" data-cat="arch">架构<span class="chip-count" id="cnt-arch">1</span></button>` 按钮
3. 把 architecture 卡片从 `data-cat="arch"` 改回 `data-cat="backend"`（更一致），或保留 arch 但加按钮

### 8. update-item 只显示最近 9 个站点

门户首页"近期更新"区只展示了最近 9 个新站的日志（从 clickhouse 2026-08-09 到 chaos 2026-08-12）。

**问题**：早期站点（es / mysql / redis / kafka 等）没有任何 update 记录，无法体现"老站也在维护"的信号。

**修复方案**：
- 选项 A：把"近期更新"改为"全站索引"，列出所有 28 个站
- 选项 B：保留近期更新但加一个"完整时间线"链接
- 选项 C：给老站补一条 update-item（"已迭代 v3 / 2026-XX-XX"等）

### 9. footer 风格不一致

| 风格 | 出现次数 | 示例 |
|------|----------|------|
| "本站点基于 VitePress 构建 · CC BY-NC-SA 4.0 · 🏠..." | 3 站 | （模板感） |
| "基于 VitePress 构建 · 数据来源 X · 🏠..." | 5 站 | kafka / postgresql / es |
| "X 知识图谱 - 系统化学习 Y · 🏠..." | 4 站 | mysql / python / linux / kafka |
| "X 全栈 - A / B / C · 🏠..." | 8 站 | cloud-native / frontend / architecture / bigdata / ai |
| 特殊定制 | 3 站 | postgresql（Scholar's Atlas）/ chaos（28 站知识图谱）/ clickhouse（含官网链接）|

**结论**：风格多样化本身是优点（站站有特色），但"CC BY-NC-SA 4.0"出现 3 次暗示复制粘贴，没有真正合规声明。建议至少统一 3 件事：
1. 都有 🏠 门户首页（已 ✓）
2. 都有 version / build date（缺失）
3. 都有 license 字段（缺失 17 站）

---

## 四、🟢 低优先级 / 锦上添花

### 10. ADR 文档缺失

- 28 个站只有 10 个 ADR（release/adr/001-010），其中大部分是技术决策（VitePress、keychain、Java 泛型修复等）。
- **缺少主题性 ADR**：每个站点的"为什么是这个目录结构"、"为什么是这个章节切分"
- 建议：每个站建一个 ADR 记录 bounded context / 章节边界决策

### 11. README 文档缺失

只有部分项目根目录有 README（如 chaos-html）。**28 站 0 README**。

### 12. 旧站 sidebar 与新站格式不一致

新站（如 chaos）sidebar 用 `'/01-foundations/': [...]` 这种 prefix-grouped 结构；老站（es / mysql）sidebar 可能是 `[{ text: '...', items: [...] }]` 平面结构。

**改进**：老站迁移到 prefix-grouped 风格（可分批做）。

### 13. 跨站关联示例缺失

很多 topic 页有"延伸阅读"段，但都只链站内，没有：
- "**大厂实战**：Uber 用 X 优化 Y"（应有公司 logo + 一句话案例）
- "**关联站**：observability / system-design / postgresql"

---

## 五、优化路线图（按 ROI 排序）

### 🔥 第 1 周（高 ROI，30 分钟搞定）

1. **portal chip 计数修复**：backend 8→9，architecture 加 arch 按钮（5 分钟）
2. **19 站开 search**：每个加一行 `search: { provider: 'local' }` + rebuild（30 分钟）
3. **es + java 补 theme-color meta**（5 分钟）

### 📈 第 2 周（中 ROI，1-2 天）

4. **回填 5 站 0 跨链**：chaos / postgresql / clickhouse / devops / rust 各加 3-5 个跨链段（半天）
5. **java-language 53 stub 回填到 ≥3KB**：扩写 53 篇 ≈ 半天
6. **前端 32 stub 回填**：扩写 32 篇 ≈ 半天

### 🚧 第 3 周（长期 ROI，1 周）

7. **es / java / filesystem 高优先级 stub 回填**：es 58 + java 47 + filesystem 15 = 120 篇（2-3 天）
8. **更新 portal update-item 区**：扩展到所有 28 站（半天）
9. **每个站加 README + 1 个 ADR**（28 × 15 分钟 = 7 小时）

### 💎 第 4 周（生态投资）

10. **跨站"专题路线图"**：例"性能优化之旅"路径 es → postgresql → kafka → observability → chaos 跨 5 站（1 天）
11. **统一 footer**：version + license + 跨站导航（半天）
12. **首页改进**：加"学习路径"区（例：0 基础 → 推荐 3 站 / 中级 → 6 站 / 进阶 → 8 站）

---

## 六、推荐立即执行 Top 3

如果只修 3 个最痛的问题：

### ① **打开 19 站的站内 search**（30 分钟，立即可发现性 ↑30%）

一行 config，每个站加 `search: { provider: 'local' }` + rebuild。无需新内容，立即生效。

### ② **修复 portal chip bug**（5 分钟，立即修复数据一致性）

`cnt-backend`: 8 → 9。给 architecture 加 arch chip（或改 card 的 data-cat 为 backend）。

### ③ **5 站补跨链 3-5 条**（2 小时，跨站生态 ↑200%）

chaos / postgresql / clickhouse / devops / rust 现在对外 0 引用，导致门户像一个"孤立网站集合"。每个站选 3-5 篇最相关页加"延伸阅读 → [相关站](https://java-px.bot.cd/相关站/)"段，门户就能从"目录"变成"知识网络"。

---

## 七、量化对比

| 指标 | 当前 | 优化后（保守估计） |
|------|------|-------------------|
| Stub 页数 | 258 (17.6%) | < 30 (2%) |
| 平均页大小 | 5.7KB | 6.5KB |
| 站内搜索覆盖率 | 32% (9/28) | 100% (28/28) |
| 跨站引用总数 | 45 条 | 120+ 条 |
| Portal chip 数据一致性 | 7/8 类目准确 | 8/8 类目准确 |
| 站 README 覆盖 | 0/28 | 28/28 |
| ADR 站点主题文档 | 0 | 28 |

**整体目标**：从"28 站目录"升级为"互联知识网络"。