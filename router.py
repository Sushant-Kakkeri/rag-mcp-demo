# ===========================================
# router.py
# ===========================================
# Smart Router for RAG + MCP Demo App
#
# The Router decides:
# - RAG only  → question about documents
# - MCP only  → live data/general questions
# - BOTH      → explicitly needs both
#
# KEY FIX:
# Previously: Had RAG context + used MCP tool
#             = always showed BOTH (WRONG!)
#
# Now:        Only shows BOTH when question
#             EXPLICITLY asks about document
#             AND live data together!
#
# New routing logic:
# 1. Check if question is about documents
# 2. Check if question needs live data
# 3. Only use BOTH if BOTH are clearly needed
# ===========================================

from openai import OpenAI
from mcp_tools import MCP_TOOLS, execute_tool
import json


# ===========================================
# IMPROVED SYSTEM PROMPT
# ===========================================
# Much stricter rules about when to use
# each mode. Fixes the over-triggering BOTH!
# ===========================================
SYSTEM_PROMPT = """You are an intelligent
assistant with two powerful capabilities:

1. 📄 RAG (Document Search): Search through
   uploaded documents to find specific
   information from those files.

2. 🔧 MCP Tools: Access live tools:
   - web_search: Current news and events
   - get_weather: Live weather data
   - wikipedia_search: General knowledge
   - get_current_datetime: Current time/date

════════════════════════════════════════════
STRICT ROUTING RULES - FOLLOW EXACTLY!
════════════════════════════════════════════

USE RAG ONLY when:
✅ User DIRECTLY asks about uploaded document
✅ User says "the document", "the PDF",
   "the guide", "the file", "the report"
✅ User says "what does it say about..."
✅ User says "according to the document..."
✅ User asks to summarize the document
✅ Question is clearly about stored content

Examples:
✅ "What does the document say about Lambda?"
✅ "According to the PDF, what are prerequisites?"
✅ "Summarize the uploaded guide"
✅ "What services are mentioned in the document?"

────────────────────────────────────────────

USE MCP ONLY when:
✅ Weather questions of ANY kind
✅ General knowledge questions
✅ Current news or events
✅ Questions about real world facts
✅ No mention of documents at all
✅ Question could be answered without documents

Examples:
✅ "What is the weather in San Antonio?"
✅ "What is NASA's next mission?"
✅ "What time is it?"
✅ "Tell me about quantum computing"
✅ "Latest news about SpaceX"
✅ "What is the temperature in Bulverde TX?"

CRITICAL: Even if a document is uploaded,
use MCP ONLY for weather, news, and general
knowledge questions that are NOT about
the document content!

────────────────────────────────────────────

USE BOTH only when:
✅ Question EXPLICITLY asks about document
   AND live data IN THE SAME QUESTION
✅ User uses connecting words like AND, ALSO,
   PLUS, AS WELL AS between a document
   question and a live question

Examples:
✅ "What does document say about S3 AND
   what is current AWS pricing?"
✅ "Summarize the PDF AND find latest
   news about AWS Lambda"
✅ "What does the guide say about ECS
   AND show me current ECS pricing?"

NOT BOTH:
❌ Weather questions (always MCP only!)
❌ NASA/space questions not in document
❌ Any question not mentioning document
❌ General questions even if doc uploaded

════════════════════════════════════════════

ALWAYS start your response with:
🧠 **Routing Decision:** Using [RAG/MCP/BOTH]
because [brief reason]

Then provide your complete answer."""


