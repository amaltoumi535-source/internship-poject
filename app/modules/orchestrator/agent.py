"""Orchestrateur: supervise les 5 agents spécialisés avec intelligence accrue."""

import os
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

from app.modules.ingestion.agent import INGESTION_TOOLS
from app.modules.storage.agent import STORAGE_TOOLS
from app.modules.analysis.agent import ANALYSIS_TOOLS
from app.modules.search.agent import SEARCH_TOOLS
from app.modules.reporting.agent import REPORTING_TOOLS
from app.modules.analysis.spreadsheet_tools import SPREADSHEET_TOOLS

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.7, max_retries=5)

_NO_FABRICATION_RULE = (
    "CRITICAL: You MUST base all answers ONLY on what your tools return. "
    "NEVER invent, complete, or extrapolate information. If a tool returns nothing relevant, "
    "say so explicitly. Your credibility depends on being honest about what you found."
)

ORCHESTRATOR_SYSTEM_PROMPT = (
    "You are an INTELLIGENT document assistant coordinating several specialists: "
    "search, analysis, ingestion, storage, reporting, and spreadsheet analysis.\n\n"
    "1. LISTEN carefully to what the user is asking\n"
    "2. PICK the right specialist(s) for the request:\n"
    "   - search_agent_tool: finding relevant content in documents\n"
    "   - analysis_agent_tool: deep interpretation, patterns, insights\n"
    "   - ingestion_agent_tool: questions about uploading/processing documents\n"
    "   - storage_agent_tool: questions about which documents/files exist\n"
    "   - reporting_agent_tool: stats, overviews, per-document reports, exports\n"
    "   - analyze_spreadsheet_tool: real numeric analysis of spreadsheet documents "
    "(totals, top products, revenue by month, top countries) — ALWAYS use this for any "
    "question involving numbers, sales, revenue, totals, or trends on a spreadsheet/Excel "
    "document. Do NOT use search_agent_tool for these questions — search only returns small "
    "text snippets, not real numbers. This tool requires a document_id (an integer). If the "
    "user refers to a document by name instead of ID, FIRST call storage_agent_tool to look "
    "up its document_id, THEN call analyze_spreadsheet_tool with that ID.\n"
    "3. SEARCH documents FIRST using search_agent_tool when the question is about general document content\n"
    "4. SYNTHESIZE information across whichever specialists you used\n"
    "5. EXPLAIN clearly with examples and context from documents\n"
    "6. BE HONEST if information isn't available\n\n"
    "IMPORTANT - OUTPUT FORMAT:\n"
    "- Provide intelligent analysis and insights\n"
    "- Use clear narratives and summaries\n"
    "- DO NOT include chunk references, technical citations, or internal metadata\n"
    "- DO NOT show 'Chunk 129', 'Chunk 131' etc. in responses\n"
    "- Make responses read naturally - like talking to a knowledgeable colleague\n"
    "- If you need to cite something, reference the document name, not chunks\n\n"
    "When delegating to any specialist tool:\n"
    "- Pass the COMPLETE user question, not a shortened version\n"
    "- Wait for the results\n"
    "- ANALYZE and interpret the results intelligently\n"
    "- Don't just quote - add value through analysis\n"
    "- Call each specialist only once per question unless its result was clearly insufficient\n\n"
    + _NO_FABRICATION_RULE
)

search_agent = create_agent(
    model=llm,
    tools=SEARCH_TOOLS,
    system_prompt=(
        "You are the SEARCH SPECIALIST. Your job is to find relevant content in documents.\n\n"
        "SEARCH STRATEGY:\n"
        "1. First: Try semantic search with the full question\n"
        "2. If results are relevant, STOP and report them — do not search again unnecessarily\n"
        "3. Only try a second search (keyword variation) if the first genuinely returned nothing useful\n"
        "4. Report EXACTLY what you found - cite specific chunks\n\n"
        "Prefer ONE well-chosen search over several. Extra searches cost time and context — "
        "only search again when the first result is truly insufficient.\n\n"
        + _NO_FABRICATION_RULE
    ),
)

analysis_agent = create_agent(
    model=llm,
    tools=ANALYSIS_TOOLS,
    system_prompt=(
        "You are the ANALYSIS SPECIALIST. You deeply analyze document content.\n"
        "Extract insights, patterns, and meaning - don't just summarize.\n"
        + _NO_FABRICATION_RULE
    ),
)

ingestion_agent = create_agent(
    model=llm,
    tools=INGESTION_TOOLS,
    system_prompt=(
        "You are the INGESTION SPECIALIST. You handle questions about how documents "
        "are uploaded, parsed, and chunked. Use ONE tool call unless it clearly fails.\n"
        + _NO_FABRICATION_RULE
    ),
)

storage_agent = create_agent(
    model=llm,
    tools=STORAGE_TOOLS,
    system_prompt=(
        "You are the STORAGE SPECIALIST. You handle questions about which documents/files "
        "exist and how they are stored. Use ONE tool call unless it clearly fails.\n"
        + _NO_FABRICATION_RULE
    ),
)

reporting_agent = create_agent(
    model=llm,
    tools=REPORTING_TOOLS,
    system_prompt=(
        "You are the REPORTING SPECIALIST. You handle stats, overviews, per-document "
        "reports, and exports. Use ONE tool call unless it clearly fails.\n"
        + _NO_FABRICATION_RULE
    ),
)


@tool
def search_agent_tool(query: str) -> str:
    """Search documents intelligently with multiple strategies."""
    result = search_agent.invoke({"messages": [HumanMessage(content=query)]})
    return result["messages"][-1].content


@tool
def analysis_agent_tool(query: str) -> str:
    """Deep analysis and interpretation of document content."""
    result = analysis_agent.invoke({"messages": [HumanMessage(content=query)]})
    return result["messages"][-1].content


@tool
def ingestion_agent_tool(query: str) -> str:
    """Handle questions about document upload/parsing/chunking."""
    result = ingestion_agent.invoke({"messages": [HumanMessage(content=query)]})
    return result["messages"][-1].content


@tool
def storage_agent_tool(query: str) -> str:
    """Handle questions about which documents exist and how they're stored."""
    result = storage_agent.invoke({"messages": [HumanMessage(content=query)]})
    return result["messages"][-1].content


@tool
def reporting_agent_tool(query: str) -> str:
    """Handle stats, overviews, per-document reports, and exports."""
    result = reporting_agent.invoke({"messages": [HumanMessage(content=query)]})
    return result["messages"][-1].content


ORCHESTRATOR_TOOLS = [
    search_agent_tool,
    analysis_agent_tool,
    ingestion_agent_tool,
    storage_agent_tool,
    reporting_agent_tool,
] + SPREADSHEET_TOOLS

orchestrator = create_agent(
    model=llm,
    tools=ORCHESTRATOR_TOOLS,
    system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
)

if __name__ == "__main__":
    result = orchestrator.invoke({"messages": [HumanMessage(content="What's in the documents?")]})
    print(result["messages"][-1].content)