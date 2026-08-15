#!/usr/bin/env python3
"""
更激进地修复 rust-html markdown 文件中所有 <XXX> 形式（包括标题）。
Vue 把这些当成 HTML 标签，导致 "Element is missing end tag" 错误。
策略：用 \ 转义 < （最不影响显示）。
"""
import re
from pathlib import Path

ROOT = Path("rust-html/docs")

# 匹配 <identifier> 或 <keyword identifier>（含逗号、& 空格）
# 不匹配反引号内的
pattern = re.compile(r'<([a-zA-Z][a-zA-Z0-9_:&\' ,]*[a-zA-Z0-9_&\',])>')


def escape_in_line(line: str) -> tuple[str, int]:
    """把不在反引号内的 <XXX> 转义为 \\<XXX\\>。返回 (新行, 修改次数)。"""
    new_chars = []
    last = 0
    count = 0
    for m in pattern.finditer(line):
        # 检查是否在反引号内
        prefix = line[:m.start()]
        if prefix.count('`') % 2 == 1:
            continue
        new_chars.append(line[last:m.start()])
        # 用 \ 转义 < 和 >
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
