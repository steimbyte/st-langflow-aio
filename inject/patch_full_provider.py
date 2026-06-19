#!/usr/bin/env python3
"""Patch all necessary Langflow files to register MiniMax as a Global Model Provider.

Files patched:
1. lfx/base/models/minimax_constants.py (NEW)
2. lfx/base/models/model_metadata.py (add MODEL_PROVIDER_METADATA["MiniMax"])
3. lfx/base/models/unified_models/provider_queries.py (add MINIMAX_MODELS_DETAILED)
4. lfx/base/models/model_input_constants.py (add to MODEL_PROVIDERS_DICT + MODEL_PROVIDERS_LIST)
5. lfx/base/models/unified_models/instantiation.py (add MiniMax base_url support to get_llm)
"""
import sys
from pathlib import Path

SITE = None
for p in Path(sys.prefix).glob("lib/python*/site-packages"):
    if (p / "lfx" / "base" / "models" / "model_input_constants.py").exists():
        SITE = p
        break
if not SITE:
    print("ERROR: site-packages not found")
    sys.exit(1)

MODELS = SITE / "lfx" / "base" / "models"
UM = MODELS / "unified_models"
print(f"Patching in: {SITE}")

# ============================================================================
# 1. minimax_constants.py
# ============================================================================
(MODELS / "minimax_constants.py").write_text('''from .model_metadata import create_model_metadata

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
TOOL_CALLING_SUPPORTED_MINIMAX_MODELS = [m["name"] for m in MINIMAX_MODELS_DETAILED if m.get("tool_calling", False)]
DEFAULT_MINIMAX_API_URL = "https://api.minimax.io/anthropic"
''')
print("OK  minimax_constants.py created")

# ============================================================================
# 2. model_metadata.py - MODEL_PROVIDER_METADATA["MiniMax"]
# ============================================================================
f = MODELS / "model_metadata.py"
content = f.read_text()

# Drop old entry if present
if '"MiniMax":' in content:
    # Remove old insertion (find from MiniMax to next provider)
    import re
    content = re.sub(
        r'\s*"MiniMax":\s*\{[^}]*(?:\{[^}]*\}[^}]*)*\},?\s*',
        '\n    ',
        content,
        count=1
    )

# Add MiniMax WITH base_url mapping via a second variable
# (Anthropic SDK uses 'anthropic_api_url' param, OpenAI uses 'base_url')
minimax_entry = '''
    "MiniMax": {
        "icon": "MiniMax",
        "max_tokens_field_name": "max_tokens",
        "base_url": "https://api.minimax.io/anthropic",
        "variables": [
            {
                "variable_name": "MiniMax API Key",
                "variable_key": "MINIMAX_API_KEY",
                "required": True,
                "is_secret": True,
                "is_list": False,
                "options": [],
                "langchain_param": "api_key",
                "component_metadata": {
                    "mapping_field": "api_key",
                    "required": False,
                    "advanced": True,
                    "info": "Falls back to MINIMAX_API_KEY environment variable",
                },
            },
            {
                "variable_name": "MiniMax API Base",
                "variable_key": "MINIMAX_BASE_URL",
                "required": False,
                "is_secret": False,
                "is_list": False,
                "options": [],
                "langchain_param": "anthropic_api_url",
                "component_metadata": {
                    "mapping_field": "anthropic_api_url",
                    "required": False,
                    "advanced": True,
                    "info": "Anthropic-compatible endpoint URL",
                },
            },
        ],
        "api_docs_url": "https://platform.minimax.io/docs/api-reference/text-anthropic-api",
        "mapping": {
            "model_class": "ChatAnthropic",
            "model_param": "model",
        },
    },
'''

# Insert before OpenRouter (keep alphabetical-ish ordering)
content = content.replace('    "OpenRouter": {', minimax_entry + '    "OpenRouter": {', 1)
f.write_text(content)
print("OK  model_metadata.py patched")

# ============================================================================
# 3. provider_queries.py
# ============================================================================
f = UM / "provider_queries.py"
content = f.read_text()

if 'minimax_constants' not in content:
    content = content.replace(
        "from lfx.base.models.openrouter_constants import OPENROUTER_MODELS_DETAILED",
        "from lfx.base.models.openrouter_constants import OPENROUTER_MODELS_DETAILED\nfrom lfx.base.models.minimax_constants import MINIMAX_MODELS_DETAILED",
        1
    )
    content = content.replace(
        "    WATSONX_MODELS_DETAILED,\n]",
        "    WATSONX_MODELS_DETAILED,\n    MINIMAX_MODELS_DETAILED,\n]",
        1
    )
    f.write_text(content)
    print("OK  provider_queries.py patched")
