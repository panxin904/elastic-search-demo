#!/usr/bin/env python3
"""Add '视频处理' link to '更多站点' menu in all sites' config.mts files."""
import os
import re

SITES = ['ai', 'architecture', 'bigdata', 'cloud-native', 'es', 'frontend',
         'java-language', 'java-web-manual', 'kafka', 'linux', 'mysql',
         'network', 'python', 'redis', 'springcloud', 'tools']

ROOT = '/Users/a1111/work_space/elastic-search-demo'

new_entry = "{ text: '视频处理', link: 'https://java-px.bot.cd/video/' }"

for site in SITES:
    config_path = os.path.join(ROOT, f'{site}-html', '.vitepress', 'config.mts')
    if not os.path.exists(config_path):
        print(f'SKIP {site}: config not found')
        continue
    with open(config_path, 'r') as f:
        content = f.read()

    if 'java-px.bot.cd/video/' in content:
        print(f'SKIP {site}: already has video link')
        continue

    # Find "更多站点" section and add the new entry at the end (before the closing)
    pattern = r"(items:\s*\[)([^\]]*?)(\])"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        print(f'WARN {site}: items array not found')
        continue

    pre, body, post = match.group(1), match.group(2).rstrip(), match.group(3)

    # Determine whether the last entry has a trailing comma
    last_entry_match = re.search(r"({[^{}]*}\s*)$", body)
    if last_entry_match:
        last_entry = last_entry_match.group(1)
        body_no_last = body[:last_entry_match.start(1)].rstrip()
        has_comma = last_entry.rstrip().endswith(',')
        if not has_comma:
            # Add comma to the existing entry, then new entry without trailing comma
            new_body = body_no_last + '\n        ' + last_entry + ',\n        ' + new_entry
        else:
            # Existing last entry has comma, just append new entry
            new_body = body.rstrip() + '\n        ' + new_entry
    else:
        new_body = new_entry

    new_section = pre + new_body + '\n      ' + post
    new_content = content[:match.start()] + new_section + content[match.end():]
    with open(config_path, 'w') as f:
        f.write(new_content)
    print(f'OK {site}')
