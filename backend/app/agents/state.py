from typing import TypedDict, Annotated, Sequence, Optional
import operator
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str
    session_id: Optional[str]  # 用于路由日志
