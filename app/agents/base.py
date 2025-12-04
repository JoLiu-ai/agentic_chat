from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from app.agents.state import AgentState
from typing import List
from langchain_core.tools import BaseTool

class BaseAgent:
    def __init__(self, name: str, model: ChatOpenAI, system_prompt: str, tools: List[BaseTool] = []):
        self.name = name
        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        if self.tools:
            self.model = self.model.bind_tools(self.tools)
            
        self.runnable = self.prompt | self.model

    def __call__(self, state: AgentState):
        """
        Entry point for the graph node.
        """
        messages = state["messages"]
        response = self.runnable.invoke({"messages": messages})
        return {"messages": [response]}
