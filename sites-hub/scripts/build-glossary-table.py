"""
§8.63 C8 多语言收尾：build glossary bilingual table
读 shared-assets/glossary/keywords.json，输出：
1. shared-assets/glossary/terms.md（双语对照表）
2. 缺失 en 字段的术语清单（提示补充）
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
GLOSSARY_FILE = ROOT / 'shared-assets' / 'glossary' / 'keywords.json'
OUTPUT_MD = ROOT / 'shared-assets' / 'glossary' / 'terms.md'


def main():
    if not GLOSSARY_FILE.exists():
        print(f'ERROR: {GLOSSARY_FILE} not found')
        sys.exit(1)

    data = json.loads(GLOSSARY_FILE.read_text())
    data.pop('_doc', None)
    data.pop('_schema_version', None)

    # 按 site 数量排序
    items = sorted(data.items(), key=lambda x: (-len(x[1].get('sites', [])), x[0]))

    # 统计 en 覆盖
    with_en = [k for k, v in data.items() if v.get('en')]
    without_en = [k for k, v in data.items() if not v.get('en')]

    lines = []
    lines.append('# 术语表（中英对照）')
    lines.append('')
    lines.append('> 自动生成 by `sites-hub/scripts/build-glossary-table.py`（§8.63 C8）')
    lines.append(f'> 共 {len(data)} 个术语，{len(with_en)} 有 EN 翻译，{len(without_en)} 待补')
    lines.append('')
    lines.append('## 〇、EN 覆盖率')
    lines.append('')
    lines.append(f'| 状态 | 数量 | 占比 |')
    lines.append(f'|------|-----:|-----:|')
    pct = 100 * len(with_en) / len(data) if data else 0
    lines.append(f'| 已有 EN | {len(with_en)} | {pct:.1f}% |')
    lines.append(f'| 待补 EN | {len(without_en)} | {100-pct:.1f}% |')
    lines.append('')
    lines.append('## 一、术语详情（按跨站引用数排序）')
    lines.append('')
    lines.append('| 中文 | English | 跨站数 | 主要关联 |')
    lines.append('|------|---------|------:|---------|')
    for term, info in items:
        en = info.get('en', '—')
        sites = info.get('sites', [])
        n = len(sites)
        primary = sites[0]['label'] if sites else '—'
        lines.append(f'| {term} | {en} | {n} | {primary} |')

    lines.append('')
    lines.append('## 二、待补 EN 清单')
    lines.append('')
    lines.append('> 这些术语目前没填 en 字段，多为英文原词（JVM/K8s/Redis）通常无需翻译，或中文术语需补翻译。')
    lines.append('')
    lines.append('| 术语 | 跨站数 | 建议 EN |')
    lines.append('|------|------:|---------|')
    for term in sorted(without_en, key=lambda t: -len(data[t].get('sites', []))):
        n = len(data[term].get('sites', []))
        # 极简启发：英文原词无需翻译（保留自身）；中文给空（待补）
        suggested = term if all(ord(c) < 128 for c in term) else ''
        lines.append(f'| {term} | {n} | {suggested} |')

    lines.append('')
    lines.append('## 三、维护说明')
    lines.append('')
    lines.append('- 新增术语：编辑 `shared-assets/glossary/keywords.json` 加 `"en"` 字段')
    lines.append('- 重生成：跑 `python3 sites-hub/scripts/build-glossary-table.py`')
    lines.append('- EN 翻译约定：')
    lines.append('  - 英文原词（JVM/K8s/Redis）→ en 与 term 相同')
    lines.append('  - 中文术语 → 标准英文翻译（如"事务" → "Transaction"）')
    lines.append('  - 复合术语 → Title Case（如"流处理" → "Stream Processing"）')

    OUTPUT_MD.write_text('\n'.join(lines))
    print(f'✓ {OUTPUT_MD.relative_to(ROOT)}')
    print(f'  total terms: {len(data)}')
    print(f'  with EN: {len(with_en)} ({pct:.1f}%)')
    print(f'  without EN: {len(without_en)}')


if __name__ == '__main__':
    main()
