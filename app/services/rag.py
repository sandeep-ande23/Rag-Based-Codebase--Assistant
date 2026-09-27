from app.services.embeddings import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.llm import LLMService
from app.models import Source


class RAGService:

    def __init__(
        self,
        embeddings: EmbeddingService,
        store: VectorStore,
        llm: LLMService
    ):
        self.embeddings = embeddings
        self.store = store
        self.llm = llm

    def ask(self, question: str, top_k: int):
        query_embedding = self.embeddings.embed_query(question)

        results = self.store.search(
            query_embedding,
            top_k
        )

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        ids = results.get("ids", [[]])[0]

        if not docs:
            return (
                "I could not find relevant information in the indexed project.",
                []
            )

        context_parts = []
        sources = []

        for doc, meta, chunk_id in zip(
            docs,
            metas,
            ids
        ):
            path = meta["path"]

            start = int(meta.get("start_line", 1))
            end = int(meta.get("end_line", start))

            page = int(meta.get("page", 0))

            # PDF source
            if path.lower().endswith(".pdf") and page > 0:

                source_label = f"{path} — Page {page}"

                context_parts.append(
                    f"Source: {source_label}\n{doc}"
                )

                sources.append(
                    Source(
                        path=path,
                        start_line=start,
                        end_line=end,
                        chunk_id=chunk_id,
                        page=page
                    )
                )

            # Normal file source
            else:

                source_label = f"{path}:{start}-{end}"

                context_parts.append(
                    f"Source: {source_label}\n{doc}"
                )

                sources.append(
                    Source(
                        path=path,
                        start_line=start,
                        end_line=end,
                        chunk_id=chunk_id
                    )
                )

        answer = self.llm.answer(
            question,
            "\n\n---\n\n".join(context_parts)
        )

        return answer, sources