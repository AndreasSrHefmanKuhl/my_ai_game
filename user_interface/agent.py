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
"""TO DO (hier kommen die tool für den agent hin, damit er weiß später wie zu reagieren(funkti0nen sind erwünscht))"""
#TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

#  Setup Tools
#tavily_tool = TavilySearchResults(max_results=5)
#tools = [tavily_tool]

#  Define State
class AgentState(TypedDict):
    #  appends new messages to the existing list
    messages: Annotated[Sequence[BaseMessage], operator.add]

#  Setup Model
model = ChatOpenAI(
    temperature=0,
    model="gpt-3.5-turbo",
    streaming=True
).bind_tools(tools)

#  Define Nodes
def call_model(state: AgentState):
    print("--- Calling Model ---")
    response = model.invoke(state["messages"])
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

#  Run Execution
if __name__ == "__main__":
    user_prompt = input("Was ist deine Frage? ")

    initial_state = {
        "messages": [HumanMessage(content=user_prompt)]
    }

    # Stream the events
    for output in app.stream(initial_state):
        for key, value in output.items():
            print(f"\n[Node: {key}]")
            for message in value.get("messages", []):
                message.pretty_print()
            print("-" * 20)