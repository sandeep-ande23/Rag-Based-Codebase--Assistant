import chromadb

from app.config import CHROMA_DIR, COLLECTION_NAME
from app.services.chunking import Chunk


class VectorStore:

    def __init__(self):

        client = chromadb.PersistentClient(
            path=str(CHROMA_DIR)
        )

        self.collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={
                "hnsw:space": "cosine"
            }
        )


    # =====================================================
    # DELETE ONE PATH
    # =====================================================

    def delete_path(self, path: str):

        self.collection.delete(
            where={
                "path": path
            }
        )


    # =====================================================
    # CLEAR ENTIRE KNOWLEDGE BASE
    # =====================================================

    def clear(self):

        ids = self.collection.get(
            include=[]
        ).get("ids", [])


        if ids:

            self.collection.delete(
                ids=ids
            )


    # =====================================================
    # ADD CHUNKS
    # =====================================================

    def add_chunks(
        self,
        chunks: list[Chunk],
        embeddings: list[list[float]]
    ):

        if not chunks:
            return


        self.collection.upsert(

            ids=[
                c.chunk_id
                for c in chunks
            ],

            documents=[
                c.text
                for c in chunks
            ],

            embeddings=embeddings,

            metadatas=[

                {
                    "path": c.path,

                    "start_line":
                        c.start_line,

                    "end_line":
                        c.end_line,

                    "page":
                        c.page
                        if c.page is not None
                        else 0
                }

                for c in chunks
            ]
        )


    # =====================================================
    # SEARCH
    # =====================================================

    def search(
        self,
        query_embedding: list[float],
        top_k: int
    ):

        return self.collection.query(

            query_embeddings=[
                query_embedding
            ],

            n_results=top_k,

            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )


    # =====================================================
    # COUNT
    # =====================================================

    def count(self) -> int:

        return self.collection.count()