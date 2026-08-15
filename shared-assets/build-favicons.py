#!/usr/bin/env python3
"""Generate favicon.svg + favicon.ico from a base SVG."""
import io, struct, zlib
from pathlib import Path
from PIL import Image

SVG_PATH = Path('/Users/a1111/work_space/elastic-search-demo/shared-assets/favicon.svg')
OUT_DIR = Path('/Users/a1111/work_space/elastic-search-demo/shared-assets')
OUT_DIR.mkdir(exist_ok=True)

svg = SVG_PATH.read_text()
print(f'Source SVG: {len(svg)} bytes')

# Render SVG to PNG via cairo? Or use PIL on a hand-built icon
# Simpler: use the gradient + book design but rendered directly with PIL
def build_icon(size: int) -> Image.Image:
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    px = img.load()
    # Rounded rect gradient background
    accent_a = (196, 98, 61, 255)    # rust
    accent_b = (124, 58, 237, 255)   # purple
    radius = int(size * 14 / 64)
    for y in range(size):
        for x in range(size):
            # Rounded rect mask
            dx = max(0, max(radius - x, x - (size - 1 - radius)))
            dy = max(0, max(radius - y, y - (size - 1 - radius)))
            if (dx * dx + dy * dy) > radius * radius:
                continue
            t = (x + y) / (2 * (size - 1))
            r = int(accent_a[0] * (1 - t) + accent_b[0] * t)
            g = int(accent_a[1] * (1 - t) + accent_b[1] * t)
            b = int(accent_a[2] * (1 - t) + accent_b[2] * t)
            px[x, y] = (r, g, b, 255)
    # Draw book outline + center line
    overlay = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = Image.new('RGB', (size, size), 'white')
    from PIL import ImageDraw
    d = ImageDraw.Draw(overlay)
    fg_color = (251, 247, 238, 255)  # cream
    # Book outline (left page, spine, right page)
    margin = int(size * 16 / 64)
    w = int(size * 1.6 / 64)
    # Left page edge
    d.line([(margin, margin), (margin, size - margin)], fill=fg_color, width=max(2, w))
    # Right page edge
    d.line([(size - margin, margin), (size - margin, size - margin)], fill=fg_color, width=max(2, w))
    # Top
    d.line([(margin, margin), (size - margin, margin)], fill=fg_color, width=max(2, w))
    # Spine (slightly diagonal)
    cx = size // 2
    d.line([(cx, margin + 2), (cx, size - margin - 2)], fill=fg_color, width=max(2, w))
    img = Image.alpha_composite(img, overlay)
    return img

# Build 32x32 ICO (single image)
icon32 = build_icon(32)
icon32_path = OUT_DIR / 'favicon-32.png'
icon32.save(icon32_path)
icon16 = build_icon(16).resize((16, 16))
icon16_path = OUT_DIR / 'favicon-16.png'
icon16.save(icon16_path)

# Build proper ICO with both 16 and 32
ico_path = OUT_DIR / 'favicon.ico'
icon32.save(ico_path, format='ICO', sizes=[(16, 16), (32, 32)])
print(f'ICO: {ico_path} ({ico_path.stat().st_size} bytes)')

# Also output 180x180 apple-touch-icon PNG
apple = build_icon(180)
apple_path = OUT_DIR / 'apple-touch-icon.png'
apple.save(apple_path)
print(f'Apple touch icon: {apple_path} ({apple_path.stat().st_size} bytes)')
print('Done')