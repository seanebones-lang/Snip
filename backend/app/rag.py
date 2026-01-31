"""
RAG (Retrieval Augmented Generation) Pipeline
Document processing, embedding, and retrieval
"""
import os
from typing import List, Optional
from uuid import UUID
import hashlib

# Document processing
from pypdf import PdfReader
from docx import Document as DocxDocument

# Embeddings and vector store
import chromadb
from chromadb.config import Settings as ChromaSettings

from .config import get_settings

settings = get_settings()

# Initialize ChromaDB
chroma_client = chromadb.Client(ChromaSettings(
    chroma_db_impl="duckdb+parquet",
    persist_directory=settings.chroma_persist_directory,
    anonymized_telemetry=False
))


def get_collection_name(client_id: UUID) -> str:
    """Get unique collection name for a client"""
    return f"client_{str(client_id).replace('-', '_')}"


def extract_text_from_pdf(content: bytes) -> str:
    """Extract text from PDF file with error handling"""
    try:
        import io
        reader = PdfReader(io.BytesIO(content))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip() or ""
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {e}")


def extract_text_from_docx(content: bytes) -> str:
    """Extract text from DOCX file with error handling"""
    try:
        import io
        doc = DocxDocument(io.BytesIO(content))
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n".join(paragraphs) or ""
    except Exception as e:
        raise ValueError(f"Failed to extract text from DOCX: {e}")


def extract_text_from_txt(content: bytes) -> str:
    """Extract text from TXT file"""
    return content.decode('utf-8', errors='ignore')


def extract_text_from_markdown(content: bytes) -> str:
    """Extract text from Markdown file"""
    text = content.decode('utf-8', errors='ignore')
    # Remove markdown syntax while preserving text
    import re
    # Remove headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic markers
    text = re.sub(r'\*\*|\*|__|_', '', text)
    # Remove links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove code blocks but keep content
    text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # Remove images
    text = re.sub(r'!\[[^\]]*\]\([^\)]+\)', '', text)
    return text


def extract_text_from_html(content: bytes) -> str:
    """Extract text from HTML file"""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        # Get text and clean up whitespace
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        return text
    except ImportError:
        # Fallback to simple regex if BeautifulSoup not available
        import re
        text = content.decode('utf-8', errors='ignore')
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


def extract_text_from_csv(content: bytes) -> str:
    """Extract text from CSV file"""
    try:
        import csv
        import io
        text_lines = []
        reader = csv.reader(io.StringIO(content.decode('utf-8', errors='ignore')))
        for row in reader:
            # Combine row into readable text
            row_text = ' | '.join(cell.strip() for cell in row if cell.strip())
            if row_text:
                text_lines.append(row_text)
        return '\n'.join(text_lines)
    except Exception:
        # Fallback to simple split
        text = content.decode('utf-8', errors='ignore')
        return text.replace(',', ' | ').replace('\n', ' ')


def extract_text_from_excel(content: bytes) -> str:
    """Extract text from Excel file (XLSX/XLS)"""
    try:
        import pandas as pd
        import io
        # Try reading as Excel
        df = pd.read_excel(io.BytesIO(content))
        # Convert to text representation
        text_lines = []
        for idx, row in df.iterrows():
            row_text = ' | '.join(str(val) for val in row.values if pd.notna(val) and str(val).strip())
            if row_text:
                text_lines.append(f"Row {idx + 1}: {row_text}")
        return '\n'.join(text_lines)
    except ImportError:
        raise ValueError("pandas and openpyxl required for Excel support. Install with: pip install pandas openpyxl")
    except Exception as e:
        raise ValueError(f"Failed to extract text from Excel: {e}")


def extract_text(content: bytes, file_type: str) -> str:
    """Extract text from file based on type - supports multiple formats"""
    extractors = {
        'pdf': extract_text_from_pdf,
        'docx': extract_text_from_docx,
        'txt': extract_text_from_txt,
        'md': extract_text_from_markdown,
        'markdown': extract_text_from_markdown,
        'html': extract_text_from_html,
        'htm': extract_text_from_html,
        'csv': extract_text_from_csv,
        'xlsx': extract_text_from_excel,
        'xls': extract_text_from_excel,
    }
    
    extractor = extractors.get(file_type.lower())
    if not extractor:
        raise ValueError(
            f"Unsupported file type: {file_type}. "
            f"Supported: PDF, DOCX, TXT, MD, HTML, CSV, XLSX, XLS"
        )
    
    return extractor(content)


