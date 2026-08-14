from app.rag.ingest import chunk_text


def test_chunk_text_keeps_short_document_as_one_chunk():
    text = "# Title\n\nShort paragraph."
    chunks = chunk_text(text, size=700, overlap=100)
    assert len(chunks) == 1
    assert "Short paragraph." in chunks[0]


def test_chunk_text_splits_long_document():
    paragraph = "word " * 400  # ~2000 chars, well over the chunk size
    chunks = chunk_text(paragraph, size=700, overlap=100)
    assert len(chunks) > 1
    assert all(len(c) <= 700 for c in chunks)


def test_chunk_text_groups_multiple_short_paragraphs():
    text = "\n\n".join(["Paragraph one.", "Paragraph two.", "Paragraph three."])
    chunks = chunk_text(text, size=700, overlap=100)
    assert len(chunks) == 1
    assert "Paragraph one." in chunks[0] and "Paragraph three." in chunks[0]
