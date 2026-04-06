/* ═══════════════════════════════════════════════════════════════
   Sử Việt AI — Client-side JavaScript
   ═══════════════════════════════════════════════════════════════ */

const API_URL = "/api/chat";

// ─── State ──────────────────────────────────────────────────────
let currentMode = "agent";
let isLoading = false;

// ─── DOM Elements ───────────────────────────────────────────────
const chatMessages = document.getElementById("chat-messages");
const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");
const welcomeScreen = document.getElementById("welcome-screen");
const modeBadge = document.getElementById("mode-badge");
const charCount = document.getElementById("char-count");
const sidebar = document.getElementById("sidebar");
const mobileToggle = document.getElementById("mobile-toggle");

// ─── Mode Toggle ────────────────────────────────────────────────
document.querySelectorAll(".mode-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
        if (isLoading) return;

        document.querySelectorAll(".mode-btn").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");

        currentMode = btn.dataset.mode;
        updateModeBadge();
    });
});

function updateModeBadge() {
    if (currentMode === "agent") {
        modeBadge.textContent = "🧠 Agent";
    } else {
        modeBadge.textContent = "⚡ Baseline";
    }
}

// ─── Suggestion Buttons ─────────────────────────────────────────
document.querySelectorAll(".suggestion-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
        const question = btn.dataset.question;
        chatInput.value = question;
        autoResizeInput();
        updateCharCount();
        sendMessage();
        // Close sidebar on mobile
        sidebar.classList.remove("open");
    });
});

// ─── Mobile Toggle ──────────────────────────────────────────────
mobileToggle.addEventListener("click", () => {
    sidebar.classList.toggle("open");
});

// Close sidebar when clicking outside on mobile
document.addEventListener("click", (e) => {
    if (
        window.innerWidth <= 768 &&
        sidebar.classList.contains("open") &&
        !sidebar.contains(e.target) &&
        !mobileToggle.contains(e.target)
    ) {
        sidebar.classList.remove("open");
    }
});

// ─── Input Handling ─────────────────────────────────────────────
chatInput.addEventListener("input", () => {
    autoResizeInput();
    updateCharCount();
});

chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendBtn.addEventListener("click", sendMessage);

function autoResizeInput() {
    chatInput.style.height = "auto";
    chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + "px";
}

function updateCharCount() {
    charCount.textContent = `${chatInput.value.length} / 2000`;
}

// ─── Markdown Renderer (simple) ─────────────────────────────────
function renderMarkdown(text) {
    let html = text;

    // Escape HTML
    html = html.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

    // Headers
    html = html.replace(/^### (.+)$/gm, "<h3>$1</h3>");
    html = html.replace(/^## (.+)$/gm, "<h2>$1</h2>");
    html = html.replace(/^# (.+)$/gm, "<h1>$1</h1>");

    // Bold & italic
    html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");

    // Inline code
    html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

    // Unordered list items (- or *)
    html = html.replace(/^[\-\*] (.+)$/gm, "<li>$1</li>");

    // Ordered list items
    html = html.replace(/^\d+\.\s(.+)$/gm, "<li>$1</li>");

    // Wrap consecutive <li> in <ul>
    html = html.replace(/((?:<li>.*<\/li>\n?)+)/g, "<ul>$1</ul>");

    // Paragraphs: double newlines
    html = html.replace(/\n{2,}/g, "</p><p>");
    html = "<p>" + html + "</p>";

    // Clean up empty paragraphs
    html = html.replace(/<p>\s*<\/p>/g, "");
    html = html.replace(/<p>\s*(<h[123]>)/g, "$1");
    html = html.replace(/(<\/h[123]>)\s*<\/p>/g, "$1");
    html = html.replace(/<p>\s*(<ul>)/g, "$1");
    html = html.replace(/(<\/ul>)\s*<\/p>/g, "$1");

    return html;
}


// ─── Chat Logic ─────────────────────────────────────────────────
function addMessage(role, content, meta = {}) {
    // Hide welcome screen on first message
    if (welcomeScreen) {
        welcomeScreen.style.display = "none";
    }

    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${role}`;

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = role === "user" ? "👤" : "⭐";

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";

    if (role === "ai") {
        bubble.innerHTML = renderMarkdown(content);
    } else {
        bubble.textContent = content;
    }

    contentDiv.appendChild(bubble);

    // Meta tags
    if (meta.latency || meta.mode) {
        const metaDiv = document.createElement("div");
        metaDiv.className = "message-meta";

        if (meta.mode) {
            const modeTag = document.createElement("span");
            modeTag.className = "meta-tag";
            modeTag.textContent = meta.mode === "agent" ? "🧠 Agent" : "⚡ Baseline";
            metaDiv.appendChild(modeTag);
        }

        if (meta.latency) {
            const latTag = document.createElement("span");
            latTag.className = "meta-tag meta-latency";
            latTag.textContent = `⏱ ${meta.latency}s`;
            metaDiv.appendChild(latTag);
        }

        contentDiv.appendChild(metaDiv);
    }

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(contentDiv);
    chatMessages.appendChild(msgDiv);

    scrollToBottom();
    return msgDiv;
}

function addTypingIndicator() {
    const msgDiv = document.createElement("div");
    msgDiv.className = "message ai";
    msgDiv.id = "typing-indicator";

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = "⭐";

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.innerHTML = `<div class="typing-dots"><span></span><span></span><span></span></div>`;

    contentDiv.appendChild(bubble);
    msgDiv.appendChild(avatar);
    msgDiv.appendChild(contentDiv);
    chatMessages.appendChild(msgDiv);

    scrollToBottom();
}

function removeTypingIndicator() {
    const el = document.getElementById("typing-indicator");
    if (el) el.remove();
}

function scrollToBottom() {
    requestAnimationFrame(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    });
}


// ─── Send Message ───────────────────────────────────────────────
async function sendMessage() {
    const question = chatInput.value.trim();
    if (!question || isLoading) return;

    isLoading = true;
    sendBtn.disabled = true;

    // Add user message
    addMessage("user", question);

    // Clear input
    chatInput.value = "";
    autoResizeInput();
    updateCharCount();

    // Show typing
    addTypingIndicator();

    try {
        const res = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                question: question,
                mode: currentMode,
            }),
        });

        if (!res.ok) {
            throw new Error(`HTTP ${res.status}`);
        }

        const data = await res.json();

        removeTypingIndicator();

        addMessage("ai", data.answer, {
            mode: data.mode,
            latency: data.latency_s,
        });

    } catch (err) {
        removeTypingIndicator();
        addMessage("ai", `⚠️ Lỗi kết nối: ${err.message}. Hãy đảm bảo server đang chạy tại http://localhost:8000`, {
            mode: currentMode,
        });
    } finally {
        isLoading = false;
        sendBtn.disabled = false;
        chatInput.focus();
    }
}

// ─── Init ───────────────────────────────────────────────────────
chatInput.focus();
updateModeBadge();
