#!/usr/bin/env python3
"""
build-images.py — C11 图片处理工具（PNG/JPG → WebP + markdown snippet 生成）

背景：
  - 28 站当前 0 真实文章图片（imgs: 0 from audit-content.py）
  - 未来新增图片时，需要：(1) 转 WebP (2) 输出正确 markdown
  - 此工具让"放入图片 → 得到 <picture> snippet"一步到位

依赖：
  - PIL (Pillow) >= 10.0
  - macOS: 已自带 PIL（v11+），无需安装
  - Linux: pip install Pillow

用法：
  python3 build-images.py <input.png>                    # 单文件，转 WebP + 生成 snippet
  python3 build-images.py <input.png> --alt "图说明"      # 自定义 alt
  python3 build-images.py <dir/> --recursive              # 批量
  python3 build-images.py <input.png> --no-snippet        # 只转，不生成 markdown

输出：
  - 同目录生成 <input>.webp（q=85，有损压缩）
  - stdout 输出 markdown `<img>` snippet（lazy + decoding + alt）

为什么不用 cwebp：
  - macOS 默认不装 webp CLI
  - PIL 跨平台 + 内置，无需额外依赖

为什么不用 AVIF：
  - PIL 默认不带 AVIF 支持
  - WebP 已覆盖 95%+ 浏览器，体积比 PNG 小 25-35%，足够

未来扩展（按需）：
  - 多尺寸 srcset（480w / 960w / 1920w）
  - 暗色模式版本（PIL ImageEnhance 调亮度 + 饱和度）
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print('ERROR: Pillow not installed. Run: pip install Pillow', file=sys.stderr)
    sys.exit(1)

WEBP_QUALITY = 85  # VitePress/Chromium 推荐值（>80 视觉无损，<90 体积可控）

def to_webp(src: Path, q: int = WEBP_QUALITY) -> Path:
    """PNG/JPG → WebP（同尺寸，q=85），返回输出路径"""
    out = src.with_suffix('.webp')
    img = Image.open(src)
    # PNG 带 alpha 通道 → 保留；JPG 不带 → RGB
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGBA')
    else:
        img = img.convert('RGB')
    img.save(out, 'WEBP', quality=q, method=6)  # method=6 = 最慢但最小
    saved_pct = (1 - out.stat().st_size / src.stat().st_size) * 100
    print(f'  {src.name} → {out.name}  '
          f'{src.stat().st_size//1024}KB → {out.stat().st_size//1024}KB  '
          f'(-{saved_pct:.0f}%)', file=sys.stderr)
    return out

def make_snippet(webp: Path, src: Path, alt: str, *, lazy: bool = True, decoding: bool = True) -> str:
    """生成 markdown 图片 snippet（VitePress 友好）

    相对路径策略：snippet 中 src = webp 相对于当前 cwd（用户调用工具的目录）。
    用户通常在子站 docs/<chapter>/ 下执行工具，输出到 docs/public/images/。
    此时 snippet 会显示 ../public/images/xxx.webp（正确）。
    """
    attrs = []
    if lazy:
        attrs.append('loading="lazy"')
    if decoding:
        attrs.append('decoding="async"')
    attr_str = ' '.join(attrs)
    try:
        rel = webp.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        # webp 不在 cwd 下，回退到绝对路径
        rel = webp.resolve()
    return f'<img src="{rel}" alt="{alt}" {attr_str} />'.replace('  />', ' />')

def process_one(src: Path, alt: str, *, quality: int, no_snippet: bool, dry_run: bool, snippet_kwargs: dict) -> None:
    if not src.is_file():
        print(f'ERROR: {src} not found', file=sys.stderr)
        sys.exit(1)
    if src.suffix.lower() not in ('.png', '.jpg', '.jpeg'):
        print(f'ERROR: {src} not PNG/JPG (got {src.suffix})', file=sys.stderr)
        sys.exit(1)
    if dry_run:
        print(f'[dry-run] would convert {src}', file=sys.stderr)
        webp = src.with_suffix('.webp')
    else:
        webp = to_webp(src, q=quality)
    if not no_snippet:
        print(make_snippet(webp, src, alt, **snippet_kwargs))

def process_dir(d: Path, alt_suffix: str, *, quality: int, no_snippet: bool, recursive: bool, dry_run: bool) -> None:
    pattern = '**/*' if recursive else '*'
    files = [p for p in d.glob(pattern)
             if p.is_file() and p.suffix.lower() in ('.png', '.jpg', '.jpeg')]
    if not files:
        print(f'No PNG/JPG in {d}', file=sys.stderr)
        return
    for src in sorted(files):
        # alt 默认 = 文件名去后缀 + alt_suffix
        alt = f'{src.stem}{alt_suffix}'.strip()
        process_one(src, alt, quality=quality, no_snippet=no_snippet,
                    dry_run=dry_run, snippet_kwargs={})

def quality_range(value: str) -> int:
    quality = int(value)
    if not 0 <= quality <= 100:
        raise argparse.ArgumentTypeError('quality must be between 0 and 100')
    return quality

def main():
    ap = argparse.ArgumentParser(description='C11 图片处理：PNG/JPG → WebP + 生成 markdown snippet')
    ap.add_argument('input', help='输入图片路径 或 目录')
    ap.add_argument('--alt', default='', help='alt 文本（默认：文件名去后缀）')
    ap.add_argument('--alt-suffix', default='', help='批量时附加到文件名后作为 alt')
    ap.add_argument('--recursive', action='store_true', help='目录递归')
    ap.add_argument('--no-snippet', action='store_true', help='只转 WebP，不输出 markdown')
    ap.add_argument('--dry-run', action='store_true', help='只打印，不写文件')
    ap.add_argument('-q', '--quality', type=quality_range, default=WEBP_QUALITY, help=f'WebP 质量 0-100 (默认 {WEBP_QUALITY})')
    args = ap.parse_args()

    src = Path(args.input)
    if src.is_dir():
        process_dir(src, args.alt_suffix or args.alt,
                    quality=args.quality,
                    no_snippet=args.no_snippet,
                    recursive=args.recursive,
                    dry_run=args.dry_run)
    else:
        alt = args.alt or src.stem
        process_one(src, alt, quality=args.quality, no_snippet=args.no_snippet,
                    dry_run=args.dry_run, snippet_kwargs={})

if __name__ == '__main__':
    main()
