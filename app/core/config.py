from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Agentic Chat"
    API_V1_STR: str = "/api/v1"
    
    # OpenAI配置
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str | None = None  # 可选，用于自定义API端点
    OPENAI_MODEL: str = "gpt-4o"  # 默认模型
    
    # 其他API
    ANTHROPIC_API_KEY: str | None = None
    TAVILY_API_KEY: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
