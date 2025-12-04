from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.agents.graph import graph
from app.services.session import SessionService
from langchain_core.messages import HumanMessage

router = APIRouter()
session_service = SessionService()

class ChatRequest(BaseModel):
    message: str
    session_id: str
    user_id: str = "default_user"

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Ensure session exists
        session_service.create_session(request.session_id, request.user_id)
        
        # Add user message to DB
        session_service.add_message(request.session_id, "user", request.message)
        
        # Get context (history)
        history = session_service.get_messages(request.session_id)
        # Convert to LangChain format (simplified for now)
        # In a real app, we'd convert dicts to HumanMessage/AIMessage
        
        inputs = {"messages": [HumanMessage(content=request.message)]}
        result = graph.invoke(inputs)
        response_content = result['messages'][-1].content
        
        # Add assistant message to DB
        session_service.add_message(request.session_id, "assistant", response_content)
        
        return {"response": response_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
