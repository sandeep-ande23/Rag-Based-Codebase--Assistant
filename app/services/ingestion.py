from pathlib import Path

from app.services.loaders import (
    iter_supported_files,
    load_file
)

from app.services.chunking import (
    chunk_document
)

from app.services.embeddings import (
    EmbeddingService
)

from app.services.vector_store import (
    VectorStore
)


class IngestionService:

    def __init__(
        self,
        embeddings: EmbeddingService,
        store: VectorStore
    ):

        self.embeddings = embeddings

        self.store = store


    # =====================================================
    # INGEST PATH
    # =====================================================

    def ingest_path(
        self,
        root: Path
    ):

        root = root.resolve()


        files = list(
            iter_supported_files(root)
        )


        total_chunks = 0


        for path in files:

            path = path.resolve()


            # ---------------------------------------------
            # Relative path
            # ---------------------------------------------

            relative = (

                str(
                    path.relative_to(root)
                )

                if root.is_dir()

                else path.name
            )


            # ---------------------------------------------
            # Load file
            # ---------------------------------------------

            text = load_file(path)


            if not text.strip():

                continue


            # ---------------------------------------------
            # Create chunks
            # ---------------------------------------------

            chunks = chunk_document(
                text,
                relative
            )


            if not chunks:

                continue


            # ---------------------------------------------
            # Delete existing version
            # ---------------------------------------------

            self.store.delete_path(
                relative
            )


            # ---------------------------------------------
            # Create embeddings
            # ---------------------------------------------

            vectors = (
                self.embeddings
                .embed_documents(
                    [
                        c.text
                        for c in chunks
                    ]
                )
            )


            # ---------------------------------------------
            # Store
            # ---------------------------------------------

            self.store.add_chunks(
                chunks,
                vectors
            )


            total_chunks += len(chunks)


        return (
            len(files),
            total_chunks
        )