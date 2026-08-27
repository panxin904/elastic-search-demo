"""
§8.75 C3 趋势 Dashboard · 自动采集 + 简易 HTML 报告

- 每次跑 audit-content.py 后调用本脚本，提取关键指标
- 生成 sites-hub/reports/history/audit-YYYYMMDD.json（历史数据）
- 生成 sites-hub/reports/trend-dashboard.html（可视化 4 指标）

追踪 4 个核心指标：
- imgs（图片数）
- xsite（跨站引用数）
- dups（重复标题数：cross + intra）
- low_completeness（低完整度页数 ≤3）

用法：
  python3 sites-hub/scripts/audit-trend.py
"""
import json
import re
import subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
HISTORY_DIR = ROOT / 'sites-hub' / 'reports' / 'history'
DASHBOARD_HTML = ROOT / 'sites-hub' / 'reports' / 'trend-dashboard.html'

# 注意：Python 字符串中 \\s 表示正则的 \s
PATTERN_FILES = r'files:\s*(\d+)\s+words:\s*([\d,]+)\s+thin:\s*(\d+)\s+imgs:\s*(\d+)\s+xsite:\s*(\d+)'
PATTERN_DUPS = r'broken:\s*(\d+)\s+dups:\s*(\d+)\s*\(cross-site\)\s*\+\s*(\d+)\s*\(intra-site\)'
PATTERN_LOW = r'内容完整度低（(\d+)\s*篇'


def parse_latest_audit() -> dict:
    """通过运行 audit-content.py 解析 stdout"""
    today = date.today().isoformat()
    result = subprocess.run(
        ['python3', str(ROOT / 'sites-hub' / 'scripts' / 'audit-content.py')],
        capture_output=True, text=True, cwd=ROOT
    )
    output = result.stdout + result.stderr

    metrics = {'date': today, 'source': f'content-quality-{today}.md'}

    m = re.search(PATTERN_FILES, output)
    if m:
        metrics.update({
            'files': int(m.group(1)),
            'words': int(m.group(2).replace(',', '')),
            'thin': int(m.group(3)),
            'imgs': int(m.group(4)),
            'xsite': int(m.group(5)),
        })

    m = re.search(PATTERN_DUPS, output)
    if m:
        metrics.update({
            'broken': int(m.group(1)),
            'dups_cross': int(m.group(2)),
            'dups_intra': int(m.group(3)),
        })

    md_path = ROOT / 'sites-hub' / f'reports/content-quality-{today}.md'
    if md_path.exists():
        text = md_path.read_text()
        m = re.search(PATTERN_LOW, text)
        if m:
            metrics['low_completeness'] = int(m.group(1))

    return metrics


def save_history(metrics: dict):
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    date_str = metrics.get('date', date.today().isoformat())
    out = HISTORY_DIR / f'audit-{date_str}.json'
    out.write_text(json.dumps(metrics, ensure_ascii=False, indent=2))
    print(f'✓ 历史已存: {out.relative_to(ROOT)}')
    return out


def load_all_history() -> list[dict]:
    if not HISTORY_DIR.exists():
        return []
    files = sorted(HISTORY_DIR.glob('audit-*.json'))
    return [json.loads(f.read_text()) for f in files]


def render_dashboard(history: list[dict]):
    if not history:
        print('⚠ 无历史数据，跳过 dashboard 生成')
        return

    dates = [h['date'] for h in history]
    imgs = [h.get('imgs', 0) for h in history]
    xsite = [h.get('xsite', 0) for h in history]
    dups_total = [h.get('dups_cross', 0) + h.get('dups_intra', 0) for h in history]
    low = [h.get('low_completeness', 0) for h in history]

    def delta(curr, prev_arr):
        if not prev_arr:
            return ''
        d = curr - prev_arr[-2] if len(prev_arr) >= 2 else 0
        return f'+{d}' if d > 0 else (f'{d}' if d < 0 else '±0')

    last = history[-1]
    rows = []
    for i, h in enumerate(history):
        spark_imgs = spark_bar(imgs, i)
        spark_xsite = spark_bar(xsite, i)
        spark_dups = spark_bar(dups_total, i)
        spark_low = spark_bar(low, i)
        rows.append(
            f'<tr><td>{h["date"]}</td>'
            f'<td>{h.get("imgs", 0)}</td>'
            f'<td>{h.get("xsite", 0)}</td>'
            f'<td>{h.get("dups_cross", 0) + h.get("dups_intra", 0)}</td>'
            f'<td>{h.get("low_completeness", 0)}</td>'
            f'<td class="spark">{spark_imgs}{spark_xsite}{spark_dups}{spark_low}</td></tr>'
        )
    rows_html = '\n'.join(rows)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>Audit Trend Dashboard</title>
