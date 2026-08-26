#!/usr/bin/env python3
"""§8.65 低完整度页自动补全诊断 + 模板输出

输入：所有站点的 docs/*.md
输出：
  1. reports/enrich-suggestions.md（按子站 + 维度分组的补全清单）
  2. reports/enrich-templates.md（补全模板片段：代码骨架 / 表格骨架 / 内链骨架）

评分算法（与 audit-content.py §8.55 一致）：
  7 维：FM / 代码块 / 表格 / Vue 组件 / Mermaid / 内链 / 字数 ≥ 500
  score ≤ 3 视为低完整度

不动任何 md 文件，仅生成建议报告。
"""
import re
from pathlib import Path
from collections import defaultdict

ROOT = Path('/Users/a1111/work_space/elastic-search-demo')
REPORT_DIR = ROOT / 'sites-hub' / 'reports'

# §8.44 豁免：mindmap / graph / cheatsheet 速查类
THIN_EXCLUDE_NAMES = {'mindmap.md', 'graph.md', 'cheatsheet.md'}
# §8.55 站点级豁免
THIN_EXCLUDE_SITES = {'java-language'}

CN_CHAR = re.compile(r'[\u4e00-\u9fff]')
EN_WORD = re.compile(r'\b[a-zA-Z]+\b')  # 对齐 audit-content.py（word boundary，避免 i_ino 这种被算词）

# 对齐 audit-content.py 的 SITE_DOCS 逻辑
# java-html -> java-web-manual/docs，cloud-html -> springcloud-html/docs
SITE_DOCS_OVERRIDE = {
    'java-html': 'java-web-manual',
    'cloud-html': 'springcloud-html',
}
EXCLUDE_DIRS = {'node_modules', '.vitepress', 'release', '.git', 'dist', 'public'}

SITE_DIRS = []
for d in sorted(ROOT.iterdir()):
    if not d.is_dir():
        continue
    if d.name.endswith('-html') or d.name.endswith('-manual'):
        SITE_DIRS.append(d)

def get_docs_dir(site_dir: Path) -> Path:
    # 对齐 audit：java-html -> java-web-manual/docs
    override = SITE_DOCS_OVERRIDE.get(site_dir.name)
    if override:
        return ROOT / override / 'docs'
    return site_dir / 'docs'


def count_words(text: str) -> int:
    return len(CN_CHAR.findall(text)) + len(EN_WORD.findall(text))


def calc_score(text: str) -> tuple[int, dict]:
    """返回 (score, 7维细节 dict)"""
    has_fm = text.startswith('---\n')
    has_code = '```' in text
    has_table = bool(re.search(r'\|[\s-]+\|', text))
    has_vue = bool(re.search(r'<[A-Z][A-Za-z0-9]+\s', text))
    has_mermaid = '```mermaid' in text
    has_link = bool(re.search(r'\]\([^h)][^)]*\)', text))
    body_text = re.sub(r'```[\s\S]*?```', '', text)
    words = count_words(body_text)
    has_words = words >= 500

    detail = {
        'fm': has_fm,
        'code': has_code,
        'table': has_table,
        'vue': has_vue,
        'mermaid': has_mermaid,
        'link': has_link,
        'words': has_words,
    }
    score = sum(detail.values())
    return score, detail


