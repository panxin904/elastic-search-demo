---
title: AI 应用概览
---

# 🤖 AI 应用概览

> Python 是 **AI/ML 领域的首选语言**，拥有最丰富的生态（PyTorch、TensorFlow、Hugging Face、LangChain 等）。本章概览 Python AI 应用的**主要方向**。

## 🎯 Python AI 生态

```
深度学习框架：
  - PyTorch（Meta，研究社区首选）
  - TensorFlow（Google，工业部署成熟）
  - JAX（Google，研究新星）
  - PaddlePaddle（百度）

传统机器学习：
  - scikit-learn（最常用）
  - XGBoost / LightGBM（梯度提升）
  - CatBoost（Yandex）

预训练模型：
  - Hugging Face Transformers（最大社区）
  - timm（图像模型）
  - sentence-transformers（嵌入模型）

LLM 应用：
  - LangChain（LLM 应用框架）
  - LlamaIndex（RAG 框架）
  - OpenAI SDK
  - Anthropic SDK

计算机视觉：
  - OpenCV
  - Pillow
  - torchvision

自然语言处理：
  - NLTK
  - spaCy
  - transformers

数据处理：
  - pandas / NumPy / SciPy
  - scikit-learn
```

## 🚀 LLM 应用开发

### OpenAI SDK

```bash
pip install openai
```

```python
from openai import OpenAI

client = OpenAI(api_key="sk-...")

# 文本生成
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "介绍一下 Python"}
    ],
    temperature=0.7,
    max_tokens=1000
)
print(response.choices[0].message.content)
```

### 流式输出

```python
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "讲个故事"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
```

## 🛠️ LangChain（LLM 应用框架）

```bash
pip install langchain langchain-openai
```

```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

# 1. LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# 2. Prompt 模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的{role}"),
    ("user", "{input}")
])

# 3. Chain
chain = LLMChain(llm=llm, prompt=prompt)

# 4. 调用
result = chain.invoke({
    "role": "Python 老师",
    "input": "什么是装饰器？"
})
print(result["text"])
```

### RAG（检索增强生成）

```python
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA

# 1. 加载文档
loader = TextLoader("docs.txt")
documents = loader.load()

# 2. 文档分块
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)

# 3. 创建向量数据库
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(texts, embeddings)

# 4. 创建 RAG Chain
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever()
)

# 5. 查询
result = qa.invoke("文档中讲了什么？")
print(result["result"])
```

## 🤗 Hugging Face

```bash
pip install transformers torch
```

### 加载预训练模型

```python
from transformers import pipeline

# 情感分析
classifier = pipeline("sentiment-analysis")
result = classifier("I love this movie!")
print(result)
# [{'label': 'POSITIVE', 'score': 0.9998}]

# 文本生成
generator = pipeline("text-generation", model="gpt2")
result = generator("Once upon a time", max_length=50)
print(result)

# 问答
qa = pipeline("question-answering")
result = qa(question="What is Python?", context="Python is a programming language.")
print(result)
```

### 文本嵌入

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

# 编码句子
sentences = ["Python is great", "Java is also great"]
embeddings = model.encode(sentences)

# 计算相似度
similarity = model.similarity(embeddings[0], embeddings[1])
print(f"Similarity: {similarity}")
```

## 📊 传统机器学习

### scikit-learn

```bash
pip install scikit-learn
```

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# 1. 加载数据
iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, test_size=0.2, random_state=42
)

# 2. 训练模型
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# 3. 预测
y_pred = model.predict(X_test)

# 4. 评估
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2f}")
```

### XGBoost

```bash
pip install xgboost
```

```python
import xgboost as xgb
import numpy as np

# 训练数据
X = np.random.rand(1000, 10)
y = np.random.randint(0, 2, 1000)

# 训练
dtrain = xgb.DMatrix(X, label=y)
params = {"objective": "binary:logistic", "max_depth": 3}
model = xgb.train(params, dtrain, num_boost_round=100)

# 预测
dtest = xgb.DMatrix(X[:10])
pred = model.predict(dtest)
```

## 🖼️ 计算机视觉

### OpenCV

```bash
pip install opencv-python
```

```python
import cv2

# 读取图片
img = cv2.imread("image.jpg")

# 灰度
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 人脸检测
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

# 画框
for (x, y, w, h) in faces:
    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

# 保存
cv2.imwrite("result.jpg", img)
```

### YOLOv8（目标检测）

```bash
pip install ultralytics
```

```python
from ultralytics import YOLO

# 加载模型
model = YOLO("yolov8n.pt")

# 检测
results = model("image.jpg")

# 打印结果
for result in results:
    boxes = result.boxes
    for box in boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        print(f"Class: {cls}, Confidence: {conf:.2f}")
```

## 🗣️ 自然语言处理

### spaCy

```bash
pip install spacy
python -m spacy download zh_core_web_sm
python -m spacy download en_core_web_sm
```

```python
import spacy

# 加载模型
nlp = spacy.load("en_core_web_sm")

# 处理文本
doc = nlp("Apple is looking at buying U.K. startup for $1 billion")

# 分词
for token in doc:
    print(token.text, token.pos_, token.dep_)

# 命名实体识别
for ent in doc.ents:
    print(ent.text, ent.label_)
# Apple ORG
# U.K. GPE
# $1 billion MONEY
```

## 📊 综合应用：智能客服

```python
from langchain_openai import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# 1. 加载知识库
loader = DirectoryLoader("knowledge/", glob="**/*.txt")
documents = loader.load()

# 2. 文档分块
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)

# 3. 向量数据库
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(texts, embeddings)

# 4. LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# 5. 记忆（对话历史）
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# 6. RAG + 对话链
qa = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    memory=memory
)

# 7. 对话
while True:
    query = input("用户: ")
    if query == "quit":
        break
    result = qa({"question": query})
    print(f"客服: {result['answer']}")
```

## 📊 应用场景

| 场景 | 工具 | 难度 |
|------|------|------|
| 文本分类 | scikit-learn | 入门 |
| 情感分析 | Hugging Face | 入门 |
| 文本生成 | GPT/Llama | 中等 |
| 聊天机器人 | LangChain | 中等 |
| 图像分类 | torchvision | 中等 |
| 目标检测 | YOLOv8 | 中等 |
| 人脸识别 | OpenCV + dlib | 中等 |
| 语音识别 | Whisper | 入门 |
| 机器翻译 | Hugging Face | 入门 |
| RAG 问答 | LangChain | 中等 |
| Agent 智能体 | LangChain/LlamaIndex | 高级 |
| 微调 LLM | Hugging Face/LoRA | 高级 |

## 🎯 总结

**Python AI 生态核心要点**：
- ✅ PyTorch / TensorFlow：深度学习框架
- ✅ scikit-learn：传统机器学习
- ✅ Hugging Face：预训练模型社区
- ✅ LangChain：LLM 应用框架
- ✅ OpenCV：计算机视觉
- ✅ YOLOv8：目标检测
- ✅ LLM 应用：RAG / Agent / 微调
- ⚠️ 选择合适工具（不要重复造轮子）
- ⚠️ 关注成本（API 调用费用）

**下一步：** [🧠 机器学习基础](/06-ai-ml/ml-basics) — scikit-learn
