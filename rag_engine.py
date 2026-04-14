# ===========================================
# rag_engine.py
# ===========================================
# RAG Engine for RAG + MCP Demo App
#
# FIXES IN THIS VERSION:
# - chromadb 0.6.3 compatible
# - Removed Settings class (removed in 0.6.x)
# - EphemeralClient without settings
# - Works on Python 3.14!
# - Works on Streamlit Cloud!
# ===========================================

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter)
from langchain_community.vectorstores import (
    Chroma)
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import (
    PyPDFLoader)

# chromadb 0.6.3 - no Settings needed!
import chromadb

import tempfile
import os


class RAGEngine:
    """
    RAG Engine for document search.
    Uses pypdf - no compilation needed!
    Uses EphemeralClient - works on cloud!
    Compatible with Python 3.14!
    """

    def __init__(self, openai_key: str):
        """
        Initialize RAG Engine.

        Args:
            openai_key: OpenAI API key
        """
        self.openai_key = openai_key

        # ChromaDB 0.6.3 EphemeralClient
        # No Settings class needed anymore!
        # Stores in memory - no disk needed!
        # Works on Streamlit Cloud! ✅
        self.chroma_client = (
            chromadb.EphemeralClient())

        # Vector store - empty until PDF loaded
        self.vectorstore = None

        # Convert text to numbers for search
        self.embeddings = OpenAIEmbeddings(
            api_key=openai_key)

        # Track loaded pages count
        self.doc_count = 0

        # Track loaded file names
        self.loaded_files = []

    def load_pdf(self,
                 uploaded_file) -> tuple:
        """
        Load and index a PDF file.

        Args:
            uploaded_file: Streamlit file

        Returns:
            (True, chunk_count) if success
            (False, error_msg) if failed
        """
        tmp_path = None

        try:
            # Save to temp file
            # pypdf needs file on disk
            with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            # Read PDF with pypdf
            # Simple and reliable!
            # Works on all platforms!
            loader = PyPDFLoader(tmp_path)
            documents = loader.load()

            # Validate we got content
            if not documents:
                return False, (
                    "PDF appears empty "
                    "or image-based!")

            # Filter empty pages
            # Less than 50 chars = blank
            documents = [
                d for d in documents
                if len(
                    d.page_content.strip()) > 50
            ]

            if not documents:
                return False, (
                    "No readable text found! "
                    "Try a Wikipedia PDF.")

            # Split into chunks
            # chunk_size=1000 = ~150 words
            # chunk_overlap=200 = shared chars
            splitter = (
                RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200))
            chunks = splitter.split_documents(
                documents)

            # Store in ChromaDB
            # Using EphemeralClient!
            if self.vectorstore is None:
                # First PDF - create new store
                self.vectorstore = (
                    Chroma.from_documents(
                        documents=chunks,
                        embedding=self.embeddings,
                        client=self.chroma_client
                    ))
            else:
                # More PDFs - add to existing
                self.vectorstore.add_documents(
                    documents=chunks)

            # Track stats
            self.doc_count += len(documents)
            self.loaded_files.append(
                uploaded_file.name)

            # Clean up temp file safely
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

            return True, len(chunks)

        except Exception as e:
            # Clean up on error
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
            return False, str(e)

    def search(self,
               query: str,
               k: int = 4) -> str:
        """
        Search documents for relevant content.

        Args:
            query: What to search for
            k:     Number of results

        Returns:
            Relevant sections as string
            or None if nothing found
        """
        if self.vectorstore is None:
            return None

        try:
            # Search by MEANING not keywords!
            docs = self.vectorstore\
                .similarity_search(query, k=k)

            if not docs:
                return None

            # Format results with metadata
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
        # Fresh client clears everything!
        self.chroma_client = (
            chromadb.EphemeralClient())
        self.vectorstore = None
        self.doc_count = 0
        self.loaded_files = []