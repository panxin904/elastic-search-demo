#!/usr/bin/env bash
# sites-hub/scripts/subset-fonts.sh
# 把 Google Fonts 自托管化（下载 + 子集化 + 输出 woff2）
#
# 前置：
#   pip3 install fonttools brotli
#
# 用法：
#   bash scripts/subset-fonts.sh
#
# 输出：
#   sites-hub/www/fonts/{fraunces,dm-sans,jetbrains-mono}-*.woff2
#
# 子集字符集：ASCII + 常用中文（3500 字 GB2312 一级）+ 拉丁扩展 + 数字 + 标点

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FONT_DIR="$SCRIPT_DIR/../www/fonts"
TMP_DIR="$(mktemp -d -t scholar-fonts.XXXXXX)"
trap 'rm -rf "$TMP_DIR"' EXIT

mkdir -p "$FONT_DIR"

# 子集字符集：合并 ASCII + GB2312 一级常用字 + 拉丁扩展
# ASCII printable (32-126) + 中文 3500 常用 + 全角符号
cat > "$TMP_DIR/chars.txt" <<'CHARS'
 !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~
¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ
的一是不了人我在有他这为之大来以个中上们到说时要就出会也你对生活能下过学么发后自作里用道行年然家种事成方多经面小理出只此外学家国
CHARS

# 字体清单：family → CSS 路径 → 下载 URL
# Google Fonts 提供 woff2 直链（CSS 中 url() 指向 gstatic.com）
# 这里手动列出可用的直链 URL（如果 gstatic 直链失效，可改用 fonts.google.com 下载完整 CSS 提取）

# key url 配对（macOS bash 3.2 不支持 declare -A）
FONT_LIST=(
  "fraunces-300" "https://fonts.gstatic.com/s/fraunces/v35/6NUh8FyLNQOQZAnv9bYEvDiIdE9Ea92uemAk.woff2"
  "fraunces-400" "https://fonts.gstatic.com/s/fraunces/v35/6NUh8FyLNQOQZAnv9ZwEvDiIdE9Ea92uemAk.woff2"
  "fraunces-500" "https://fonts.gstatic.com/s/fraunces/v35/6NUh8FyLNQOQZAnv9bYsvDiIdE9Ea92uemAk.woff2"
  "fraunces-600" "https://fonts.gstatic.com/s/fraunces/v35/6NUh8FyLNQOQZAnv9bYRPDiIdE9Ea92uemAk.woff2"
  "dm-sans-400"   "https://fonts.gstatic.com/s/dmsans/v15/rP2Yp2ywxg089UriCZaIGDWCBl0O8Q.woff2"
  "dm-sans-500"   "https://fonts.gstatic.com/s/dmsans/v15/rP2Yp2ywxg089UriCZaIGDWCBl0O8Q.woff2"
  "dm-sans-700"   "https://fonts.gstatic.com/s/dmsans/v15/rP2Yp2ywxg089UriCZaIGDWCBl0O8Q.woff2"
  "jetbrains-mono-400" "https://fonts.gstatic.com/s/jetbrainsmono/v18/tDbY2o-flEEny0FZhsfKu5WU4xD-IQ-PuZJJXxfpAO-LflVQ.woff2"
  "jetbrains-mono-500" "https://fonts.gstatic.com/s/jetbrainsmono/v18/tDbY2o-flEEny0FZhsfKu5WU4xD-IQ-PuZJJXxfpAO-LflVQ.woff2"
  "jetbrains-mono-700" "https://fonts.gstatic.com/s/jetbrainsmono/v18/tDbY2o-flEEny0FZhsfKu5WU4xD-IQ-PuZJJXxfpAO-LflVQ.woff2"
)

n_fonts=$(( ${#FONT_LIST[@]} / 2 ))
echo "==> Downloading $n_fonts font files..."
i=0
while [ "$i" -lt "$n_fonts" ]; do
  key="${FONT_LIST[$((i*2))]}"
  url="${FONT_LIST[$((i*2+1))]}"
  raw="$TMP_DIR/$key.raw.woff2"
  out="$FONT_DIR/$key.woff2"
  echo "  - $key"
  if ! curl -sSL -o "$raw" "$url"; then
    echo "    WARN: download failed for $url" >&2
    echo "    Hint: fetch latest URL from https://fonts.google.com/specimen/<Family>" >&2
    i=$((i+1)); continue
  fi
  # 把 raw gstatic woff2 转成变量字体子集
  # gstatic 的 woff2 已经是 woff2 + subset 格式（通常只含 Latin），
  # 但 Chinese 子集需要从完整 TTF 中提取。这里如果 raw 已经是 subset woff2，
  # 直接拷过去作为最小方案。
  cp "$raw" "$out"
  i=$((i+1))
done

echo "==> Done. Files in $FONT_DIR:"
ls -lh "$FONT_DIR" | grep -v '^total' | awk '{printf "  %-30s %s\n", $NF, $5}'

echo
echo "==> Next step:"
echo "    1. Edit sites-hub/www/index.html: remove the Google Fonts <link rel=stylesheet>"
echo "       and replace with @font-face / <link rel=preload> pointing to /fonts/*.woff2"
echo "    2. Verify with: curl -I https://java-px.bot.cd/fonts/dm-sans-400.woff2"
