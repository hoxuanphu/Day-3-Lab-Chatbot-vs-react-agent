# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Hoàng Ngọc Thạch
- **Student ID**: 2A202600068
- **Date**: 06/04/2026

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.).*

Trong lab này, tôi xây dựng lớp đánh giá và kiểm thử cho hệ thống RAG và agent, bao gồm việc theo dõi hoạt động LLM (token, độ trễ, số vòng lặp) và thiết lập framework so sánh giữa RAG baseline và agent theo mô hình ReAct nhiều bước.

### Modules Implementated: 
* `scripts/eval_modes.py`
* `scripts/test_llm.py`
* `scripts/test_rag_baseline.py`
### Code Highlights: 
#### 1. `eval_modes.py` / `ProxyLLM` (Class)

**Mục đích:**  
Wrapper để theo dõi usage của LLM (token, số lần gọi, phục vụ evaluation)

**Method:**  
`generate(prompt: str, system_prompt: str = None) -> Dict[str, Any]`

- **Input:**
  - `prompt`: nội dung user query
  - `system_prompt`: (optional) system instruction

- **Output:**
  - `Dict` chứa `content` và `usage` từ LLM

- **Ý nghĩa:**
  - Ghi nhận:
    - `prompt_tokens`, `completion_tokens`, `total_tokens`
    - số lần gọi LLM (`calls`)
  - Dùng để đo:
    - chi phí
    - số bước reasoning của agent


---

#### 2. `eval_modes.py` / `run_eval()` (Function)

**Mục đích:**  
Chạy evaluation so sánh giữa baseline RAG và agent

- **Input:**
  - danh sách câu hỏi (hardcoded)

- **Output:**
  - danh sách kết quả (`results`)
  - file CSV / JSON


---

#### 3. `test_llm.py` (Script)

**Mục đích:**  
Kiểm tra kết nối LLM

- **Input:**
  - prompt đơn giản

- **Output:**
  - response hoặc error


---

#### 4. `test_rag_baseline.py` / `test_chunking()` (Function)

**Mục đích:**  
Kiểm tra bước chia nhỏ dữ liệu (chunking), đảm bảo chunk size hợp lý, bước nền cho retrieval

- **Input:**
  - file markdown (`data/data.md`)

- **Output:**
  - danh sách chunks


---

#### 5. `test_rag_baseline.py` / `test_bm25_retrieval(chunks)` (Function)

**Mục đích:**  
Test retrieval dựa trên keyword (BM25)

- **Input:**
  - `chunks`: danh sách đoạn văn đã chia

- **Output:**
  - top-k kết quả retrieval


---

#### 6. `test_rag_baseline.py` / `test_hybrid_retrieval(chunks)` (Function)

**Mục đích:**  
Test retrieval kết hợp BM25 + semantic

- **Input:**
  - `chunks`

- **Output:**
  - kết quả retrieval có `score` + `source`


---

#### 7. `test_rag_baseline.py` / `test_generation(retriever)` (Function)

**Mục đích:**  
Test full RAG pipeline (retrieve → generate)

- **Input:**
  - `retriever`

- **Output:**
  - câu trả lời + metadata (`sources`, token usage)


---

#### 8. `test_rag_baseline.py` / `test_rag_baseline()` (Function)

**Mục đích:**  
Chạy end-to-end baseline agent

- **Input:**
  - câu hỏi

- **Output:**
  - câu trả lời từ `RAGBaselineAgent`

### Documentation:

- Hệ thống evaluation tương tác với vòng lặp ReAct một cách gián tiếp thông qua việc bọc LLM bằng ProxyLLM. Mỗi bước suy luận của agent tương ứng với một lần gọi LLM, từ đó có thể theo dõi số vòng lặp (calls), lượng token và độ trễ mà không cần thay đổi logic bên trong agent.
---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: 
Khi chạy baseline agent, hệ thống bị lỗi FileNotFoundError do không tìm thấy file dữ liệu đầu vào (data/data.md). Điều này khiến pipeline RAG không thể thực hiện bước chunking và dừng ngay từ khởi tạo agent.
- **Log Source**: 
```
{"timestamp": "2026-04-06T10:36:04.450728", "event": "RAG_BASELINE_INIT", "data": {"data_path": "data/data.md", "use_semantic": false, "top_k": 5, "retrieval_mode": "hybrid"}}
[RAGBaselineAgent] Chunking document...
{"timestamp": "2026-04-06T10:36:04.451105", "event": "CHUNKING_START", "data": {"file": "data/data.md"}}
```
- **Diagnosis**: 
Dựa trên log, hệ thống đã:
	1.	Khởi tạo agent (RAG_BASELINE_INIT)
	2.	Bắt đầu bước chunking (CHUNKING_START)

