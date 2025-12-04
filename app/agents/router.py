from typing import Literal
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from app.agents.state import AgentState
from langchain_core.pydantic_v1 import BaseModel, Field

# Define the routing output structure
class RouteResponse(BaseModel):
    next: Literal["researcher", "coder", "general_assistant"] = Field(
        ..., description="The next agent to route the request to."
    )

class RouterAgent:
    def __init__(self, model: ChatOpenAI):
        self.model = model
        self.system_prompt = (
            "You are a router. Your job is to route the user's request to the appropriate agent.\n"
            "Available agents:\n"
            "- researcher: For questions requiring web search or factual lookup.\n"
            "- coder: For questions involving writing or debugging code.\n"
            "- general_assistant: For general chit-chat or questions not fitting other categories."
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        # Bind the structured output
        self.runnable = self.prompt | self.model.with_structured_output(RouteResponse)

    def __call__(self, state: AgentState):
        messages = state["messages"]
        response = self.runnable.invoke({"messages": messages})
        return {"next": response.next}
