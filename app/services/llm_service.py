import time
from google import genai


class LLMService:
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash", temperature: float = 0.2):
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.temperature = temperature

    def generate(self, prompt: str):
        last_exc = None
        start = time.time()
        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config={"temperature": self.temperature},
                )
                latency_ms = int((time.time() - start) * 1000)
                tokens = 0
                usage = getattr(response, "usage_metadata", None)
                if usage and getattr(usage, "total_token_count", None) is not None:
                    tokens = int(usage.total_token_count)
                return response.text or "", tokens, latency_ms
            except Exception as exc:
                last_exc = exc
                msg = str(exc).lower()
                if "unavailable" in msg or "503" in msg or "high demand" in msg:
                    # Brief backoff for temporary capacity spikes.
                    if attempt < 2:
                        time.sleep(1.5 * (attempt + 1))
                        continue
                    raise RuntimeError("Model temporarily unavailable. Please try again in a moment.") from exc
                if "api key" in msg or "permission_denied" in msg or "unauthorized" in msg:
                    raise RuntimeError("Invalid API key") from exc
                if "timeout" in msg or "deadline" in msg:
                    raise RuntimeError("Request timeout") from exc
                if "rate" in msg or "429" in msg or "resource_exhausted" in msg:
                    raise RuntimeError("Rate limit exceeded") from exc
                raise RuntimeError(f"API failure: {exc}") from exc
        raise RuntimeError(f"API failure: {last_exc}")
