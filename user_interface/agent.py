from typing import Annotated, Sequence, TypedDict
import operator
import os
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
load_dotenv()

# Ensure keys are set in your .env file
OPENAI_API_KEY = os.getenv("OAI_KEY")
"""TO DO (hier kommen die tool für den agent hin, damit er weiß später wie zu reagieren(funktionen sind erwünscht))"""

tools =[]
#  Define State
class AgentState(TypedDict):

    messages: Annotated[Sequence[BaseMessage], operator.add]

#  Setup Model
model = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    temperature=1.2,
    model= "gpt-4o-mini",
    streaming=True
).bind_tools(tools)

#  Define Nodes
def call_model(state: AgentState):
    # System-Anweisung hinzufügen
    system_message = {
        "role": "system",
        "content": "You are an API. answer ONLY with a python-list, NO text,NO explanation"
    }
    messages = [system_message] + list(state["messages"])

    print("--- Calling Model ---")
    response = model.invoke(messages)
    return {"messages": [response]}

#  Build Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("ai", call_model)
workflow.add_node("tools", ToolNode(tools))

# Set Entry Point
workflow.set_entry_point("ai")

# Define Transitions
workflow.add_conditional_edges(
    "ai",
    tools_condition,
)

workflow.add_edge("tools", "ai")

# Compile
app = workflow.compile()


