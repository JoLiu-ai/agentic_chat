from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Dict, Union
from pathlib import Path
from enum import Enum
import os

# 项目根目录（相对于config.py文件）
BASE_DIR = Path(__file__).parent.parent.parent


class Environment(str, Enum):
    """环境类型枚举"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class Settings(BaseSettings):
    # 基础配置
    PROJECT_NAME: str = "Agentic Chat"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "多Agent智能对话系统"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True  # 默认开启调试模式
    
    # 功能开关
    DOCS_ENABLED: bool = True  # API文档开关
    OPENAPI_ENABLED: bool = True  # OpenAPI开关
    SERVE_STATIC: bool = False  # 静态文件服务开关（前后端分离，建议关闭）
    
    # 前端配置（前后端分离）
    FRONTEND_URL: str = "http://localhost:3000"  # 前端地址
    
    # 路径配置（可通过环境变量覆盖）
    UI_DIR: str | None = None  # UI目录路径，默认使用项目根目录下的ui
    STATIC_DIR: str | None = None  # 静态文件目录路径
    LOG_DIR: str | None = None  # 日志目录路径
    
    # 日志配置
    LOG_LEVEL: str = "DEBUG"  # 默认DEBUG级别，显示所有日志
    LOG_FILE_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    LOG_FILE_BACKUP_COUNT: int = 5
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s"
    
    # CORS配置（支持环境变量，用逗号分隔）
    CORS_ENABLED: bool = True
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://localhost:8000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: Union[List[str], str] = ["*"]
    CORS_ALLOW_HEADERS: Union[List[str], str] = ["*"]
    
    @field_validator("CORS_ORIGINS", "CORS_ALLOW_METHODS", "CORS_ALLOW_HEADERS", mode="before")
    @classmethod
    def parse_list(cls, v):
        """解析列表类型的环境变量（支持逗号分隔的字符串）"""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v
    
    # 安全配置
    ALLOWED_HOSTS: Union[List[str], str] = ["*"]  # 生产环境应设置具体域名
    GZIP_ENABLED: bool = True
    GZIP_MIN_SIZE: int = 1000  # 字节
    
    # 限流配置
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "60/minute"  # slowapi 格式
    
    # 性能监控配置
    SLOW_QUERY_THRESHOLD: float = 1.0  # 秒
    SLOW_REQUEST_THRESHOLD: float = 2.0  # 秒
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///data/agentic_chat.db"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    
    # OpenAI配置
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str | None = None  # 可选，用于自定义API端点
    OPENAI_MODEL: str = "gpt-4o"  # 默认模型
    
    # 其他API
    ANTHROPIC_API_KEY: str | None = None
    TAVILY_API_KEY: str | None = None

    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.ENVIRONMENT == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.ENVIRONMENT == Environment.PRODUCTION
    
    @property
    def is_testing(self) -> bool:
        """是否为测试环境"""
        return self.ENVIRONMENT == Environment.TESTING

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()


def get_ui_path() -> Path:
    """获取UI目录路径"""
    if settings.UI_DIR:
        return Path(settings.UI_DIR).resolve()
    return BASE_DIR / "ui"


def get_static_path() -> Path:
    """获取静态文件目录路径"""
    if settings.STATIC_DIR:
        return Path(settings.STATIC_DIR).resolve()
    return get_ui_path() / "static"


def get_index_html_path() -> Path:
    """获取index.html文件路径"""
    return get_ui_path() / "index.html"


def get_log_dir() -> Path:
    """获取日志目录路径"""
    if settings.LOG_DIR:
        log_dir = Path(settings.LOG_DIR).resolve()
    else:
        log_dir = BASE_DIR / "logs"
    
    # 确保日志目录存在
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir

# 可用模型列表配置
# 可以从环境变量 AVAILABLE_MODELS 读取，格式: "gpt-4o,GPT-4o;gpt-4-turbo,GPT-4 Turbo;gpt-3.5-turbo,GPT-3.5"
# 格式: "value1,Label1;value2,Label2;..."
def get_available_models() -> List[Dict[str, str]]:
    """
    获取可用模型列表
    优先从环境变量读取，否则使用默认值
    """
    models_env = os.getenv("AVAILABLE_MODELS", "")
    
    if models_env:
        # 解析环境变量: "gpt-4o,GPT-4o;gpt-4-turbo,GPT-4 Turbo"
        models = []
        for item in models_env.split(";"):
            if "," in item:
                value, label = item.split(",", 1)
                models.append({"value": value.strip(), "label": label.strip()})
        if models:
            return models
    
    # 默认模型列表
    return [
        {"value": "gpt-4o", "label": "GPT-4o"},
        {"value": "gpt-4-turbo", "label": "GPT-4 Turbo"},
        {"value": "gpt-3.5-turbo", "label": "GPT-3.5"},
        {"value": "deepseek-chat", "label": "DeepSeek Chat"},
        {"value": "claude-3-5-sonnet", "label": "Claude 3.5 Sonnet"},
        {"value": "gemini-3-flash", "label": "Gemini 3 Flash"},
    ]
