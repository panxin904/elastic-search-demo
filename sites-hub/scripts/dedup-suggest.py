"""
§8.66 C3 dups 治理辅助工具
读取 audit baseline + 重复标题清单，输出建议：
- 真重复（同概念多站）：建议合并 / 加跨站引用
- 配置示例标题：识别为"代码块子标题"，建议豁免
- 操作章节（"4. 验证"）：建议加站前缀

输出：sites-hub/reports/dedup-suggestions.md（人工 review 用）
"""
import re
import sys
import json
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, ROOT / 'sites-hub' / 'scripts')
from importlib.util import spec_from_file_location, module_from_spec
spec = spec_from_file_location('audit_content', ROOT / 'sites-hub' / 'scripts' / 'audit-content.py')
m = module_from_spec(spec)
spec.loader.exec_module(m)

# 主题分类（按关键词）
CONCEPT_TITLES = {
    'architecture': ['Saga', 'Sidecar', '微服务', 'CAP', 'BASE', 'Raft', 'Paxos', '一致性', '可靠性',
                    '缓存架构', '三大支柱', '可观测性', '事务', '分布式事务', '多级缓存', '流量控制'],
    'bigdata': ['Kafka Streams', '数据写入', '故障切换', '数据血缘'],
    'database': ['窗口函数', 'CTE', 'JOIN', '索引', '事务', 'MVCC', '锁'],
    'devops': ['5xx', '告警', '监控', 'GitHub Actions'],
    'security': ['加密', '证书', 'TLS', 'mTLS', 'JWT', 'OAuth'],
}


def categorize(title: str) -> str:
    """按标题关键词分类到主题"""
    for theme, kws in CONCEPT_TITLES.items():
        if any(kw in title for kw in kws):
            return theme
    return 'other'


def get_dups():
    """复用 audit 的 dups 检测逻辑"""
    files = m.find_all_md_files()
    all_titles = []
    for path, site in files:
        text = path.read_text(errors='replace')
        _, body = m.parse_frontmatter(text)
        site_short = site.replace('-html', '').replace('java-web-manual', 'java')
        for h1 in m.TITLE_H1.findall(body):
            all_titles.append((h1.strip(), site_short, path))
        for h2 in m.TITLE_H2.findall(body):
            all_titles.append((h2.strip(), site_short, path))

    # §8.66：内联 TEMPLATE_TITLES（不能从 module 导入，因为是 main() 内局部变量）
    TEMPLATE_TITLES = {
        '在图谱中的位置', '常见问题', '一句话定义', '与其他站点关系',
        '面试高频问题', '参考资料', '关键 takeaway', '一句话总结',
        '实战案例', '其他资源', '推荐阅读', '小结', '总结', '总结与回顾',
        '实战 checklist', '为什么需要', '三种部署模式', '🆚 vs 其他',
        '秒杀系统设计', '分布式限流', 'Fallback 策略',
        'application.yml', 'docker-compose.yml', 'config.yaml', 'AWS Secrets Manager',
        'macOS', 'Linux', 'Docker', 'Docker 镜像', 'Node.js', 'Python',
        'Python 客户端', 'JSON 输出', '多 GPU', '命令行启动', '用 curl', 'Schema 设计',
        '路径 1：纯新手（1 周）', 'Easy（基础）', 'Hello World',
        '双写一致性', 'ShardingSphere 实战', 'Hystrix（已停止维护）', '熔断器（Circuit Breaker）',
        'prometheus.yml', 'otel-collector-config.yaml',
        '选型决策树', '学习路径建议', '与其他站点的关系',
        '缓存三大问题', '三大问题对比', '适用 vs 不适用',
        'P99 延迟', '字符串函数',
        'postgresql.conf', '/etc/fstab', '/etc/ssh/sshd_config',
        'Windows', 'GitHub Actions',
        '4. 验证', '3. 配置', '2. 安装', '5. 测试',
        '安装并启动', '配置示例',
    }
    by_title = defaultdict(list)
    for t, s, p in all_titles:
        t_clean = re.sub(r'\s+', ' ', t.strip())
        if 4 < len(t_clean) < 40 and t_clean not in TEMPLATE_TITLES:
            by_title[t_clean].append((s, p))

    cross_dups = []
    for title, locs in by_title.items():
        if len(locs) < 2:
            continue
        sites = {l[0] for l in locs}
        file_list = [f'{l[0]}/{l[1].name}' for l in locs]
        if len(sites) >= 2:
            cross_dups.append((title, file_list, sites))

    # 排除 §8.60 注入的标题
    cross_dups = [(t, f, s) for t, f, s in cross_dups if t != '📚 相关阅读（跨站导航）']
    return cross_dups


