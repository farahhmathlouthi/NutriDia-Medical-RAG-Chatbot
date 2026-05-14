from langchain_community.document_loaders import PyPDFLoader

#It reads raw documents (PDFs) and converts them into text chunks (LangChain Document objects).
def load_pdf(file_path: str):
    loader = PyPDFLoader(file_path)
    return loader.load()