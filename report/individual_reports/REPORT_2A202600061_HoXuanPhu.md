# Individual Report: Lab 3 - Chatbot vs ReAct Agent

**Student Name:** [Hồ Xuân Phú]
**Student ID:** [2A202600061]
**Date:** [04/06/2024]

## I. Technical Contribution (15 Points)

Tôi đã thực hiện thiết kế và triển khai hệ thống công cụ (Tools) và bộ quản lý công cụ tập trung cho Agent để tối ưu hóa việc truy xuất dữ liệu lịch sử.

- **Modules Implementated**: 
    - `src/tools/search_docs.py`: Công cụ tìm kiếm văn bản tổng quát sử dụng Hybrid Retriever.
    - `src/tools/build_timeline.py`: Công cụ trích xuất mốc thời gian và sắp xếp diễn biến lịch sử.
    - `src/tools/lookup_entity.py`: Công cụ tra cứu thực thể cụ thể (nhân vật, địa danh).
    - `src/tools/tool_registry.py`: Bộ đăng ký quản lý công cụ, giúp dùng chung tài nguyên `retriever` để tiết kiệm bộ nhớ.

- **Code Highlights**:
    - **Xử lý Regex trong Timeline**: Sử dụng các pattern như `r'ngày\s+(\d{1,2})[/-](\d{1,2})[/-](\d{4})'` để chuẩn hóa ngày tháng từ văn bản thô.
    - **Logic Sắp xếp**: Hàm `_extract_date_sort_key` chuyển đổi các thực thể thời gian thành tuple `(year, month, day)` để Agent có thể hiển thị diễn biến theo đúng trình tự thời gian thực tế.
    - **Quản lý tập trung**: `ToolRegistry` khởi tạo `HybridRetriever` một lần duy nhất và truyền vào tất cả các công cụ, tránh việc xây dựng lại chỉ mục BM25 nhiều lần.

- **Documentation**: 
    Các công cụ này đóng vai trò là "đôi mắt và bàn tay" của ReAct loop. Khi Agent nhận được câu hỏi, nó sẽ dựa vào `description` của từng công cụ trong Registry để quyết định gọi `search_docs` (cho câu hỏi "tại sao"), `build_timeline` (cho câu hỏi "diễn biến") hoặc `lookup_entity` (cho câu hỏi "ai/cái gì"). Kết quả trả về (Observation) sau đó được nạp lại vào context để Agent đưa ra `Thought` tiếp theo.

---

## II. Debugging Case Study (10 Points)

- **Problem Description**: Agent rơi vào vòng lặp vô hạn hoặc trả về lỗi khi không tìm thấy mốc thời gian cụ thể trong các đoạn văn bản (chunks) mặc dù có nội dung liên quan.
- **Log Source**: `logs/2026-04-06.log` - `TOOL_BUILD_TIMELINE: No specific dates extracted for query: 'Chiến dịch Điện Biên Phủ'`.
- **Diagnosis**: Do hàm `_extract_timeline_entries` quá khắt khe, chỉ chấp nhận các câu có chứa đầy đủ ngày/tháng/năm. Nếu tài liệu chỉ ghi "năm 1954" ở đầu đoạn và các câu sau kể diễn biến, công cụ sẽ bỏ qua các câu đó.
- **Solution**: Triển khai cơ chế **Fallback** trong `build_timeline.py`. Nếu không trích xuất được mốc thời gian chi tiết, công cụ sẽ lấy 5 đoạn văn bản liên quan nhất, trích xuất năm sơ bộ bằng `_extract_year` và trả về dưới dạng danh sách tóm tắt để Agent vẫn có dữ liệu để trả lời thay vì trả về kết quả rỗng.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1.  **Reasoning**: Khối `Thought` giúp Agent phân rã các câu hỏi phức tạp. Ví dụ, với câu hỏi "So sánh đợt 1 và đợt 2 của chiến dịch", Chatbot thông thường có thể trộn lẫn thông tin. Agent thông qua `Thought` sẽ quyết định gọi `build_timeline` để lấy danh sách sự kiện trước, sau đó mới phân tích điểm khác biệt.
2.  **Reliability**: Agent đôi khi tệ hơn Chatbot khi câu hỏi quá đơn giản hoặc mang tính chất hội thoại (ví dụ: "Chào bạn"). Khi đó, Agent vẫn cố gắng gọi công cụ `search_docs`, dẫn đến kết quả trả về rườm rà và tốn tài nguyên (token/time) không cần thiết.
3.  **Observation**: Phản hồi từ môi trường đóng vai trò sửa lỗi. Nếu `lookup_entity` trả về "Không tìm thấy thông tin", Agent nhìn vào `Observation` đó và tự điều chỉnh trong `Thought` tiếp theo để thử một từ khóa tìm kiếm khác rộng hơn bằng `search_docs`.

---

## IV. Future Improvements (5 Points)

- **Scalability**: Sử dụng **Asynchronous API (asyncio)** cho các hàm `run()` của công cụ để có thể thực hiện nhiều truy vấn song song khi Agent cần gọi nhiều công cụ cùng lúc.
- **Safety**: Thiết lập một **Validation Layer** để kiểm tra đầu ra của Tool (Observation) trước khi đưa vào LLM, nhằm loại bỏ các thông tin nhạy cảm hoặc không liên quan.
- **Performance**: Chuyển đổi từ BM25 thuần túy sang **Vector Database (như Pinecone hoặc ChromaDB)** trong `HybridRetriever` để tăng độ chính xác khi tìm kiếm ngữ nghĩa cho các câu hỏi không chứa từ khóa chính xác.

---

