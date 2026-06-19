from .model_metadata import create_model_metadata

MINIMAX_MODELS_DETAILED = [
    create_model_metadata(provider="MiniMax", name="MiniMax-M3", icon="MiniMax", tool_calling=True),
    create_model_metadata(provider="MiniMax", name="MiniMax-M2.7", icon="MiniMax", tool_calling=True),
    create_model_metadata(provider="MiniMax", name="MiniMax-M2.7-highspeed", icon="MiniMax", tool_calling=True),
    create_model_metadata(provider="MiniMax", name="MiniMax-M2.5", icon="MiniMax", tool_calling=True),
    create_model_metadata(provider="MiniMax", name="MiniMax-M2.5-highspeed", icon="MiniMax", tool_calling=True),
    create_model_metadata(provider="MiniMax", name="MiniMax-M2.1", icon="MiniMax", tool_calling=True),
    create_model_metadata(provider="MiniMax", name="MiniMax-M2.1-highspeed", icon="MiniMax", tool_calling=True),
    create_model_metadata(provider="MiniMax", name="MiniMax-M2", icon="MiniMax", tool_calling=True),
]

MINIMAX_MODELS = [m["name"] for m in MINIMAX_MODELS_DETAILED]

TOOL_CALLING_SUPPORTED_MINIMAX_MODELS = [
    m["name"] for m in MINIMAX_MODELS_DETAILED if m.get("tool_calling", False)
]

DEFAULT_MINIMAX_API_URL = "https://api.minimax.io/anthropic"