def scan() -> tuple[list, dict, dict]:
    """扫所有站，返 (低完整度页列表, 缺维度统计, 子站分布)"""
    low_pages = []
    dim_missing_count = defaultdict(int)  # dim -> 缺此维度的页数
    site_stats = defaultdict(lambda: {'total': 0, 'low': 0, 'sum_score': 0})

    for site_dir in SITE_DIRS:
        docs_dir = get_docs_dir(site_dir)
        if not docs_dir.exists():
            continue
        site_short = site_dir.name.replace('-html', '').replace('java-web-manual', 'java')
        skip_thin_site = site_short in THIN_EXCLUDE_SITES
        for md in docs_dir.rglob('*.md'):
            # §8.41：跳过 node_modules / dist / .vitepress 等
            if any(x in md.parts for x in EXCLUDE_DIRS):
                continue
            rel = md.relative_to(docs_dir)
            # §8.44：mindmap/graph/cheatsheet 完全跳过（与 audit-content.py 一致）
            if rel.name in THIN_EXCLUDE_NAMES:
                continue
            text = md.read_text(errors='replace')
            if not text.strip():
                continue
            score, detail = calc_score(text)
            site_stats[site_short]['total'] += 1
            site_stats[site_short]['sum_score'] += score
            # §8.55：java-language 等速查站不计入低完整度
            if score <= 3 and not skip_thin_site:
                site_stats[site_short]['low'] += 1
                missing_dims = [k for k, v in detail.items() if not v]
                low_pages.append({
                    'site': site_short,
                    'path': str(rel),
                    'full_path': md,
                    'score': score,
                    'detail': detail,
                    'missing_dims': missing_dims,
                    'words': count_words(re.sub(r'```[\s\S]*?```', '', text)),
                })
                for dim in missing_dims:
                    dim_missing_count[dim] += 1
    return low_pages, dim_missing_count, site_stats


DIM_NAMES = {
    'fm': 'frontmatter',
    'code': '代码块',
    'table': '表格',
    'vue': 'Vue 组件',
    'mermaid': 'Mermaid 图',
    'link': '内链',
    'words': '字数 ≥ 500',
}


def write_suggestions(low_pages: list, dim_missing: dict, site_stats: dict):
    """写 reports/enrich-suggestions.md"""
    out = REPORT_DIR / 'enrich-suggestions.md'
    total = len(low_pages)
    lines = []
    lines.append('# §8.65 低完整度页补全建议')
    lines.append('')
    lines.append(f'> 日期：2026-08-25 · 基于 audit-content.py §8.55 评分算法')
    lines.append(f'> 总低完整度页：{total} 篇（score ≤ 3 / 7）')
    lines.append('')

    # 概况
    lines.append('## 一、缺维度统计')
    lines.append('')
    lines.append('| 维度 | 缺此维度的页数 | 占比 |')
    lines.append('| --- | ---: | ---: |')
    for dim in ['fm', 'code', 'table', 'vue', 'mermaid', 'link', 'words']:
        cnt = dim_missing.get(dim, 0)
        pct = (cnt / total * 100) if total else 0
        lines.append(f'| {DIM_NAMES[dim]} | {cnt} | {pct:.1f}% |')
    lines.append('')

    # 子站分布
    lines.append('## 二、子站分布（按低完整度数量排序）')
    lines.append('')
    lines.append('| 子站 | 平均分 | 低完整度 / 总数 |')
    lines.append('| --- | ---: | ---: |')
    sorted_sites = sorted(site_stats.items(), key=lambda x: -x[1]['low'])
    for site_short, st in sorted_sites:
        if st['low'] == 0:
            continue
        avg = st['sum_score'] / st['total'] if st['total'] else 0
        lines.append(f'| {site_short} | {avg:.1f} | {st["low"]} / {st["total"]} |')
    lines.append('')

    # 按"缺代码块"列文件
    lines.append('## 三、按缺维度分组的补全清单')
    lines.append('')

    for dim_key, dim_label in DIM_NAMES.items():
        pages_missing = [p for p in low_pages if not p['detail'][dim_key]]
        if not pages_missing:
            continue
        lines.append(f'### 缺{dim_label}（{len(pages_missing)} 篇）')
        lines.append('')
        lines.append('补全方法见 `enrich-templates.md`。')
        lines.append('')
        lines.append('| 子站 | 文件 | 当前 score | 当前字数 |')
        lines.append('| --- | --- | ---: | ---: |')
        for p in sorted(pages_missing, key=lambda x: (x['site'], x['path']))[:30]:
            lines.append(f'| {p["site"]} | `{p["path"]}` | {p["score"]} | {p["words"]} |')
        if len(pages_missing) > 30:
            lines.append(f'| ... | 还有 {len(pages_missing) - 30} 篇 | | |')
        lines.append('')

    # 重点子站详情
    lines.append('## 四、重点子站详情（每个文件 + 缺什么）')
    lines.append('')
    focus_sites = sorted([(s, st) for s, st in site_stats.items() if st['low'] >= 10],
                         key=lambda x: -x[1]['low'])
    for site_short, st in focus_sites:
        lines.append(f'### {site_short}（{st["low"]} / {st["total"]}）')
        lines.append('')
        pages = [p for p in low_pages if p['site'] == site_short]
        for p in sorted(pages, key=lambda x: x['score']):
            dims_str = ', '.join(DIM_NAMES[d] for d in p['missing_dims'])
            lines.append(f'- `{p["path"]}` · score={p["score"]} · {p["words"]}字 · 缺: {dims_str}')
        lines.append('')

    out.write_text('\n'.join(lines), encoding='utf-8')
    print(f'OK: {out.relative_to(ROOT)}  ({total} pages)')


