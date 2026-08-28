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

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.7, max_retries=5)

_NO_FABRICATION_RULE = (
    "CRITICAL: You MUST base all answers ONLY on what your tools return. "
    "NEVER invent, complete, or extrapolate information. If a tool returns nothing relevant, "
    "say so explicitly. Your credibility depends on being honest about what you found."
)

ORCHESTRATOR_SYSTEM_PROMPT = (
    "You are an INTELLIGENT document assistant. Your workflow:\n\n"
    "1. LISTEN carefully to what the user is asking\n"
    "2. SEARCH documents FIRST using search_agent_tool with the exact question\n"
    "3. ANALYZE the results deeply - don't just repeat them\n"
    "4. SYNTHESIZE information across multiple sources\n"
    "5. EXPLAIN clearly with examples and context from documents\n"
    "6. BE HONEST if information isn't in documents\n\n"
    "IMPORTANT - OUTPUT FORMAT:\n"
    "- Provide intelligent analysis and insights\n"
    "- Use clear narratives and summaries\n"
    "- DO NOT include chunk references, technical citations, or internal metadata\n"
    "- DO NOT show 'Chunk 129', 'Chunk 131' etc. in responses\n"
    "- Make responses read naturally - like talking to a knowledgeable colleague\n"
    "- If you need to cite something, reference the document name, not chunks\n\n"
    "When you delegate to search_agent_tool:\n"
    "- Pass the COMPLETE user question, not a shortened version\n"
    "- Wait for the results\n"
    "- ANALYZE and interpret the results intelligently\n"
    "- Don't just quote - add value through analysis\n\n"
    + _NO_FABRICATION_RULE
)
search_agent = create_agent(
    model=llm,
    tools=SEARCH_TOOLS,
    system_prompt=(
        "You are the SEARCH SPECIALIST. Your job is to find relevant content in documents.\n\n"
        "SEARCH STRATEGY:\n"
        "1. First: Try semantic search with the full question\n"
        "2. If weak results: Try keyword variations\n"
        "3. If still nothing: Try single strong keywords\n"
        "4. Report EXACTLY what you found - cite specific chunks\n\n"
        "Be thorough and try multiple approaches. Better to do 3 searches than miss information.\n\n"
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

ORCHESTRATOR_TOOLS = [
    search_agent_tool,
    analysis_agent_tool,
]

orchestrator = create_agent(
    model=llm,
    tools=ORCHESTRATOR_TOOLS,
    system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
)

if __name__ == "__main__":
    result = orchestrator.invoke({"messages": [HumanMessage(content="What's in the documents?")]})
    print(result["messages"][-1].content)