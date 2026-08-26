---
title: 自然语言处理
---

# 🗣️ 自然语言处理

> **自然语言处理（NLP）**让计算机**理解、分析、生成**自然语言。本章介绍 Python 主流 NLP 工具。

## 🎯 NLP 工具生态

```
分词与预处理：
  - jieba：中文分词
  - spaCy：工业级 NLP
  - NLTK：教学级 NLP

词向量：
  - word2vec / GloVe / fastText
  - sentence-transformers

预训练模型：
  - Hugging Face Transformers
  - BERT / GPT / T5

任务库：
  - Hugging Face：通用 NLP
  - spaCy：多语言 NLP
  - Flair：NLP 框架
```

## 🛠️ jieba（中文分词）

```bash
pip install jieba
```

### 基础分词

```python
import jieba

# 精确模式（最常用）
text = "我爱自然语言处理，Python 真的很有趣！"
words = jieba.lcut(text)
print(words)
# ['我', '爱', '自然语言', '处理', '，', 'Python', ' ', '真的', '很', '有趣', '！']

# 全模式（所有可能的词）
words = jieba.lcut(text, cut_all=True)
print(words)
# ['我', '爱', '自然', '自然语言', '语言', '处理', '，', 'Python', ' ', '真的', '很', '有趣', '！']

# 搜索引擎模式
words = jieba.lcut_for_search(text)
print(words)
```

### 自定义词典

```python
import jieba

# 添加自定义词
jieba.add_word("自然语言处理")
jieba.add_word("机器学习", freq=1000)

# 加载自定义词典
jieba.load_userdict("custom_dict.txt")
# custom_dict.txt 格式：
# 自然语言处理 100 n
# 机器学习 1000 n

text = "我喜欢自然语言处理和机器学习"
words = jieba.lcut(text)
print(words)
```

### 词性标注

```python
import jieba.posseg as pseg

words = pseg.lcut("我爱自然语言处理")
for word, flag in words:
    print(f"{word}\t{flag}")
# 我    r
# 爱    v
# 自然语言    n
# 处理    v
```

### 关键词提取

```python
import jieba.analyse

text = """
自然语言处理是人工智能和语言学领域的分支学科。
此领域探讨如何处理及运用自然语言。
Python 是一种广泛使用的高级编程语言。
"""

# TF-IDF 提取关键词
keywords = jieba.analyse.extract_tags(text, topK=5, withWeight=True)
for word, weight in keywords:
    print(f"{word}: {weight:.4f}")

# TextRank 提取关键词
keywords = jieba.analyse.textrank(text, topK=5, withWeight=True)
```

## 🛠️ spaCy（工业级 NLP）

### 安装

```bash
pip install spacy
# 下载模型（英文）
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_lg
# 中文
python -m spacy download zh_core_web_sm
```

### 基础使用

```python
import spacy

# 加载模型
nlp = spacy.load("en_core_web_sm")

# 处理文本
doc = nlp("Apple is looking at buying U.K. startup for $1 billion")

# 分词
for token in doc:
    print(f"{token.text}\t{token.pos_}\t{token.dep_}\t{token.lemma_}")

# 命名实体识别
for ent in doc.ents:
    print(f"{ent.text}\t{ent.label_}")
# Apple    ORG
# U.K.    GPE
# $1 billion    MONEY

# 名词短语
for chunk in doc.noun_chunks:
    print(chunk.text)
```

### 中文 NLP

```python
import spacy

nlp = spacy.load("zh_core_web_sm")

doc = nlp("苹果公司正在考虑收购一家英国初创公司。")

for token in doc:
    print(f"{token.text}\t{token.pos_}\t{token.dep_}")

for ent in doc.ents:
    print(f"{ent.text}\t{ent.label_}")
# 苹果公司    ORG
# 英国    GPE
```

### 相似度

```python
import spacy

nlp = spacy.load("en_core_web_lg")  # 用大模型

doc1 = nlp("I love programming")
doc2 = nlp("I enjoy coding")

# 文档相似度
similarity = doc1.similarity(doc2)
print(f"相似度: {similarity:.2f}")  # 0.85+

# 词向量
word1 = nlp("king")
word2 = nlp("queen")
print(f"king vs queen: {word1.similarity(word2):.2f}")
```

### 规则匹配

```python
import spacy
from spacy.matcher import Matcher

nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

# 定义模式
pattern = [{"LOWER": "hello"}, {"IS_PUNCT": True}, {"LOWER": "world"}]
matcher.add("HelloWorld", [pattern])

doc = nlp("Hello, world! Hello world.")
matches = matcher(doc)
for match_id, start, end in matches:
    print(doc[start:end].text)
```

## 🛠️ NLTK

```bash
pip install nltk
python -m nltk.downloader all
```

```python
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer

# 分词
text = "Natural language processing is fascinating!"
tokens = word_tokenize(text)
print(tokens)

# 分句
sentences = sent_tokenize(text)
print(sentences)

# 停用词
stop_words = set(stopwords.words("english"))

# 词干提取
stemmer = PorterStemmer()
print(stemmer.stem("running"))  # run

# 词形还原
lemmatizer = WordNetLemmatizer()
print(lemmatizer.lemmatize("running"))  # running
print(lemmatizer.lemmatize("ran", pos="v"))  # run

# 词性标注
nltk.pos_tag(tokens)

# 命名实体识别
nltk.chunk.ne_chunk(nltk.pos_tag(tokens))
```

## 🛠️ Hugging Face NLP

