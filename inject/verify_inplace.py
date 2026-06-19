#!/usr/bin/env python3
"""IN-PLACE verification + patcher for MiniMax integration.

This script is INJECTED INTO THE IMAGE via RUN with a heredoc, so it always
works regardless of the COPY / path situation.

It:
1. Detects the site-packages directory
2. Verifies all 5 patches are in place
3. Re-applies any missing patches
4. Prints final status
"""
import sys
from pathlib import Path

print("=" * 60)
print("MiniMax Provider Verification & Auto-Patch")
print("=" * 60)

# Find site-packages
SITE = None
for p in Path(sys.prefix).glob("lib/python*/site-packages"):
    if (p / "lfx" / "base" / "models").exists():
        SITE = p
        break

if not SITE:
    print("ERROR: Could not find site-packages!")
    print(f"sys.prefix = {sys.prefix}")
    print(f"sys.path = {sys.path}")
    sys.exit(1)

MODELS = SITE / "lfx" / "base" / "models"
print(f"Site packages: {SITE}")
print(f"Models dir:    {MODELS}")
print()

# Check 1: minimax_constants.py
print("[1] minimax_constants.py")
f = MODELS / "minimax_constants.py"
if f.exists():
    content = f.read_text()
    if "MINIMAX_MODELS_DETAILED" in content and "MiniMax-M3" in content:
        print("    OK - exists with models")
    else:
        print("    EXISTS but incomplete -> rewriting")
        f.write_text('''from .model_metadata import create_model_metadata

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
        print("    REWRITTEN")
else:
    print("    MISSING -> creating")
    f.write_text('''from .model_metadata import create_model_metadata

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
    print("    CREATED")

# Check 2: model_metadata.py
print("\n[2] model_metadata.py - MODEL_PROVIDER_METADATA")
f = MODELS / "model_metadata.py"
content = f.read_text()
if '"MiniMax":' in content:
    print("    OK - MiniMax entry found")
else:
    print("    MISSING -> inserting before 'OpenRouter'")
    minimax_entry = '''    "MiniMax": {
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
            }
        ],
        "api_docs_url": "https://platform.minimax.io/docs/api-reference/text-anthropic-api",
        "mapping": {
            "model_class": "ChatAnthropic",
            "model_param": "model",
        },
    },
'''
    if '"OpenRouter":' in content:
        content = content.replace('    "OpenRouter":', minimax_entry + '    "OpenRouter":', 1)
        f.write_text(content)
        print("    INSERTED")
    else:
        print("    ERROR: Could not find OpenRouter to insert before")

# Check 3: provider_queries.py
print("\n[3] provider_queries.py - _STATIC_MODELS_DETAILED")
f = MODELS / "unified_models" / "provider_queries.py"
if f.exists():
    content = f.read_text()
    if "minimax_constants" in content and "MINIMAX_MODELS_DETAILED" in content:
        print("    OK - already patched")
    else:
        print("    PATCHING")
        if "from lfx.base.models.openrouter_constants import OPENROUTER_MODELS_DETAILED" in content:
            content = content.replace(
                "from lfx.base.models.openrouter_constants import OPENROUTER_MODELS_DETAILED",
                "from lfx.base.models.openrouter_constants import OPENROUTER_MODELS_DETAILED\nfrom lfx.base.models.minimax_constants import MINIMAX_MODELS_DETAILED",
                1
            )
        if "    WATSONX_MODELS_DETAILED,\n]" in content:
            content = content.replace(
                "    WATSONX_MODELS_DETAILED,\n]",
                "    WATSONX_MODELS_DETAILED,\n    MINIMAX_MODELS_DETAILED,\n]",
                1
            )
            f.write_text(content)
            print("    PATCHED")
        else:
            print("    ERROR: Could not find WATSONX_MODELS_DETAILED list end")
else:
    print("    ERROR: provider_queries.py not found")

# Check 4: model_input_constants.py
print("\n[4] model_input_constants.py - MODEL_PROVIDERS_DICT + LIST")
f = MODELS / "model_input_constants.py"
if f.exists():
    content = f.read_text()
    needs_patch = False
    if "_get_minimax_inputs_and_fields" not in content:
        needs_patch = True
        print("    Missing: _get_minimax_inputs_and_fields()")
    if '"MiniMax"' not in content:
        needs_patch = True
        print("    Missing: MiniMax in MODEL_PROVIDERS_DICT")
    if 'MODEL_PROVIDERS_LIST = ["Anthropic", "Google Generative AI", "OpenAI", "IBM watsonx.ai", "Ollama"]' in content:
        needs_patch = True
        print("    Missing: MiniMax in MODEL_PROVIDERS_LIST")
    if needs_patch:
        # Apply all patches
        if "_get_minimax_inputs_and_fields" not in content:
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
        if '# Expose only active providers' in content and '"MiniMax"' not in content:
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
        content = content.replace(
            'MODEL_PROVIDERS_LIST = ["Anthropic", "Google Generative AI", "OpenAI", "IBM watsonx.ai", "Ollama"]',
            'MODEL_PROVIDERS_LIST = ["Anthropic", "Google Generative AI", "MiniMax", "OpenAI", "IBM watsonx.ai", "Ollama"]',
        )
        f.write_text(content)
        print("    PATCHED")
    else:
        print("    OK - all patches present")
else:
    print("    ERROR: model_input_constants.py not found")

# Check 5: Component file
print("\n[5] MiniMaxModelComponent (LCModelComponent)")
f = SITE / "lfx" / "components" / "minimax" / "minimax.py"
if f.exists():
    content = f.read_text()
    if "class MiniMaxModelComponent" in content and "build_model" in content:
        print("    OK - component exists")
    else:
        print("    EXISTS but incomplete")
else:
    print("    MISSING - see inject/lfx_components/lfx/components/minimax/")
    f.parent.mkdir(parents=True, exist_ok=True)
    init_file = f.parent / "__init__.py"
    if not init_file.exists():
        init_file.write_text('''from __future__ import annotations
from typing import TYPE_CHECKING, Any
from lfx.components._importing import import_mod
if TYPE_CHECKING:
    from lfx.components.minimax.minimax import MiniMaxModelComponent
_dynamic_imports = {"MiniMaxModelComponent": "minimax"}
__all__ = ["MiniMaxModelComponent"]
def __getattr__(attr_name: str) -> Any:
    if attr_name not in _dynamic_imports:
        raise AttributeError(attr_name)
    try:
        result = import_mod(attr_name, _dynamic_imports[attr_name], __spec__.parent)
    except (ModuleNotFoundError, ImportError, AttributeError) as e:
        raise AttributeError(str(e)) from e
    globals()[attr_name] = result
    return result
''')
        print("    Created __init__.py")

# Final live test
print("\n" + "=" * 60)
print("LIVE TEST - get_model_providers():")
print("=" * 60)
try:
    # Clear import cache
    for mod in list(sys.modules.keys()):
        if "lfx" in mod or "langflow" in mod:
            del sys.modules[mod]
    from lfx.base.models.unified_models import get_model_providers
    providers = get_model_providers()
    print("Providers found:", providers)
    print()
    if "MiniMax" in providers:
        print("SUCCESS: MiniMax is in the provider list!")
    else:
        print("FAILURE: MiniMax is NOT in the provider list")
        print("  -> Container needs restart to pick up patched files")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("RESTART REQUIRED:")
print("  docker compose restart langflow")
print("=" * 60)
