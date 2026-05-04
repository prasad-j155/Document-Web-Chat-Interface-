# app/services/retriever.py
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# 1. Initialize the embedding model
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 2. Define where to save the database on your local hard drive
DB_DIR = os.path.join(os.getcwd(), "chroma_db")

def get_vector_store():
    """Initializes and returns the ChromaDB connection."""
    return Chroma(
        persist_directory=DB_DIR, 
        embedding_function=embeddings
    )

def store_chunks_in_db(session_id: str, chunks: list[str]):
    """
    Wraps text chunks into LangChain Document objects, attaches the session_id
    as metadata, and saves them to ChromaDB.
    """
    vector_store = get_vector_store()
    
    documents = []
    for chunk in chunks:
        doc = Document(
            page_content=chunk,
            metadata={"session_id": session_id}
        )
        documents.append(doc)
    
    vector_store.add_documents(documents)
    return True

def search_documents(session_id: str, query: str, top_k: int = 3) -> list[str]:
    """Searches the database for relevant chunks."""
    vector_store = get_vector_store()
    
    results = vector_store.similarity_search(
        query=query,
        k=top_k,
        filter={"session_id": session_id}
    )
    
    return [doc.page_content for doc in results]