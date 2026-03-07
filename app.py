import json
import numpy as np
import os
import time
from flask import Flask, request, jsonify, render_template
from sklearn.metrics.pairwise import cosine_similarity
from google import genai
import uuid

# ---------------------------------------------------
# Gemini Configuration
# ---------------------------------------------------

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("Please set GEMINI_API_KEY environment variable")

client = genai.Client(api_key=API_KEY)

LLM_MODEL = "gemini-2.5-flash"
EMBED_MODEL = "gemini-embedding-001"

# ---------------------------------------------------
# Flask Setup
# ---------------------------------------------------

app = Flask(__name__)

# ---------------------------------------------------
# Load Documents
# ---------------------------------------------------

with open("docs.json", "r", encoding="utf-8") as f:
    documents = json.load(f)

print("Documents loaded:", len(documents))

# ---------------------------------------------------
# Chunk Documents
# ---------------------------------------------------

def chunk_text(text, chunk_size=120):

    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks


# ---------------------------------------------------
# Generate Embedding
# ---------------------------------------------------

def get_embedding(text):

    response = client.models.embed_content(
        model=EMBED_MODEL,
        contents=[text]
    )

    return response.embeddings[0].values


# ---------------------------------------------------
# Load or Build Vector Store
# ---------------------------------------------------

VECTOR_FILE = "vector_store.json"

if os.path.exists(VECTOR_FILE):

    print("Loading existing embeddings...")

    with open(VECTOR_FILE, "r", encoding="utf-8") as f:
        vector_store = json.load(f)

else:

    print("Generating embeddings...")

    vector_store = []

    for doc in documents:

        chunks = chunk_text(doc["content"])

        for chunk in chunks:

            embedding = get_embedding(chunk)

            vector_store.append({
                "title": doc["title"],
                "content": chunk,
                "embedding": embedding
            })

            time.sleep(1)   # avoid API rate limits

    with open(VECTOR_FILE, "w", encoding="utf-8") as f:
        json.dump(vector_store, f)

print("Vector DB Loaded:", len(vector_store))


# ---------------------------------------------------
# Similarity Search
# ---------------------------------------------------

def retrieve_chunks(query_embedding, top_k=3):

    scores = []

    for item in vector_store:

        similarity = cosine_similarity(
            np.array(query_embedding).reshape(1, -1),
            np.array(item["embedding"]).reshape(1, -1)
        )[0][0]

        scores.append((similarity, item))

    scores.sort(reverse=True, key=lambda x: x[0])

    return scores[:top_k]


# ---------------------------------------------------
# Session Memory
# ---------------------------------------------------

sessions = {}


# ---------------------------------------------------
# Prompt Builder
# ---------------------------------------------------

def build_prompt(context, history, question):

    history_text = ""

    for h in history[-5:]:
        history_text += f"User: {h['user']}\nAssistant: {h['assistant']}\n"

    prompt = f"""
You are a helpful AI assistant.

Answer ONLY using the provided context.

If the answer is not in the context say:
"I don't have enough information."

Context:
{context}

Conversation History:
{history_text}

User Question:
{question}

Answer:
"""

    return prompt


# ---------------------------------------------------
# Generate LLM Response
# ---------------------------------------------------

def generate_answer(prompt):

    response = client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt,
        config={"temperature": 0.2}
    )

    return response.text, 0


# ---------------------------------------------------
# Routes
# ---------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------------------------------------------
# Chat API
# ---------------------------------------------------

@app.route("/api/chat", methods=["POST"])
def chat():

    try:

        data = request.json

        if not data or "message" not in data:
            return jsonify({"error": "Message required"}), 400

        message = data["message"]
        session_id = data.get("sessionId", str(uuid.uuid4()))

        if session_id not in sessions:
            sessions[session_id] = []

        history = sessions[session_id]

        # Query embedding
        query_embedding = get_embedding(message)

        # Retrieve chunks
        results = retrieve_chunks(query_embedding)

        if not results or results[0][0] < 0.3:

            return jsonify({
                "reply": "I don't have enough information to answer that.",
                "tokensUsed": 0,
                "retrievedChunks": 0
            })

        context = "\n".join([r[1]["content"] for r in results])

        prompt = build_prompt(context, history, message)

        answer, tokens = generate_answer(prompt)

        history.append({
            "user": message,
            "assistant": answer
        })

        sessions[session_id] = history[-5:]

        return jsonify({
            "reply": answer,
            "tokensUsed": tokens,
            "retrievedChunks": len(results)
        })

    except Exception as e:

        return jsonify({
            "error": "Server error",
            "message": str(e)
        }), 500


# ---------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)