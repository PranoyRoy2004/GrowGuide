// frontend/js/chat.js

const API     = "http://127.0.0.1:5000";
let history   = [];
let isWaiting = false;

// ── Add a bubble to the chat window ──────────────────────────
function addBubble(text, role) {
    const window = document.getElementById("chat-window");
    const bubble = document.createElement("div");
    bubble.classList.add("chat-bubble", role);
    bubble.textContent = text;
    window.appendChild(bubble);
    window.scrollTop = window.scrollHeight;
    return bubble;
}

// ── Typing indicator ──────────────────────────────────────────
function showTyping() {
    const window = document.getElementById("chat-window");
    const bubble = document.createElement("div");
    bubble.classList.add("chat-bubble", "typing");
    bubble.id = "typing-indicator";
    bubble.innerHTML = `
        <div class="typing-dots">
            <span></span><span></span><span></span>
        </div>`;
    window.appendChild(bubble);
    window.scrollTop = window.scrollHeight;
}

function hideTyping() {
    const el = document.getElementById("typing-indicator");
    if (el) el.remove();
}

// ── Send a message ────────────────────────────────────────────
async function sendMessage() {
    if (isWaiting) return;

    const input = document.getElementById("chat-input");
    const message = input.value.trim();
    if (!message) return;

    input.value = "";
    addBubble(message, "user");
    showTyping();
    isWaiting = true;

    const sendBtn = document.getElementById("send-btn");
    sendBtn.disabled = true;

    try {
        const res = await fetch(`${API}/chat`, {
            method : "POST",
            headers: { "Content-Type": "application/json" },
            body   : JSON.stringify({ message, history })
        });

        const data = await res.json();
        hideTyping();

        if (data.success) {
            addBubble(data.response, "bot");
            history = data.updated_history;
        } else {
            addBubble("Sorry, something went wrong. Please try again.", "bot");
        }

    } catch (err) {
        hideTyping();
        addBubble("Cannot connect to server. Make sure Flask is running on port 5000.", "bot");
    } finally {
        isWaiting = false;
        sendBtn.disabled = false;
        input.focus();
    }
}

// ── Suggested question buttons ────────────────────────────────
function sendSuggestion(btn) {
    document.getElementById("chat-input").value = btn.textContent.trim();
    sendMessage();
}

// ── Clear conversation ────────────────────────────────────────
function clearChat() {
    history = [];
    document.getElementById("chat-window").innerHTML = "";
    loadWelcome();
}

// ── Load welcome message on page open ────────────────────────
async function loadWelcome() {
    try {
        const res  = await fetch(`${API}/chat/welcome`);
        const data = await res.json();
        if (data.success) addBubble(data.message, "bot");
    } catch {
        addBubble("👋 Hello! I'm GrowGuide. Ask me anything about farming! 🌱", "bot");
    }
}

// ── Init ──────────────────────────────────────────────────────
loadWelcome();