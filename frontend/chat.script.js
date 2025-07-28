// const API_BASE_URL = "http://127.0.0.1:8000/api/v1";
const API_BASE_URL = "/api/v1";
const chatWindow = document.getElementById("chat-window");
const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");

function addMessage(text, sender) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}`;
    messageDiv.textContent = text;
    chatWindow.appendChild(messageDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight; // Auto-scroll to bottom
}

async function handleSendMessage() {
    const prompt = chatInput.value.trim();
    if (!prompt) return;

    addMessage(prompt, "user");
    chatInput.value = ""; // Clear input

    // Show thinking indicator
    const thinkingDiv = document.createElement("div");
    thinkingDiv.className = "message ai thinking";
    thinkingDiv.textContent = "Thinking...";
    chatWindow.appendChild(thinkingDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: prompt }),
        });

        const result = await response.json();
        chatWindow.removeChild(thinkingDiv); // Remove thinking indicator

        if (!response.ok) {
            addMessage(result.detail || "An error occurred.", "ai");
        } else {
            addMessage(result.response, "ai");
        }
    } catch (error) {
        chatWindow.removeChild(thinkingDiv);
        addMessage(`Failed to connect to the server: ${error.message}`, "ai");
    }
}

sendBtn.addEventListener("click", handleSendMessage);
chatInput.addEventListener("keypress", (event) => {
    if (event.key === "Enter") {
        handleSendMessage();
    }
});