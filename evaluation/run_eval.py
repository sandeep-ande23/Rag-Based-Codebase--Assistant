"""
Simple retrieval evaluation.

This evaluates whether the expected source path appears in Top-K retrieval.
Run after indexing data/sample_repo.
"""
import json
from openai import OpenAI
from app.config import TOP_K
from app.services.embeddings import EmbeddingService
from app.services.vector_store import VectorStore

def main():
    questions = json.load(open("evaluation/questions.json", encoding="utf-8"))
    client = OpenAI()
    embeddings = EmbeddingService(client)
    store = VectorStore()

    hits = 0
    for item in questions:
        q = item["question"]
        expected = item["expected_path"]
        vector = embeddings.embed_query(q)
        result = store.search(vector, TOP_K)
        paths = [m["path"].replace("\\", "/") for m in result["metadatas"][0]]
        expected = item["expected_path"].replace("\\", "/")

        hit = expected in paths
        hits += int(hit)
        print(f"{'HIT ' if hit else 'MISS'} {q} -> {paths}")

    score = hits / len(questions) if questions else 0
    print(f"\nRecall@{TOP_K}: {score:.2%}")

if __name__ == "__main__":
    main()
