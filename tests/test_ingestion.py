from pathlib import Path

from app.services.ingestion import IngestionService


class FakeEmbeddings:
    def __init__(self):
        self.calls = []

    def embed_documents(self, texts):
        self.calls.append(texts)

        # Return one deterministic vector per chunk.
        return [[1.0, 0.0, 0.0] for _ in texts]


class FakeStore:
    def __init__(self):
        self.deleted_paths = []
        self.added_chunks = []
        self.added_embeddings = []

    def delete_path(self, path):
        self.deleted_paths.append(path)

    def add_chunks(self, chunks, embeddings):
        self.added_chunks.extend(chunks)
        self.added_embeddings.extend(embeddings)


def test_ingest_indexes_supported_files(tmp_path):
    (tmp_path / "main.py").write_text(
        "def hello():\n"
        "    return 'hello'\n"
    )

    (tmp_path / "README.md").write_text(
        "# Test Project\n"
        "This is a test repository.\n"
    )

    embeddings = FakeEmbeddings()
    store = FakeStore()

    ingestion = IngestionService(embeddings, store)

    indexed_files, indexed_chunks = ingestion.ingest_path(tmp_path)

    assert indexed_files == 2
    assert indexed_chunks > 0

    assert len(store.added_chunks) == indexed_chunks
    assert len(store.added_embeddings) == indexed_chunks
    assert len(embeddings.calls) == 2


def test_ingest_preserves_relative_paths(tmp_path):
    services = tmp_path / "services"
    services.mkdir()

    file = services / "database.py"

    file.write_text(
        "def connect():\n"
        "    return 'connected'\n"
    )

    embeddings = FakeEmbeddings()
    store = FakeStore()

    ingestion = IngestionService(embeddings, store)

    ingestion.ingest_path(tmp_path)

    paths = {chunk.path for chunk in store.added_chunks}

    assert str(Path("services") / "database.py") in paths


def test_ingest_ignores_unsupported_files(tmp_path):
    (tmp_path / "main.py").write_text(
        "print('hello')"
    )

    (tmp_path / "image.exe").write_text(
        "not a supported source file"
    )

    embeddings = FakeEmbeddings()
    store = FakeStore()

    ingestion = IngestionService(embeddings, store)

    indexed_files, indexed_chunks = ingestion.ingest_path(tmp_path)

    assert indexed_files == 1
    assert indexed_chunks > 0

    paths = {chunk.path for chunk in store.added_chunks}

    assert "main.py" in paths
    assert "image.exe" not in paths


def test_empty_files_are_not_indexed(tmp_path):
    (tmp_path / "empty.py").write_text("")
    (tmp_path / "main.py").write_text(
        "print('hello')"
    )

    embeddings = FakeEmbeddings()
    store = FakeStore()

    ingestion = IngestionService(embeddings, store)

    indexed_files, indexed_chunks = ingestion.ingest_path(tmp_path)

    assert indexed_files == 2
    assert indexed_chunks > 0

    paths = {chunk.path for chunk in store.added_chunks}

    assert "empty.py" not in paths
    assert "main.py" in paths


def test_existing_path_is_deleted_before_reindexing(tmp_path):
    (tmp_path / "main.py").write_text(
        "print('updated version')"
    )

    embeddings = FakeEmbeddings()
    store = FakeStore()

    ingestion = IngestionService(embeddings, store)

    ingestion.ingest_path(tmp_path)

    assert "main.py" in store.deleted_paths