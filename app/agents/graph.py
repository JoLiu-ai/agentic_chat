from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.base import BaseAgent
from app.agents.router import RouterAgent
from app.agents.researcher import get_researcher_agent
from app.agents.coder import get_coder_agent
from langchain_openai import ChatOpenAI

# Initialize Model
llm = ChatOpenAI(model="gpt-4o")

# Initialize Agents
router_agent = RouterAgent(model=llm)

researcher_agent = get_researcher_agent(model=llm)
coder_agent = get_coder_agent(model=llm)

general_agent = BaseAgent(
    name="general_assistant",
    model=llm,
    system_prompt="You are a helpful general assistant."
)

# Define Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("router", router_agent)
workflow.add_node("researcher", researcher_agent)
workflow.add_node("coder", coder_agent)
workflow.add_node("general_assistant", general_agent)

# Define Conditional Logic
def route_next(state: AgentState):
    return state["next"]

# Add Edges
workflow.set_entry_point("router")

workflow.add_conditional_edges(
    "router",
    route_next,
    {
        "researcher": "researcher",
        "coder": "coder",
        "general_assistant": "general_assistant"
    }
)

workflow.add_edge("researcher", END)
workflow.add_edge("coder", END)
workflow.add_edge("general_assistant", END)

# Compile Graph
graph = workflow.compile()
