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
    """Extract text from PDF file"""
    import io
    reader = PdfReader(io.BytesIO(content))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def extract_text_from_docx(content: bytes) -> str:
    """Extract text from DOCX file"""
    import io
    doc = DocxDocument(io.BytesIO(content))
    return "\n".join([para.text for para in doc.paragraphs])


def extract_text_from_txt(content: bytes) -> str:
    """Extract text from TXT file"""
    return content.decode('utf-8', errors='ignore')


def extract_text(content: bytes, file_type: str) -> str:
    """Extract text from file based on type"""
    extractors = {
        'pdf': extract_text_from_pdf,
        'docx': extract_text_from_docx,
        'txt': extract_text_from_txt
    }
    
    extractor = extractors.get(file_type)
    if not extractor:
        raise ValueError(f"Unsupported file type: {file_type}")
    
    return extractor(content)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks
    Uses sentence boundaries when possible
    """
    # Split by sentences (roughly)
    sentences = text.replace('\n', ' ').split('. ')
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Add sentence to current chunk
        if len(current_chunk) + len(sentence) < chunk_size:
            current_chunk += sentence + ". "
        else:
            # Save current chunk and start new one
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            # Start new chunk with overlap from previous
            if chunks and overlap > 0:
                # Get last N characters from previous chunk
                last_chunk = chunks[-1]
                overlap_text = last_chunk[-overlap:] if len(last_chunk) > overlap else last_chunk
                current_chunk = overlap_text + " " + sentence + ". "
            else:
                current_chunk = sentence + ". "
    
    # Add final chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
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
    n_results: int = 3
) -> Optional[str]:
    """
    Retrieve relevant context for a query
    Returns concatenated relevant chunks or None if no collection exists
    """
    collection_name = get_collection_name(client_id)
    
    try:
        collection = chroma_client.get_collection(collection_name)
    except:
        return None
    
    # Query the collection
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    if not results['documents'] or not results['documents'][0]:
        return None
    
    # Combine relevant chunks
    chunks = results['documents'][0]
    metadatas = results['metadatas'][0] if results['metadatas'] else []
    
    context_parts = []
    for i, chunk in enumerate(chunks):
        source = metadatas[i].get('filename', 'Unknown') if metadatas else 'Unknown'
        context_parts.append(f"[Source: {source}]\n{chunk}")
    
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
