import os
from openai import OpenAI
from app.config import EMBEDDING_MODEL

class EmbeddingService:
    def __init__(self, client: OpenAI = None):
        """
        Initializes the OpenAI client. Reads OPENAI_BASE_URL if set in .env
        to automatically support alternative providers like OpenRouter.
        """
        if client:
            self.client = client
        else:
            base_url = os.getenv("OPENAI_BASE_URL")
            api_key = os.getenv("OPENAI_API_KEY")
            
            # Pass base_url only if defined in environment variables
            if base_url:
                self.client = OpenAI(api_key=api_key, base_url=base_url)
            else:
                self.client = OpenAI(api_key=api_key)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts
        )
        return [item.embedding for item in response.data]

    def embed_query(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=[text]
        )
        return response.data[0].embedding