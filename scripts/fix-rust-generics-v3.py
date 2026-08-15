#!/usr/bin/env python3
"""
最终修复版：把所有 <X> 或 <X,Y> 形式（即使单个字符）都转义。
Vue 把这些当成 HTML 标签。用 \ 转义 < 和 >。
"""
import re
from pathlib import Path

ROOT = Path("rust-html/docs")

# 至少 1 字符 + 0 字符 + 至少 1 字符 = 至少 1 字符
# 但允许像 <T> 这种单字符
pattern = re.compile(r"<([a-zA-Z][a-zA-Z0-9_:&\' ,]*)>")


def escape_in_line(line: str) -> tuple[str, int]:
    new_chars = []
    last = 0
    count = 0
    for m in pattern.finditer(line):
        prefix = line[:m.start()]
        if prefix.count("`") % 2 == 1:
            continue
        new_chars.append(line[last:m.start()])
        new_chars.append(f"\\<{m.group(1)}\\>")
        last = m.end()
        count += 1
    new_chars.append(line[last:])
    return "".join(new_chars), count


total_files = 0
total_changes = 0
for f in sorted(ROOT.rglob("*.md")):
    if f.name == "index.md":
        continue
    text = f.read_text(encoding="utf-8")
    lines = text.split("\n")
    new_lines = []
    in_code_block = False
    file_changes = 0
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            new_lines.append(line)
            continue
        if in_code_block:
            new_lines.append(line)
            continue
        new_line, count = escape_in_line(line)
        if count:
            file_changes += count
        new_lines.append(new_line)
    if file_changes:
        new_text = "\n".join(new_lines)
        f.write_text(new_text, encoding="utf-8")
        print(f"  {f.relative_to(ROOT)}: {file_changes}")
        total_files += 1
        total_changes += file_changes

print(f"\nTotal: {total_files} files, {total_changes} replacements")
