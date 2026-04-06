# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyễn Minh Trí
- **Student ID**: 2A202600182
- **Date**: 06/04/2026

---

## I. Technical Contribution (15 Points)

Em đóng góp phần triển khai hệ thống Server API và lớp điều phối để vận hành các Agent.

- **Modules Implementated**: `server.py`
- **Code Highlights**: 
    * Sử dụng biến global `_agents` và các hàm getter (`get_history_agent`, `get_baseline_agent`) để đảm bảo mỗi loại agent chỉ được khởi tạo một lần, giúp tiết kiệm tài nguyên hệ thống.
    * Cấu hình `_get_llm()` để kết nối với model `gemini-2.5-flash` thông qua `GeminiProvider`.
    * Sử dụng `asyncio.to_thread(agent.run, req.question)` để thực hiện các tác vụ suy luận của Agent mà không làm chặn server FastAPI.
- **Documentation**: Code trong `server.py` tiếp nhận yêu cầu từ người dùng qua endpoint `/api/chat`, sau đó dựa vào tham số `mode` để gọi đúng logic xử lý tương ứng và trả về kết quả kèm theo thời gian phản hồi.

---

## II. Debugging Case Study (10 Points)

Xử lý lỗi Blocking Event Loop khi Agent thực hiện tác vụ suy luận dài.

- **Problem Description**: Server bị treo và không thể phản hồi các request khác.
- **Log Source**: Hệ thống dừng lại ở `log.info(f"📩...")` và các request song song bị timeout.
- **Diagnosis**: Phương thức `agent.run()` là tác vụ đồng bộ. Khi gọi trực tiếp trong hàm `async def chat`, nó chiếm dụng Event Loop của FastAPI, khiến toàn bộ server phải dừng lại để đợi Agent xong việc.
- **Solution**: Sử dụng `asyncio.to_thread` để đẩy việc chạy Agent sang một thread riêng biệt, giải phóng Event Loop cho server.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1.  **Reasoning**: `HistoryAgent` sử dụng `ToolRegistry` để truy xuất dữ liệu từ `data/data.md`. Khác với Chatbot thông thường, Agent này có quy trình "Planner" để quyết định cách sử dụng dữ liệu trước khi trả lời.
2.  **Reliability**: Trong code, `latency_s` được tính toán cho thấy Agent thường có độ trễ cao hơn Baseline. Tuy nhiên, Agent có khả năng xử lý lỗi tốt hơn bằng cách trả về thông báo lỗi chi tiết thay vì sập hệ thống.
3.  **Observation**: Thông qua logging, em quan sát thấy phản hồi từ Agent có độ dài và cấu trúc phức tạp hơn nhờ vào việc sử dụng các công cụ hỗ trợ.

---

## IV. Future Improvements (5 Points)

- **Scalability**: Hiện tại `_agents` lưu trong RAM, nếu số lượng agent tăng lên hoặc cần lưu session người dùng, cần chuyển sang sử dụng Redis hoặc một cơ chế quản lý state tập trung.
- **Safety**: Bổ sung validation chặt chẽ hơn cho `ChatRequest`, ví dụ như giới hạn độ dài của `question` để tránh việc gửi các prompt quá dài gây tốn kém tài nguyên LLM.
- **Performance**: Chuyển đổi từ `FileResponse` cho giao diện tĩnh sang một hệ thống quản lý giao diện riêng biệt để tối ưu hóa tốc độ tải trang và khả năng mở rộng UI.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.