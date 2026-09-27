from app.services.chunking import chunk_document

def test_chunks_respect_hard_limit():
    text = "A" * 5000
    chunks = chunk_document(text, "big.txt", size=500, overlap=50)
    assert chunks
    assert all(len(c.text) <= 500 for c in chunks)

def test_code_chunks_have_line_metadata():
    text = "def a():\n    return 1\n\n\ndef b():\n    return 2\n"
    chunks = chunk_document(text, "x.py", size=100, overlap=10)
    assert chunks
    assert all(c.start_line >= 1 and c.end_line >= c.start_line for c in chunks)

def test_overlap_does_not_break_limit():
    text = "\n\n".join(["paragraph " + ("x" * 200) for _ in range(20)])
    chunks = chunk_document(text, "x.md", size=250, overlap=50)
    assert all(len(c.text) <= 250 for c in chunks)
