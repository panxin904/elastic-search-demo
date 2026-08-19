#!/usr/bin/env python3
"""Build a dependency-free C3 content-quality trend dashboard."""
from __future__ import annotations

import argparse
import html
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

REPORT_PATTERN = re.compile(r"content-quality-(\d{4}-\d{2}-\d{2})\.md$")
SUMMARY_ROW = re.compile(r"^\|")

METRICS = (
    ("files", r"^总文件数$", "文件数", "#2563eb"),
    ("words", r"总字数（中英混合）", "总字数", "#7c3aed"),
    ("thin", r"^薄页（", "薄页", "#f59e0b"),
    ("no_fm", r"^缺 frontmatter$", "缺 frontmatter", "#ef4444"),
    ("no_date", r"^frontmatter 缺 date$", "缺 date", "#64748b"),
    ("stale", r"^过期内容", "过期内容", "#0f766e"),
    ("imgs", r"^图片总数$", "图片总数", "#0891b2"),
    ("broken", r"^内部死链$", "内部死链", "#dc2626"),
    ("xsite", r"^跨站引用$", "跨站引用", "#059669"),
    ("dups", r"^跨子站重复标题$", "重复标题", "#db2777"),
)
TREND_METRICS = (
    ("files", "文件数", "#2563eb"),
    ("words", "总字数", "#7c3aed"),
    ("thin", "薄页", "#f59e0b"),
    ("no_fm", "缺 frontmatter", "#ef4444"),
    ("broken", "内部死链", "#dc2626"),
    ("xsite", "跨站引用", "#059669"),
    ("dups", "跨子站重复标题", "#db2777"),
)


def parse_number(value: str) -> int | None:
    normalized = value.replace(",", "").replace("，", "").replace("%", "").replace("％", "")
    match = re.search(r"[-+]?\d+(?:\.\d+)?", normalized)
    if not match:
        return None
    number = float(match.group(0))
    return int(number) if number.is_integer() else int(round(number))


def parse_report(path: Path) -> dict[str, Any] | None:
    match = REPORT_PATTERN.search(path.name)
    if not match:
        return None
    try:
        report_date = date.fromisoformat(match.group(1))
    except ValueError:
        return None

    values: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not SUMMARY_ROW.match(line):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        label, value = cells[0], cells[1]
        for key, pattern, _, _ in METRICS:
            if re.search(pattern, label) and key not in values:
                number = parse_number(value)
                if number is not None:
                    values[key] = number

    if not values:
        return None
    return {
        "date": report_date.isoformat(),
        "path": str(path),
        **values,
    }


def load_reports(reports_dir: Path, max_weeks: int = 12) -> list[dict[str, Any]]:
    candidates: dict[str, tuple[str, dict[str, Any]]] = {}
    for path in reports_dir.glob("content-quality-*.md"):
        record = parse_report(path)
        if record is None:
            continue
        previous = candidates.get(record["date"])
        if previous is None or path.name > previous[0]:
            candidates[record["date"]] = (path.name, record)
    records = [item[1] for item in candidates.values()]
    records.sort(key=lambda item: item["date"])
    return records[-max_weeks:] if max_weeks > 0 else []


def format_number(value: int | None) -> str:
    return "—" if value is None else f"{value:,}"


def delta_text(current: int | None, previous: int | None) -> str:
    if current is None or previous is None:
        return "暂无对比"
    delta = current - previous
    if delta == 0:
        return "持平"
    return f"{delta:+,}"


def delta_class(current: int | None, previous: int | None) -> str:
    if current is None or previous is None:
        return "delta-muted"
    delta = current - previous
    if delta == 0:
        return "delta-neutral"
    return "delta-down" if delta < 0 else "delta-up"


def chart_points(records: list[dict[str, Any]], key: str) -> list[tuple[str, int]]:
    return [
        (record["date"], record[key])
        for record in records
        if key in record and isinstance(record[key], (int, float))
    ]


