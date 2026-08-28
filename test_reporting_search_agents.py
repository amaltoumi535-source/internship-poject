from app.modules.reporting.agent import reporting_overview_tool
from app.modules.search.agent import search_chunks_tool

print("--- reporting ---")
print(reporting_overview_tool.invoke({}))

print("--- search ---")
print(search_chunks_tool.invoke({"query": "sample"}))