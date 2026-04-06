# Individual Report: Lab 3 - Chatbot vs ReAct Agent

**Student Name:** [Đào Danh Đăng Phụng]
**Student ID:** [2A202600358]
**Date:** [04/06/2024]

---

## I. Technical Contribution (15 Points)

### Describe your specific contribution to the codebase

Trong lab này, tôi đã phát triển giao diện người dùng (UI/UX) hoàn chỉnh cho hệ thống chatbot lịch sử Việt Nam, bao gồm ba thành phần chính:

* Responsive Web Interface (HTML/CSS/JavaScript)
* Real-time Chat Experience
* User Experience Design cho AI Agent System

Giao diện này đóng vai trò là cầu nối giữa người dùng và hệ thống AI, đảm bảo trải nghiệm mượt mà và trực quan.

---

### Modules Implemented

* `static/index.html` - Cấu trúc HTML chính
* `static/style.css` - Styling với Dark Theme Premium
* `static/app.js` - JavaScript logic cho chat functionality

---

### Code Highlights

#### 1. Responsive Dark Theme Design

Tôi thiết kế giao diện với dark theme professional sử dụng CSS custom properties:

```css
:root {
    --bg-primary: #060a1a;
    --gold-primary: #d4a853;
    --text-primary: #e8eaf0;
    /* ... */
}
```

* Gradient backgrounds với radial effects
* Gold accent colors cho branding
* Glass morphism effects với backdrop-filter
* Responsive design cho mobile/desktop

#### 2. Real-time Chat Interface

Implement hệ thống chat real-time với JavaScript vanilla:

```javascript
async function sendMessage() {
    // 1. Add user message to UI
    // 2. Show typing indicator
    // 3. Send POST request to /api/chat
    // 4. Handle response and display
}
```

* Auto-resize textarea
* Character counter (2000 chars limit)
* Typing animation với bounce effect
* Markdown rendering cho AI responses

#### 3. Mode Toggle System

Xây dựng hệ thống chuyển đổi giữa Baseline và Agent mode:

```javascript
document.querySelectorAll(".mode-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        currentMode = btn.dataset.mode;
        updateModeBadge();
    });
});
```

* Visual feedback với active states
* Real-time mode indicator
* Smooth transitions và animations

### Documentation: UI/UX Integration with Backend

* Frontend: HTML/CSS/JS thuần (không framework)
* Backend: FastAPI với WebSocket support
* API Integration: RESTful endpoints cho chat
* State Management: Client-side state cho chat history

---

## II. Debugging Case Study (10 Points)

### Problem Description

Giao diện gặp các vấn đề UX:

* Loading states không rõ ràng
* Error handling cho API failures
* Mobile responsiveness issues
* Accessibility concerns

---

### Log Source

```javascript
console.log("API Error:", error);
console.log("UI State:", { isLoading, currentMode });
```

Quan sát:

* Network timeouts không hiển thị
* Error messages không user-friendly
* Mobile sidebar không hoạt động đúng

---

### Diagnosis

Nguyên nhân:

1. Thiếu error boundaries
2. Loading states không comprehensive
3. Mobile CSS media queries chưa tối ưu
4. Accessibility attributes thiếu

---

### Solution

#### 1. Enhanced Error Handling

```javascript
catch (err) {
    addMessage("ai", `⚠️ Lỗi kết nối: ${err.message}. Hãy đảm bảo server đang chạy tại http://localhost:8000`, {
        mode: currentMode,
    });
}
```

* User-friendly error messages
* Fallback UI states
* Retry mechanisms

#### 2. Loading States Improvement

* Typing indicator với animation
* Disabled send button khi loading
* Visual feedback cho mode switching

#### 3. Mobile UX Optimization

```css
@media (max-width: 768px) {
    .sidebar {
        transform: translateX(-100%);
    }
    .sidebar.open {
        transform: translateX(0);
    }
}
```

* Collapsible sidebar
* Touch-friendly buttons
* Responsive chat bubbles

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

### Reasoning

Từ góc nhìn UI/UX:

* Chatbot: UX đơn giản, response time nhanh
* ReAct: UX phức tạp hơn với multiple steps, cần loading indicators tốt hơn

---

### Reliability

ReAct cần UX tốt hơn cho:

* Multi-step reasoning display
* Progress indicators
* Intermediate results preview

---

### Observation

UI nên hiển thị:

* Thought process của agent
* Tool usage visualization
* Confidence scores
* Source attribution

Chatbot cần grounding indicators để user hiểu độ tin cậy.

---

## IV. Future Improvements (5 Points)

### Scalability

* Progressive Web App (PWA)
* Offline capability với service workers
* Chat history persistence (localStorage/IndexedDB)

---

### Safety

* Input sanitization
* Rate limiting UI feedback
* Content moderation indicators

---

### Performance

* Virtual scrolling cho long conversations
* Lazy loading cho chat history
* WebSocket cho real-time updates
* Dark mode toggle với system preference detection
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
