# ===========================================
# Author:      Sushant Kakkeri
# Title:       Senior Enterprise Software
#              Engineer
# Application: Smart RAG + MCP Assistant
# Created:     April 2026
# Copyright:   © 2026 Sushant Kakkeri
#              All Rights Reserved
# ===========================================

import streamlit as st
from dotenv import load_dotenv
from rag_engine import RAGEngine
from router import SmartRouter
import os

load_dotenv()

# ─────────────────────────────
# PAGE CONFIG
# ─────────────────────────────
st.set_page_config(
    page_title="RAG + MCP Smart Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────
# CUSTOM STYLING
# ─────────────────────────────
st.markdown("""
<style>
.rag-box {
    background: #e8f4f8;
    border-left: 4px solid #2196F3;
    padding: 10px;
    border-radius: 5px;
    margin: 5px 0;
}
.mcp-box {
    background: #e8f8e8;
    border-left: 4px solid #4CAF50;
    padding: 10px;
    border-radius: 5px;
    margin: 5px 0;
}
.both-box {
    background: #fff3e0;
    border-left: 4px solid #FF9800;
    padding: 10px;
    border-radius: 5px;
    margin: 5px 0;
}
.routing-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-weight: bold;
    font-size: 14px;
}
.chunk-box {
    background: #f8f9ff;
    border-left: 3px solid #9C27B0;
    padding: 8px 12px;
    border-radius: 4px;
    font-family: monospace;
    font-size: 12px;
    margin: 4px 0;
}
.author-bar {
    background: linear-gradient(
        90deg, #1a1a2e, #16213e);
    padding: 8px 15px;
    border-radius: 8px;
    margin-bottom: 10px;
}
.footer-bar {
    text-align: center;
    padding: 15px;
    background: linear-gradient(
        90deg, #1a1a2e, #16213e);
    border-radius: 10px;
    margin-top: 20px;
}
.stat-box {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 10px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────
# SIDEBAR
# ─────────────────────────────
st.sidebar.title("🧠 RAG + MCP Demo")
st.sidebar.markdown("---")

# API Key
openai_key = st.sidebar.text_input(
    "🔑 OpenAI API Key",
    value=os.getenv("OPENAI_API_KEY", ""),
    type="password")

st.sidebar.markdown("---")

# Initialize engines
if openai_key:
    if "rag_engine" not in st.session_state:
        st.session_state.rag_engine = (
            RAGEngine(openai_key))
        st.session_state.router = SmartRouter(
            openai_key,
            st.session_state.rag_engine)
        st.session_state.chat_history = []
        st.session_state.message_log = []

    # PDF Upload
    st.sidebar.subheader("📄 Upload Documents")
    uploaded_files = st.sidebar.file_uploader(
        "Upload PDFs for RAG",
        type="pdf",
        accept_multiple_files=True)

    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_key = (
                "loaded_" + uploaded_file.name)
            if file_key not in st.session_state:
                with st.spinner(
                        "📚 Indexing "
                        + uploaded_file.name
                        + "..."):
                    success, info = (
                        st.session_state
                        .rag_engine
                        .load_pdf(uploaded_file))
                    if success:
                        st.session_state[
                            file_key] = True
                        st.sidebar.success(
                            "✅ "
                            + uploaded_file.name
                            + " ("
                            + str(info)
                            + " chunks)")
                    else:
                        st.sidebar.error(
                            "❌ Error: "
                            + str(info))

    # Document status
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 System Status")

    if (st.session_state.get("rag_engine")
            and st.session_state.rag_engine
            .has_documents()):
        st.sidebar.success(
            "📄 RAG: Documents loaded")

        # ─────────────────────────────
        # CHUNK STATS IN SIDEBAR
        # ─────────────────────────────
        stats = (st.session_state.rag_engine
                 .get_chunk_stats())
        if stats:
            st.sidebar.markdown("---")
            st.sidebar.subheader(
                "🔬 Chunk Statistics")
            st.sidebar.metric(
                "Total Chunks",
                stats["total"])
            st.sidebar.metric(
                "Avg Chunk Size",
                str(stats["avg_length"])
                + " chars")
            st.sidebar.metric(
                "Total Characters",
                str(stats["total_chars"]))

    else:
        st.sidebar.warning(
            "📄 RAG: No documents yet")

    st.sidebar.success("🔧 MCP: Tools ready")
    st.sidebar.info(
        "🌐 Web Search\n"
        "🌤️ Weather\n"
        "📖 Wikipedia\n"
        "🕐 Date/Time")

    # Clear chat
    st.sidebar.markdown("---")
    if st.sidebar.button(
            "🗑️ Clear Conversation",
            use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.message_log = []
        st.rerun()

    # Sidebar Author Signature
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
<div style='text-align: center;
    padding: 10px;'>
    <div style='color: #e94560;
        font-weight: bold;
        font-size: 13px;'>
        👨‍💻 Sushant Kakkeri
    </div>
    <div style='color: gray;
        font-size: 10px;
        margin-top: 2px;'>
        © 2026 All Rights Reserved
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────
# MAIN INTERFACE
# ─────────────────────────────
st.title("🧠 Smart RAG + MCP Assistant")
st.caption(
    "AI that intelligently decides when to "
    "search your documents vs use live tools")

# How it works expander
with st.expander(
        "💡 How does the AI decide? "
        "Click to learn more"):
    col1, col2, col3 = st.columns(3)
    col1.markdown("""
    ### 📄 Uses RAG when:
    - You ask about uploaded documents
    - Questions about stored content
    - "What does the document say about..."
    - Finding specific content in files
    """)
    col2.markdown("""
    ### 🔧 Uses MCP when:
    - Needs live/current information
    - Weather questions
    - Recent news or events
    - General knowledge lookup
    """)
    col3.markdown("""
    ### 🔄 Uses BOTH when:
    - Needs document info + live data
    - Find in docs AND search web
    - Complex multi-source questions
    """)

st.markdown("---")

# ─────────────────────────────
# TABS
# ─────────────────────────────
if openai_key:
    tab1, tab2 = st.tabs([
        "💬 Chat Assistant",
        "🔬 Chunk Inspector"
    ])

    # ═════════════════════════════
    # TAB 1 — CHAT
    # ═════════════════════════════
    with tab1:

        # Display chat history
        for msg in st.session_state.get(
                "message_log", []):
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.write(msg["content"])
            else:
                with st.chat_message(
                        "assistant",
                        avatar="🧠"):
                    tool = msg.get(
                        "tool_used", "")
                    if tool == "RAG":
                        st.markdown(
                            '<span class='
                            '"routing-badge" '
                            'style="background:'
                            '#e3f2fd;color:'
                            '#1565c0">'
                            '📄 Used RAG'
                            '</span>',
                            unsafe_allow_html
                            =True)
                    elif tool == "MCP":
                        st.markdown(
                            '<span class='
                            '"routing-badge" '
                            'style="background:'
                            '#e8f5e9;color:'
                            '#2e7d32">'
                            '🔧 Used MCP'
                            '</span>',
                            unsafe_allow_html
                            =True)
                    elif tool == "BOTH":
                        st.markdown(
                            '<span class='
                            '"routing-badge" '
                            'style="background:'
                            '#fff3e0;color:'
                            '#e65100">'
                            '🔄 Used RAG + MCP'
                            '</span>',
                            unsafe_allow_html
                            =True)
                    st.write(msg["content"])

        # Suggested questions
        st.subheader(
            "💬 Try These Demo Questions")
        col1, col2, col3 = st.columns(3)

        rag_q = col1.button(
            "📄 What does the document "
            "say about this topic?",
            use_container_width=True)
        mcp_q = col2.button(
            "🌤️ What's the weather in "
            "San Antonio?",
            use_container_width=True)
        both_q = col3.button(
            "🔄 Summarize document + "
            "search related news",
            use_container_width=True)

        # Chat input
        user_input = st.chat_input(
            "Ask anything — I'll decide "
            "whether to search your docs "
            "or use live tools!")

        # Handle suggested questions
        if rag_q:
            user_input = (
                "What are the main points "
                "in the uploaded document?")
        if mcp_q:
            user_input = (
                "What is the weather in "
                "San Antonio Texas right now?")
        if both_q:
            user_input = (
                "Summarize the key points "
                "from the uploaded document "
                "and search for related "
                "recent news online")

        # Process input
        if user_input:
            with st.chat_message("user"):
                st.write(user_input)

            st.session_state.message_log\
                .append({
                    "role": "user",
                    "content": user_input
                })
            st.session_state.chat_history\
                .append({
                    "role": "user",
                    "content": user_input
                })

            with st.chat_message(
                    "assistant",
                    avatar="🧠"):
                with st.spinner(
                        "🤔 Thinking and "
                        "routing..."):
                    result = (
                        st.session_state
                        .router
                        .route_and_respond(
                            user_input,
                            st.session_state
                            .chat_history))

                tool = result["tool_used"]
                if tool == "RAG":
                    st.markdown(
                        '<span class='
                        '"routing-badge" '
                        'style="background:'
                        '#e3f2fd;color:'
                        '#1565c0">'
                        '📄 Used RAG'
                        '</span>',
                        unsafe_allow_html
                        =True)
                elif tool == "MCP":
                    st.markdown(
                        '<span class='
                        '"routing-badge" '
                        'style="background:'
                        '#e8f5e9;color:'
                        '#2e7d32">'
                        '🔧 Used MCP'
                        '</span>',
                        unsafe_allow_html
                        =True)
                elif tool == "BOTH":
                    st.markdown(
                        '<span class='
                        '"routing-badge" '
                        'style="background:'
                        '#fff3e0;color:'
                        '#e65100">'
                        '🔄 Used RAG + MCP'
                        '</span>',
                        unsafe_allow_html
                        =True)

                st.write(result["answer"])

                if result["rag_context"]:
                    with st.expander(
                            "📄 View RAG "
                            "Sources"):
                        st.caption(
                            result[
                                "rag_context"
                            ][:500] + "...")

                if result["mcp_result"]:
                    with st.expander(
                            "🔧 View MCP "
                            "Tool Result"):
                        st.code(
                            result["mcp_result"])

            st.session_state.message_log\
                .append({
                    "role": "assistant",
                    "content": result["answer"],
                    "tool_used": (
                        result["tool_used"])
                })
            st.session_state.chat_history\
                .append({
                    "role": "assistant",
                    "content": result["answer"]
                })

    # ═════════════════════════════
    # TAB 2 — CHUNK INSPECTOR
    # ═════════════════════════════
    with tab2:
        st.subheader("🔬 Document Chunk Inspector")
        st.caption(
            "See exactly how your PDF was "
            "broken into searchable chunks. "
            "Each chunk is what the AI "
            "searches through!")

        if not (
                st.session_state.get(
                    "rag_engine")
                and st.session_state.rag_engine
                .has_documents()):
            st.info(
                "👈 Upload a PDF first to "
                "see how it gets chunked!")

            # Show explanation even without docs
            st.markdown("---")
            st.markdown(
                "### 📖 How Chunking Works")
            col1, col2 = st.columns(2)
            col1.markdown("""
            **What is a chunk?**
            When you upload a PDF it gets
            split into small pieces called
            chunks. Each chunk is about
            1000 characters (~150 words).

            **Why chunk at all?**
            AI has limited input size.
            Smaller chunks = more precise
            search. We find exact paragraphs
            not whole pages.
            """)
            col2.markdown("""
            **What is chunk overlap?**
            Adjacent chunks share 200
            characters. This prevents
            answers from being cut in half
            at chunk boundaries.

            **How does search work?**
            When you ask a question we
            convert it to numbers and find
            the 4 most similar chunks by
            MEANING not just keywords.
            """)

        else:
            chunks = (
                st.session_state.rag_engine
                .get_chunks_for_display())
            stats = (
                st.session_state.rag_engine
                .get_chunk_stats())

            if chunks and stats:

                # Summary stats
                st.markdown(
                    "### 📊 Chunk Statistics")
                col1, col2, col3, col4 = (
                    st.columns(4))

                col1.metric(
                    "📦 Total Chunks",
                    stats["total"],
                    help="Total number of "
                         "chunks created")
                col2.metric(
                    "📏 Avg Chunk Size",
                    str(stats["avg_length"])
                    + " chars",
                    help="Average characters "
                         "per chunk")
                col3.metric(
                    "⬆️ Max Chunk",
                    str(stats["max_length"])
                    + " chars",
                    help="Largest chunk size")
                col4.metric(
                    "📄 Total Characters",
                    str(stats["total_chars"]),
                    help="Total text indexed")

                st.markdown("---")

                # Chunk size explanation
                with st.expander(
                        "💡 Why these settings?"):
                    st.markdown("""
                    **Chunk Size: 1000 chars**
                    Each chunk holds about
                    150 words. Big enough
                    to have context, small
                    enough to be precise.

                    **Chunk Overlap: 200 chars**
                    Adjacent chunks share
                    200 characters so answers
                    near boundaries are never
                    cut in half.

                    **Top K Results: 4**
                    When you ask a question
                    the AI finds the 4 most
                    relevant chunks and reads
                    those to answer you.
                    """)

                st.markdown(
                    "### 🔍 Browse All Chunks")

                # Search filter
                col1, col2 = st.columns([3, 1])
                search_chunks = col1.text_input(
                    "Search within chunks:",
                    placeholder=(
                        "Type to filter "
                        "chunks by content..."))
                source_filter = col2.selectbox(
                    "Filter by file:",
                    options=["All Files"] + list(
                        set(c["source"]
                            for c in chunks)))

                # Apply filters
                filtered = chunks
                if search_chunks:
                    filtered = [
                        c for c in filtered
                        if search_chunks.lower()
                        in c["content"].lower()]
                if source_filter != "All Files":
                    filtered = [
                        c for c in filtered
                        if c["source"]
                        == source_filter]

                # Show filter results
                if search_chunks or (
                        source_filter
                        != "All Files"):
                    st.caption(
                        "Showing "
                        + str(len(filtered))
                        + " of "
                        + str(len(chunks))
                        + " chunks")

                st.markdown("---")

                # Display chunks
                if not filtered:
                    st.warning(
                        "No chunks match "
                        "your filter!")
                else:
                    for i, chunk in enumerate(
                            filtered):

                        # Chunk size color
                        size_pct = (
                            chunk["length"]
                            / 1000)
                        if size_pct > 0.8:
                            size_color = "#F44336"
                        elif size_pct > 0.5:
                            size_color = "#FF9800"
                        else:
                            size_color = "#4CAF50"

                        chunk_num = i + 1
                        page_num = chunk["page"]
                        char_len = chunk["length"]
                        src = chunk["source"]

                        with st.expander(
                                "📄 Chunk "
                                + str(chunk_num)
                                + "  |  Page "
                                + str(page_num)
                                + "  |  "
                                + str(char_len)
                                + " chars  |  "
                                + str(src)):

                            # Visual size bar
                            st.markdown(
                                "**Chunk Size:**")
                            st.progress(
                                min(size_pct,
                                    1.0))
                            st.caption(
                                str(char_len)
                                + " / 1000 "
                                + "characters max")

                            st.markdown("---")

                            # Content
                            st.markdown(
                                "**Content:**")
                            st.text_area(
                                label=(
                                    "chunk_content"
                                    + str(i)),
                                value=(
                                    chunk[
                                        "content"]),
                                height=200,
                                key=(
                                    "chunk_ta_"
                                    + str(i)),
                                label_visibility=(
                                    "collapsed"))

                            # Metadata
                            col1, col2, col3 = (
                                st.columns(3))
                            col1.caption(
                                "📌 Source: "
                                + str(src))
                            col2.caption(
                                "📖 Page: "
                                + str(page_num))
                            col3.caption(
                                "📏 Length: "
                                + str(char_len)
                                + " chars")

else:
    st.warning(
        "👈 Please enter your OpenAI "
        "API key in the sidebar")

# ─────────────────────────────
# FOOTER
# ─────────────────────────────
st.markdown("---")
st.markdown("""
<div class='footer-bar'>
    <div style='color: #e94560;
        font-weight: bold;
        font-size: 14px;'>
        🧠 Smart RAG + MCP Assistant
    </div>
    <div style='color: #aaa;
        font-size: 12px;
        margin-top: 5px;'>
        Built by
        <b style='color: white;'>
            Sushant Kakkeri
        </b>
    </div>
    <div style='color: gray;
        font-size: 11px;
        margin-top: 4px;'>
        Powered by OpenAI GPT-4o +
        LangChain + FAISS + Streamlit
        &nbsp;|&nbsp;
        © 2026 All Rights Reserved
    </div>
</div>
""", unsafe_allow_html=True)