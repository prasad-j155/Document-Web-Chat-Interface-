import io
from pypdf import PdfReader
import docx
from langchain_text_splitters import RecursiveCharacterTextSplitter

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Reads a PDF file from memory and extracts all text."""
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

def extract_text_from_docx(file_bytes: bytes) -> str:
    """Reads a Word document from memory and extracts all text."""
    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join([para.text for para in doc.paragraphs])

def clean_and_chunk_text(text: str) -> list[str]:
    """
    Cleans extra whitespace and splits the text into smaller, manageable pieces.
    We use an overlap so that if a sentence is cut in half, the context isn't lost.
    """
    # 1. Clean basic whitespace issues
    cleaned_text = " ".join(text.split())
    
    # 2. Define the chunking strategy
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,   # Roughly 200-250 words per chunk
        chunk_overlap=200, # 200 characters overlap between chunks
        length_function=len,
    )
    
    # 3. Split and return the chunks
    return splitter.split_text(cleaned_text)

def process_file(filename: str, file_bytes: bytes) -> list[str]:
    """Master function to handle routing based on file type."""
    if filename.endswith('.pdf'):
        text = extract_text_from_pdf(file_bytes)
    elif filename.endswith('.docx'):
        text = extract_text_from_docx(file_bytes)
    else:
        raise ValueError("Unsupported file type. Only PDF and DOCX are allowed.")
        
    chunks = clean_and_chunk_text(text)
    return chunks
