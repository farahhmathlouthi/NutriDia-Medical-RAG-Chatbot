from langchain.text_splitter import  
from config.settings import settings


def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP
    )

    return splitter.split_documents(documents)