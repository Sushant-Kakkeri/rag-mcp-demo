# ===========================================
# Author:      Sushant Kakkeri
# Title:       Senior System Architect
# Application: Smart RAG + MCP Assistant
# Created:     April 2026
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
.routing-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-weight: bold;
    font-size: 14px;
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
.stat-card {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 15px;
    text-align: center;
}
.chunk-preview {
    background: #f8f9ff;
    border-left: 3px solid #9C27B0;
    padding: 8px 12px;
    border-radius: 4px;
    font-family: monospace;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────
# ROUTING BADGE HELPER
# ─────────────────────────────
def show_badge(tool):
    """Show colored routing badge."""
    if tool == "RAG":
        st.markdown(
            '<span class="routing-badge"'
            ' style="background:#e3f2fd;'
            'color:#1565c0">'
            '📄 Used RAG</span>',
            unsafe_allow_html=True)
    elif tool == "MCP":
        st.markdown(
            '<span class="routing-badge"'
            ' style="background:#e8f5e9;'
            'color:#2e7d32">'
            '🔧 Used MCP</span>',
            unsafe_allow_html=True)
    elif tool == "BOTH":
        st.markdown(
            '<span class="routing-badge"'
            ' style="background:#fff3e0;'
            'color:#e65100">'
            '🔄 Used RAG + MCP</span>',
            unsafe_allow_html=True)


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
                "loaded_"
                + uploaded_file.name)
            if file_key not in (
                    st.session_state):
                with st.spinner(
                        "📚 Indexing "
                        + uploaded_file.name
                        + "..."):
                    success, info = (
                        st.session_state
                        .rag_engine
                        .load_pdf(
                            uploaded_file))
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

        # Chunk stats in sidebar
        stats = (
            st.session_state.rag_engine
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
                "Total Words Indexed",
                stats["total_words"])
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
        font-size: 11px;
        margin-top: 4px;'>
        Senior Enterprise Software Engineer
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
    "AI that intelligently decides when "
    "to search your documents vs use "
    "live tools")

# How it works
with st.expander(
        "💡 How does the AI decide? "
        "Click to learn more"):
    col1, col2, col3 = st.columns(3)
    col1.markdown("""
    ### 📄 Uses RAG when:
    - You ask about uploaded documents
    - "What does the document say..."
    - Finding specific content in files
    """)
    col2.markdown("""
    ### 🔧 Uses MCP when:
    - Needs live/current information
    - Weather questions
    - Recent news or events
    """)
    col3.markdown("""
    ### 🔄 Uses BOTH when:
    - Needs document info + live data
    - Find in docs AND search web
    """)

st.markdown("---")