else:
    print("SKIP provider_queries.py")

# ============================================================================
# 4. model_input_constants.py
# ============================================================================
f = MODELS / "model_input_constants.py"
content = f.read_text()

if '_get_minimax_inputs_and_fields' not in content:
    minimax_func = '''

def _get_minimax_inputs_and_fields():
    try:
        from lfx.components.minimax.minimax import MiniMaxModelComponent
        minimax_inputs = get_filtered_inputs(MiniMaxModelComponent)
    except ImportError:
        minimax_inputs = []
    return minimax_inputs, create_input_fields_dict(minimax_inputs, "")

'''
    content = content.replace(
        "MODEL_PROVIDERS_DICT: dict[str, ModelProvidersDict] = {}",
        minimax_func + "MODEL_PROVIDERS_DICT: dict[str, ModelProvidersDict] = {}",
        1
    )

    minimax_block = '''
try:
    from lfx.components.minimax.minimax import MiniMaxModelComponent
    minimax_inputs, minimax_fields = _get_minimax_inputs_and_fields()
    if minimax_inputs:
        MODEL_PROVIDERS_DICT["MiniMax"] = {
            "fields": minimax_fields,
            "inputs": minimax_inputs,
            "prefix": "",
            "component_class": MiniMaxModelComponent(),
            "icon": MiniMaxModelComponent.icon,
            "is_active": True,
        }
except Exception:
    pass

'''
    content = content.replace(
        "# Expose only active providers",
        minimax_block + "# Expose only active providers",
        1
    )

    old_list = 'MODEL_PROVIDERS_LIST = ["Anthropic", "Google Generative AI", "OpenAI", "IBM watsonx.ai", "Ollama"]'
    new_list = 'MODEL_PROVIDERS_LIST = ["Anthropic", "Google Generative AI", "MiniMax", "OpenAI", "IBM watsonx.ai", "Ollama"]'
    content = content.replace(old_list, new_list)
    f.write_text(content)
    print("OK  model_input_constants.py patched")
else:
    print("SKIP model_input_constants.py")

# ============================================================================
# 5. CRITICAL: unified_models/instantiation.py - Add MiniMax to get_llm()
#    This is the function that ACTUALLY builds the LLM, and it doesn't
#    know about MiniMax's custom base URL. We need to add a special case
#    for MiniMax similar to OpenRouter.
# ============================================================================
f = UM / "instantiation.py"
content = f.read_text()

# Find the OpenRouter block and add MiniMax right after it
if 'elif provider == "OpenRouter":' in content and 'provider == "MiniMax"' not in content:
    # Find the block that handles OpenRouter
    # It looks like:
    #   elif provider == "OpenRouter":
    #       ...
    #       if default_headers:
    #           kwargs["default_headers"] = default_headers
    # We need to add MiniMax after this block

    minimax_block = '''    elif provider == "MiniMax":
        # MiniMax exposes an Anthropic-SDK-compatible endpoint.
        # ChatAnthropic uses 'anthropic_api_url' to override the base URL.
        provider_meta = model_provider_metadata.get(provider, {})
        # Look for the base URL in: variable_key value > env var > provider meta default
        provider_vars = unified_models_module.get_all_variables_for_provider(user_id, provider)
        base_url_value = (
            provider_vars.get("MINIMAX_BASE_URL")
            or _env_if_allowed("MINIMAX_BASE_URL")
            or provider_meta.get("base_url")
        )
        if base_url_value:
            kwargs["anthropic_api_url"] = base_url_value

'''
    # Insert after the OpenRouter block, before the next "try:"
    # The structure is: ...OpenRouter block...   try:
    # Find the "    try:" after the OpenRouter block
    content = content.replace(
        '        if default_headers:\n            kwargs["default_headers"] = default_headers\n\n    try:\n        return model_class(**kwargs)',
        '        if default_headers:\n            kwargs["default_headers"] = default_headers\n\n' + minimax_block + '    try:\n        return model_class(**kwargs)',
        1
    )
    f.write_text(content)
    print("OK  instantiation.py patched (MiniMax base_url)")
else:
    if 'provider == "MiniMax"' in content:
        print("SKIP instantiation.py (already patched)")
    else:
        print("WARN  Could not find OpenRouter block in instantiation.py")

print("\nDone! All MiniMax patches applied.")
