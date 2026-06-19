#!/usr/bin/env python3
"""Patch model_input_constants.py to add MiniMax as a global model provider."""
import re
import sys
from pathlib import Path

# Find the file
site_packages = next(
    (p for p in Path(sys.prefix).rglob("lfx/base/models/model_input_constants.py")),
    None
)
if not site_packages:
    print("model_input_constants.py not found, skipping patch")
    sys.exit(0)

content = site_packages.read_text()

# 1. Add the _get_minimax_inputs_and_fields() function BEFORE the MODEL_PROVIDERS_DICT definition
minimax_func = '''

def _get_minimax_inputs_and_fields():
    try:
        from lfx.components.minimax.minimax import MiniMaxModelComponent
        minimax_inputs = get_filtered_inputs(MiniMaxModelComponent)
    except ImportError:
        minimax_inputs = []
    return minimax_inputs, create_input_fields_dict(minimax_inputs, "")

'''

# Insert before "MODEL_PROVIDERS_DICT: dict"
if "_get_minimax_inputs_and_fields" not in content:
    content = content.replace(
        "MODEL_PROVIDERS_DICT: dict[str, ModelProvidersDict] = {}",
        minimax_func + "MODEL_PROVIDERS_DICT: dict[str, ModelProvidersDict] = {}"
    )

# 2. Add MiniMax to MODEL_PROVIDERS_DICT (before "# Expose only active providers")
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

if '"MiniMax"' not in content:
    content = content.replace(
        "# Expose only active providers",
        minimax_block + "# Expose only active providers"
    )

# 3. Add "MiniMax" to MODEL_PROVIDERS_LIST
if '"MiniMax"' not in content or 'MODEL_PROVIDERS_LIST' not in content:
    # Find and update MODEL_PROVIDERS_LIST
    old_list = 'MODEL_PROVIDERS_LIST = ["Anthropic", "Google Generative AI", "OpenAI", "IBM watsonx.ai", "Ollama"]'
    new_list = 'MODEL_PROVIDERS_LIST = ["Anthropic", "Google Generative AI", "MiniMax", "OpenAI", "IBM watsonx.ai", "Ollama"]'
    if old_list in content:
        content = content.replace(old_list, new_list)

site_packages.write_text(content)
print(f"Patched {site_packages}")
