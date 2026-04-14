# ===========================================
# rag_engine.py
# ===========================================
# RAG Engine for RAG + MCP Demo App
#
# FIXES IN THIS VERSION:
# - Removed pymupdf (caused build errors)
# - Using pypdf only (works on cloud!)
# - Uses ChromaDB EphemeralClient
# - Fixed indentation errors
# - Works on Streamlit Cloud!
# ===========================================

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter)
from langchain_community.vectorstores import (
    Chroma)
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import (
    PyPDFLoader)
import chromadb
from chromadb.config import Settings
import tempfile
import os


class RAGEngine:
    """
    RAG Engine for document search.
    Uses pypdf only - no compilation!
    Uses EphemeralClient - no disk issues!
    Works on Streamlit Cloud!
    """

    def __init__(self, openai_key: str):
        self.openai_key = openai_key
        self.chroma_client = (
            chromadb.EphemeralClient(
                settings=Settings(
                    anonymized_telemetry=False
                )
            ))
        self.vectorstore = None
        self.embeddings = OpenAIEmbeddings(
            api_key=openai_key)
        self.doc_count = 0
        self.loaded_files = []

    def load_pdf(self,
                 uploaded_file) -> tuple:
        """Load and index a PDF file."""
        tmp_path = None
        try:
            # Save to temp file
            with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            # Read PDF with pypdf
            loader = PyPDFLoader(tmp_path)
            documents = loader.load()

            # Validate content
            if not documents:
                return False, (
                    "PDF appears empty "
                    "or image-based!")

            # Filter empty pages
            documents = [
                d for d in documents
                if len(
                    d.page_content.strip()) > 50
            ]

            if not documents:
                return False, (
                    "No readable text found!")

            # Split into chunks
            splitter = (
                RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200))
            chunks = splitter.split_documents(
                documents)

            # Store in ChromaDB
            if self.vectorstore is None:
                self.vectorstore = (
                    Chroma.from_documents(
                        documents=chunks,
                        embedding=self.embeddings,
                        client=self.chroma_client
                    ))
            else:
                self.vectorstore.add_documents(
                    documents=chunks)

            self.doc_count += len(documents)
            self.loaded_files.append(
                uploaded_file.name)

            # Clean up temp file
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

            return True, len(chunks)

        except Exception as e:
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
            return False, str(e)

    def search(self,
               query: str,
               k: int = 4) -> str:
        """Search documents for relevant content."""
        if self.vectorstore is None:
            return None
        try:
            docs = self.vectorstore\
                .similarity_search(query, k=k)
            if not docs:
                return None
            context = ""
            for i, doc in enumerate(docs):
                page = doc.metadata.get(
                    'page', '?')
                source = doc.metadata.get(
                    'source', 'Document')
                context += (
                    f"[Section {i+1} - "
                    f"Page {page} - "
                    f"From: {source}]\n"
                    f"{doc.page_content}\n\n"
                    f"{'─' * 30}\n\n")
            return context
        except Exception:
            return None

    def has_documents(self) -> bool:
        """Check if documents are loaded."""
        return self.vectorstore is not None

    def get_doc_count(self) -> int:
        """Return number of pages loaded."""
        return self.doc_count

    def get_loaded_files(self) -> list:
        """Return list of loaded filenames."""
        return self.loaded_files

    def clear_documents(self):
        """Clear all loaded documents."""
        self.chroma_client = (
            chromadb.EphemeralClient(
                settings=Settings(
                    anonymized_telemetry=False
                )
            ))
        self.vectorstore = None
        self.doc_count = 0
        self.loaded_files = []