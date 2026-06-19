from typing import Any

import requests
from pydantic.v1 import SecretStr
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

MINIMAX_API_BASE = "https://api.minimax.io/anthropic"

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

# M2.x models don't support image/video, M3 does
TOOL_CALLING_SUPPORTED_MODELS = [
    "MiniMax-M3",
    "MiniMax-M2.7",
    "MiniMax-M2.7-highspeed",
    "MiniMax-M2.5",
    "MiniMax-M2.5-highspeed",
    "MiniMax-M2.1",
    "MiniMax-M2.1-highspeed",
    "MiniMax-M2",
]


class MiniMaxModelComponent(LCModelComponent):
    """MiniMax LLM via Anthropic-compatible API.

    MiniMax exposes an Anthropic SDK-compatible endpoint at:
    https://api.minimax.io/anthropic

    Docs: https://platform.minimax.io/docs/api-reference/text-anthropic-api
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
                "Your MiniMax API key. "
                "Get one at https://platform.minimax.io/"
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
            info="MiniMax model to use. M3 supports image/video input; M2.x only text.",
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
        SliderInput(
            name="top_p",
            display_name="Top P",
            info="Nucleus sampling. Default 0.95 for M3, 0.9 for M2.x.",
            value=0.95,
            range_spec=RangeSpec(min=0, max=1, step=0.01),
            advanced=True,
        ),
        MessageTextInput(
            name="base_url",
            display_name="API Base URL",
            info=(
                "Anthropic-compatible endpoint. "
                "Defaults to https://api.minimax.io/anthropic"
            ),
            value=MINIMAX_API_BASE,
            real_time_refresh=True,
            advanced=True,
        ),
        BoolInput(
            name="tool_model_enabled",
            display_name="Enable Tool Calling",
            info=(
                "Filter model list to only show models that support "
                "tool_calling (function calling)."
            ),
            value=False,
            real_time_refresh=True,
            advanced=False,
        ),
        DictInput(
            name="model_kwargs",
            display_name="Model Kwargs",
            info="Additional keyword arguments passed to the model.",
            advanced=True,
        ),
    ]

    def get_models(self, *, tool_model_enabled: bool | None = None) -> list[str]:
        """Return the model list. M3 + M2.x all support tool calling via Anthropic format."""
        if tool_model_enabled:
            return TOOL_CALLING_SUPPORTED_MODELS
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
                "Install it with: pip install langchain-anthropic"
            )
            raise ImportError(msg) from e

        try:
            api_key = SecretStr(self.api_key).get_secret_value() if self.api_key else None
            max_tokens_val = getattr(self, "max_tokens", "") or 4096
            max_tokens_val = int(max_tokens_val) if max_tokens_val else 4096

            output = ChatAnthropic(
                model=self.model_name or "MiniMax-M3",
                anthropic_api_key=api_key,
                anthropic_api_url=self.base_url or MINIMAX_API_BASE,
                max_tokens=max_tokens_val,
                temperature=self.temperature,
                top_p=self.top_p,
                model_kwargs=self.model_kwargs or {},
                streaming=self.stream if hasattr(self, "stream") else False,
                stream_usage=True,
            )
        except Exception as e:
            msg = f"Could not connect to MiniMax Anthropic API: {e}"
            raise ValueError(msg) from e

        return output

    def _get_exception_message(self, exception: Exception) -> str | None:
        """Extract user-friendly error message from MiniMax API exceptions."""
        try:
            from anthropic import BadRequestError

            if isinstance(exception, BadRequestError):
                body = getattr(exception, "body", None)
                if body:
                    if isinstance(body, dict):
                        return body.get("error", {}).get("message")
                    return str(body)
        except ImportError:
            pass
        return None