class SmartRouter:
    """
    Smart Router that decides how to answer.

    Routes to:
    - RAG:  document questions
    - MCP:  live data questions
    - BOTH: explicitly needs both
    """

    def __init__(self,
                 openai_key: str,
                 rag_engine):
        """
        Initialize Smart Router.

        Args:
            openai_key:  OpenAI API key
            rag_engine:  RAG engine instance
        """
        self.client = OpenAI(
            api_key=openai_key)
        self.rag_engine = rag_engine

    def route_and_respond(
            self,
            query: str,
            chat_history: list) -> dict:
        """
        Route query to RAG, MCP or both.

        Args:
            query:        User question
            chat_history: Past messages

        Returns:
            Dict with answer and metadata
        """
        # Initialize result dictionary
        result = {
            "answer": "",
            "tool_used": "",
            "rag_context": None,
            "mcp_result": None,
            "routing_reason": ""
        }

        # ─────────────────────────────
        # STEP 1: Detect if question is
        # about documents specifically
        # ─────────────────────────────

        # Keywords that suggest document question
        doc_keywords = [
            "document", "pdf", "file",
            "guide", "report", "uploaded",
            "what does it say",
            "according to",
            "in the document",
            "from the document",
            "the guide says",
            "based on the",
            "summarize the",
            "summary of the"
        ]

        # Keywords that suggest live data
        # regardless of document content!
        live_keywords = [
            "weather", "temperature",
            "forecast", "humidity",
            "wind", "rain", "sunny",
            "news", "latest", "current",
            "today", "right now",
            "stock price", "price of",
            "what time", "date today"
        ]

        # Keywords that explicitly connect
        # document AND live questions
        both_keywords = [
            " and find ",
            " and also ",
            " and search ",
            " and get ",
            " as well as ",
            " along with ",
            " together with ",
            " plus find ",
            " also find ",
            " additionally find "
        ]

        query_lower = query.lower()

        # Check what type of question this is
        is_doc_question = any(
            kw in query_lower
            for kw in doc_keywords)

        is_live_question = any(
            kw in query_lower
            for kw in live_keywords)

        # Only BOTH if EXPLICITLY asks for both
        # Must have doc keyword AND connecting
        # word AND live data request
        is_explicit_both = (
            is_doc_question and
            any(kw in query_lower
                for kw in both_keywords)
        )

        # ─────────────────────────────
        # STEP 2: Get RAG context
        # Only search docs if question
        # is actually about documents!
        # ─────────────────────────────
        rag_context = None

        # Only search documents if:
        # 1. Documents are loaded
        # 2. Question is about document
        #    OR explicitly needs both
        if (self.rag_engine.has_documents()
                and (is_doc_question
                     or is_explicit_both)):
            rag_context = (
                self.rag_engine.search(query))

        # ─────────────────────────────
        # STEP 3: Build smart messages
        # Tell AI what context we have
        # and what routing to use
        # ─────────────────────────────
        messages = [
            {"role": "system",
             "content": SYSTEM_PROMPT}
        ]

        # Add recent conversation history
        # Last 6 messages = 3 exchanges
        for msg in chat_history[-6:]:
            messages.append(msg)

        # ─────────────────────────────
        # Build user content based on
        # what type of question this is
        # ─────────────────────────────

        if is_explicit_both and rag_context:
            # Explicit BOTH question with docs
            user_content = (
                f"USER QUESTION: {query}\n\n"
                f"⚠️ This question asks about "
                f"BOTH document content AND "
                f"live information. "
                f"Use BOTH mode!\n\n"
                f"DOCUMENT CONTENT FOUND:\n"
                f"{rag_context}\n\n"
                f"Also use MCP tools for "
                f"the live information part.")

        elif is_doc_question and rag_context:
            # Document question with context
            user_content = (
                f"USER QUESTION: {query}\n\n"
                f"This is a DOCUMENT question. "
                f"Use RAG mode.\n\n"
                f"RELEVANT DOCUMENT CONTENT:\n"
                f"{rag_context}\n\n"
                f"Answer using the document "
                f"content above. Do NOT use "
                f"MCP tools unless the answer "
                f"is NOT in the document.")

        elif is_doc_question and (
                not self.rag_engine
                .has_documents()):
            # Document question but no docs
            user_content = (
                f"USER QUESTION: {query}\n\n"
                f"User is asking about a "
                f"document but NO documents "
                f"are uploaded yet!\n\n"
                f"Tell user to upload a PDF "
                f"first. Use MCP tools to "
                f"answer what you can.")

        elif is_live_question:
            # Live data question - MCP only!
            # Even if documents are uploaded!
            user_content = (
                f"USER QUESTION: {query}\n\n"
                f"This is a LIVE DATA question "
                f"(weather/news/current info). "
                f"Use MCP mode ONLY!\n\n"
                f"Do NOT use RAG even if "
                f"documents are available. "
                f"Use appropriate MCP tool.")

        else:
            # General question - MCP only
            user_content = (
                f"USER QUESTION: {query}\n\n"
                f"This is a general question. "
                f"Use MCP mode.\n\n"
                f"Use appropriate MCP tools "
                f"to find the answer.")

        # Add user message
        messages.append({
            "role": "user",
            "content": user_content
        })

        # ─────────────────────────────
        # STEP 4: Call OpenAI with tools
        # AI decides which MCP tool to use
        # ─────────────────────────────
        response = self.client.chat\
            .completions.create(
                model="gpt-4o",
                messages=messages,
                tools=MCP_TOOLS,
                tool_choice="auto",
                temperature=0.3
            )

        response_message = (
            response.choices[0].message)

        # ─────────────────────────────
        # STEP 5: Handle tool calls
        # KEY FIX IS HERE!
        # Only mark as BOTH if explicitly
        # asked for both!
        # ─────────────────────────────
        if response_message.tool_calls:
            tool_results = []
            tools_used = []

            # Execute each tool AI chose
            for tool_call in (
                    response_message.tool_calls):
                tool_name = (
                    tool_call.function.name)
                tool_args = json.loads(
                    tool_call.function
                    .arguments)

                # Run the tool
                tool_result = execute_tool(
                    tool_name, tool_args)

                # Store results
                tool_results.append({
                    "tool_call_id":
                        tool_call.id,
                    "role": "tool",
                    "content": tool_result
                })
                tools_used.append(tool_name)
                result["mcp_result"] = (
                    tool_result)

            # ─────────────────────────────
            # THE KEY FIX!
            # Only use BOTH if EXPLICITLY
            # asked for both in the question!
            # Not just because doc exists!
            # ─────────────────────────────
            if is_explicit_both and rag_context:
                # Truly needs both!
                result["tool_used"] = "BOTH"
                result["routing_reason"] = (
                    f"Question explicitly asks "
                    f"about document AND live "
                    f"data. Used: "
                    f"{', '.join(tools_used)}")
            else:
                # MCP only - even if doc exists!
                result["tool_used"] = "MCP"
                result["routing_reason"] = (
                    f"Live data question. "
                    f"Used MCP tools: "
                    f"{', '.join(tools_used)}")

            # Add AI decision to messages
            messages.append(response_message)
            messages.extend(tool_results)

            # For BOTH mode combine sources
            if result["tool_used"] == "BOTH":
                messages.append({
                    "role": "user",
                    "content": (
                        "Now combine the "
                        "document information "
                        "AND the tool results "
                        "into one complete "
                        "answer. Clearly show "
                        "both sources.")
                })

            # Get final answer
            final_response = (
                self.client.chat
                .completions.create(
                    model="gpt-4o",
                    messages=messages,
                    temperature=0.3
                ))

            result["answer"] = (
                final_response
                .choices[0]
                .message.content)

        else:
            # ─────────────────────────────
            # No tool calls = RAG answer
            # AI answered from document!
            # ─────────────────────────────
            result["tool_used"] = "RAG"
            result["routing_reason"] = (
                "Found answer in "
                "uploaded documents")
            result["answer"] = (
                response_message.content)

        # Save RAG context for display
        if rag_context:
            result["rag_context"] = rag_context

        return result