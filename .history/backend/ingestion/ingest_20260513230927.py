from loader import load_pdf
from vectorstore.chroma_store import VectorStore
from chunker import chunk_documents

PDF_PATH = "data/diabetes/diabetes_WHO_report.pdf.pdf"


def ingest():
    print("Loading PDF...")
    docs = load_pdf(PDF_PATH)

    print("Chunking...")
    chunks = chunk_documents(docs)

    print("Embedding + storing in Chroma...")
    Vectorstore.add_documents(chunks)

    print("DONE ✔ RAG database ready")


if __name__ == "__main__":
    ingest()