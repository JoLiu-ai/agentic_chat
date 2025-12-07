from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.session import SessionService
from app.services.message import MessageService
from app.db.database import get_db
from app.agents.graph import graph  # Import compiled graph
from app.core.logging import get_logger
from langchain_core.messages import HumanMessage

logger = get_logger(__name__)

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
    logger.info(f"收到聊天请求: session_id={request.session_id}, message_length={len(request.message)}")
    
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
            logger.info(f"创建新会话: session_id={request.session_id}")
        
        # Get message count BEFORE saving user message
        message_count = MessageService.get_message_count(request.session_id)
        
        # 检查是否有相同内容的用户消息（用于版本分组）
        existing_user_msg_id = MessageService.find_user_message_by_content(
            request.session_id, 
            request.message
        )
        
        # Save user message to database
        # 如果是相同内容，不创建新的用户消息，而是使用现有的
        if existing_user_msg_id:
            logger.debug(f"找到相同内容的用户消息: message_id={existing_user_msg_id}, 将创建新版本")
            user_message_id = existing_user_msg_id
        else:
            # 创建新的用户消息（parent_id为NULL，表示根节点）
            user_message_id = MessageService.create_message(
                session_id=request.session_id,
                role="user",
                content=request.message,
                model=request.model,
                parent_id=None,  # 用户消息是根节点
                sibling_index=0
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
        
        # Save assistant message as child of user message
        # sibling_index会自动计算（同一父节点下的第几个子节点）
        assistant_message_id = MessageService.create_message(
            session_id=request.session_id,
            role="assistant",
            content=response_content,
            agent_type=agent_type,
            model=request.model,
            parent_id=user_message_id,  # 助手消息的父节点是用户消息
            sibling_index=None  # 自动计算
        )
        
        logger.info(f"助手消息创建成功: message_id={assistant_message_id}, agent_type={agent_type}")
        
        # Auto-generate title for first message (message_count was 0 before user message)
        if message_count == 0:
            SessionService.auto_generate_title(request.session_id, request.message)
            logger.debug(f"自动生成会话标题: session_id={request.session_id}")
        
        # Update session timestamp
        SessionService.update_session_timestamp(request.session_id)
        
        logger.info(f"聊天请求处理完成: session_id={request.session_id}")
        
        return {
            "response": response_content,
            "agent_type": agent_type,
            "session_id": request.session_id
        }
    except Exception as e:
        logger.error(
            f"聊天请求处理失败: session_id={request.session_id}",
            exc_info=True,
            extra={
                "session_id": request.session_id,
                "message": request.message[:100],  # 只记录前100个字符
                "model": request.model
            }
        )
        raise HTTPException(status_code=500, detail=str(e))
