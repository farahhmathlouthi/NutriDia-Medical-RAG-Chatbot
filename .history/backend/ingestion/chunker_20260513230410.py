from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import settings


def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        #overlap keeps meaning connected between chunks, which is crucial for retrieval quality.
        chunk_overlap=settings.CHUNK_OVERLAP
    )

    return splitter.split_documents(documents)