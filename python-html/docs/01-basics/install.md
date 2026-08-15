---
title: 安装与环境
---

# 📥 安装与环境

> 5 分钟搭建 Python 开发环境。本章覆盖 Windows / macOS / Linux 三平台 + 虚拟环境 + 包管理。

## 🛠️ 安装 Python

### Windows

```powershell
# 方式 1：官方安装包
# 下载：https://www.python.org/downloads/windows/
# 推荐：Python 3.11.x
# 安装时勾选 "Add Python to PATH"

# 方式 2：Microsoft Store
# 搜索 "Python 3.11" 直接安装

# 方式 3：包管理器（推荐）
choco install python311

# 验证
python --version
```

### macOS

```bash
# 方式 1：官方安装包
# 下载：https://www.python.org/downloads/macos/

# 方式 2：Homebrew（推荐）
brew install python@3.11

# 配置 PATH（如果用 Homebrew）
echo 'export PATH="/opt/homebrew/opt/python@3.11/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 验证
python3 --version
```

### Linux

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# CentOS/RHEL
sudo yum install python3.11

# 验证
python3 --version
python3 -m pip --version
```

## 📦 包管理

### pip（官方）

```bash
# 安装包
pip install requests
pip install requests==2.31.0
pip install requests>=2.30

# 升级包
pip install --upgrade requests

# 卸载
pip uninstall requests

# 列出已安装
pip list
pip list --outdated

# 导出依赖
pip freeze > requirements.txt
pip install -r requirements.txt

# 显示包信息
pip show requests

# 搜索
pip search fastapi
```

### pip 配置镜像源

```bash
# 临时使用
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple requests

# 永久配置
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << EOF
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF
```

## 🌐 虚拟环境（重要）

> **每个项目应有独立的虚拟环境**，避免依赖冲突。

### venv（标准库，推荐）

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate

# 停用
deactivate

# 删除虚拟环境
rm -rf venv
```

### virtualenv（第三方，功能更强）

```bash
pip install virtualenv

# 创建
virtualenv venv
# 或指定 Python 版本
virtualenv -p python3.11 venv
```

### conda（数据科学常用）

```bash
# 创建
conda create -n myenv python=3.11

# 激活
conda activate myenv

# 安装包
conda install numpy pandas

# 停用
conda deactivate

# 删除
conda env remove -n myenv
```

## 🛠️ 开发工具

### IDE / 编辑器

```
✅ PyCharm（JetBrains，最专业）
   - Community（免费）
   - Professional（付费）
   - 内置虚拟环境、调试、测试

✅ VS Code（推荐，免费）
   - 安装 Python 扩展
   - 安装 Pylance
   - 安装 Python Test Explorer
   - 设置 settings.json：

{
  "python.defaultInterpreterPath": "venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "[python]": {
    "editor.formatOnSave": true
  }
}

✅ Jupyter Notebook（数据科学）
   pip install jupyter
   jupyter notebook
```

### 格式化工具

```bash
# Black（最流行）
pip install black
black myfile.py
black myproject/

# autopep8
pip install autopep8
autopep8 --in-place myfile.py

# isort（import 排序）
pip install isort
isort myfile.py
```

### 静态检查

```bash
# mypy（类型检查）
pip install mypy
mypy myfile.py

# flake8
pip install flake8
flake8 myfile.py

# pylint
pip install pylint
pylint myfile.py
```

## 🚀 第一个 Python 程序

### Hello World

```python
# hello.py
print("Hello, World!")
```

```bash
python hello.py
# 输出: Hello, World!
```

### REPL（交互式解释器）

```bash
# 启动
python3

# 交互式执行
>>> print("Hello, World!")
Hello, World!
>>> 1 + 2
3
>>> name = "Python"
>>> f"Hello, {name}!"
'Hello, Python!'
>>> exit()
```

### 脚本模式

```python
# script.py
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <name>")
        sys.exit(1)
    
    name = sys.argv[1]
    print(f"Hello, {name}!")

if __name__ == "__main__":
    main()
```

```bash
python script.py World
# 输出: Hello, World!
```

## 🛠️ 常用工具

```bash
# 虚拟环境
python3 -m venv venv

# 依赖管理
pip install package
pip freeze > requirements.txt
pip install -r requirements.txt

# 包管理升级
python3 -m pip install --upgrade pip

# 测试
python3 -m unittest
python3 -m pytest

# 性能分析
python3 -m cProfile script.py

# 模块文档
python3 -m pydoc module_name
```

## 📁 项目结构示例

```
myproject/
├── venv/                  # 虚拟环境（不提交到 git）
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── module1.py
│   └── module2.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── docs/
├── data/
├── requirements.txt        # 生产依赖
├── requirements-dev.txt    # 开发依赖
├── .gitignore
├── README.md
└── setup.py 或 pyproject.toml
```

## 🎯 总结

**Python 环境搭建核心要点**：
- ✅ Python 3.11+（推荐）
- ✅ 每个项目独立虚拟环境
- ✅ pip 是包管理工具
- ✅ VS Code 或 PyCharm 作 IDE
- ✅ 格式化（black）+ 检查（mypy）
- ⚠️ 避免全局 pip install
- ⚠️ requirements.txt 提交到版本控制

**下一步：** [🔤 基础语法](/01-basics/syntax) — 变量、字符串、运算符