def render_svg(records: list[dict[str, Any]], key: str, label: str, color: str) -> str:
    points = chart_points(records, key)
    if len(points) < 2:
        return '<p class="chart-empty">至少需要两份报告才能绘制趋势。</p>'

    width, height = 920, 250
    left, right, top, bottom = 72, 24, 20, 46
    plot_width = width - left - right
    plot_height = height - top - bottom
    values = [value for _, value in points]
    minimum, maximum = min(values), max(values)
    span = maximum - minimum
    if span == 0:
        padding = max(1, abs(maximum) // 10 or 1)
        minimum -= padding
        maximum += padding
    else:
        padding = max(1, span // 10)
        minimum = max(0, minimum - padding)
        maximum += padding

    def x_position(index: int) -> float:
        return left + plot_width * index / (len(points) - 1)

    def y_position(value: int) -> float:
        return top + plot_height * (maximum - value) / (maximum - minimum)

    coordinates = [(x_position(index), y_position(value)) for index, (_, value) in enumerate(points)]
    path = " ".join(("M" if index == 0 else "L") + f" {x:.1f} {y:.1f}" for index, (x, y) in enumerate(coordinates))
    circles = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}"><title>{html.escape(day)}：{value:,}</title></circle>'
        for (day, value), (x, y) in zip(points, coordinates)
    )
    x_labels = "".join(
        f'<text x="{x:.1f}" y="{height - 14}" text-anchor="middle">{html.escape(day[5:])}</text>'
        for (day, _), (x, _) in zip(points, coordinates)
    )
    y_labels = "".join(
        f'<text x="{left - 10}" y="{y_position(value) + 4:.1f}" text-anchor="end">{value:,}</text>'
        for value in (minimum, maximum)
    )
    return (
        f'<svg class="trend-chart" viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="{html.escape(label)}趋势">'
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" class="axis"/>'
        f'<line x1="{left}" y1="{top + plot_height}" x2="{width - right}" y2="{top + plot_height}" class="axis"/>'
        f'{y_labels}<path d="{path}" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
        f'{circles}{x_labels}</svg>'
    )


def render_dashboard(records: list[dict[str, Any]]) -> str:
    if not records:
        return """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>内容质量趋势 · Scholar's Atlas</title><style>body{font-family:system-ui,sans-serif;max-width:760px;margin:5rem auto;padding:0 1.5rem;color:#1f2937;line-height:1.7}a{color:#2563eb}</style></head>
<body><h1>内容质量趋势</h1><p>暂无可用的 C3 审计报告。</p><p><a href="/">← 返回门户首页</a></p></body></html>"""

    latest, previous = records[-1], records[-2] if len(records) > 1 else None
    cards = []
    for key, label, color in TREND_METRICS:
        current = latest.get(key)
        before = previous.get(key) if previous else None
        cards.append(
            f'<article class="metric-card" style="--metric-color:{color}">'
            f'<div class="metric-label">{html.escape(label)}</div>'
            f'<div class="metric-value">{format_number(current)}</div>'
            f'<div class="metric-delta {delta_class(current, before)}">较前次 {delta_text(current, before)}</div>'
            "</article>"
        )
    auxiliary = []
    for key, _, label, _ in METRICS:
        if key in {"no_date", "stale", "imgs"} and key in latest:
            auxiliary.append(f"<li><span>{html.escape(label)}</span><strong>{format_number(latest[key])}</strong></li>")
    charts = "".join(
        f'<section class="chart-card"><h2>{html.escape(label)}</h2>{render_svg(records, key, label, color)}</section>'
        for key, label, color in TREND_METRICS
    )
    report_date = html.escape(latest["date"])
    report_count = len(records)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>内容质量趋势 · Scholar's Atlas</title>
