# ===========================================
# rag_engine.py
# ===========================================
# RAG Engine for RAG + MCP Demo App
#
# FIXES IN THIS VERSION:
# - Uses ChromaDB EphemeralClient
#   (in-memory storage)
# - Fixes "chroma_db_impl" error
# - Fixes protobuf conflicts
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

# ChromaDB client - NEW way to initialize
import chromadb
from chromadb.config import Settings

# File handling
import tempfile
import os


class RAGEngine:
    """
    RAG Engine for document search.
    Uses EphemeralClient (in-memory)
    to avoid Streamlit Cloud issues!
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
        # No disk needed = no permission issues!
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
        # Converts text to numbers
        self.embeddings = OpenAIEmbeddings(
            api_key=openai_key)

        # Track loaded pages
        self.doc_count = 0

        # Track loaded filenames
        self.loaded_files = []

    def load_pdf(self,
                 uploaded_file) -> tuple:
        """
        Load and index a PDF file.

        Args:
            uploaded_file: Streamlit file

        Returns:
            (True, chunk_count) or
            (False, error_message)
        """
        tmp_path = None

        try:
            # STEP 1: Save to temp file
            with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            # STEP 2: Read PDF text
            documents = []

            # Try PyMuPDF first (best)
            try:
                import fitz
                from langchain.schema import (
                    Document)

                doc = fitz.open(tmp_path)

                for page_num in range(len(doc)):
                    page = doc[page_num]
                    text = page.get_text()

                    if text.strip():
                        documents.append(
                            Document(
                                page_content=text,
                                metadata={
                                    "page":
                                        page_num + 1,
                                    "source":
                                        uploaded_file
                                        .name
                                }
                            )
                        )
                doc.close()

            # Fallback to pypdf
            except ImportError:
                from langchain_community\
                    .document_loaders import (
                    PyPDFLoader)
                loader = PyPDFLoader(tmp_path)
                documents = loader.load()

            # STEP 3: Validate content
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

            # STEP 4: Split into chunks
            splitter = (
                RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200))
            chunks = splitter.split_documents(
                documents)

            # STEP 5: Store in ChromaDB
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
                # Additional PDFs - add to store
                self.vectorstore.add_documents(
                    documents=chunks)

            self.doc_count += len(documents)
            self.loaded_files.append(
                uploaded_file.name)

            # STEP 6: Clean up temp file
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
        """
        Search documents for relevant content.

        Args:
            query: Search query
            k:     Number of results

        Returns:
            Relevant sections as string
        """
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
        # Create fresh client
        self.chroma_client = (
            chromadb.EphemeralClient(
                settings=Settings(
                    anonymized_telemetry=False
                )
            ))
        self.vectorstore = None
        self.doc_count = 0
        self.loaded_files = []