from openai import OpenAI
from app.config import LLM_MODEL

class LLMService:
    def __init__(self, client: OpenAI):
        self.client = client

    def answer(self, question: str, context: str) -> str:
        instructions = (
            "You are a technical documentation and codebase assistant. "
            "Answer only from the supplied context. "
            "If the context does not contain enough evidence, say so clearly. "
            "Do not invent files, functions, line numbers, or behavior."
        )
        response = self.client.responses.create(
            model=LLM_MODEL,
            instructions=instructions,
            input=f"Context:\n{context}\n\nQuestion:\n{question}",
            max_output_tokens=2048,
        )
        return response.output_text
