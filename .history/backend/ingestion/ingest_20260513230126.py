from ingestion.loader import load_pdf
from ingestion.chunker import chunk_documents
from vectorstore.chroma_store import vectorstore

PDF_PATH = "dataiabetes_WHO_report.pdf.pdf"


def ingest():
    print("Loading PDF...")
    docs = load_pdf(PDF_PATH)

    print("Chunking...")
    chunks = chunk_documents(docs)

    print("Embedding + storing in Chroma...")
    vectorstore.add_documents(chunks)

    print("DONE ✔ RAG database ready")


if __name__ == "__main__":
    ingest()