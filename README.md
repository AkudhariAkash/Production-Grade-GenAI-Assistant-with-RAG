# 🧠 Production-Grade GenAI Assistant with RAG

This project implements a **Production-Style GenAI Chat Assistant** using **Retrieval-Augmented Generation (RAG)**.

The assistant answers user questions by retrieving relevant information from a **document knowledge base** and generating responses using a **Large Language Model (LLM)**.

The system ensures that responses are **grounded in retrieved documents**, preventing hallucinations.

---

# 🎯 Objective

The goal of this project is to build a **GenAI-powered chat assistant** that:

1. Converts documents into embeddings
2. Stores embeddings in a vector database
3. Retrieves relevant documents using similarity search
4. Injects retrieved context into the LLM prompt
5. Generates accurate grounded responses

---

# 🛠 Tech Stack

| Component | Technology |
|----------|------------|
| Backend | Python (Flask) |
| Frontend | HTML, CSS, JavaScript |
| LLM API | Google Gemini |
| Embedding Model | gemini-embedding-001 |
| Vector Storage | In-memory vector store |
| Similarity Search | Cosine Similarity |
| Libraries | numpy, scikit-learn |

---

# 🧩 System Architecture

User
│
│ Ask Question
▼
Frontend (HTML Chat UI)
│
│ POST /api/chat
▼
Flask Backend
│
├── Query Embedding
│
▼
Vector Store
(Document Embeddings)
│
│ Cosine Similarity Search
▼
Top 3 Relevant Chunks
│
▼
Prompt Builder
(Context + History + Question)
│
▼
Gemini LLM
│
▼
Generated Answer
│
▼
Return JSON Response
│
▼
Frontend Chat Display



---

# 📚 RAG Workflow

The system follows a **Retrieval-Augmented Generation pipeline**.

---

## 1️⃣ Document Knowledge Base

Documents are stored in:

```

docs.json

```

Example:

```json
{
"title": "Reset Password",
"content": "Users can reset their password from Settings > Security."
}


2️⃣ Document Chunking

Large documents are split into smaller chunks.

Example:

Chunk Size = 120 words

Purpose:

Improves semantic retrieval

Prevents token overflow

Improves embedding accuracy

3️⃣ Embedding Generation

Each document chunk is converted into a vector embedding using:

gemini-embedding-001

Example embedding:

[0.23, -0.14, 0.89, ...]

These embeddings represent the semantic meaning of the text.

4️⃣ Vector Storage

Embeddings are stored in memory as a vector store.

Example structure:

{
"title": "Reset Password",
"content": "Users can reset their password...",
"embedding": [0.23, -0.11, 0.54]
}
5️⃣ Query Embedding

When a user asks a question:

How can I reset my password?

The system generates a query embedding.

6️⃣ Similarity Search

Cosine similarity compares the query embedding with document embeddings.

Formula:

cosine_similarity(A,B) =
(A · B) / (||A|| ||B||)

The system retrieves the Top 3 most relevant document chunks.

7️⃣ Context Injection

Retrieved chunks are injected into the LLM prompt.

Example prompt:

Context:
Users can reset their password from Settings > Security.

User Question:
How can I reset my password?

Answer:
8️⃣ Response Generation

The LLM generates the final grounded response.

Example:

Users can reset their password by navigating to Settings > Security > Reset Password.
🧠 Prompt Design

Prompt structure:

System Instruction
Context
Conversation History
User Question

Example:

You are a helpful AI assistant.

Answer ONLY using the provided context.

Context:
...

Conversation History:
...

User Question:
...

Answer:

Purpose:

Prevent hallucinations

Maintain conversation flow

Ensure grounded responses

🔌 API Design
Endpoint
POST /api/chat
Request
{
"sessionId": "abc123",
"message": "How can I reset my password?"
}
Response
{
"reply": "Users can reset their password from Settings > Security.",
"tokensUsed": 120,
"retrievedChunks": 3
}
Error Response
{
"error": "Message required"
}
💻 Frontend Features

The chat interface includes:

User message input

Send button

Chat history display

Auto scroll

Session handling using localStorage

Loading indicator

🧠 Conversation Memory

The assistant stores the last 3–5 conversation pairs.

Example:

User: Reset password
Assistant: Instructions...

User: Where is security settings?
Assistant: Security settings are located...

This enables context-aware conversations.

📂 Project Structure
genai-rag-assistant
│
├── app.py
├── docs.json
├── requirements.txt
│
├── templates
│   └── index.html
│
├── static
│   ├── script.js
│   └── styles.css
│
└── README.md
⚙️ Setup Instructions
1️⃣ Clone Repository
git clone https://github.com/your-username/genai-rag-assistant
cd genai-rag-assistant
2️⃣ Create Virtual Environment
python -m venv venv

Activate:

Windows

venv\Scripts\activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Set Gemini API Key

Windows:

set GEMINI_API_KEY=your_api_key

Linux / Mac:

export GEMINI_API_KEY=your_api_key
5️⃣ Run the Application
python app.py
6️⃣ Open in Browser
http://localhost:5000


