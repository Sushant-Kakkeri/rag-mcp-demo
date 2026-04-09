# router.py
from openai import OpenAI
from mcp_tools import MCP_TOOLS, execute_tool
import json

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

STRICT DECISION RULES:

Use RAG ONLY when:
- User asks about uploaded documents
- Question contains words like:
  'document', 'PDF', 'uploaded file',
  'what does it say', 'according to'
- Question is clearly about stored content

Use MCP ONLY when:
- User needs live/current information
- Weather questions
- General knowledge questions  
- Recent news or events
- No mention of documents at all

Use BOTH when:
- Question contains AND, ALSO, PLUS,
  ADDITIONALLY, AS WELL AS
- User asks about document AND 
  something live at the same time
- Example: "What does document say 
  about X AND find latest news about X"
- Any question combining document 
  content with live information

CRITICAL RULE:
If user uses the word AND between a 
document question and a live question
ALWAYS use BOTH tools together!

ALWAYS start your response with:
🧠 **Routing Decision:** Using [RAG/MCP/BOTH]
because [brief reason]

Then provide your complete answer."""


class SmartRouter:
    def __init__(self, openai_key: str,
                 rag_engine):
        self.client = OpenAI(
            api_key=openai_key)
        self.rag_engine = rag_engine

    def route_and_respond(
            self, query: str,
            chat_history: list) -> dict:
        """
        Intelligently route query to
        RAG, MCP or both
        """
        result = {
            "answer": "",
            "tool_used": "",
            "rag_context": None,
            "mcp_result": None,
            "routing_reason": ""
        }

        # ─────────────────────────────
        # Step 1 - Check for BOTH keywords
        # ─────────────────────────────
        both_keywords = [
            " and ", " also ", " plus ",
            " additionally ", " as well as ",
            " combine ", " along with ",
            " together with "
        ]
        query_lower = query.lower()
        likely_both = any(
            kw in query_lower
            for kw in both_keywords)

        # ─────────────────────────────
        # Step 2 - Check RAG documents
        # ─────────────────────────────
        rag_context = None
        if self.rag_engine.has_documents():
            rag_context = (
                self.rag_engine.search(query))

        # ─────────────────────────────
        # Step 3 - Build messages
        # ─────────────────────────────
        messages = [
            {"role": "system",
             "content": SYSTEM_PROMPT}
        ]

        # Add recent chat history
        for msg in chat_history[-6:]:
            messages.append(msg)

        # Build user content based on context
        if rag_context and likely_both:
            user_content = (
                f"USER QUESTION: {query}\n\n"
                f"IMPORTANT: This question "
                f"uses AND/ALSO — use BOTH "
                f"RAG and MCP tools!\n\n"
                f"DOCUMENT CONTENT FOUND:\n"
                f"{rag_context}\n\n"
                f"Also use MCP tools for "
                f"the live information part.")

        elif rag_context:
            user_content = (
                f"USER QUESTION: {query}\n\n"
                f"RELEVANT DOCUMENT CONTENT:\n"
                f"{rag_context}\n\n"
                f"Use document content if "
                f"relevant, or MCP tools "
                f"if live data is needed.")

        else:
            user_content = (
                f"USER QUESTION: {query}\n\n"
                f"No documents uploaded yet. "
                f"Use MCP tools to answer.")

        messages.append({
            "role": "user",
            "content": user_content
        })

        # ─────────────────────────────
        # Step 4 - Call OpenAI with tools
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
        # Step 5 - Handle MCP tool calls
        # ─────────────────────────────
        if response_message.tool_calls:
            tool_results = []
            tools_used = []

            for tool_call in (
                    response_message.tool_calls):
                tool_name = (
                    tool_call.function.name)
                tool_args = json.loads(
                    tool_call.function.arguments)

                # Execute the tool
                tool_result = execute_tool(
                    tool_name, tool_args)
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "content": tool_result
                })
                tools_used.append(tool_name)
                result["mcp_result"] = (
                    tool_result)

            # Determine RAG + MCP or MCP only
            if rag_context and (
                    likely_both or
                    len(tools_used) > 0):
                result["tool_used"] = "BOTH"
            else:
                result["tool_used"] = "MCP"

            result["routing_reason"] = (
                f"Used MCP tools: "
                f"{', '.join(tools_used)}")

            # Get final response
            messages.append(response_message)
            messages.extend(tool_results)

            # Add RAG context reminder
            # for BOTH responses
            if result["tool_used"] == "BOTH":
                messages.append({
                    "role": "user",
                    "content": (
                        "Now combine the document "
                        "information AND the tool "
                        "results into one complete "
                        "answer. Show both sources "
                        "clearly.")
                })

            final_response = self.client.chat\
                .completions.create(
                    model="gpt-4o",
                    messages=messages,
                    temperature=0.3
                )
            result["answer"] = (
                final_response.choices[0]
                .message.content)

        else:
            # Pure RAG response
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