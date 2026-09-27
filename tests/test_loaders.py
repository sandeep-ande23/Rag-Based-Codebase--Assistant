from pathlib import Path

from app.services.loaders import (
    iter_supported_files,
    is_code_file,
    line_number_at,
    load_file,
)


def test_supported_files_are_discovered(tmp_path):
    (tmp_path / "main.py").write_text("print('hello')")
    (tmp_path / "README.md").write_text("# README")
    (tmp_path / "data.csv").write_text("a,b\n1,2")

    files = list(iter_supported_files(tmp_path))

    names = {path.name for path in files}

    assert "main.py" in names
    assert "README.md" in names
    assert "data.csv" not in names


def test_ignored_directories_are_skipped(tmp_path):
    ignored = tmp_path / ".git"
    ignored.mkdir()

    (ignored / "config.py").write_text("secret")
    (tmp_path / "main.py").write_text("print('hello')")

    files = list(iter_supported_files(tmp_path))

    names = {path.name for path in files}

    assert "main.py" in names
    assert "config.py" not in names


def test_dockerfile_is_supported(tmp_path):
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("FROM python:3.12")

    files = list(iter_supported_files(tmp_path))

    assert dockerfile in files


def test_load_text_file(tmp_path):
    file = tmp_path / "example.py"
    file.write_text("line one\nline two\nline three")

    result = load_file(file)

    assert result == "line one\nline two\nline three"


def test_line_number_at():
    text = "first\nsecond\nthird"

    assert line_number_at(text, 0) == 1
    assert line_number_at(text, 6) == 2
    assert line_number_at(text, 13) == 3


def test_is_code_file():
    assert is_code_file(Path("main.py"))
    assert is_code_file(Path("app.js"))
    assert is_code_file(Path("schema.sql"))

    assert not is_code_file(Path("README.md"))
    assert not is_code_file(Path("notes.txt"))