<style>
  body {{ font-family: -apple-system, sans-serif; max-width: 960px; margin: 32px auto; padding: 0 16px; color: #1e293b; }}
  h1 {{ font-size: 24px; }}
  .meta {{ color: #64748b; font-size: 13px; margin-bottom: 32px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 32px; }}
  .card {{ border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; background: #fafafa; }}
  .card .label {{ font-size: 12px; color: #64748b; }}
  .card .value {{ font-size: 28px; font-weight: 700; margin: 8px 0; }}
  .card .delta {{ font-size: 12px; color: #10b981; }}
  .card .delta.down {{ color: #ef4444; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th, td {{ padding: 6px 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
  th {{ background: #f1f5f9; font-weight: 600; }}
  .spark {{ font-family: monospace; letter-spacing: 1px; }}
</style>
</head>
<body>
<h1>📊 Content Quality Trend</h1>
<p class="meta">来源：sites-hub/reports/content-quality-*.md · 自动采集 · 共 {len(history)} 条记录</p>

<div class="grid">
  <div class="card">
    <div class="label">📷 图片数 (imgs)</div>
    <div class="value">{last.get('imgs', 0)}</div>
    <div class="delta">{delta(last.get('imgs', 0), imgs[:-1])} vs 上次</div>
  </div>
  <div class="card">
    <div class="label">🔗 跨站引用 (xsite)</div>
    <div class="value">{last.get('xsite', 0)}</div>
    <div class="delta">{delta(last.get('xsite', 0), xsite[:-1])} vs 上次</div>
  </div>
  <div class="card">
    <div class="label">🔁 重复标题 (dups)</div>
    <div class="value">{last.get('dups_cross', 0) + last.get('dups_intra', 0)}</div>
    <div class="delta">{delta(last.get('dups_cross', 0) + last.get('dups_intra', 0), dups_total[:-1])} vs 上次</div>
  </div>
  <div class="card">
    <div class="label">⚠️ 低完整度</div>
    <div class="value">{last.get('low_completeness', 0)}</div>
    <div class="delta">{delta(last.get('low_completeness', 0), low[:-1])} vs 上次</div>
  </div>
</div>

<h2>趋势明细（按日期）</h2>
<table>
<tr><th>日期</th><th>imgs</th><th>xsite</th><th>dups</th><th>低完整度</th><th>Sparkline</th></tr>
{rows_html}
</table>

<p class="meta">每次 audit-content.py 运行后会自动更新本页面</p>
</body>
</html>
"""
    DASHBOARD_HTML.write_text(html)
    print(f'✓ Dashboard: {DASHBOARD_HTML.relative_to(ROOT)}')


def spark_bar(values, idx):
    """为单个值生成 sparkline 字符（基于相对位置）"""
    if not values or idx >= len(values):
        return '·'
    mx = max(values) or 1
    pos = int(values[idx] / mx * 7)
    return '▁▂▃▄▅▆▇█'[min(max(pos, 0), 7)]


def main():
    print('=== §8.75 C3 趋势 Dashboard ===')
    metrics = parse_latest_audit()
    if not metrics:
        print('⚠ 解析 audit 报告失败')
        return
    print(f'当前: imgs={metrics.get("imgs", "?")} xsite={metrics.get("xsite", "?")} '
          f'dups={metrics.get("dups_cross", 0) + metrics.get("dups_intra", 0)} '
          f'低完整度={metrics.get("low_completeness", "?")}')

    save_history(metrics)
    history = load_all_history()
    render_dashboard(history)
    print(f'\n历史记录: {len(history)} 条')


if __name__ == '__main__':
    main()
