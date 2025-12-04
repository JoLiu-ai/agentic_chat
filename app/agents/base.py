from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from app.agents.state import AgentState

class BaseAgent:
    def __init__(self, name: str, model: ChatOpenAI, system_prompt: str):
        self.name = name
        self.model = model
        self.system_prompt = system_prompt
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        self.runnable = self.prompt | self.model

    def __call__(self, state: AgentState):
        """
        Entry point for the graph node.
        """
        messages = state["messages"]
        response = self.runnable.invoke({"messages": messages})
        return {"messages": [response]}
