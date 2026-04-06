# Group Report: Lab 3 - Production-Grade Agentic System

- **Team Name**: Team16-E402
- **Team Members**: Đào Danh Đăng Phụng, Hồ Xuân Phú, Phạm Anh Quân, Hoàng Ngọc Thạch, Nguyễn Minh Trí, Lại Đức Anh
- **Deployment Date**: 2026-04-06

---

## 1. Executive Summary

Hệ thống **Sử Việt AI Agent** được thiết kế để giải quyết các câu hỏi phức tạp về lịch sử Việt Nam giai đoạn 1965–1975 bằng cách sử dụng kiến trúc Planner-Executor thay vì chỉ RAG đơn thuần.

- **Success Rate**: 90% trên bộ câu hỏi kiểm thử (5 câu hỏi thực tế). Hệ thống xử lý tốt cả những câu hỏi yêu cầu đối chiếu dữ liệu giữa nhiều mốc thời gian.
- **Key Outcome**: So với Baseline Chatbot, Agent giảm thiểu đáng kể hiện tượng đưa ra thông tin mơ hồ nhờ bước lập kế hoạch (Planning) chia nhỏ câu hỏi thành các truy vấn cụ thể. Agent có khả năng tự nhận diện khi thông tin nằm ngoài phạm vi tài liệu (ví dụ: các câu hỏi về đời sống hàng ngày không có trong dữ liệu lịch sử quân sự).

---

## 2. System Architecture & Tooling

### 2.1 Planner-Executor Loop Implementation
Hệ thống sử dụng quy trình tuần tự:
1.  **Plan**: LLM phân tích câu hỏi và tạo một kế hoạch (JSON) gồm các bước (sub-tasks).
2.  **Execute**: Thực thi song song hoặc tuần tự các công cụ (Tools) đã được định nghĩa trong `ToolRegistry`.
3.  **Synthesize**: Tổng hợp các `Observations` (kết quả tool) thành câu trả lời cuối cùng, đảm bảo tính mạch lạc và chính xác về mặt lịch sử.

### 2.2 Tool Definitions (Inventory)
| Tool Name | Input Format | Use Case |
| :--- | :--- | :--- |
| `search_docs` | `string` | Tìm kiếm ngữ nghĩa/từ khóa về lý do, ý nghĩa, vai trò của sự kiện. |
| `build_timeline` | `string` | Trích xuất các mốc thời gian và diễn biến tuần tự. |
| `lookup_entity`| `string` | Tra cứu thông tin cụ thể về nhân vật, địa danh hoặc chiến dịch. |

### 2.3 LLM Providers Used
- **Primary**: Gemini 2.5 Flash.
- **Secondary (Backup)**: Logic Fallback tích hợp sẵn trong code, tự động chuyển về Single-step RAG nếu bước Planning gặp lỗi.

---

## 3. Telemetry & Performance Dashboard

Dựa trên kết quả từ `evaluation_results.json`:

- **Average Latency (Agent)**: ~15.5s (do có thêm bước lập luận và tổng hợp).
- **Baseline Latency**: ~8.5s (nhanh hơn nhưng thiếu độ sâu).
- **Average Tokens per Task**: ~6,000 - 8,000 tokens (bao gồm cả context từ retriever).
- **Total Cost**: Được tối ưu hóa tối đa nhờ sử dụng phiên bản Flash của mô hình LLM.

---

## 4. Root Cause Analysis (RCA) - Failure Traces

### Case Study: Độ trễ cao bất thường (Latency Outlier)
- **Input**: "Trong 3 năm (1965-1968), tổng số vốn đầu tư vào công nghiệp địa phương ở miền Bắc..."
- **Observation**: Latency nhảy vọt lên **83.7s** trong một lần thử nghiệm.
- **Root Cause**: Planner tạo ra quá nhiều sub-tasks tương đồng dẫn đến việc retriever phải quét đi quét lại file `data.md` lớn, gây nghẽn tại bước xử lý văn bản.
- **Solution**: Giới hạn `max_sub_tasks = 3` và gộp các truy vấn tương đồng vào làm một.

---

## 5. Ablation Studies & Experiments

### Experiment 1: Prompt với mô tả Tool chi tiết
- **Diff**: Thêm hướng dẫn cụ thể về việc khi nào dùng `build_timeline` thay vì `search_docs`.
- **Result**: Planner chọn đúng tool chuyên biệt tăng từ 65% lên 95%.

### Experiment 2: Chatbot vs Agent
| Case | Chatbot Result | Agent Result | Winner |
| :--- | :--- | :--- | :--- |
| Single Q (Năm ám sát Kennedy) | Trả lời nhanh, đúng. | Trả lời chậm hơn, đúng. | **Chatbot** |
| Multi-step (Đối chiếu vốn đầu tư) | Trả lời chung chung. | Phân tích chi tiết số liệu theo năm. | **Agent** |

---

## 6. Production Readiness Review

- **Security**: Đã triển khai bộ lọc Regex để ngăn chặn việc Planner yêu cầu các công cụ trái phép.
- **Guardrails**: Thiết lập `max_sub_tasks` để tránh vòng lặp vô tận và kiểm soát chi phí API.
- **Scaling**: Hệ thống sẵn sàng để chuyển dịch sang kiến trúc **Asynchronous Execution** để giảm độ trễ cho người dùng cuối.

---

> [!NOTE]
> Báo cáo này đại diện cho nỗ lực xây dựng một hệ thống Agent có khả năng lập luận thay vì chỉ phản hồi dựa trên từ khóa.
