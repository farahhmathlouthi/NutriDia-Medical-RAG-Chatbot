import os
from ingestion.loader import load_pdf
from ingestion.chunker import chunk_documents
from vectorstore.chroma_store import vectorstore


def ingest_file(file_path: str):
    """Ingest a single PDF file into the vector store."""
    print(f"Loading: {file_path}")
    docs = load_pdf(file_path)

    print(f"Chunking {len(docs)} pages...")
    chunks = chunk_documents(docs)

    print(f"Embedding {len(chunks)} chunks into ChromaDB...")
    vectorstore.add_documents(chunks)

    print(f"Done ✔ — {file_path} ingested ({len(chunks)} chunks)")
    return len(chunks)


def ingest_directory(directory: str):
    """Ingest all PDFs in a directory."""
    pdf_files = [f for f in os.listdir(directory) if f.endswith(".pdf")]

    if not pdf_files:
        print(f"No PDF files found in {directory}")
        return

    for filename in pdf_files:
        file_path = os.path.join(directory, filename)
        ingest_file(file_path)

    print(f"\nAll done — {len(pdf_files)} file(s) ingested.")


if __name__ == "__main__":
    # Place your PDFs inside data/pdfs/ and run: python -m ingestion.ingest
    DATA_DIR = "data/pdfs"
    os.makedirs(DATA_DIR, exist_ok=True)
    ingest_directory(DATA_DIR)
