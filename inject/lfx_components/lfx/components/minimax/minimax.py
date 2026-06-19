from typing import Any

import requests
from typing_extensions import override

from lfx.base.models.model import LCModelComponent
from lfx.field_typing import LanguageModel
from lfx.field_typing.range_spec import RangeSpec
from lfx.inputs.inputs import (
    BoolInput,
    DictInput,
    DropdownInput,
    IntInput,
    MessageTextInput,
    SecretStrInput,
    SliderInput,
)
from lfx.log.logger import logger
from lfx.schema.dotdict import dotdict

DEFAULT_MINIMAX_API_URL = "https://api.minimax.io/anthropic"

MINIMAX_MODELS = [
    "MiniMax-M3",
    "MiniMax-M2.7",
    "MiniMax-M2.7-highspeed",
    "MiniMax-M2.5",
    "MiniMax-M2.5-highspeed",
    "MiniMax-M2.1",
    "MiniMax-M2.1-highspeed",
    "MiniMax-M2",
]


def _resolve_api_key(value):
    """Sicheres Aufloesen eines moeglicherweise SecretStr-umwickelten API-Keys.

    SecretStrInput gibt je nach Aufruf-Pfad manchmal einen SecretStr,
    manchmal einen normalen String zurueck. Wir normalisieren beides.
    """
    if value is None or value == "":
        return None
    # SecretStr hat get_secret_value()
    if hasattr(value, "get_secret_value"):
        try:
            return value.get_secret_value()
        except Exception:
            return str(value)
    # Falls schon ein String
    if isinstance(value, str):
        return value.strip() or None
    return str(value)


class MiniMaxModelComponent(LCModelComponent):
    """MiniMax LLM via Anthropic-compatible API.

    API-Docs: https://platform.minimax.io/docs/api-reference/text-anthropic-api

    MiniMax exponiert einen Anthropic-SDK-kompatiblen Endpunkt unter
    https://api.minimax.io/anthropic. Wir nutzen langchain_anthropic.ChatAnthropic
    mit angepasster anthropic_api_url.

    Auth: x-api-key Header (Standard Anthropic SDK Verhalten)
    """

    display_name = "MiniMax"
    description = (
        "Generate text using MiniMax LLMs via the Anthropic-compatible API. "
        "Supports MiniMax-M3, M2.7, M2.5, M2.1 and M2 models."
    )
    icon = "MiniMax"
    name = "MiniMaxModel"

    inputs = [
        *LCModelComponent.get_base_inputs(),
        SecretStrInput(
            name="api_key",
            display_name="MiniMax API Key",
            info=(
                "Your MiniMax API key from https://platform.minimax.io/. "
                "Used as x-api-key header by the Anthropic-compatible endpoint."
            ),
            required=True,
            real_time_refresh=True,
        ),
        DropdownInput(
            name="model_name",
            display_name="Model",
            options=MINIMAX_MODELS,
            value="MiniMax-M3",
            combobox=True,
            info="M3 supports image/video input; M2.x only text.",
        ),
        IntInput(
            name="max_tokens",
            display_name="Max Tokens",
            advanced=True,
            value=4096,
            info="Maximum number of tokens to generate. Set to 0 for unlimited.",
        ),
        SliderInput(
            name="temperature",
            display_name="Temperature",
            info="Controls randomness. Range [0, 2]. Recommended: 1.",
            value=1.0,
            range_spec=RangeSpec(min=0, max=2, step=0.01),
            advanced=True,
        ),
        MessageTextInput(
            name="base_url",
            display_name="API Base URL",
            info=(
                "Anthropic-compatible endpoint. "
                "Defaults to https://api.minimax.io/anthropic"
            ),
            value=DEFAULT_MINIMAX_API_URL,
            real_time_refresh=True,
            advanced=True,
        ),
        BoolInput(
            name="tool_model_enabled",
            display_name="Enable Tool Calling",
            info="Filter to models that support function calling.",
            value=False,
            real_time_refresh=True,
            advanced=False,
        ),
        DictInput(
            name="model_kwargs",
            display_name="Model Kwargs",
            info="Additional keyword arguments for the model.",
            advanced=True,
        ),
    ]

    def get_models(self, *, tool_model_enabled: bool | None = None) -> list[str]:
        return MINIMAX_MODELS

    @override
    def update_build_config(
        self, build_config: dotdict, field_value: Any, field_name: str | None = None
    ):
        if field_name in {"base_url", "model_name", "tool_model_enabled", "api_key"}:
            try:
                models = self.get_models(tool_model_enabled=self.tool_model_enabled)
                build_config.setdefault("model_name", {})
                build_config["model_name"]["options"] = models
                build_config["model_name"].setdefault("value", models[0])
                build_config["model_name"]["combobox"] = True
            except Exception as e:
                logger.exception(f"Error updating model list: {e}")
        return build_config

    def build_model(self) -> LanguageModel:
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError as e:
            msg = (
                "langchain-anthropic is not installed. "
                "Install with: pip install langchain-anthropic"
            )
            raise ImportError(msg) from e

        # API-Key korrekt aufloesen (SecretStr oder String)
        api_key = _resolve_api_key(self.api_key)
        if not api_key:
            raise ValueError(
                "MiniMax API key is missing. "
                "Set the api_key field in the MiniMax component."
            )

        max_tokens_val = int(getattr(self, "max_tokens", "") or 4096)
        base_url = (self.base_url or DEFAULT_MINIMAX_API_URL).rstrip("/")

        logger.debug(
            "Building MiniMax ChatAnthropic: model=%s base_url=%s key_len=%d",
            self.model_name,
            base_url,
            len(api_key),
        )

        try:
            output = ChatAnthropic(
                model=self.model_name or "MiniMax-M3",
                anthropic_api_key=api_key,
                anthropic_api_url=base_url,
                max_tokens=max_tokens_val,
                temperature=self.temperature,
                model_kwargs=self.model_kwargs or {},
                streaming=self.stream if hasattr(self, "stream") else False,
                stream_usage=True,
            )
        except Exception as e:
            msg = f"Could not build MiniMax ChatAnthropic: {e}"
            raise ValueError(msg) from e

        return output
