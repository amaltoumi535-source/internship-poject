from app.modules.orchestrator.agent import search_agent
from langchain_core.messages import HumanMessage

result = search_agent.invoke({"messages": [HumanMessage(content="What does the report say about risk mitigation strategies?")]})

for msg in result["messages"]:
    print(f"--- {msg.__class__.__name__} ---")
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        print("TOOL CALLS:", msg.tool_calls)
    print(msg.content)
    print()
