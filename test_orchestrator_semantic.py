from app.modules.orchestrator.agent import orchestrator
from langchain_core.messages import HumanMessage

result = orchestrator.invoke({"messages": [HumanMessage(content="What does the report say about risk mitigation strategies?")]})
print(result["messages"][-1].content)
