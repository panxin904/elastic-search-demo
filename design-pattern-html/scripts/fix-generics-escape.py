#!/usr/bin/env python3
"""Escape Java/TypeScript generics like <User> in design-pattern-html docs.

Vue Markdown parser interprets <X> as HTML tag, breaking build.
Escape with backslash: \\<X\\>
"""
import re
from pathlib import Path

ROOT = Path("/Users/a1111/work_space/elastic-search-demo/design-pattern-html/docs")

# At least 1 alphanumeric + 0+ [a-zA-Z0-9_:&\' ,]
pattern = re.compile(r"<([a-zA-Z][a-zA-Z0-9_:&\' ,]*)>")


def escape_in_line(line: str) -> tuple[str, int]:
    new_chars = []
    last = 0
    count = 0
    for m in pattern.finditer(line):
        prefix = line[:m.start()]
        # Skip if inside inline code (odd number of backticks)
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
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            new_lines.append(line)
            continue
        if in_code_block:
            new_lines.append(line)
            continue
        new_line, count = escape_in_line(line)
        new_lines.append(new_line)
        file_changes += count
    if file_changes > 0:
        f.write_text("\n".join(new_lines), encoding="utf-8")
        total_files += 1
        total_changes += file_changes
        print(f"  + {f.relative_to(ROOT.parent)} ({file_changes} changes)")

print(f"\nDone. {total_files} files, {total_changes} generics escaped.")