from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_ask_returns_answer_and_sources(monkeypatch):
    class FakeRAGService:
        def ask(self, question, top_k=5):
            return (
    "The database connection is created in database.py.",
    [
        {
            "chunk_id": "chunk-001",
            "path": "services/database.py",
            "start_line": 1,
            "end_line": 10,
        }
    ],
)

    monkeypatch.setattr(
        "app.main.rag",
        FakeRAGService(),
    )

    response = client.post(
        "/api/ask",
        json={
            "question": "Where is the database connection created?",
            "top_k": 5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == "The database connection is created in database.py."
    assert len(data["sources"]) == 1
    assert data["sources"][0]["path"] == "services/database.py"

def test_upload_indexes_file(monkeypatch):
    class FakeStore:
        def __init__(self):
            self.clear_called = False

        def clear(self):
            self.clear_called = True

        def count(self):
            return 1

    class FakeIngestion:
        def ingest_path(self, path):
            assert path.exists()
            assert (path / "main.py").exists()

            return 1, 1

    fake_store = FakeStore()
    fake_ingestion = FakeIngestion()

    monkeypatch.setattr(
        "app.main.store",
        fake_store,
    )

    monkeypatch.setattr(
        "app.main.ingestion",
        fake_ingestion,
    )

    response = client.post(
        "/api/upload",
        files={
            "files": (
                "main.py",
                "print('hello')",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["indexed_files"] == 1
    assert data["indexed_chunks"] == 1
    assert data["collection_count"] == 1
    assert fake_store.clear_called is True 

def test_upload_rejects_dangerous_path():
    response = client.post(
        "/api/upload",
        files={
            "files": (
                "../secret.txt",
                "top secret",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid file path."    

def test_upload_rejects_too_many_files():
    files = [
        (
            "files",
            (
                f"file_{i}.py",
                "print('hello')",
                "text/plain",
            ),
        )
        for i in range(101)
    ]

    response = client.post(
        "/api/upload",
        files=files,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Too many files in one request."       

def test_upload_rejects_excessive_total_size(monkeypatch):
    monkeypatch.setattr(
        "app.main.MAX_UPLOAD_MB",
        1,
    )

    response = client.post(
        "/api/upload",
        files={
            "files": (
                "large.py",
                "x" * (1024 * 1024 + 1),
                "text/plain",
            )
        },
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "Upload exceeds size limit."    

def test_index_folder(monkeypatch, tmp_path):
    sample_repo = tmp_path / "sample_repo"
    sample_repo.mkdir()

    (sample_repo / "main.py").write_text(
        "print('hello')",
        encoding="utf-8",
    )

    class FakeStore:
        def __init__(self):
            self.clear_called = False

        def clear(self):
            self.clear_called = True

        def count(self):
            return 3

    class FakeIngestion:
        def ingest_path(self, path):
            assert path == sample_repo
            return 1, 3

    fake_store = FakeStore()
    fake_ingestion = FakeIngestion()

    monkeypatch.setattr(
        "app.main.store",
        fake_store,
    )

    monkeypatch.setattr(
        "app.main.ingestion",
        fake_ingestion,
    )

    monkeypatch.setattr(
        "app.main.Path",
        lambda _: sample_repo,
    )

    response = client.post("/api/index-folder")

    assert response.status_code == 200

    data = response.json()

    assert data["indexed_files"] == 1
    assert data["indexed_chunks"] == 3
    assert data["collection_count"] == 3
    assert fake_store.clear_called is True    

def test_upload_clears_previous_knowledge(monkeypatch):
    class FakeStore:
        def __init__(self):
            self.clear_calls = 0

        def clear(self):
            self.clear_calls += 1

        def count(self):
            return 2

    class FakeIngestion:
        def ingest_path(self, path):
            assert path.exists()
            return 1, 2

    fake_store = FakeStore()
    fake_ingestion = FakeIngestion()

    monkeypatch.setattr(
        "app.main.store",
        fake_store,
    )

    monkeypatch.setattr(
        "app.main.ingestion",
        fake_ingestion,
    )

    response = client.post(
        "/api/upload",
        files={
            "files": (
                "project.py",
                "print('new project')",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200
    assert fake_store.clear_calls == 1

    data = response.json()

    assert data["indexed_files"] == 1
    assert data["indexed_chunks"] == 2
    assert data["collection_count"] == 2    