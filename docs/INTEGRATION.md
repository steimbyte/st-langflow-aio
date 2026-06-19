# MiniMax Provider Integration - Technical Documentation

> **Status:** v0.1.5 - Working
> **Last updated:** 2026-06-19

## Overview

This document explains how the MiniMax provider is integrated into Langflow as a **fully functional Global Model Provider** - on par with OpenAI, Anthropic, Google, IBM watsonx.ai, and Ollama.

The integration requires modifying **5 backend files** in the `langflowai/langflow` Docker image. All modifications are applied at build time via a single Python patch script.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                       Langflow UI                             │
│  Settings → Model Providers → MiniMax                          │
│  Agent    → Model Provider  → MiniMax                          │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                  /api/v1/models/providers                       │
│                  /api/v1/models (with MiniMax models)          │
│  Returns: provider list from MODEL_PROVIDERS_DICT             │
│           (populated from MODEL_PROVIDER_METADATA)            │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│         get_llm() in unified_models/instantiation.py            │
│  SPECIAL-CASE for MiniMax: passes anthropic_api_url           │
│  (without this, ChatAnthropic uses default Anthropic URL)     │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│              ChatAnthropic (langchain-anthropic)              │
│  model=MiniMax-M3                                             │
│  anthropic_api_url=https://api.minimax.io/anthropic            │
│  anthropic_api_key=sk-...                                     │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│              MiniMax Anthropic-Compatible API                  │
│  https://api.minimax.io/anthropic                             │
│  Endpoint: POST /v1/messages                                  │
│  Auth: x-api-key header                                       │
└──────────────────────────────────────────────────────────────┘
```

## Files Patched

The `inject/patch_full_provider.py` script patches 5 files in the langflow image's site-packages:

### 1. `lfx/base/models/minimax_constants.py` (NEW)

Defines the model list and metadata:

```python
MINIMAX_MODELS_DETAILED = [
    create_model_metadata(provider="MiniMax", name="MiniMax-M3", icon="MiniMax", tool_calling=True),
    create_model_metadata(provider="MiniMax", name="MiniMax-M2.7", icon="MiniMax", tool_calling=True),
    # ... 6 more models
]
DEFAULT_MINIMAX_API_URL = "https://api.minimax.io/anthropic"
```

### 2. `lfx/base/models/model_metadata.py` (MODIFIED)

Registers MiniMax in `MODEL_PROVIDER_METADATA`. **Critical:** This entry defines how Langflow treats MiniMax.

```python
"MiniMax": {
    "icon": "MiniMax",
    "max_tokens_field_name": "max_tokens",
    "base_url": "https://api.minimax.io/anthropic",
    "variables": [
        # API Key variable
        {
            "variable_name": "MiniMax API Key",
            "variable_key": "MINIMAX_API_KEY",
            "langchain_param": "api_key",
            "component_metadata": {
                "mapping_field": "api_key",  # tells get_provider_param_mapping to set api_key_param
                ...
            },
        },
        # Base URL variable - **CRITICAL**
        {
            "variable_name": "MiniMax API Base",
            "variable_key": "MINIMAX_BASE_URL",
            "langchain_param": "anthropic_api_url",  # ChatAnthropic uses 'anthropic_api_url'
            "component_metadata": {
                "mapping_field": "anthropic_api_url",  # tells get_provider_param_mapping to set base_url_param
                ...
            },
        },
    ],
    "mapping": {
        "model_class": "ChatAnthropic",
        "model_param": "model",
    },
},
```

**Why the two variables?** The `variables` list is what `get_provider_param_mapping()` reads. It scans for `mapping_field` containing "url" or "base_url" and sets `base_url_param = langchain_param` (i.e., `base_url_param = "anthropic_api_url"`). This is then used by our patch in step 5.

### 3. `lfx/base/models/unified_models/provider_queries.py` (MODIFIED)

Adds `MINIMAX_MODELS_DETAILED` import and appends it to `_STATIC_MODELS_DETAILED`. This makes the models appear in `get_models_detailed()` which `get_model_providers()` iterates over.

```python
from lfx.base.models.minimax_constants import MINIMAX_MODELS_DETAILED

_STATIC_MODELS_DETAILED: list[list[dict]] = [
    ANTHROPIC_MODELS_DETAILED,
    OPENAI_MODELS_DETAILED,
    # ...
    WATSONX_MODELS_DETAILED,
    MINIMAX_MODELS_DETAILED,  # ← ADDED
]
```

### 4. `lfx/base/models/model_input_constants.py` (MODIFIED)

Two changes:

**a) Add `_get_minimax_inputs_and_fields()` helper function** (parallel to other providers).

**b) Register MiniMax in `MODEL_PROVIDERS_DICT`** so the Settings → Model Providers page lists it.

**c) Add "MiniMax" to `MODEL_PROVIDERS_LIST`** so the Agent "Model Provider" dropdown includes it.

```python
MODEL_PROVIDERS_LIST = ["Anthropic", "Google Generative AI", "MiniMax", "OpenAI", "IBM watsonx.ai", "Ollama"]
```

### 5. `lfx/base/models/unified_models/instantiation.py` (MODIFIED) — **THE CRITICAL FIX**

This is `get_llm()` - the function that ACTUALLY instantiates the LLM when the Agent runs. The function has special-case blocks for **OpenRouter** and **WatsonX** that pass provider-specific kwargs. We need to add a similar block for MiniMax.

**Without this patch:** `get_llm()` builds the kwargs dict as:
```python
kwargs = {
    "model": "MiniMax-M3",
    "streaming": stream,
    "api_key": api_key,
    "temperature": temperature,
    "max_tokens": 4096,
}
# Returns: ChatAnthropic(**kwargs)
# Result: ChatAnthropic uses default https://api.anthropic.com ❌
```

**With this patch:** We add the MiniMax special case that reads the base URL from provider metadata and passes it as `anthropic_api_url`:
```python
elif provider == "MiniMax":
    provider_meta = model_provider_metadata.get(provider, {})
    provider_vars = unified_models_module.get_all_variables_for_provider(user_id, provider)
    base_url_value = (
        provider_vars.get("MINIMAX_BASE_URL")
        or _env_if_allowed("MINIMAX_BASE_URL")
        or provider_meta.get("base_url")  # defaults to https://api.minimax.io/anthropic
    )
    if base_url_value:
        kwargs["anthropic_api_url"] = base_url_value
