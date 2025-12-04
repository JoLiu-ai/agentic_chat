from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.core.config import settings
from app.agents.graph import graph
from langchain_core.messages import HumanMessage

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def root():
    return {"message": "Welcome to Agentic Chat API"}

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        inputs = {"messages": [HumanMessage(content=request.message)]}
        result = graph.invoke(inputs)
        return {"response": result['messages'][-1].content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
