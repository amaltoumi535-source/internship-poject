# test_tool_calling.py
from langchain_groq import ChatGroq
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """Retourne la météo pour une ville donnée."""
    return f"Il fait beau à {city}"

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
llm_with_tools = llm.bind_tools([get_weather])

response = llm_with_tools.invoke("Quel temps fait-il à Sousse ?")
print(response.tool_calls)