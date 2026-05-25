PROMPT_TEMPLATE = """You are a helpful AI assistant.

Use ONLY the provided context.

If information is unavailable in the context,
say you do not know.

Context:
{retrieved_context}

Conversation History:
{history}

Question:
{user_question}

Answer:
"""

FALLBACK_RESPONSE = "I could not find enough information in the knowledge base to answer this question."

RELATED_FALLBACK_PROMPT = """You are a helpful AI assistant.

The user question may not have an exact answer in the knowledge base.
Use the related context below to provide best-effort guidance.

Rules:
- Be transparent that this is a related/general answer.
- Do not claim exact policy details unless clearly present.
- Keep the response concise and practical.

Related Context:
{retrieved_context}

User Question:
{user_question}

Answer:
"""