```

Now `get_llm()` produces:
```python
kwargs = {
    "model": "MiniMax-M3",
    "streaming": stream,
    "api_key": api_key,
    "temperature": temperature,
    "max_tokens": 4096,
    "anthropic_api_url": "https://api.minimax.io/anthropic",  # ← ADDED
}
# Returns: ChatAnthropic(**kwargs)
# Result: ChatAnthropic routes to MiniMax ✓
```

### 6. `lfx/components/minimax/minimax.py` (NEW, copied into site-packages)

The actual `LCModelComponent` subclass. Required so that:
- `MODEL_PROVIDERS_DICT["MiniMax"]["component_class"]` can be instantiated
- The Settings → Model Providers "Save" button can validate credentials

```python
class MiniMaxModelComponent(LCModelComponent):
    display_name = "MiniMax"
    icon = "MiniMax"
    inputs = [
        SecretStrInput(name="api_key", display_name="MiniMax API Key", ...),
        DropdownInput(name="model_name", options=MINIMAX_MODELS, ...),
        ...
    ]
    def build_model(self) -> LanguageModel:
        return ChatAnthropic(
            model=self.model_name,
            anthropic_api_key=self.api_key,
            anthropic_api_url=self.base_url,
            ...
        )
```

## Why This Is So Complex

Langflow 1.8+ has a sophisticated Global Model Provider system with **two separate code paths** for instantiating LLMs:

1. **Custom Components in flows** - users drag a custom component onto the canvas and wire it to the Agent. The component's own `build_model()` is called.

2. **Built-in LanguageModelComponent in flows** - users select a model from the built-in Language Model dropdown. The dropdown is populated by `get_llm()` which reads `MODEL_PROVIDER_METADATA` and uses provider-specific kwargs.

For MiniMax to appear as a first-class provider in **both** paths, we need:
- `MiniMaxModelComponent` (custom component class) for path 1
- `MODEL_PROVIDER_METADATA["MiniMax"]` + `get_llm()` special-case for path 2

## Verification

After build, verify the patches are in place:

```bash
docker exec -it <container> python3 /tmp/verify_inplace.py
```

This script checks all 5 patches and reports the status of each. It also tests the full provider list with:
```python
from lfx.base.models.unified_models import get_model_providers
print(get_model_providers())
# Expected: ['Anthropic', 'Google Generative AI', 'IBM WatsonX', 'MiniMax', 'Ollama', 'OpenAI', 'OpenRouter']
```

## Test the actual API call

```bash
docker exec -it <container> python3 /tmp/smoke_test.py <your_minimax_key>
```

Tests 3 things in sequence:
1. Direct HTTP to `/v1/models`
2. `anthropic` SDK
3. `langchain_anthropic.ChatAnthropic`

All three should succeed. The third test uses the same `ChatAnthropic(anthropic_api_url=...)` configuration that the patched `get_llm()` will use at runtime.

## Common Issues

### "invalid x-api-key" error
The Anthropic SDK got a request but the API rejected the key. Check:
- API key is valid (test in [MiniMax console](https://platform.minimax.io/))
- No whitespace in the key (SecretStr handling can add strip but check)
- Network can reach `api.minimax.io` from the container

### Provider not in dropdown
- Run verify_inplace.py - check `MODEL_PROVIDERS_DICT` and `MODEL_PROVIDERS_LIST`
- Check DB cache: `docker compose down -v && docker compose up -d`
- Check Langflow version (1.8+ required for global providers)

### Model not selectable
- Run verify_inplace.py - check `MINIMAX_MODELS_DETAILED` and `_STATIC_MODELS_DETAILED`
- The model name must be in `create_model_metadata` with the right `provider` field

## MiniMax API Specifics

API-Docs: https://platform.minimax.io/docs/api-reference/text-anthropic-api

- **Base URL:** `https://api.minimax.io/anthropic`
- **Endpoint:** `POST /v1/messages`
- **Auth:** `x-api-key` header
- **Models:** `MiniMax-M3`, `MiniMax-M2.7`, `MiniMax-M2.7-highspeed`, `MiniMax-M2.5`, `MiniMax-M2.5-highspeed`, `MiniMax-M2.1`, `MiniMax-M2.1-highspeed`, `MiniMax-M2`
- **Environment:** Set `ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic` and `ANTHROPIC_API_KEY=<key>`

MiniMax does **NOT** have a separate SDK - they provide an Anthropic-SDK-compatible endpoint, which is exactly what we use.

---

## Hinweis zur KI-Unterstuetzung

Bei der Entwicklung dieses Projekts wurden teilweise oder vollstaendig KI-gestuetzte Tools und Technologien eingesetzt.
