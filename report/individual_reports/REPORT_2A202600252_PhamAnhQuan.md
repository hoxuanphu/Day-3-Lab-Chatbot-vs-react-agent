# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Phạm Anh Quân
- **Student ID**: 2A202600252
- **Date**: 06/04/2026

---

## I. Technical Contribution (15 Points)

*Mô tả đóng góp cụ thể vào phân hệ Agent định hướng Planner-Executor.*

- **Modules Implementated**: 
    - `src/tools/tool_registry.py`: Xây dựng hệ thống quản lý các công cụ, khởi tạo shared retriever (BM25) một lần duy nhất để tối ưu hiệu suất cho tất cả các tool.
    - `src/agent/agent.py`: Triển khai lớp `HistoryAgent` với pipeline 3 bước: **Plan** (Lập kế hoạch) -> **Execute** (Thực thi tool) -> **Synthesize** (Tổng hợp câu trả lời).
    - `src/tools/search_docs.py`, `src/tools/build_timeline.py`, `src/tools/lookup_entity.py`: Phát triển các công cụ chuyên biệt để Agent có thể gọi tùy theo mục đích tìm kiếm.

- **Code Highlights**:
    - Tích hợp logic **Planning** sử dụng prompt kỹ thuật để ép LLM trả về JSON định dạng các sub-tasks:
    ```python
    # Trích từ src/agent/agent.py
    PLANNER_SYSTEM_PROMPT = """Bạn là một Planner... Nhiệm vụ của bạn: Phân tích câu hỏi... chia thành các bước nhỏ (sub-tasks), và chọn tool phù hợp..."""
    # Logic thực thi tuần tự các sub-task và thu thập kết quả
    for task_data in plan.get("sub_tasks", []):
        result = self.tools.execute(tool_name, query)
        sub_task.result = result
    ```

- **Documentation**: Code của tôi thay thế vòng lặp ReAct truyền thống bằng kiến trúc **Planner-Executor**. Thay vì để Agent "suy nghĩ" từng bước một cách rời rạc, Planner sẽ nhìn nhận toàn bộ vấn đề, chia nhỏ thành các truy vấn cụ thể cho Registry, giúp giảm thiểu hiện tượng lập lại (looping) và tiết kiệm token.

---

## II. Debugging Case Study (10 Points)

*Phân tích một lỗi cụ thể gặp phải trong quá trình phát triển Agent.*

- **Problem Description**: Planner đôi khi chọn các công cụ không tồn tại trong Registry (ví dụ: `web_search`) hoặc trả về JSON không hợp lệ do kèm theo lời dẫn giải văn bản.
- **Log Source**: Kiểm tra log tại `logs/` thấy sự kiện `PLAN_FAILED` hoặc lỗi `json.JSONDecodeError` khi parse output từ LLM.
- **Diagnosis**: Do System Prompt chưa đủ nghiêm ngặt về việc "CHỈ trả về JSON" và danh sách các công cụ khả dụng chưa được cung cấp động một cách rõ ràng cho Planner.
- **Solution**: 
    1. Sử dụng hàm `self.tools.get_tool_descriptions()` để chèn trực tiếp danh sách tool khả dụng vào System Prompt của Planner.
    2. Thêm logic Regex xử lý `re.search(r'\{.*\}', raw_output, re.DOTALL)` để bóc tách JSON ngay cả khi LLM trả về văn bản thừa.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Suy nghĩ về sự khác biệt giữa Chatbot (RAG đơn thuần) và Planner Agent.*

1.  **Reasoning**: Bước `Plan` giúp Agent có khả năng "chia để trị". Với các câu hỏi phức tạp (ví dụ: "So sánh chiến dịch Điện Biên Phủ và trận Điện Biên Phủ trên không"), Chatbot thường chỉ tìm kiếm 1 lần và bỏ lỡ chi tiết, trong khi Agent tự biết tách thành 2 bước tìm kiếm riêng biệt rồi mới tổng hợp.
2.  **Reliability**: Agent đôi khi hoạt động kém hơn Chatbot ở các câu hỏi cực kỳ đơn giản. Việc "lập kế hoạch" cho một câu hỏi chỉ cần 1 ý trả lời trực tiếp làm tăng độ trễ (latency) và đôi khi Planner phân tích quá đà dẫn đến kết quả nhiễu.
3.  **Observation**: Kết quả trả về từ `Observation` (kết quả của tool) đóng vai trò là "chứng cứ" thực tế. Nếu tool không tìm thấy dữ liệu, Agent sẽ nhìn thấy điều đó và thay vì bịa ra câu trả lời, nó sẽ báo cáo là không đủ thông tin trong khâu `Synthesize`.

---

## IV. Future Improvements (5 Points)

*Hướng phát triển hệ thống Agent lên quy mô sản xuất.*

- **Scalability**: Triển khai thực thi công cụ song song (Parallel Tool Execution) sử dụng `asyncio` để giảm thiểu thời gian chờ khi Agent có nhiều sub-tasks.
- **Safety**: Thêm một lớp kiểm duyệt (Guardrails) để kiểm tra các sub-tasks mà Planner đưa ra, đảm bảo Agent không thực hiện các hành động gây tốn kém tài nguyên hoặc vi phạm chính sách nội dung.
- **Performance**: Thay thế BM25 hiện tại bằng một Vector Database thực thụ (như ChromaDB hoặc Milvus) để hỗ trợ tìm kiếm ngữ nghĩa sâu hơn và quản lý hàng triệu chunk dữ liệu lịch sử.

---

