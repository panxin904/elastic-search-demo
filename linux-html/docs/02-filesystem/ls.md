---
title: ls / cp / mv
date: 2026-08-15  # date-auto-injected
---

# ls / cp / mv / cd / pwd

> 最高频的 5 个命令。

## 📜 ls - 列出文件

```bash
ls                  # 当前目录
ls /etc             # 指定目录
ls -l               # 长格式（权限、属主、大小、时间）
ls -a               # 显示隐藏文件（.开头）
ls -lh              # 长格式 + 人类可读大小
ls -lt              # 按修改时间倒序
ls -lS              # 按大小排序
ls -R               # 递归列出
ls -ld /etc        # 看目录本身（不是内容）

# 实战
ls -lhS | head            # 最大的 10 个文件
ls -lt | head             # 刚改的文件
ls -lh /var/log/*.log     # 日志
```

### 输出字段含义

```
-rw-r--r-- 1 alice alice 1.2K Jun  1 10:23 file.txt
││└┬┘│└┬┘ │    │      │    │      │
││ │ ││ │ │    │      │    │      └─ 文件名
││ │ ││ │ │    │      │    └─ 修改时间
││ │ ││ │ │    │      └─ 大小
││ │ ││ │ │    │      └─ 属组
││ │ ││ │ │    │      └─ 属主
││ │ ││ │ │    └─ 链接数
││ │ ││ │ └── 其他 (r=读 w=写 x=执行 -无权限)
││ │ ││ └── 属组权限
││ │ │└── 属主权限
││ │ └─── 文件类型 (- 普通 / d 目录 / l 软链)
└─ 第一位隐藏权限（文件类型）
```

## 📁 cd - 切换目录

```bash
cd /                  # 绝对路径
cd ..                 # 上级
cd ~                  # HOME
cd -                  # 上一目录
cd ~/projects        # 相对 HOME
cd "My Documents"    # 带空格的目录要加引号
```

## 📋 pwd - 当前路径

```bash
pwd                          # 物理路径（解软链）
pwd -P                       # 同上
```

## 📦 cp - 复制

```bash
cp file dst/                 # 复制文件
cp -r dir/ dst/              # 递归
cp -r src/* dst/             # 复制 src 下所有内容（不含 src 本身）
cp -a src/ dst/              # archive 模式（保留权限/时间/软链）
cp -n file dst/              # 不覆盖已存在
cp -i file dst/              # 覆盖前确认
cp -v file dst/              # 详细
cp file{,.bak}               # file + file.bak（花括号展开）
```

## 🚚 mv - 移动 / 重命名

```bash
mv old new                   # 改名
mv file dir/                 # 移动
mv -i file dir/              # 覆盖前确认
mv -n file dir/              # 不覆盖
mv -v file dir/              # 详细

# 批量改后缀
for f in *.html; do mv "$f" "${f%.html}.htm"; done
```

## 🗑️ rm - 删除

```bash
rm file                      # 单文件
rm -r dir                    # 递归
rm -rf dir                   # 强制递归（**慎用**）
rm -i file                   # 删前确认
rm -- file                   # 删 - 开头的文件

# 安全替代：trash-cli
trash-put file               # 移到回收站
trash-list                   # 看回收站
trash-restore                # 还原

# 文件保险：先备份再删
mkdir -p bak && mv * bak/ 2>/dev/null
```

## ⚡ 速查表

| 命令 | 关键选项 |
|------|---------|
| ls | `-l -a -h -t -S -R -d` |
| cp | `-r -a -n -i -v` |
| mv | `-i -n -v` |
| rm | `-r -f -i` |
| cd | `-` |
| pwd | `-P` |

## ⚠️ 危险操作

```bash
# ❌ 绝对不要
rm -rf /                       # 删根
rm -rf /*                      # 同上
rm -rf .*                      # 删隐藏文件但漏 . 和 ..

# ⚠️ 小心
rm -rf $VAR/*                  # 变量为空 = /（删根）
```

## 🔗 下一步

- [find 查找](/02-filesystem/find)
- [软链与硬链](/02-filesystem/ln)
- [权限 (rwx)](/02-filesystem/permissions)