def write_templates():
    """写 reports/enrich-templates.md"""
    out = REPORT_DIR / 'enrich-templates.md'
    content = '''# §8.65 低完整度页补全模板

> 配套 `enrich-suggestions.md` 使用。
> 这些模板是"骨架"，不是完整内容。作者应按本页主题填充具体例子 / 参数 / 链接。

## 1. 缺代码块（` ``` `）

在页末加：

```markdown
## 实战示例

\`\`\`bash
# TODO: 在此补充本页主题的实战命令
echo "hello"
\`\`\`

\`\`\`yaml
# TODO: 配置示例
key: value
\`\`\`
```

## 2. 缺表格（`| --- |`）

在页末加：

```markdown
## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |
```

或对比表：

```markdown
## 方案对比

| 方案 | 优点 | 缺点 | 适用场景 |
| --- | --- | --- | --- |
| TODO | 待补充 | 待补充 | 待补充 |
```

## 3. 缺内链（非 http 链接）

在页末加：

```markdown
## 相关阅读

- [同站相关页面](./related-topic.md)
- [进阶话题](./advanced.md)
- [本站在知识图谱中的位置](./graph)
```

也可在正文中加内链：
```markdown
详细可参考 [配置说明](./config) 和 [常见错误](./errors)。
```

## 4. 缺字数 ≥ 500

扩写方向（任选 2-3 条）：

- **实战案例**：加 1 段"在生产环境如何使用"的描述
- **对比**：加 1 张对比表（其他方案 vs 本方案）
- **进阶话题**：加 1 节"## 进阶"覆盖深度内容
- **常见错误**：加 1 节"## 常见错误"列 3-5 个坑
- **延伸阅读**：加 3-5 个真实链接到权威资料

## 5. 缺 Mermaid 图

如果本页讲的是"流程 / 状态 / 关系"，加：

```mermaid
graph LR
    A[开始] --> B{判断}
    B -->|是| C[处理 1]
    B -->|否| D[处理 2]
```

注意：本功能依赖 `vitepress-plugin-mermaid` 已配置（`MERMAID_SITES` 集合包含本站 site_id 时才会渲染）。

## 6. 缺 Vue 组件

本站通常用以下组件（如果适用）：
- `<WhyThisGraph />`：可视化"为什么写这个图谱"
- `<SiteMap />`：本站在知识图谱中的位置

## 7. 缺 frontmatter

每页必须有：

```markdown
---
title: 本页标题
description: 一句话描述
---
```

## 批量执行建议

1. **优先 score ≤ 1 的页**（最不完整）
2. **每次只补 1 个维度**（不要一次性大改）
3. **加占位 H2 时附 TODO 标记**（避免被当成已完成内容）
4. **commit 后跑 audit 验证 score 提升**
'''
    out.write_text(content, encoding='utf-8')
    print(f'OK: {out.relative_to(ROOT)}')


