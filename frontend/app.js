const chatWindow = document.getElementById("chatWindow");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const loading = document.getElementById("loading");
const newChatBtn = document.getElementById("newChatBtn");
const sendBtn = document.getElementById("sendBtn");
const statusText = document.getElementById("statusText");

let sessionId = localStorage.getItem("sessionId") || crypto.randomUUID();
localStorage.setItem("sessionId", sessionId);
let token = localStorage.getItem("accessToken") || "";

function ts() { return new Date().toLocaleTimeString(); }
function addMessage(role, text) {
  const el = document.createElement("div");
  el.className = `msg ${role}`;
  el.innerHTML = `<strong>${role === "user" ? "You" : "Assistant"}:</strong> ${text}<div class="meta">${ts()}</div>`;
  chatWindow.appendChild(el);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function setBusyState(isBusy) {
  loading.classList.toggle("hidden", !isBusy);
  sendBtn.disabled = isBusy;
  messageInput.disabled = isBusy;
  if (!isBusy) {
    messageInput.focus();
  }
}

async function ensureToken() {
  if (token) return token;
  const res = await fetch("/auth/token", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username: "demo-user" }) });
  const data = await res.json();
  token = data.access_token;
  localStorage.setItem("accessToken", token);
  return token;
}

newChatBtn.addEventListener("click", () => {
  sessionId = crypto.randomUUID();
  localStorage.setItem("sessionId", sessionId);
  localStorage.removeItem("accessToken");
  token = "";
  chatWindow.innerHTML = "";
  statusText.textContent = "Started a fresh chat session.";
  addMessage("bot", "New chat started. Ask me anything from the knowledge base.");
});

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = messageInput.value.trim();
  if (!message) return;
  addMessage("user", message);
  messageInput.value = "";
  statusText.textContent = "Retrieving relevant context and generating answer...";
  setBusyState(true);

  try {
    const jwt = await ensureToken();
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${jwt}` },
      body: JSON.stringify({ sessionId, message })
    });
    const data = await res.json();
    addMessage("bot", res.ok ? data.reply : (data.detail || data.error || "Request failed"));
    if (res.ok) {
      const sims = Array.isArray(data.similarityScores) ? data.similarityScores.join(", ") : "n/a";
      statusText.textContent = `Retrieved ${data.retrievedChunks ?? 0} chunks | Scores: ${sims}`;
    } else {
      statusText.textContent = "Request failed. Please try again.";
    }
  } catch {
    addMessage("bot", "Unable to connect to server");
    statusText.textContent = "Network error. Check connection and retry.";
  } finally {
    setBusyState(false);
  }
});

addMessage("bot", "Hi. I can answer questions using your support knowledge base.");
