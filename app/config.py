from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = Path(os.getenv("CHROMA_DIR", BASE_DIR / "chroma_db"))
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "data" / "uploads"))

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-5.6-luna")
TOP_K = int(os.getenv("TOP_K", "5"))
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "20"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1200"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "codebase_assistant")

ALLOWED_EXTENSIONS = {
    # Programming languages
    ".py",
    ".js",
    ".ts",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".hpp",

    # Database / SQL
    ".sql",

    # Web
    ".html",
    ".css",

    # Documentation
    ".md",
    ".txt",
    ".pdf",

    # Configuration / data
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".xml",
}

IGNORED_DIRS = {
    ".git", ".venv", "venv", "env", "node_modules", "__pycache__",
    ".pytest_cache", "dist", "build", ".idea", ".vscode", "chroma_db"
}

for directory in (CHROMA_DIR, UPLOAD_DIR):
    directory.mkdir(parents=True, exist_ok=True)