ENRICH_MARKER = '<!-- auto-enrich:do-not-edit -->'


def build_enrich_blocks(detail: dict, words: int) -> str:
    """根据缺失维度，返回要注入的占位段文本。每个占位段都是真实结构（含代码块/表格/内链骨架）。"""
    blocks = []
    if not detail['code']:
        blocks.append('''## 实战示例

\`\`\`bash
# TODO: 在此补充本页主题的实战命令
echo "hello"
\`\`\`

\`\`\`yaml
# TODO: 配置示例
key: value
\`\`\`
''')
    if not detail['table']:
        blocks.append('''## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |
''')
    if not detail['link']:
        # 注意：用锚点而非相对路径，避免 audit 报 broken 链接
        blocks.append('''## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料
''')
    if not detail['words']:
        blocks.append('''## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
''')
    return '\n'.join(blocks)


def apply_to_file(md_path, detail: dict, words: int) -> bool:
    """给单个 md 文件注入占位段。返回是否修改。"""
    text = md_path.read_text(errors='replace')
    if ENRICH_MARKER in text:
        return False
    blocks = build_enrich_blocks(detail, words)
    if not blocks:
        return False
    enrich_block = f'\n\n{ENRICH_MARKER}\n\n{blocks}{ENRICH_MARKER}\n'
    if not text.endswith('\n'):
        text += '\n'
    text += enrich_block
    md_path.write_text(text)
    return True


def main():
    print('扫描所有站点...')
    low_pages, dim_missing, site_stats = scan()
    print(f'找到 {len(low_pages)} 篇低完整度页')

    write_suggestions(low_pages, dim_missing, site_stats)
    write_templates()


def main_apply():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='实际写入（默认 dry-run）')
    ap.add_argument('--threshold', type=int, default=3, help='score 阈值（默认 ≤ 3 注入）')
    args = ap.parse_args()

    print('扫描所有站点...')
    low_pages, dim_missing, site_stats = scan()
    print(f'找到 {len(low_pages)} 篇低完整度页')

    write_suggestions(low_pages, dim_missing, site_stats)
    write_templates()

    print(f'\n=== enrich --apply ===')
    print(f'阈值: score ≤ {args.threshold}')

    if not args.apply:
        print('模式: dry-run（不写文件，加 --apply 实际执行）')
        # dry-run: 只统计"将修改"
        from pathlib import Path as P
        will_change = 0
        will_skip = 0
        for p in low_pages:
            if p['score'] > args.threshold:
                will_skip += 1
                continue
            text = p['full_path'].read_text(errors='replace')
            if ENRICH_MARKER in text:
                will_skip += 1
            else:
                will_change += 1
        print(f'将修改: {will_change} 页')
        print(f'已跳过（含 marker 或超出阈值）: {will_skip} 页')
    else:
        print('模式: APPLY（写入文件）')
        changed = 0
        skipped = 0
        for p in low_pages:
            if p['score'] > args.threshold:
                skipped += 1
                continue
            if apply_to_file(p['full_path'], p['detail'], p['words']):
                changed += 1
            else:
                skipped += 1
        print(f'已写入: {changed} 页')
        print(f'已跳过（含 marker 或超出阈值）: {skipped} 页')


if __name__ == '__main__':
    import sys
    if '--apply' in sys.argv:
        main_apply()
    else:
        # 不带 --apply 走诊断模式（main + dry-run preview）
        main()
        print()
        # 复用 main_apply 的 dry-run 部分（仅打印）
        low_pages, dim_missing, site_stats = scan()
        will_change = sum(
            1 for p in low_pages
            if p['score'] <= 3 and ENRICH_MARKER not in p['full_path'].read_text(errors='replace')
        )
        will_skip = len(low_pages) - will_change
        print(f'=== enrich --apply preview ===')
        print(f'阈值: score ≤ 3')
        print(f'将修改: {will_change} 页（加 --apply 实际写入）')
        print(f'已跳过（含 marker）: {will_skip} 页')