"""
Configuration API Endpoints
Provides configuration data to frontend
"""
from fastapi import APIRouter
from app.core.config import get_available_models, settings

router = APIRouter()

@router.get("/config/models")
async def get_models():
    """
    Get available models list
    Returns models from config and default model from settings
    """
    models = get_available_models()
    # Use OPENAI_MODEL from settings as default, or first model if not found
    default_model = settings.OPENAI_MODEL
    # Verify default model is in the list, if not use first one
    model_values = [m["value"] for m in models]
    if default_model not in model_values:
        default_model = models[0]["value"] if models else "gpt-4o"
    
    return {
        "models": models,
        "default": default_model
    }

