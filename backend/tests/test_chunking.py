from app.ingestion.parsers import clean_text, chunk_text

def test_clean_and_chunk():
    text = "Refund Policy\n\nCustomers can request a refund.\n\nSupport Policy\n\nSupport is available weekdays."
    cleaned = clean_text(text)
    chunks = chunk_text(cleaned, chunk_size=80, overlap=10)
    assert "Refund Policy" in cleaned
    assert chunks
    assert all(c.strip() for c in chunks)
