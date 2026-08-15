// Python 知识图谱数据 - 60+ 节点 + 关系边
export interface GraphNode {
  id: string
  name: string
  category: string
  value: number
  link: string
}

export interface GraphLink {
  source: string
  target: string
}

export interface GraphData {
  nodes: GraphNode[]
  links: GraphLink[]
}

export const graphData: GraphData = {
  "nodes": [
    // ============== 01 入门 ==============
    { "id": "intro",         "name": "Python 是什么",         "category": "basics",     "value": 10, "link": "/01-basics/intro" },
    { "id": "install",       "name": "安装与环境",              "category": "basics",     "value": 9,  "link": "/01-basics/install" },
    { "id": "syntax",        "name": "基础语法",                "category": "basics",     "value": 10, "link": "/01-basics/syntax" },
    { "id": "data-structures","name": "数据结构",                "category": "basics",     "value": 9,  "link": "/01-basics/data-structures" },
    { "id": "control-flow",  "name": "控制流",                  "category": "basics",     "value": 8,  "link": "/01-basics/control-flow" },

    // ============== 02 底层原理 ==============
    { "id": "interpreter",   "name": "Python 解释器",          "category": "principles", "value": 9,  "link": "/02-principles/interpreter" },
    { "id": "bytecode",      "name": "字节码与执行",            "category": "principles", "value": 9,  "link": "/02-principles/bytecode" },
    { "id": "object-model",  "name": "对象模型",                "category": "principles", "value": 10, "link": "/02-principles/object-model" },
    { "id": "memory",        "name": "内存管理",                "category": "principles", "value": 9,  "link": "/02-principles/memory" },
    { "id": "gil",           "name": "GIL 全局锁",              "category": "principles", "value": 10, "link": "/02-principles/gil" },
    { "id": "gc",            "name": "垃圾回收",                "category": "principles", "value": 8,  "link": "/02-principles/gc" },
    { "id": "profiling",     "name": "性能剖析",                "category": "principles", "value": 8,  "link": "/02-principles/profiling" },

    // ============== 03 常用库 ==============
    { "id": "stdlib",        "name": "标准库概览",              "category": "libraries",  "value": 8,  "link": "/03-libraries/stdlib" },
    { "id": "requests",      "name": "requests HTTP",          "category": "libraries",  "value": 10, "link": "/03-libraries/requests" },
    { "id": "beautifulsoup", "name": "BeautifulSoup",          "category": "libraries",  "value": 9,  "link": "/03-libraries/beautifulsoup" },
    { "id": "sqlalchemy",    "name": "SQLAlchemy ORM",         "category": "libraries",  "value": 8,  "link": "/03-libraries/sqlalchemy" },
    { "id": "pandas",        "name": "pandas 数据分析",         "category": "libraries",  "value": 10, "link": "/03-libraries/pandas" },
    { "id": "pytest",        "name": "pytest 测试",            "category": "libraries",  "value": 8,  "link": "/03-libraries/pytest" },

    // ============== 04 并发 ==============
    { "id": "threading",     "name": "threading 多线程",       "category": "concurrency","value": 9,  "link": "/04-concurrency/threading" },
    { "id": "multiprocessing","name": "multiprocessing",      "category": "concurrency","value": 8,  "link": "/04-concurrency/multiprocessing" },
    { "id": "asyncio",       "name": "asyncio 协程",          "category": "concurrency","value": 10, "link": "/04-concurrency/asyncio" },
    { "id": "sync-primitives","name": "同步原语",               "category": "concurrency","value": 8,  "link": "/04-concurrency/sync-primitives" },
    { "id": "pool",          "name": "线程池与进程池",         "category": "concurrency","value": 8,  "link": "/04-concurrency/pool" },
    { "id": "patterns",      "name": "并发模式",                "category": "concurrency","value": 8,  "link": "/04-concurrency/patterns" },

    // ============== 05 爬虫 ==============
    { "id": "scrape-basics", "name": "爬虫基础",                "category": "scraping",   "value": 8,  "link": "/05-scraping/basics" },
    { "id": "requests-bs4",  "name": "requests+BS4",            "category": "scraping",   "value": 9,  "link": "/05-scraping/requests-bs4" },
    { "id": "scrapy",        "name": "Scrapy 框架",            "category": "scraping",   "value": 10, "link": "/05-scraping/scrapy" },
    { "id": "dynamic",       "name": "动态渲染",                "category": "scraping",   "value": 9,  "link": "/05-scraping/dynamic" },
    { "id": "anti-crawl",    "name": "反爬对抗",                "category": "scraping",   "value": 9,  "link": "/05-scraping/anti-crawl" },

    // ============== 06 AI/ML ==============
    { "id": "ai-overview",   "name": "AI 应用概览",            "category": "ai-ml",      "value": 9,  "link": "/06-ai-ml/overview" },
    { "id": "ml-basics",     "name": "机器学习基础",            "category": "ai-ml",      "value": 9,  "link": "/06-ai-ml/ml-basics" },
    { "id": "huggingface",   "name": "Hugging Face",            "category": "ai-ml",      "value": 10, "link": "/06-ai-ml/huggingface" },
    { "id": "llm-apps",      "name": "LLM 应用开发",           "category": "ai-ml",      "value": 10, "link": "/06-ai-ml/llm-apps" },
    { "id": "cv",            "name": "计算机视觉",              "category": "ai-ml",      "value": 8,  "link": "/06-ai-ml/cv" },
    { "id": "nlp",           "name": "自然语言处理",            "category": "ai-ml",      "value": 8,  "link": "/06-ai-ml/nlp" },

    // ============== 07 数据处理 ==============
    { "id": "pd-basics",     "name": "pandas 入门",            "category": "data",       "value": 10, "link": "/07-data/pandas" },
    { "id": "numpy",         "name": "NumPy 数值计算",         "category": "data",       "value": 9,  "link": "/07-data/numpy" },
    { "id": "matplotlib",    "name": "Matplotlib 可视化",      "category": "data",       "value": 8,  "link": "/07-data/matplotlib" },
    { "id": "cleaning",      "name": "数据清洗",                "category": "data",       "value": 9,  "link": "/07-data/cleaning" },
    { "id": "analysis",      "name": "数据分析实战",           "category": "data",       "value": 8,  "link": "/07-data/analysis" },
    { "id": "big-data",      "name": "大数据处理",              "category": "data",       "value": 8,  "link": "/07-data/big-data" },

    // ============== 08 算法 ==============
    { "id": "complexity",    "name": "复杂度分析",              "category": "algorithms", "value": 9,  "link": "/08-algorithms/complexity" },
    { "id": "builtin",       "name": "内置数据结构",            "category": "algorithms", "value": 8,  "link": "/08-algorithms/builtin" },
    { "id": "sort",          "name": "排序算法",                "category": "algorithms", "value": 10, "link": "/08-algorithms/sort" },
    { "id": "search",        "name": "搜索算法",                "category": "algorithms", "value": 8,  "link": "/08-algorithms/search" },
    { "id": "tree-graph",    "name": "树与图",                  "category": "algorithms", "value": 9,  "link": "/08-algorithms/tree-graph" },
    { "id": "dp",            "name": "动态规划",                "category": "algorithms", "value": 10, "link": "/08-algorithms/dp" },

    // ============== 09 企业实战 ==============
    { "id": "structure",     "name": "项目结构",                "category": "enterprise", "value": 8,  "link": "/09-enterprise/structure" },
    { "id": "dependencies",  "name": "依赖管理",                "category": "enterprise", "value": 8,  "link": "/09-enterprise/dependencies" },
    { "id": "testing",       "name": "单元测试",                "category": "enterprise", "value": 8,  "link": "/09-enterprise/testing" },
    { "id": "performance",   "name": "性能优化",                "category": "enterprise", "value": 9,  "link": "/09-enterprise/performance" },
    { "id": "fastapi",       "name": "FastAPI Web 实战",       "category": "enterprise", "value": 10, "link": "/09-enterprise/fastapi" },
    { "id": "docker",        "name": "Docker 部署",            "category": "enterprise", "value": 8,  "link": "/09-enterprise/docker" },
    { "id": "logging",       "name": "日志与监控",              "category": "enterprise", "value": 8,  "link": "/09-enterprise/logging" },
    { "id": "security",      "name": "安全最佳实践",            "category": "enterprise", "value": 8,  "link": "/09-enterprise/security" }
  ],
  "links": [
    // ====== 01 入门关联 ======
    { "source": "intro", "target": "install" },
    { "source": "install", "target": "syntax" },
    { "source": "syntax", "target": "data-structures" },
    { "source": "data-structures", "target": "control-flow" },

    // ====== 02 底层原理关联 ======
    { "source": "syntax", "target": "interpreter" },
    { "source": "interpreter", "target": "bytecode" },
    { "source": "bytecode", "target": "object-model" },
    { "source": "object-model", "target": "memory" },
    { "source": "memory", "target": "gc" },
    { "source": "interpreter", "target": "gil" },
    { "source": "gil", "target": "profiling" },

    // ====== 03 常用库关联 ======
    { "source": "syntax", "target": "stdlib" },
    { "source": "stdlib", "target": "requests" },
    { "source": "requests", "target": "beautifulsoup" },
    { "source": "stdlib", "target": "sqlalchemy" },
    { "source": "stdlib", "target": "pandas" },
    { "source": "pandas", "target": "pytest" },

    // ====== 04 并发关联 ======
    { "source": "threading", "target": "multiprocessing" },
    { "source": "threading", "target": "sync-primitives" },
    { "source": "asyncio", "target": "sync-primitives" },
    { "source": "threading", "target": "pool" },
    { "source": "multiprocessing", "target": "pool" },
    { "source": "asyncio", "target": "patterns" },

    // ====== 05 爬虫关联 ======
    { "source": "requests", "target": "scrape-basics" },
    { "source": "beautifulsoup", "target": "requests-bs4" },
    { "source": "requests-bs4", "target": "scrapy" },
    { "source": "scrapy", "target": "dynamic" },
    { "source": "dynamic", "target": "anti-crawl" },

    // ====== 06 AI/ML 关联 ======
    { "source": "pandas", "target": "ml-basics" },
    { "source": "ml-basics", "target": "huggingface" },
    { "source": "huggingface", "target": "llm-apps" },
    { "source": "ml-basics", "target": "cv" },
    { "source": "ml-basics", "target": "nlp" },
    { "source": "ai-overview", "target": "huggingface" },

    // ====== 07 数据处理关联 ======
    { "source": "stdlib", "target": "pd-basics" },
    { "source": "pd-basics", "target": "numpy" },
    { "source": "pd-basics", "target": "matplotlib" },
    { "source": "pd-basics", "target": "cleaning" },
    { "source": "cleaning", "target": "analysis" },
    { "source": "analysis", "target": "big-data" },

    // ====== 08 算法关联 ======
    { "source": "data-structures", "target": "complexity" },
    { "source": "complexity", "target": "builtin" },
    { "source": "builtin", "target": "sort" },
    { "source": "sort", "target": "search" },
    { "source": "search", "target": "tree-graph" },
    { "source": "tree-graph", "target": "dp" },

    // ====== 09 企业实战关联 ======
    { "source": "syntax", "target": "structure" },
    { "source": "structure", "target": "dependencies" },
    { "source": "pytest", "target": "testing" },
    { "source": "profiling", "target": "performance" },
    { "source": "requests", "target": "fastapi" },
    { "source": "fastapi", "target": "docker" },
    { "source": "docker", "target": "logging" },
    { "source": "logging", "target": "security" },

    // ====== 跨域关联 ======
    { "source": "intro", "target": "interpreter" },
    { "source": "data-structures", "target": "builtin" },
    { "source": "complexity", "target": "dp" },
    { "source": "sqlalchemy", "target": "fastapi" },
    { "source": "huggingface", "target": "llm-apps" },
    { "source": "pandas", "target": "analysis" }
  ]
}
