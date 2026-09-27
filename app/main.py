import os
import shutil
import tempfile

from pathlib import Path
from pathlib import PurePosixPath

from fastapi import (
    FastAPI,
    File,
    HTTPException,
    UploadFile
)

from fastapi.middleware.cors import (
    CORSMiddleware
)

from fastapi.staticfiles import (
    StaticFiles
)

from openai import OpenAI


from app.config import (
    MAX_UPLOAD_MB,
    UPLOAD_DIR
)

from app.models import (
    AskRequest,
    AskResponse,
    IngestResponse
)

from app.services.embeddings import (
    EmbeddingService
)

from app.services.llm import (
    LLMService
)

from app.services.vector_store import (
    VectorStore
)

from app.services.rag import (
    RAGService
)

from app.services.ingestion import (
    IngestionService
)


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="AI Technical Documentation & Codebase Assistant"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=[
        "http://localhost:8000"
    ],

    allow_credentials=False,

    allow_methods=[
        "GET",
        "POST"
    ],

    allow_headers=[
        "Content-Type"
    ]
)


# =========================================================
# OPENAI
# =========================================================

api_key = os.getenv(
    "OPENAI_API_KEY"
)


if not api_key:

    raise RuntimeError(
        "OPENAI_API_KEY is not set. "
        "Copy .env.example to .env and add your key."
    )


openai_client = OpenAI(
    api_key=api_key
)


# =========================================================
# SERVICES
# =========================================================

store = VectorStore()

embeddings = EmbeddingService(
    openai_client
)

llm = LLMService(
    openai_client
)

rag = RAGService(
    embeddings,
    store,
    llm
)

ingestion = IngestionService(
    embeddings,
    store
)


# =========================================================
# HEALTH
# =========================================================

@app.get("/api/health")
def health():

    return {

        "status": "ok",

        "indexed_chunks":
            store.count()
    }


# =========================================================
# SAMPLE PROJECT
# =========================================================

@app.post(
    "/api/index-folder",
    response_model=IngestResponse
)
def index_folder():

    # Clear previous knowledge
    store.clear()


    sample = Path(
        "data/sample_repo"
    )


    indexed_files, indexed_chunks = (
        ingestion.ingest_path(
            sample
        )
    )


    return IngestResponse(

        indexed_files=
            indexed_files,

        indexed_chunks=
            indexed_chunks,

        collection_count=
            store.count()
    )


# =========================================================
# UPLOAD
# =========================================================

@app.post(
    "/api/upload",
    response_model=IngestResponse
)
def upload(
    files: list[UploadFile] = File(...)
):

    # -----------------------------------------------------
    # File count limit
    # -----------------------------------------------------

    if len(files) > 100:

        raise HTTPException(
            status_code=400,
            detail="Too many files in one request."
        )


    # -----------------------------------------------------
    # Temporary upload directory
    # -----------------------------------------------------

    temp_root = Path(
        tempfile.mkdtemp(
            prefix="codebase_"
        )
    )


    try:

        total_bytes = 0


        # =================================================
        # SAVE UPLOADED FILES
        # =================================================

        for upload in files:

            raw_name = (
                upload.filename or ""
            )


            if not raw_name:

                continue


            # ---------------------------------------------
            # Normalize path separators
            # ---------------------------------------------

            normalized_name = (
                raw_name
                .replace("\\", "/")
            )


            # ---------------------------------------------
            # Use POSIX path for security
            # ---------------------------------------------

            relative_path = PurePosixPath(
                normalized_name
            )


            # ---------------------------------------------
            # Reject dangerous paths
            # ---------------------------------------------

            if (
                relative_path.is_absolute()
                or ".." in relative_path.parts
            ):

                raise HTTPException(

                    status_code=400,

                    detail=
                        "Invalid file path."
                )


            # ---------------------------------------------
            # Convert to local Path
            # ---------------------------------------------

            destination = (
                temp_root
                / Path(*relative_path.parts)
            )


            destination.parent.mkdir(
                parents=True,
                exist_ok=True
            )


            # ---------------------------------------------
            # Read file
            # ---------------------------------------------

            data = upload.file.read(
                MAX_UPLOAD_MB
                * 1024
                * 1024
                + 1
            )


            total_bytes += len(data)


            # ---------------------------------------------
            # Total size limit
            # ---------------------------------------------

            if (
                total_bytes
                >
                MAX_UPLOAD_MB
                * 1024
                * 1024
            ):

                raise HTTPException(

                    status_code=413,

                    detail=
                        "Upload exceeds size limit."
                )


            destination.write_bytes(
                data
            )


        # =================================================
        # CLEAR OLD KNOWLEDGE
        # =================================================

        store.clear()


        # =================================================
        # INDEX NEW PROJECT
        # =================================================

        indexed_files, indexed_chunks = (
            ingestion.ingest_path(
                temp_root
            )
        )


        # =================================================
        # RESPONSE
        # =================================================

        return IngestResponse(

            indexed_files=
                indexed_files,

            indexed_chunks=
                indexed_chunks,

            collection_count=
                store.count()
        )


    finally:

        shutil.rmtree(
            temp_root,
            ignore_errors=True
        )


# =========================================================
# ASK
# =========================================================

@app.post(
    "/api/ask",
    response_model=AskResponse
)
def ask(
    request: AskRequest
):

    answer, sources = (
        rag.ask(
            request.question,
            request.top_k
        )
    )


    return AskResponse(

        answer=answer,

        sources=sources
    )


# =========================================================
# FRONTEND
# =========================================================

app.mount(
    "/",
    StaticFiles(
        directory="frontend",
        html=True
    ),
    name="frontend"
)