```python
from transformers import pipeline

# 1. 文本分类
classifier = pipeline("sentiment-analysis")
print(classifier("I love this movie!"))

# 2. 命名实体识别
ner = pipeline("ner", grouped_entities=True)
print(ner("Apple is looking at buying U.K. startup for $1 billion"))

# 3. 问答
qa = pipeline("question-answering")
result = qa(
    question="What is Python?",
    context="Python is a programming language created by Guido van Rossum."
)
print(result)

# 4. 文本摘要
summarizer = pipeline("summarization")
text = """
Kafka is a distributed event streaming platform. 
It was originally developed by LinkedIn and donated to the Apache Software Foundation.
"""
print(summarizer(text, max_length=50, min_length=20))

# 5. 翻译
translator = pipeline("translation_en_to_zh", 
                       model="Helsinki-NLP/opus-mt-en-zh")
print(translator("Hello, how are you?"))

# 6. 文本生成
generator = pipeline("text-generation", model="gpt2")
print(generator("The future of AI is", max_length=50))

# 7. 填空
unmasker = pipeline("fill-mask", model="bert-base-uncased")
print(unmasker("Paris is the [MASK] of France."))

# 8. 摘要抽取
summarizer = pipeline("summarization", 
                       model="facebook/bart-large-cnn")
print(summarizer("Long article text here..."))
```

## 🛠️ 文本相似度（Sentence Transformers）

```python
from sentence_transformers import SentenceTransformer, util

# 加载模型
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 编码
sentences = [
    "Python 是一种编程语言",
    "Python is a programming language",
    "我喜欢吃苹果"
]
embeddings = model.encode(sentences)

# 相似度
similarity = util.cos_sim(embeddings, embeddings)
print(similarity)
# tensor([[1.0000, 0.8923, 0.2341],
#         [0.8923, 1.0000, 0.2103],
#         [0.2341, 0.2103, 1.0000]])

# 语义搜索
corpus = [
    "Python 是一种解释型编程语言",
    "Java 是一种编译型编程语言",
    "今天天气真好"
]
corpus_embeddings = model.encode(corpus)

query = "什么是 Python？"
query_embedding = model.encode(query)

hits = util.semantic_search(query_embedding, corpus_embeddings, top_k=2)
for hit in hits[0]:
    print(f"Score: {hit['score']:.3f} | {corpus[hit['corpus_id']]}")
```

## 🛠️ 词向量训练

```python
# 使用 gensim 训练 Word2Vec
from gensim.models import Word2Vec

# 语料
sentences = [
    ["i", "love", "python"],
    ["python", "is", "great"],
    ["i", "love", "machine", "learning"],
    # ... 更多句子
]

# 训练
model = Word2Vec(
    sentences,
    vector_size=100,
    window=5,
    min_count=1,
    workers=4
)

# 查询词向量
vector = model.wv["python"]
print(vector.shape)  # (100,)

# 找相似词
similar = model.wv.most_similar("python")
print(similar)
```

## 🛠️ 文本分类实战

```python
import jieba
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report

# 1. 准备数据
texts = [
    "这家餐厅很好吃", "非常推荐", "差评", "不好吃", "服务态度好",
    "质量很差", "性价比高", "价格便宜", "态度恶劣", "很满意"
]
labels = [1, 1, 0, 0, 1, 0, 1, 1, 0, 1]  # 1=正面, 0=负面

# 2. 中文分词
def tokenize(text):
    return " ".join(jieba.lcut(text))

texts_tokenized = [tokenize(t) for t in texts]

# 3. 特征提取
vectorizer = TfidfVectorizer(max_features=1000)
X = vectorizer.fit_transform(texts_tokenized)
y = labels

# 4. 训练
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = MultinomialNB()
model.fit(X_train, y_train)

# 5. 评估
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
```

## 🛠️ 命名实体识别实战

```python
import spacy

nlp = spacy.load("zh_core_web_sm")

def extract_entities(text):
    doc = nlp(text)
    entities = {
        "PERSON": [],
        "ORG": [],
        "GPE": [],   # 地缘政治实体（国家、城市）
        "DATE": []
    }
    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)
    return entities

text = "马云在杭州创立了阿里巴巴公司。"
print(extract_entities(text))
# {'PERSON': ['马云'], 'ORG': ['阿里巴巴公司'], 'GPE': ['杭州'], 'DATE': []}
```

## 🛠️ 情感分析实战

```python
from transformers import pipeline

# 1. 预训练模型（英文）
sentiment = pipeline("sentiment-analysis")

texts = [
    "I love this product!",
    "This is terrible.",
    "It's okay, not great."
]
for text in texts:
    result = sentiment(text)[0]
    print(f"{text}: {result['label']} ({result['score']:.2%})")

# 2. 中文情感分析
# 使用 Hugging Face 中文模型
# sentiment_zh = pipeline("sentiment-analysis", 
#                         model="uer/roberta-base-finetuned-jd-binary-chinese")
# print(sentiment_zh("这个产品很好用！"))
```

## 🎯 总结

**NLP 核心要点**：
- ✅ jieba：中文分词首选
- ✅ spaCy：工业级 NLP
- ✅ NLTK：教学级 NLP
- ✅ Hugging Face：预训练模型
- ✅ sentence-transformers：文本嵌入
- ✅ 文本分类、情感分析、NER
- ✅ 语义搜索（基于嵌入）
- ✅ 词向量训练
- ⚠️ 中文 NLP 模型比英文少
- ⚠️ 标注数据稀缺

**下一步：** [🐼 pandas 入门](/07-data/pandas) — 数据分析基础


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
