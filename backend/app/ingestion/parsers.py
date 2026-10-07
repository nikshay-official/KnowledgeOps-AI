from pathlib import Path
from pypdf import PdfReader
from docx import Document as DocxDocument

SUPPORTED = {".txt", ".pdf", ".docx"}

def extract_text(path: Path) -> tuple[str, list[dict]]:
    suffix = path.suffix.lower()
    if suffix == ".txt":
        text = path.read_text(encoding="utf-8", errors="ignore")
        return text, [{"page": None, "text": text}]
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        pages = [{"page": i, "text": page.extract_text() or ""} for i, page in enumerate(reader.pages, 1)]
        return "\n\n".join(p["text"] for p in pages), pages
    if suffix == ".docx":
        doc = DocxDocument(str(path))
        text = "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return text, [{"page": None, "text": text}]
    raise ValueError(f"Unsupported file type: {suffix}")

def clean_text(text: str) -> str:
    lines = [" ".join(line.split()) for line in text.replace("\r", "").splitlines()]
    blocks, current = [], []
    for line in lines:
        if line:
            current.append(line)
        elif current:
            blocks.append(" ".join(current)); current = []
    if current: blocks.append(" ".join(current))
    return "\n\n".join(blocks)

def chunk_text(text: str, chunk_size: int = 900, overlap: int = 120) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, buffer = [], ""
    for paragraph in paragraphs:
        candidate = f"{buffer}\n\n{paragraph}" if buffer else paragraph
        if len(candidate) <= chunk_size:
            buffer = candidate
        else:
            if buffer: chunks.append(buffer.strip())
            if len(paragraph) <= chunk_size:
                tail = chunks[-1][-overlap:] if chunks and overlap else ""
                buffer = f"{tail} {paragraph}".strip() if tail else paragraph
            else:
                start = 0
                while start < len(paragraph):
                    end = min(start + chunk_size, len(paragraph)); piece = paragraph[start:end].strip()
                    if piece: chunks.append(piece)
                    start = max(end - overlap, start + 1)
                buffer = ""
    if buffer: chunks.append(buffer.strip())
    return chunks
