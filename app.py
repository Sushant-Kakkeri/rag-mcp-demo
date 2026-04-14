# ===========================================
# Author:      Sushant Kakkeri
# Title:       Senior Enterprise Software
#              Engineer
# Application: MCP Research Assistant
# Created:     April 2026
# Copyright:   © 2026 Sushant Kakkeri
#              All Rights Reserved
# ===========================================

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
                f"loaded_{uploaded_file.name}")
            if file_key not in st.session_state:
                with st.spinner(
                        f"📚 Indexing "
                        f"{uploaded_file.name}..."):
                    success, info = (
                        st.session_state
                        .rag_engine
                        .load_pdf(uploaded_file))
                    if success:
                        st.session_state[
                            file_key] = True
                        st.sidebar.success(
                            f"✅ {uploaded_file.name}"
                            f" ({info} chunks)")
                    else:
                        st.sidebar.error(
                            f"❌ Error: {info}")

    # Document status
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 System Status")

    if (st.session_state.get("rag_engine") and
            st.session_state.rag_engine
            .has_documents()):
        st.sidebar.success(
            "📄 RAG: Documents loaded")
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

    # ─────────────────────────────
    # SIDEBAR AUTHOR SIGNATURE
    # ─────────────────────────────
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

# ─────────────────────────────
# AUTHOR BAR UNDER TITLE
# ─────────────────────────────
st.markdown("""
<div class='author-bar'>
    <span style='color: #e94560;
        font-weight: bold;
        font-size: 13px;'>
        👨‍💻 Built by Sushant Kakkeri
    </span>
    <span style='color: #aaa;
        font-size: 12px;'>
        &nbsp;|&nbsp;
        Senior Enterprise Software Engineer
        &nbsp;|&nbsp;
        © 2026 All Rights Reserved
    </span>
</div>
""", unsafe_allow_html=True)

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
    - Compare stored vs current info
    - Find in docs AND search web
    - Complex multi-source questions
    """)

st.markdown("---")

# ─────────────────────────────
# CHAT INTERFACE
# ─────────────────────────────
if not openai_key:
    st.warning(
        "👈 Please enter your OpenAI "
        "API key in the sidebar")
else:
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
                # Show routing badge
                tool = msg.get("tool_used", "")
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
                st.write(msg["content"])

    # Suggested questions
    st.subheader("💬 Try These Demo Questions")
    col1, col2, col3 = st.columns(3)

    rag_q = col1.button(
        "📄 What does the document say "
        "about this topic?",
        use_container_width=True)
    mcp_q = col2.button(
        "🌤️ What's the weather in "
        "San Antonio?",
        use_container_width=True)
    both_q = col3.button(
        "🔄 Summarize document + search "
        "related news",
        use_container_width=True)

    # Chat input
    user_input = st.chat_input(
        "Ask anything — I'll decide whether "
        "to search your docs or use live tools!")

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
            "Summarize the key points from "
            "the uploaded document and search "
            "for related recent news online")

    # Process input
    if user_input:
        # Show user message
        with st.chat_message("user"):
            st.write(user_input)

        # Add to logs
        st.session_state.message_log.append({
            "role": "user",
            "content": user_input
        })
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })

        # Get response
        with st.chat_message(
                "assistant", avatar="🧠"):
            with st.spinner(
                    "🤔 Thinking and routing..."):
                result = (
                    st.session_state
                    .router
                    .route_and_respond(
                        user_input,
                        st.session_state
                        .chat_history))

            # Show routing badge
            tool = result["tool_used"]
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

            # Show answer
            st.write(result["answer"])

            # Show sources in expander
            if result["rag_context"]:
                with st.expander(
                        "📄 View RAG Sources"):
                    st.caption(
                        result["rag_context"]
                        [:500] + "...")

            if result["mcp_result"]:
                with st.expander(
                        "🔧 View MCP Tool Result"):
                    st.code(result["mcp_result"])

        # Save to logs
        st.session_state.message_log.append({
            "role": "assistant",
            "content": result["answer"],
            "tool_used": result["tool_used"]
        })
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": result["answer"]
        })

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
        &nbsp;|&nbsp;
        Senior Enterprise Software Engineer
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