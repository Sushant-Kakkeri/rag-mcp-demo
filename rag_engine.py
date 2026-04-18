# ===========================================
# Author:      Sushant Kakkeri
# Title:       Senior Enterprise Software
#              Engineer
# Application: Smart RAG + MCP Assistant
# Created:     April 2026
# Copyright:   © 2026 Sushant Kakkeri
#              All Rights Reserved
# ===========================================

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter)
from langchain_community.vectorstores import (
    FAISS)
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import (
    PyPDFLoader)
import tempfile
import os


class RAGEngine:
    """
    RAG Engine using FAISS vector store.
    Uses pypdf - works on Streamlit Cloud!
    Includes chunk visualization support.
    """

    def __init__(self, openai_key: str):
        self.openai_key = openai_key
        self.vectorstore = None
        self.embeddings = OpenAIEmbeddings(
            api_key=openai_key)
        self.doc_count = 0
        self.loaded_files = []
        # Store chunks for visualization
        self.all_chunks = []

    def load_pdf(self,
                 uploaded_file) -> tuple:
        """
        Load and index a PDF file.
        Stores chunks for visualization.

        Returns:
            (True, chunk_count) or
            (False, error_message)
        """
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
                    "PDF appears empty!")

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

            # Store chunks for visualization!
            # This is what the chunk inspector
            # uses to display the chunks
            for chunk in chunks:
                self.all_chunks.append({
                    "content": (
                        chunk.page_content),
                    "page": (
                        chunk.metadata.get(
                            "page", "?")),
                    "source": (
                        chunk.metadata.get(
                            "source",
                            uploaded_file.name)),
                    "length": len(
                        chunk.page_content)
                })

            # Store in FAISS
            if self.vectorstore is None:
                self.vectorstore = (
                    FAISS.from_documents(
                        chunks,
                        self.embeddings))
            else:
                new_store = (
                    FAISS.from_documents(
                        chunks,
                        self.embeddings))
                self.vectorstore.merge_from(
                    new_store)

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
        """Search documents for content."""
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

    def get_chunks_for_display(self) -> list:
        """
        Returns all stored chunks for
        visualization in the UI.

        Each chunk has:
        - content: the actual text
        - page: page number in PDF
        - source: filename
        - length: character count
        """
        return self.all_chunks

    def get_chunk_stats(self) -> dict:
        """
        Returns statistics about chunks
        for display in the UI.
        """
        if not self.all_chunks:
            return {}

        lengths = [
            c['length']
            for c in self.all_chunks]

        return {
            "total": len(self.all_chunks),
            "avg_length": (
                sum(lengths) // len(lengths)),
            "max_length": max(lengths),
            "min_length": min(lengths),
            "total_chars": sum(lengths)
        }

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
        self.vectorstore = None
        self.all_chunks = []
        self.doc_count = 0
        self.loaded_files = []