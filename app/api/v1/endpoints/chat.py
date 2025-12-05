from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.session import SessionService
from app.services.message import MessageService
from app.db.database import get_db
from app.agents.graph import graph  # Import compiled graph
from langchain_core.messages import HumanMessage

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: str
    user_id: str = "default_user"
    model: Optional[str] = "gpt-4o"

@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat endpoint with message persistence
    """
    try:
        # Check if session exists
        existing = SessionService.get_session(request.session_id)
        if not existing:
            # Since the frontend generates session_id, we need to create with that ID
            # But our create_session generates a new ID, so we need to check if it's a valid format
            if request.session_id.startswith('session_'):
                # Frontend-generated session, create it
                print(f"Creating new session with ID from frontend: {request.session_id}")
                # We need to modify create_session to accept session_id or create a version that does
                # For now, let's use a workaround
                with get_db() as db:
                    from app.db.models import Session
                    new_session = Session(
                        session_id=request.session_id,
                        user_id=request.user_id or "default_user",
                        title="新对话"
                    )
                    db.add(new_session)
            else:
                # Create new session with auto-generated ID
                request.session_id = SessionService.create_session(
                    user_id=request.user_id,
                    title="新对话"
                )
            print(f"✅ Created new session: {request.session_id}")
        
        # Get message count BEFORE saving user message
        message_count = MessageService.get_message_count(request.session_id)
        
        # Save user message to database
        MessageService.create_message(
            session_id=request.session_id,
            role="user",
            content=request.message,
            model=request.model
        )
        
        # Run the workflow
        initial_state = {
            "messages": [HumanMessage(content=request.message)],
            "next": ""
        }
        result = graph.invoke(initial_state)
        response_content = result['messages'][-1].content
        
        # Detect agent type
        agent_type = "general_assistant"
        if "搜索" in str(result.get('next', '')):
            agent_type = "researcher"
        elif "代码" in response_content or "```" in response_content:
            agent_type = "coder"
        
        # Save assistant message
        MessageService.create_message(
            session_id=request.session_id,
            role="assistant",
            content=response_content,
            agent_type=agent_type,
            model=request.model
        )
        
        # Auto-generate title for first message (message_count was 0 before user message)
        if message_count == 0:
            SessionService.auto_generate_title(request.session_id, request.message)
        
        # Update session timestamp
        SessionService.update_session_timestamp(request.session_id)
        
        return {
            "response": response_content,
            "agent_type": agent_type,
            "session_id": request.session_id
        }
    except Exception as e:
        print(f"❌ Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
