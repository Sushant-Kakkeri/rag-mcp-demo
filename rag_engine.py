# ===========================================
# rag_engine.py
# ===========================================
# RAG Engine for RAG + MCP Demo App
#
# FIXES IN THIS VERSION:
# - Removed pymupdf (caused build errors)
# - Using pypdf only (works on cloud!)
# - Uses ChromaDB EphemeralClient
# - Works on Streamlit Cloud!
# ===========================================

# Text splitter - breaks PDFs into chunks
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter)

# ChromaDB - smart search database
from langchain_community.vectorstores import (
    Chroma)

# OpenAI Embeddings - converts text to numbers
from langchain_openai import OpenAIEmbeddings

# PDF loader - pypdf only!
# No compilation needed!
# Works on all platforms!
from langchain_community.document_loaders import (
    PyPDFLoader)

# ChromaDB in-memory client
# Fixes chroma_db_impl error!
import chromadb
from chromadb.config import Settings

# File handling
import tempfile
import os


class RAGEngine:
    """
    RAG Engine for document search.

    Uses pypdf only - no compilation!
    Uses EphemeralClient - no disk issues!
    Works perfectly on Streamlit Cloud!
    """

    def __init__(self, openai_key: str):
        """
        Initialize RAG Engine.

        Args:
            openai_key: OpenAI API key
        """
        self.openai_key = openai_key

        # ChromaDB in-memory client
        # EphemeralClient = stores in RAM
        # No disk permissions needed!
        # No chroma_db_impl error!
        # Perfect for Streamlit Cloud!
        self.chroma_client = (
            chromadb.EphemeralClient(
                settings=Settings(
                    # Don't send usage data
                    anonymized_telemetry=False
                )
            ))

        # Vector store - starts empty
        # Filled when PDF is uploaded
        self.vectorstore = None

        # OpenAI embeddings converter
        # Converts text chunks to numbers
        # Numbers capture MEANING of text!
        self.embeddings = OpenAIEmbeddings(
            api_key=openai_key)

        # Track how many pages loaded
        self.doc_count = 0

        # Track loaded file names
        # Example: ["Mars.pdf", "AWS.pdf"]
        self.loaded_files = []

    def load_pdf(self,
                 uploaded_file) -> tuple:
        """
        Load and index a PDF file.
        Uses pypdf only - works on cloud!

        Args:
            uploaded_file: Streamlit file

        Returns:
            (True, chunk_count) if success
            (False, error_msg) if failed
        """
        tmp_path = None

        try:
            # STEP 1: Save to temp file
            # pypdf needs file on disk to read
            # Can't process from memory!
            with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            # STEP 2: Read PDF with pypdf
            # Simple, reliable, no compilation!
            # Works on Windows, Mac, Linux,
            # and Streamlit Cloud!
            loader = PyPDFLoader(tmp_path)
            documents = loader.load()

            # STEP 3: Validate we got content
            # Some PDFs are image-based and
            # have no extractable text!
            if not documents:
                return False, (
                    "PDF appears empty "
                    "or image-based! "
                    "Try a text-based PDF.")

            # Filter out near-empty pages
            # Less than 50 chars = blank page
            documents = [
                d for d in documents
                if len(
                    d.page_content.strip()) > 50
            ]

            if not documents:
                return False, (
                    "No readable text found! "
                    "Try a Wikipedia PDF.")

            # STEP 4: Split into chunks
            # Why split?
            # - AI has input size limits
            # - Smaller = more precise search
            # - Find exact paragraphs!
            #
            # chunk_size=1000 = ~150 words
            # chunk_overlap=200 = shared chars
            # Overlap prevents cutting answers!
            # [Chunk1: chars 1-1000   ]
            # [Chunk2: chars 800-1800 ]
            #          ↑ 200 overlap!
            splitter = (
                RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200))
            chunks = splitter.split_documents(
                documents)

            # STEP 5: Store in ChromaDB
            # Convert chunks to numbers
            # Store for fast searching!
            # Using EphemeralClient = in memory!
            if self.vectorstore is None:
                # First PDF - create new database
                self.vectorstore = (
                    Chroma.from_documents(
                        documents=chunks,
                        embedding=self.embeddings,
                        client=self.chroma_client
                    ))
            else:
                # More PDFs - add to existing
                # Don't overwrite old documents!
                self.vectorstore.add_documents(
                    documents=chunks)

            # Track stats
            self.doc_count += len(documents)
            self.loaded_files.append(
                uploaded_file.name)

            # STEP 6: Clean up temp file
            # Windows sometimes locks files
            # Use try/except to handle safely!
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass  # OK if can't delete

            # Return success!
            return True, len(chunks)

        except Exception as e:
            # Something went wrong!
            # Clean up temp file if it exists
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
            # Return failure with error message
            return False, str(e)

    def search(self,
               query: str,
               k: int = 4) -> str:
        """
        Search uploaded documents.
        Finds most relevant chunks!

        Args:
            query: What to search for
            k:     Number of chunks to return
                   Default 4 = top 4 matches

        Returns:
            Relevant sections as string
            or None if nothing found
        """
        # Can't search if nothing loaded!
        if self.vectorstore is None:
            return None

        try:
            # Search by MEANING not keywords!
            # Finds semantically similar content
            # Even if exact words don't match!
            docs = self.vectorstore\
                .similarity_search(query, k=k)

            if not docs:
                return None

            # Format results nicely
            # Show section, page, source
            context = ""
            for i, doc in enumerate(docs):
                #