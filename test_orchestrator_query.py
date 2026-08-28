import sys
from app.modules.orchestrator.agent import orchestrator
from langchain_core.messages import HumanMessage

query = sys.argv[1]

result = orchestrator.invoke({"messages": [HumanMessage(content=query)]})

for msg in result["messages"]:
    print(f"--- {msg.__class__.__name__} ---")
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        print("TOOL CALLS:", msg.tool_calls)
    print(msg.content)
    print()