# ─────────────────────────────
# TABS
# ─────────────────────────────
if openai_key:
    tab1, tab2, tab3 = st.tabs([
        "💬 Chat Assistant",
        "🔬 Chunk Inspector",
        "📋 Chunk Table"
    ])

    # ═══════════════════════════
    # TAB 1 — CHAT
    # ═══════════════════════════
    with tab1:

        # Chat history
        for msg in st.session_state.get(
                "message_log", []):
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.write(msg["content"])
            else:
                with st.chat_message(
                        "assistant",
                        avatar="🧠"):
                    show_badge(
                        msg.get(
                            "tool_used", ""))
                    st.write(msg["content"])

        # Demo question buttons
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

                show_badge(result["tool_used"])
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
                            result[
                                "mcp_result"])

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

    # ═══════════════════════════
    # TAB 2 — CHUNK INSPECTOR
    # ═══════════════════════════
    with tab2:
        st.subheader(
            "🔬 Document Chunk Inspector")
        st.caption(
            "See exactly how your PDF was "
            "broken into searchable chunks!")

        if not (
                st.session_state.get(
                    "rag_engine")
                and st.session_state
                .rag_engine.has_documents()):
            st.info(
                "👈 Upload a PDF first to "
                "see how it gets chunked!")

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
            search results.
            """)
            col2.markdown("""
            **What is chunk overlap?**
            Adjacent chunks share 200
            characters preventing answers
            from being cut at boundaries.

            **How does search work?**
            AI finds the 4 most relevant
            chunks by MEANING not keywords
            and reads just those to answer.
            """)

        else:
            chunks = (
                st.session_state.rag_engine
                .get_chunks_for_display())
            stats = (
                st.session_state.rag_engine
                .get_chunk_stats())

            if chunks and stats:

                # Stats row
                st.markdown(
                    "### 📊 Chunk Statistics")
                col1, col2, col3, col4, col5 = (
                    st.columns(5))
                col1.metric(
                    "📦 Total Chunks",
                    stats["total"])
                col2.metric(
                    "📏 Avg Size",
                    str(stats["avg_length"])
                    + " chars")
                col3.metric(
                    "📝 Avg Words",
                    str(stats["avg_words"]))
                col4.metric(
                    "⬆️ Max Chunk",
                    str(stats["max_length"])
                    + " chars")
                col5.metric(
                    "📚 Total Words",
                    str(stats["total_words"]))

                st.markdown("---")

                # Settings explanation
                with st.expander(
                        "💡 Why these "
                        "chunk settings?"):
                    st.markdown("""
                    **Chunk Size: 1000 chars**
                    Each chunk holds ~150 words.
                    Big enough for context,
                    small enough for precision.

                    **Chunk Overlap: 200 chars**
                    Adjacent chunks share 200
                    characters so no answer
                    is ever cut in half.

                    **Top K Results: 4**
                    AI finds 4 most relevant
                    chunks per question using
                    semantic similarity search.
                    """)

                st.markdown(
                    "### 🔍 Browse Chunks")

                # Filters
                col1, col2 = st.columns([3, 1])
                search_chunks = col1.text_input(
                    "Search within chunks:",
                    placeholder=(
                        "Filter by content..."))

                sources = list(set(
                    c["source"]
                    for c in chunks))
                source_filter = col2.selectbox(
                    "Filter by file:",
                    options=(
                        ["All Files"] + sources))

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

                if not filtered:
                    st.warning(
                        "No chunks match "
                        "your filter!")
                else:
                    for i, chunk in enumerate(
                            filtered):
                        size_pct = (
                            chunk["length"]
                            / 1000)
                        chunk_num = (
                            chunk["chunk_id"])
                        page_num = chunk["page"]
                        char_len = chunk["length"]
                        word_cnt = (
                            chunk["word_count"])
                        src = chunk["source"]

                        with st.expander(
                                "📄 Chunk "
                                + str(chunk_num)
                                + "  |  Page "
                                + str(page_num)
                                + "  |  "
                                + str(char_len)
                                + " chars  |  "
                                + str(word_cnt)
                                + " words"):

                            # Size bar
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
                                    "content_"
                                    + str(i)),
                                value=(
                                    chunk[
                                        "content"
                                    ]),
                                height=200,
                                key=(
                                    "inspect_"
                                    + str(i)),
                                label_visibility=(
                                    "collapsed"))

                            # Metadata
                            col1, col2, col3 = (
                                st.columns(3))
                            col1.caption(
                                "📌 "
                                + str(src))
                            col2.caption(
                                "📖 Page "
                                + str(page_num))
                            col3.caption(
                                "📏 "
                                + str(char_len)
                                + " chars / "
                                + str(word_cnt)
                                + " words")

    # ═══════════════════════════
    # TAB 3 — CHUNK TABLE
    # ═══════════════════════════
    with tab3:
        st.subheader("📋 Chunk Data Table")
        st.caption(
            "Full table view of all chunks "
            "stored in the FAISS database. "
            "Search, sort, and download!")

        if not (
                st.session_state.get(
                    "rag_engine")
                and st.session_state
                .rag_engine.has_documents()):
            st.info(
                "👈 Upload a PDF first to "
                "view the chunk table!")

        else:
            df = (
                st.session_state.rag_engine
                .get_chunks_as_dataframe())

            if df.empty:
                st.warning(
                    "No chunks found!")
            else:
                # Table controls
                col1, col2, col3 = (
                    st.columns([3, 2, 1]))

                search_table = col1.text_input(
                    "🔍 Search table:",
                    placeholder=(
                        "Filter by any text..."),
                    key="table_search")

                col_filter = col2.selectbox(
                    "📄 Filter by file:",
                    options=(
                        ["All Files"]
                        + list(
                            df["Source File"]
                            .unique())),
                    key="table_file_filter")

                show_full = col3.checkbox(
                    "Show full\ncontent",
                    value=False)

                # Apply filters
                filtered_df = df.copy()

                if search_table:
                    mask = filtered_df.apply(
                        lambda row: row.astype(
                            str).str.contains(
                            search_table,
                            case=False).any(),
                        axis=1)
                    filtered_df = (
                        filtered_df[mask])

                if col_filter != "All Files":
                    filtered_df = (
                        filtered_df[
                            filtered_df[
                                "Source File"
                            ] == col_filter])

                # Row count
                st.caption(
                    "Showing "
                    + str(len(filtered_df))
                    + " of "
                    + str(len(df))
                    + " total chunks")

                # Choose columns to display
                if show_full:
                    display_df = filtered_df
                else:
                    display_df = filtered_df[
                        ["Chunk #",
                         "Source File",
                         "Page",
                         "Words",
                         "Characters",
                         "Preview"]]

                # Display interactive table
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    height=450,
                    column_config={
                        "Chunk #": (
                            st.column_config
                            .NumberColumn(
                                "Chunk #",
                                width="small")),
                        "Source File": (
                            st.column_config
                            .TextColumn(
                                "Source File",
                                width="medium")),
                        "Page": (
                            st.column_config
                            .NumberColumn(
                                "Page",
                                width="small")),
                        "Words": (
                            st.column_config
                            .NumberColumn(
                                "Words",
                                width="small")),
                        "Characters": (
                            st.column_config
                            .ProgressColumn(
                                "Characters",
                                min_value=0,
                                max_value=1000,
                                width="medium")),
                        "Preview": (
                            st.column_config
                            .TextColumn(
                                "Content Preview",
                                width="large")),
                        "Full Content": (
                            st.column_config
                            .TextColumn(
                                "Full Content",
                                width="large")),
                    })

                st.markdown("---")

                # Download options
                st.markdown(
                    "### ⬇️ Download Options")
                col1, col2 = st.columns(2)

                # CSV download
                csv_data = (
                    filtered_df.to_csv(
                        index=False))
                col1.download_button(
                    label=(
                        "📥 Download as CSV"),
                    data=csv_data,
                    file_name=(
                        "chunks_export.csv"),
                    mime="text/csv",
                    use_container_width=True)

                # Full text download
                full_text = "\n\n".join([
                    "=== CHUNK "
                    + str(row["Chunk #"])
                    + " | Page "
                    + str(row["Page"])
                    + " | "
                    + str(row["Source File"])
                    + " ===\n"
                    + str(row["Full Content"])
                    for _, row in
                    filtered_df.iterrows()
                ])
                col2.download_button(
                    label=(
                        "📥 Download Full "
                        "Text"),
                    data=full_text,
                    file_name=(
                        "chunks_full_text.txt"),
                    mime="text/plain",
                    use_container_width=True)

                # Summary stats below table
                st.markdown("---")
                st.markdown(
                    "### 📊 Table Summary")
                col1, col2, col3, col4 = (
                    st.columns(4))

                col1.metric(
                    "Rows Shown",
                    len(filtered_df))
                col2.metric(
                    "Avg Words/Chunk",
                    str(int(
                        filtered_df["Words"]
                        .mean())))
                col3.metric(
                    "Avg Chars/Chunk",
                    str(int(
                        filtered_df[
                            "Characters"]
                        .mean())))
                col4.metric(
                    "Total Words",
                    str(int(
                        filtered_df["Words"]
                        .sum())))

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