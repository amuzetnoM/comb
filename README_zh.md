<p align="center">
  <pre align="center">
     _____ _____ _____ _____
    / ____/ ___ / _  \/ _  \     COMB
   / /   / / / / / / / /_/ /     链式有序记忆库
  / /___/ /_/ / / / / ___ /
  \____/\___/_/ /_/_/   \_\      AI 代理的无损上下文归档
  </pre>
</p>

<p align="center">
  <em>你的 AI 不需要更好的摘要。它需要更好的记忆。</em>
</p>

<p align="center">
  <a href="#快速开始">快速开始</a> •
  <a href="#蜂巢结构">蜂巢结构</a> •
  <a href="#架构">架构</a> •
  <a href="#命令行">命令行</a> •
  <a href="#自定义搜索后端">自定义搜索</a>
</p>

<p align="center">
  <a href="README.md">English</a> | <b>中文</b>
</p>

<p align="center">
  <a href="https://pypi.org/project/comb-db/"><img src="https://img.shields.io/pypi/v/comb-db?color=blue&logo=pypi&logoColor=white" alt="PyPI"/></a>
  <a href="https://pypi.org/project/comb-db/"><img src="https://img.shields.io/pypi/pyversions/comb-db?logo=python&logoColor=white" alt="Python 版本"/></a>
  <img src="https://img.shields.io/badge/依赖-零-brightgreen" alt="零依赖"/>
  <img src="https://img.shields.io/badge/存储-JSON-orange" alt="JSON"/>
  <img src="https://img.shields.io/badge/链式-哈希链接-blueviolet" alt="哈希链接"/>
  <img src="https://img.shields.io/badge/许可证-MIT-green" alt="MIT"/>
</p>

---

COMB 是一个蜂巢结构的 AI 代理无损上下文归档系统。与摘要式（有损）方案不同，COMB 将完整对话文本归档为三向图文档。

零依赖。纯 Python。单目录存储。复制文件夹 = 复制记忆。

## 为什么不直接做摘要？

当今所有 AI 记忆系统的工作方式都一样：对话被摘要、压缩或嵌入为向量。每一步都在丢失信息——用户的精确措辞、分歧的细微之处、讨论过的具体数字——全部消失。

COMB 采取完全不同的方式：**保留一切。**

| | 原则 | |
|---|---|---|
| 🔒 | **无损** | 完整对话文本，随时可恢复 |
| ⛓️ | **哈希链** | 防篡改，类似区块链的对话保护 |
| 🐝 | **三向链接** | 按时间、语义或关系导航 |
| 📐 | **读时解析** | 你的数据，你的解读方式 |
| 📁 | **无服务器** | 没有数据库，没有服务器，只有目录中的文件 |

## 起源故事

COMB 诞生于真实的痛苦。我们的 AI 代理 AVA 运行在 OpenClaw 平台上，该平台会定期"压缩"上下文窗口——将长对话摘要为简短的总结。每次压缩都会丢失关键的操作细节：委派链的精确命令、工具的正确调用方式、项目的当前状态。

AVA 一次又一次地"忘记"如何完成工作。不是因为她不够聪明，而是因为记忆系统在背后默默地吞噬细节。

COMB 就是解决方案：在压缩发生之前，将结构化的操作知识写入无损归档。压缩可以摘要上下文——但 COMB 保留了真相。

> *"记忆不是功能，它是身份。"*

## 架构

```
                    ┌─────────┐
               ╱╲   │ 第一层   │   代理的上下文窗口
              ╱  ╲  │ 活跃层   │   （COMB 不管理此层）
             ╱    ╲ └─────────┘
            ╱      ╲
    ┌──────╱────────╲──────┐
    │      第二层            │   当日对话暂存
    │   每日暂存区           │   追加写入 JSONL
    │   （只追加）           │
    └──────────┬───────────┘
               │ rollup()
    ┌──────────▼───────────┐
    │      第三层            │   每日一个文档
    │   链式归档             │   哈希链接
    │                      │   蜂巢链接
    └──────────────────────┘
```

## 快速开始

```bash
pip install comb-db
```

> 💡 国内用户可使用清华源：`pip install comb-db -i https://pypi.tuna.tsinghua.edu.cn/simple`

