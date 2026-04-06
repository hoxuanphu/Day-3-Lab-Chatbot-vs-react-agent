# Individual Report: Lab 3 - Chatbot vs ReAct Agent

**Student Name:** [Lại Đức Anh]
**Student ID:** [2A202600374]
**Date:** [04/06/2024]

---

## I. Technical Contribution (15 Points)

### Describe your specific contribution to the codebase

Trong lab này, tôi đã xây dựng một pipeline hoàn chỉnh cho hệ thống **RAG (Retrieval-Augmented Generation)**, bao gồm ba thành phần chính:

* Document Chunking Module
* Hybrid Retrieval System (BM25 + Semantic Search)
* RAG Generator (LLM + Context grounding)

Hệ thống này đóng vai trò là baseline chatbot có grounding để so sánh với ReAct Agent.

---

### Modules Implemented

* `src/rag/chunker.py`
* `src/rag/retriever.py`
* `src/rag/generator.py`

---

### Code Highlights

#### 1. Markdown Chunker (Header-aware + Overlap)

Tôi implement một chunker dựa trên cấu trúc markdown:

```python
def _split_by_headers(self, text: str) -> List[Dict[str, Any]]:
```

* Tách document theo header (`#, ##, ###`)
* Giữ nguyên ngữ cảnh semantic
* Xây dựng hierarchy: chapter > section > subsection

Xử lý long context bằng overlap:

```python
def _split_long_section(self, text: str, start_line: int):
```

→ Giúp tránh mất thông tin khi chunk bị cắt.

---

#### 2. Hybrid Retriever (BM25 + Semantic + RRF)

Tôi xây dựng hệ thống retrieval kết hợp:

* BM25 (keyword-based)
* Semantic Search (embedding-based)
* RRF (Reciprocal Rank Fusion)

Core logic:

```python
def _reciprocal_rank_fusion(self, bm25_results, semantic_results):
```

→ Kết hợp ưu điểm của keyword matching và semantic understanding.

---

#### 3. RAG Generator Pipeline

Pipeline chính:

```python
def generate(self, question: str):
```

Flow:

1. Retrieve top-k chunks
2. Format context
3. Inject vào system prompt
4. Gọi LLM để generate answer

System prompt enforce grounding:

```
CHỈ trả lời dựa trên thông tin có trong các nguồn tài liệu
```

---

### Documentation: Interaction with ReAct Loop

* RAG: Retrieve → Generate (single-step)
* ReAct: Thought → Action → Observation → lặp lại

Trong hệ thống agent:

* Retriever có thể dùng như tool
* Generator tương ứng bước trả lời cuối

---

## II. Debugging Case Study (10 Points)

### Problem Description

Agent gặp lỗi:

* Trả lời sai hoặc hallucinate khi thiếu thông tin
* Không tuân thủ constraint từ context

---

### Log Source

```python
logger.log_event("RAG_GENERATE_START", {...})
logger.log_event("RETRIEVAL_COMPLETE", {...})
```

Quan sát:

* Retrieval không tốt
* LLM vẫn trả lời tự tin

---

### Diagnosis

Nguyên nhân:

1. Prompt chưa đủ mạnh
2. Retrieval chưa tối ưu
3. Context chưa rõ ràng

---

### Solution

#### 1. Strengthen Prompt

```
Nếu không có thông tin → trả lời "Không tìm thấy..."
```

---

#### 2. Hybrid Retrieval

* Kết hợp BM25 + Semantic
* Dùng RRF

---

#### 3. Context Attribution

```
--- Nguồn 1 ---
[Vị trí: Chương > Phần > Mục]
```

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

### Reasoning

* Chatbot: reasoning 1 bước
* ReAct: có Thought step → chia nhỏ bài toán

---

### Reliability

ReAct kém hơn khi:

* Query đơn giản
* Retrieval đã đủ tốt

---

### Observation

Observation giúp:

* Retry retrieval
* Điều chỉnh strategy

Chatbot không có feedback loop nên dễ sai cố định.

---

## IV. Future Improvements (5 Points)

### Scalability

* Async queue cho tool calls
* Cache embeddings
* Microservices architecture

---

### Safety

* Supervisor LLM
* Rule-based validation

---

### Performance

* Vector DB (FAISS, Weaviate)
* ANN search
* Tool selection bằng embedding

---