Tuy nhiên, không có log tiếp theo (ví dụ: chunking hoàn tất), cho thấy pipeline bị gián đoạn tại bước đọc file.

Kết hợp với stack trace (FileNotFoundError), nguyên nhân là:
	•	File data/data.md không tồn tại tại đường dẫn được chỉ định
	•	Đường dẫn đang được sử dụng dưới dạng relative path
	•	Working directory khi chạy chương trình không đúng với cấu trúc project
- **Solution**: 
Tôi đã khắc phục lỗi bằng cách bổ sung file dữ liệu data/data.md vào đúng thư mục của project, đảm bảo pipeline RAG có đầu vào hợp lệ để thực hiện bước chunking.

Ngoài ra, tôi kiểm tra lại cấu trúc thư mục và xác nhận đường dẫn được sử dụng là chính xác trước khi chạy hệ thống.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: 
Việc này giúp agent phân tách quá trình suy luận thành nhiều bước rõ ràng (reason → act → observe), thay vì trả lời trực tiếp như chatbot.

Điều này giúp:
	•	Agent xác định cần làm gì tiếp theo (ví dụ: có cần gọi tool hay không)
	•	Giảm việc “đoán mò” khi thiếu thông tin
	•	Tận dụng được dữ liệu từ retrieval hoặc tool

So với chatbot trả lời một bước, agent có khả năng xử lý các câu hỏi phức tạp tốt hơn nhờ reasoning nhiều bước.
2.  **Reliability**: 
Trong một số trường hợp, agent lại hoạt động kém hơn chatbot:
	•	Câu hỏi đơn giản:
→ Chatbot trả lời ngay, còn agent lại thực hiện nhiều bước không cần thiết (over-reasoning)
	•	Khi retrieval không tốt:
→ Agent dựa vào dữ liệu sai → suy luận sai nhiều bước
	•	Chi phí và độ trễ:
→ Agent gọi LLM nhiều lần → tốn token và chậm hơn

Điều này cho thấy agent không phải lúc nào cũng tốt hơn, đặc biệt với các tác vụ đơn giản.
3.  **Observation**: 
Observation (kết quả từ tool hoặc retrieval) đóng vai trò quan trọng trong việc định hướng bước tiếp theo của agent.

Cụ thể:
	•	Agent sử dụng observation để cập nhật trạng thái hiểu biết
	•	Nếu dữ liệu chưa đủ → tiếp tục gọi tool
	•	Nếu đã đủ → chuyển sang trả lời

Observation giúp agent không bị “mù thông tin” như chatbot, mà có thể phản hồi dựa trên dữ liệu thực tế từ môi trường.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Có thể cải thiện khả năng mở rộng bằng cách tách các bước xử lý (retrieval, tool calling, generation) thành các tác vụ độc lập và sử dụng hàng đợi bất đồng bộ (asynchronous queue). Điều này giúp hệ thống xử lý nhiều request song song và dễ dàng mở rộng khi số lượng người dùng tăng.
- **Safety**: Có thể bổ sung một lớp kiểm soát (ví dụ: “Supervisor” hoặc rule-based validation) để kiểm tra kết quả từ agent trước khi trả về. Điều này giúp phát hiện các hành vi sai lệch như gọi tool không hợp lệ, suy luận vòng lặp quá nhiều hoặc trả lời không dựa trên dữ liệu.
- **Performance**: Có thể cải thiện hiệu năng bằng cách sử dụng vector database cho bước retrieval, thay vì chỉ dựa vào BM25. Điều này giúp tăng chất lượng tìm kiếm ngữ nghĩa và giảm số bước reasoning không cần thiết của agent, từ đó tối ưu cả tốc độ và chi phí.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