```python
from comb import CombStore

# 创建存储（只是一个目录）
store = CombStore("./my-memory")

# 暂存当日对话
store.stage("用户询问了加密方案。助手解释了 AES-256...")
store.stage("用户说需要 RSA 做密钥交换...")

# 汇总归档
doc = store.rollup()
# → 自动计算哈希链、语义链接和社交链接

# 搜索
results = store.search("加密")
for r in results:
    print(r.date, r.similarity_score)

# 导航蜂巢
doc = store.get("2026-02-17")
doc.temporal.prev          # 前一天
doc.semantic.neighbors     # 相似对话
doc.social.strengthened    # 关系升温
doc.social.cooled          # 关系降温

# 验证完整性
assert store.verify_chain()  # 无篡改
```

## 蜂巢结构

每个归档文档都存在于三向图中：

```
         时间链 ←──→  按时间顺序链接（前/后哈希链接）
         语义链 ←──→  内容相似度（BM25 余弦，top-k 邻居）
         社交链 ←──→  关系梯度（升温 ↔ 降温）
```

### ⛓️ 时间链接
时间序列链。每个文档指向前一天和后一天。哈希链接——如果任何文档被篡改，链条就会断裂。对话历史的区块链级完整性保证。

### 🧠 语义链接
通过词频余弦相似度计算（内置实现，零依赖）。汇总时自动链接 top-k 最相似的文档。可插入自定义搜索后端以获得更好的效果。

### 💛 社交链接
最创新的部分。对话具有*关系温度*。COMB 追踪：

- **内向收敛**（升温）— 参与度增加，情感升温
- **外向发散**（降温）— 参与度降低，情感降温

这使 AI 代理不仅理解*讨论了什么*，还理解*关系如何演变*。

## 命令行

```bash
# 从标准输入暂存
echo "今天的对话..." | comb -s ./my-memory stage

# 从文件暂存
comb -s ./my-memory stage -f conversation.txt

# 汇总归档
comb -s ./my-memory rollup

# 搜索
comb -s ./my-memory search "加密"

# 显示文档
comb -s ./my-memory show 2026-02-17

# 验证链完整性
comb -s ./my-memory verify

# 统计信息
comb -s ./my-memory stats
```

需要安装：`pip install comb-db[cli]`

## 自定义搜索后端

内置 BM25 适用于数百个文档。大规模场景下，可实现 `SearchBackend` 协议：

```python
from comb import SearchBackend

class MyVectorBackend:
    def index(self, doc_id: str, text: str) -> None:
        ...
    def search(self, query: str, k: int = 5) -> list[tuple[str, float]]:
        ...

store = CombStore("./memory", search_backend=MyVectorBackend())
```

💡 **推荐搭配 HEKTOR** — 我们的高性能 C++ 向量搜索引擎，作为 COMB 的搜索后端。

## 存储格式

所有数据都是 JSON。人类可读。没有二进制格式。没有专有编码。

```
my-memory/
├── staging/
│   └── 2026-02-17.jsonl    # 当日暂存的对话
└── archive/
    ├── 2026-02-15.json     # 已归档，哈希链接
    ├── 2026-02-16.json     # 包含蜂巢链接
    └── 2026-02-17.json
```

## COMB 是什么 — 不是什么

**是：**
- 基于文件的对话历史归档系统
- 防篡改的每日对话文档链
- 用于导航记忆的三向图
- 零依赖库。可移植。复制目录 = 复制记忆。

**不是：**
- 不是向量数据库（搭配 [HEKTOR](https://github.com/amuzetnoM/hektor) 使用）
- 不是摘要工具
- 不是实时检索系统
- 不是代理上下文窗口的替代品

## 适用场景

| 场景 | 说明 |
|------|------|
| **AI 代理记忆** | 在上下文压缩前保存操作知识 |
| **对话审计** | 防篡改的对话记录链 |
| **机器人长期记忆** | 机器人跨会话保持经验 |
| **多代理协作** | 代理间共享无损上下文 |
| **合规存档** | 完整保留对话内容，满足监管要求 |

## 系统要求

- Python 3.10+
- 零依赖（仅标准库）
- 可选：`click`（命令行界面）

## 许可证

MIT

---

<p align="center">
  <em>由 <a href="https://github.com/amuzetnoM">Ava Shakil</a> 构建于 <a href="https://github.com/Artifact-Virtual">Artifact Virtual</a></em>
</p>