def main():
    dups = get_dups()
    dups.sort(key=lambda x: -len(x[1]))

    # 分类：concept / config / chapter
    concept_dups = []
    config_dups = []
    chapter_dups = []

    for title, files, sites in dups:
        # 配置类标题（含 yml/yaml/conf/path/数字前缀）
        if re.search(r'\.(yml|yaml|conf|json|properties|toml|ini)$', title):
            config_dups.append((title, files, sites))
        elif title.startswith(('/', 'C:', '~/')) or '/etc/' in title or 'application-' in title:
            config_dups.append((title, files, sites))
        elif re.match(r'^\d+\.', title):  # 编号章节
            chapter_dups.append((title, files, sites))
        elif categorize(title) != 'other':
            concept_dups.append((title, files, sites, categorize(title)))
        else:
            chapter_dups.append((title, files, sites))

    OUTPUT = ROOT / 'sites-hub' / 'reports' / 'dedup-suggestions.md'
    lines = []
    lines.append('# 跨子站重复标题治理建议')
    lines.append('')
    lines.append(f'> 自动生成 by `sites-hub/scripts/dedup-suggest.py`（§8.66）')
    lines.append(f'> 共 {len(dups)} 组重复，按主题分类：')
    lines.append(f'> - 概念类（需跨站链接 / 合并）：{len(concept_dups)} 组')
    lines.append(f'> - 配置类（建议加白名单）：{len(config_dups)} 组')
    lines.append(f'> - 章节类（建议加站前缀）：{len(chapter_dups)} 组')
    lines.append('')

    lines.append('## 一、概念类重复（需治理）')
    lines.append('')
    lines.append('> 同一概念在多站展开。建议：')
    lines.append('> 1. **主版本**（通常是 architecture / system-design）保留完整内容')
    lines.append('> 2. 其他站加跨站链接，指向主版本')
    lines.append('> 3. 不必合并（多视角价值高）')
    lines.append('')
    lines.append('| 标题 | 主题 | 重复数 | 涉及站 |')
    lines.append('|------|------|------:|--------|')
    for title, files, sites, theme in sorted(concept_dups, key=lambda x: (-len(x[1]), x[0]))[:30]:
        sites_str = ', '.join(sorted(sites))
        lines.append(f'| {title} | {theme} | {len(files)} | {sites_str} |')

    lines.append('')
    lines.append('## 二、配置类重复（建议加白名单）')
    lines.append('')
    lines.append('> 配置示例标题（application.yml / docker-compose.yml / *.conf 等）。多站引用同一配置模板，预期重复。')
    lines.append('> 建议加到 `audit-content.py` 的 `TEMPLATE_TITLES` 白名单。')
    lines.append('')
    config_titles = sorted(set(t for t, _, _ in config_dups))
    lines.append('```python')
    lines.append('# sites-hub/scripts/audit-content.py · TEMPLATE_TITLES 新增：')
    for t in config_titles:
        lines.append(f'        {t!r},')
    lines.append('```')

    lines.append('')
    lines.append('## 三、章节类重复（建议加站前缀或白名单）')
    lines.append('')
    lines.append('> 编号章节（如 "4. 验证"）或通用操作标题。建议加站前缀或加白名单。')
    lines.append('')
    chapter_titles = sorted(set(t for t, _, _ in chapter_dups))
    lines.append('共 {} 个不同章节标题：'.format(len(chapter_titles)))
    lines.append('')
    for t in chapter_titles[:20]:
        lines.append(f'- `{t}`')
    if len(chapter_titles) > 20:
        lines.append(f'- ... 等 {len(chapter_titles) - 20} 个')

    lines.append('')
    lines.append('## 四、建议处理优先级')
    lines.append('')
    lines.append('1. **P1**：将"配置类重复"加入 `TEMPLATE_TITLES` 白名单（一次提交，影响几十个 dups）')
    lines.append('2. **P2**：高频"概念类重复"（> 3 站）加跨站引用段落')
    lines.append('3. **P3**：低频概念重复按站逐个处理')
    lines.append('4. **P4**：章节类重复加白名单（如果确实是模板生成的）')

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text('\n'.join(lines))
    print(f'✓ {OUTPUT.relative_to(ROOT)}')
    print(f'  total dups: {len(dups)}')
    print(f'  concept: {len(concept_dups)}')
    print(f'  config: {len(config_dups)}')
    print(f'  chapter: {len(chapter_dups)}')


if __name__ == '__main__':
    main()
