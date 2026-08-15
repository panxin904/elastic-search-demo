#!/usr/bin/env python3
"""make-og-cover.py - 生成 1200x630 og-cover.png.

有 Pillow: 渐变背景 + 品牌标题 + 副标题（推荐版本）
无 Pillow: 纯色 #1a1a2e 占位版（降级）

用法:
  python3 scripts/make-og-cover.py [output_path]
默认输出: sites-hub/www/og-cover.png
"""
from pathlib import Path
import struct, zlib, sys

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "www" / "og-cover.png"
W, H = 1200, 630

def png_chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data +
            struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))

def write_solid_png(path, w, h, rgb=(26, 26, 46)):
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)
    raw = bytearray()
    r, g, b = rgb
    for _ in range(h):
        raw.append(0)
        for _ in range(w):
            raw.extend((r, g, b, 255))
    idat = zlib.compress(bytes(raw), 9)
    path.write_bytes(sig + png_chunk(b"IHDR", ihdr) + png_chunk(b"IDAT", idat) + png_chunk(b"IEND", b""))

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_OK = True
except Exception:
    PIL_OK = False

if PIL_OK:
    img = Image.new("RGB", (W, H), (26, 26, 46))
    px = img.load()
    c1, c2 = (26, 26, 46), (14, 16, 24)
    for y in range(H):
        for x in range(W):
            t = (x / (W - 1) + y / (H - 1)) / 2
            px[x, y] = (int(c1[0] * (1 - t) + c2[0] * t),
                        int(c1[1] * (1 - t) + c2[1] * t),
                        int(c1[2] * (1 - t) + c2[2] * t))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(80, 80), (W - 80, H - 80)], outline=(196, 98, 61), width=4)
    font_paths = [
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/Library/Fonts/Georgia.ttf",
    ]
    sub_paths = [
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    def first_existing(paths):
        for p in paths:
            if Path(p).exists():
                return p
        return None
    serif = first_existing(font_paths)
    sans = first_existing(sub_paths)
    f_title = ImageFont.truetype(serif, 96) if serif else ImageFont.load_default()
    f_sub = ImageFont.truetype(sans, 38) if sans else f_title
    f_meta = ImageFont.truetype(sans, 26) if sans else f_title

    def center_text(text, y, font, fill):
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text(((W - (bbox[2] - bbox[0])) / 2, y), text, font=font, fill=fill)

    center_text("Scholar's Atlas", 230, f_title, (245, 245, 245))
    center_text("28 sites  ·  1429+ pages  ·  1154 nodes", 360, f_sub, (196, 98, 61))
    center_text("java-px.bot.cd", 430, f_meta, (180, 180, 200))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    print(f"[make-og-cover] Pillow -> {OUT} ({OUT.stat().st_size} bytes)")
else:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    write_solid_png(OUT, W, H, (26, 26, 46))
    print(f"[make-og-cover] FALLBACK (solid) -> {OUT} ({OUT.stat().st_size} bytes)")
    print("[make-og-cover] Pillow missing. Branded: pip3 install --user Pillow")
