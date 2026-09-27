# AI Technical Documentation & Codebase Assistant

A RAG-based assistant that indexes source code and technical documentation, retrieves relevant evidence with vector search, and generates grounded answers with source paths and line ranges.

## Why this project is portfolio-worthy

This is designed as an engineering project rather than a generic chat-with-PDF demo. It demonstrates:

- repository/file ingestion
- code-aware and documentation-aware chunking
- OpenAI embeddings
- ChromaDB vector search
- retrieval-augmented generation
- source/line metadata
- FastAPI
- frontend integration
- upload validation
- Docker
- automated tests
- GitHub Actions CI
- retrieval evaluation with Recall@K

## Architecture

```text
Repository / Documents
        |
        v
File discovery + filtering
        |
        v
Code/doc-aware chunking
        |
        v
OpenAI text embeddings
        |
        v
ChromaDB (cosine similarity)
        |
        +-------------------+
        |                   |
        v                   v
User question         Top-K retrieval
        |                   |
        v                   |
Question embedding         |
        +---------> Context
                         |
                         v
                    OpenAI LLM
                         |
                         v
                 Answer + sources
```

## Run locally

1. Create a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and set `OPENAI_API_KEY`.
4. Start:

```bash
uvicorn app.main:app --reload
```

5. Open `http://localhost:8000`.
6. Click **Index Sample Repository**.
7. Ask questions such as:
   - Where is the database engine created?
   - How does the order service access the database?
   - What does `validate_token` do?
   - How is deployment described?

## Retrieval evaluation

The repository includes a small labeled evaluation set in `evaluation/questions.json`.

After indexing the sample repository:

```bash
python evaluation/run_eval.py
```

The script reports whether the expected source appears in Top-K retrieval and calculates Recall@K.

## Docker

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

## Current limitations

- Authentication is intentionally omitted for this portfolio demo.
- Uploads are capped by a simple request-level size limit.
- Code-aware chunking uses lightweight structural boundaries rather than a full language parser for every supported language.
- Production deployment would require stronger isolation, authentication/authorization, rate limiting, observability, secret management, and more extensive evaluation data.

## Suggested next improvements

- Git repository URL ingestion
- AST/tree-sitter based chunking
- reranking
- hybrid keyword + vector retrieval
- streaming answers
- authentication
- richer evaluation with MRR and answer faithfulness
- cloud deployment