<style>
:root{{--ink:#172033;--muted:#64748b;--line:#e2e8f0;--panel:#fff;--bg:#f8fafc;--accent:#7c3aed}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font-family:system-ui,-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;line-height:1.6}}
.wrap{{max-width:1120px;margin:0 auto;padding:3rem 1.25rem 4rem}} .hero{{display:flex;justify-content:space-between;gap:1.5rem;align-items:flex-end;margin-bottom:1.5rem}}
h1{{margin:0;font-size:clamp(1.8rem,4vw,2.8rem);letter-spacing:-.04em}} h2{{font-size:1rem;margin:0 0 .75rem}} p{{margin:.35rem 0}} .lede{{color:var(--muted);max-width:640px}} .badge{{white-space:nowrap;background:#ede9fe;color:#5b21b6;border-radius:999px;padding:.35rem .75rem;font-size:.85rem;font-weight:700}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:.8rem;margin:1.5rem 0}} .metric-card,.chart-card,.summary{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:1rem;box-shadow:0 8px 24px rgba(15,23,42,.04)}}
.metric-label{{color:var(--muted);font-size:.86rem}} .metric-value{{font-size:1.75rem;font-weight:800;margin:.15rem 0;color:var(--metric-color)}} .metric-delta{{font-size:.78rem}} .delta-up{{color:#b45309}} .delta-down{{color:#047857}} .delta-neutral,.delta-muted{{color:var(--muted)}}
.charts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(390px,1fr));gap:.8rem}} .chart-card{{min-width:0}} .trend-chart{{width:100%;height:auto;overflow:visible}} .trend-chart text{{fill:#64748b;font-size:12px}} .trend-chart .axis{{stroke:#cbd5e1;stroke-width:1}} .chart-empty{{color:var(--muted);font-size:.85rem;min-height:120px;display:flex;align-items:center;justify-content:center}}
.summary{{margin-top:.8rem}} .summary h2{{margin-bottom:.5rem}} .summary ul{{display:flex;flex-wrap:wrap;gap:.5rem 1.5rem;list-style:none;padding:0;margin:0}} .summary li{{display:flex;gap:.45rem;align-items:baseline}} .summary strong{{font-variant-numeric:tabular-nums}} .note{{color:var(--muted);font-size:.86rem;margin-top:1.25rem}} a{{color:#2563eb}}
@media(max-width:480px){{.wrap{{padding:2rem .8rem 3rem}}.hero{{display:block}}.badge{{display:inline-block;margin-top:.75rem}}.charts{{grid-template-columns:1fr}}}}
</style>
</head>
<body><main class="wrap">
<header class="hero"><div><h1>📈 内容质量趋势</h1><p class="lede">基于每周 C3 内容审计报告生成，直观查看内容规模、结构健康和跨站质量变化。</p></div><span class="badge">最近 {report_count} 份报告</span></header>
<div class="cards">{''.join(cards)}</div>
<section class="charts">{charts}</section>
<aside class="summary"><h2>最新基线 · {report_date}</h2><ul>{''.join(auxiliary)}</ul></aside>
<p class="note">数据来源：`sites-hub/reports/content-quality-*.md`。无足够历史报告时不绘制趋势；审计规则变化会在历史曲线中保留各自口径。</p>
<p><a href="/">← 返回门户首页</a> · <a href="/stats.html">访问统计</a></p>
</main></body></html>"""


def main() -> None:
    parser = argparse.ArgumentParser(description="将 C3 Markdown 审计报告生成静态趋势 Dashboard")
    parser.add_argument("--reports-dir", type=Path, required=True, help="content-quality-*.md 所在目录")
    parser.add_argument("--output", type=Path, required=True, help="生成的 HTML 路径")
    parser.add_argument("--max-weeks", type=int, default=12, help="最多展示的报告数（默认 12）")
    args = parser.parse_args()

    if args.max_weeks < 1:
        print("ERROR: --max-weeks must be at least 1", file=sys.stderr)
        raise SystemExit(2)
    records = load_reports(args.reports_dir, args.max_weeks)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_dashboard(records), encoding="utf-8")
    print(f"Dashboard: {args.output} ({len(records)} reports)")


if __name__ == "__main__":
    main()
