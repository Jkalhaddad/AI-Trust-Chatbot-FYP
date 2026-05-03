//  Generate a unique participant ID once per session
let sessionId = sessionStorage.getItem("sessionId");

if (!sessionId) {
    sessionId = "U" + Math.floor(1000 + Math.random() * 9000);
    sessionStorage.setItem("sessionId", sessionId);
}

console.log("Participant ID:", sessionId);

async function sendMessage() {
    const input = document.getElementById("userInput");
    const text = input.value;
    input.value = "";

    addMessage("User", text);

    // SHOW "Bot is typing..."
    showTyping();

    const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            message: text,
            session_id: sessionId
        })
    });

    const data = await response.json();

    // REMOVE typing indicator
    hideTyping();

    // SHOW bot reply
    addMessage("Bot", data.reply);
}

function addMessage(sender, message) {
    const chat = document.getElementById("chat");

    const bubble = document.createElement("div");

    if (sender === "User") {
        bubble.className = "msg-box user";
    } else {
        bubble.className = "msg-box bot";
    }

    // Create message text
    const text = document.createElement("div");
    text.innerText = message;

    // Create timestamp
    const time = document.createElement("div");
    time.className = "timestamp";
    time.innerText = new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });

    // Add both to the bubble
    bubble.appendChild(text);
    bubble.appendChild(time);

    chat.appendChild(bubble);

    // Auto-scroll
    chat.scrollTop = chat.scrollHeight;
}

document.getElementById("userInput").addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});

function showTyping() {
    const chat = document.getElementById("chat");

    // Prevent duplicate typing indicators
    if (document.getElementById("typing")) return;

    const typing = document.createElement("div");
    typing.id = "typing";
    typing.className = "msg-box bot typing";
    typing.innerText = "Bot is typing...";

    chat.appendChild(typing);
    chat.scrollTop = chat.scrollHeight;
}

function hideTyping() {
    const typing = document.getElementById("typing");
    if (typing) typing.remove();
}

function downloadChat() {
    window.location.href = "/download/" + sessionId;
}