def chunk_text(text: str, chunk_size: int = 1500, overlap: int = 200) -> List[str]:
    """
    Enhanced semantic chunking with paragraph and section awareness
    Uses larger chunks (1500 chars) with smart overlap (200 chars)
    Respects document structure better than simple sentence splitting
    """
    # First, try to split by paragraphs (double newlines or section markers)
    paragraphs = []
    for para in text.split('\n\n'):
        para = para.strip().replace('\n', ' ')
        if para:
            paragraphs.append(para)
    
    # If no paragraph breaks, split by single newlines
    if len(paragraphs) == 1:
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    
    # If still single paragraph, fall back to sentence splitting
    if len(paragraphs) == 1:
        sentences = text.replace('\n', ' ').split('. ')
        paragraphs = [s.strip() + '.' for s in sentences if s.strip()]
    
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # If paragraph fits, add it
        if len(current_chunk) + len(para) + 1 < chunk_size:
            current_chunk += para + " " if current_chunk else para
        else:
            # Save current chunk if it has content
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            # Handle paragraphs larger than chunk_size
            if len(para) > chunk_size:
                # Split large paragraph by sentences
                para_sentences = para.split('. ')
                temp_chunk = ""
                
                for sent in para_sentences:
                    sent = sent.strip()
                    if not sent:
                        continue
                    sent = sent + '.' if not sent.endswith('.') else sent
                    
                    if len(temp_chunk) + len(sent) < chunk_size:
                        temp_chunk += sent + " " if temp_chunk else sent
                    else:
                        if temp_chunk:
                            chunks.append(temp_chunk.strip())
                        temp_chunk = sent
                
                # Add remaining sentences
                if temp_chunk:
                    current_chunk = temp_chunk
            else:
                # Start new chunk with overlap from previous
                if chunks and overlap > 0:
                    last_chunk = chunks[-1]
                    overlap_text = last_chunk[-overlap:] if len(last_chunk) > overlap else last_chunk
                    current_chunk = overlap_text + " " + para if overlap_text else para
                else:
                    current_chunk = para
    
    # Add final chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    # Filter out very small chunks (likely artifacts)
    chunks = [c for c in chunks if len(c) > 50]
    
    return chunks


def generate_chunk_id(client_id: UUID, doc_id: UUID, chunk_index: int) -> str:
    """Generate unique ID for a chunk"""
    raw = f"{client_id}_{doc_id}_{chunk_index}"
    return hashlib.md5(raw.encode()).hexdigest()


async def process_document(
    client_id: UUID,
    doc_id: UUID,
    content: bytes,
    file_type: str,
    filename: str
) -> int:
    """
    Process a document: extract text, chunk it, and store embeddings
    Returns the number of chunks created
    """
    # Ensure persist directory exists (Railway/ephemeral fs)
    os.makedirs(settings.chroma_persist_directory, exist_ok=True)
    # Extract text
    text = extract_text(content, file_type)
    
    if not text.strip():
        raise ValueError("No text content found in document")
    
    # Chunk the text
    chunks = chunk_text(text)
    
    if not chunks:
        raise ValueError("Failed to create chunks from document")
    
    # Get or create collection for this client
    collection_name = get_collection_name(client_id)
    
    try:
        collection = chroma_client.get_collection(collection_name)
    except:
        collection = chroma_client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    # Prepare data for insertion
    ids = []
    documents = []
    metadatas = []
    
    for i, chunk in enumerate(chunks):
        chunk_id = generate_chunk_id(client_id, doc_id, i)
        ids.append(chunk_id)
        documents.append(chunk)
        metadatas.append({
            "doc_id": str(doc_id),
            "filename": filename,
            "chunk_index": i
        })
    
    # Add to collection (ChromaDB handles embedding generation)
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    
    # Persist
    chroma_client.persist()
    
    return len(chunks)


async def retrieve_context(
    client_id: UUID,
    query: str,
    n_results: int = 5  # Increased from 3 to 5 for better context
) -> Optional[str]:
    """
    Retrieve relevant context for a query with enhanced retrieval
    Returns concatenated relevant chunks or None if no collection exists
    Uses larger n_results for better context coverage
    """
    collection_name = get_collection_name(client_id)
    
    try:
        collection = chroma_client.get_collection(collection_name)
    except:
        return None
    
    # Query the collection with more results for better context
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    if not results['documents'] or not results['documents'][0]:
        return None
    
    # Combine relevant chunks with better formatting
    chunks = results['documents'][0]
    metadatas = results['metadatas'][0] if results['metadatas'] else []
    distances = results.get('distances', [[]])[0] if results.get('distances') else []
    
    context_parts = []
    for i, chunk in enumerate(chunks):
        source = metadatas[i].get('filename', 'Unknown') if i < len(metadatas) and metadatas[i] else 'Unknown'
        # Only include chunks with reasonable relevance (distance < 1.5 for cosine)
        if not distances or (i < len(distances) and distances[i] < 1.5):
            context_parts.append(f"[From: {source}]\n{chunk}")
    
    if not context_parts:
        return None
    
    return "\n\n---\n\n".join(context_parts)


async def delete_document_embeddings(client_id: UUID, doc_id: UUID) -> bool:
    """
    Delete all embeddings for a specific document
    """
    collection_name = get_collection_name(client_id)
    
    try:
        collection = chroma_client.get_collection(collection_name)
    except:
        return False
    
    # Delete by metadata filter
    collection.delete(
        where={"doc_id": str(doc_id)}
    )
    
    chroma_client.persist()
    return True


async def delete_client_collection(client_id: UUID) -> bool:
    """
    Delete entire collection for a client
    """
    collection_name = get_collection_name(client_id)
    
    try:
        chroma_client.delete_collection(collection_name)
        chroma_client.persist()
        return True
    except:
        return False
