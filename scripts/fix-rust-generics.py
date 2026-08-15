#!/usr/bin/env python3
"""
扫描所有 rust-html markdown 文件，把被 Vue 误识别为 HTML 标签的 Rust 泛型
（如 <Mutex>、<T>、&Mutex<T> 等）用反引号包裹。
"""
import re
from pathlib import Path

ROOT = Path("rust-html/docs")

# 匹配 <XXX> 或 <XXX<YYY>>（Rust 嵌套泛型）
# 不匹配代码块 / 行内代码
pattern = re.compile(r'<([A-Z][A-Za-z0-9_:&\' ,]*[A-Za-z0-9_&\',])>')


def is_in_code(line: str, pos: int) -> bool:
    """检查 pos 处是否在行内代码（反引号包围）内。"""
    # 找到所有反引号对
    backticks = [m.start() for m in re.finditer(r'`', line)]
    depth = 0
    for bt in backticks:
        if bt > pos:
            break
        depth ^= 1
    return depth == 1


total = 0
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
        # 在正文行中替换所有 <XXX> 形式（不在反引号内）
        new_chars = []
        i = 0
        last = 0
        for m in pattern.finditer(line):
            # 检查是否在行内代码内
            if not is_in_code(line, m.start()):
                # 检查前面是否有反引号紧贴
                # 简单策略：替换
                pass
            else:
                continue
            # 检查是否在反引号内（用简单启发式：前面紧邻的反引号对）
            prefix = line[:m.start()]
            # 计算前面未配对的反引号数
            bt_count = prefix.count('`')
            if bt_count % 2 == 1:
                continue  # 在反引号对内，跳过
            new_chars.append(line[last:m.start()])
            new_chars.append(f"`<{m.group(1)}>`")
            last = m.end()
        new_chars.append(line[last:])
        new_line = "".join(new_chars)
        if new_line != line:
            file_changes += 1
        new_lines.append(new_line)
    if file_changes:
        new_text = "\n".join(new_lines)
        f.write_text(new_text, encoding="utf-8")
        print(f"  {f.relative_to(ROOT)}: {file_changes} lines")
        total += file_changes

print(f"\nTotal: {total} files modified")
