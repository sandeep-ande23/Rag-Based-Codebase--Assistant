from app.services.chunking import Chunk
from app.services.vector_store import VectorStore


def make_chunk(chunk_id, path, text):
    return Chunk(
        chunk_id=chunk_id,
        path=path,
        text=text,
        start_line=1,
        end_line=5,
        page=None,
    )


def test_add_chunks_and_count(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.services.vector_store.CHROMA_DIR",
        tmp_path / "chroma",
    )

    store = VectorStore()

    chunks = [
        make_chunk(
            "chunk-1",
            "file_a.py",
            "database connection",
        ),
        make_chunk(
            "chunk-2",
            "file_a.py",
            "database query",
        ),
    ]

    embeddings = [
        [1.0, 0.0, 0.0],
        [0.9, 0.1, 0.0],
    ]

    store.add_chunks(chunks, embeddings)

    assert store.count() == 2


def test_delete_path_removes_only_that_file(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.services.vector_store.CHROMA_DIR",
        tmp_path / "chroma",
    )

    store = VectorStore()

    chunks = [
        make_chunk("chunk-a", "file_a.py", "database connection"),
        make_chunk("chunk-b", "file_b.py", "authentication"),
    ]

    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ]

    store.add_chunks(chunks, embeddings)

    assert store.count() == 2

    store.delete_path("file_a.py")

    assert store.count() == 1


def test_clear_removes_entire_knowledge_base(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.services.vector_store.CHROMA_DIR",
        tmp_path / "chroma",
    )

    store = VectorStore()

    chunks = [
        make_chunk("chunk-a", "project_a.py", "project A"),
        make_chunk("chunk-b", "project_b.py", "project B"),
    ]

    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ]

    store.add_chunks(chunks, embeddings)

    assert store.count() == 2

    store.clear()

    assert store.count() == 0


def test_search_returns_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.services.vector_store.CHROMA_DIR",
        tmp_path / "chroma",
    )

    store = VectorStore()

    chunk = make_chunk(
        "chunk-1",
        "services/database.py",
        "database connection",
    )

    store.add_chunks(
        [chunk],
        [[1.0, 0.0, 0.0]],
    )

    result = store.search(
        query_embedding=[1.0, 0.0, 0.0],
        top_k=1,
    )

    assert result["documents"][0][0] == "database connection"
    assert result["metadatas"][0][0]["path"] == "services/database.py"
    assert result["metadatas"][0][0]["start_line"] == 1
    assert result["metadatas"][0][0]["end_line"] == 5