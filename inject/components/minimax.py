"""
MiniMax LLM Custom Component for Langflow.

Dieser Component nutzt das offizielle Custom Component Interface.
Er erscheint in der Sidebar unter "Custom Components" und kann per
Drag & Drop in Flows verwendet werden.

API-Docs: https://platform.minimax.io/docs/api-reference/text-anthropic-api

Unterstuetzte Modelle:
- MiniMax-M3 (1M context, Bild/Video, Thinking)
- MiniMax-M2.7 / M2.7-highspeed
- MiniMax-M2.5 / M2.5-highspeed
- MiniMax-M2.1 / M2.1-highspeed
- MiniMax-M2
"""

from typing import Optional

from langchain_anthropic import ChatAnthropic
from langchain_anthropic.chat_models import _support_tool_choice
from pydantic.v1 import SecretStr

from langflow.custom import CustomComponent
from langflow.io import (
    BoolInput,
    DictInput,
    DropdownInput,
    FloatInput,
    IntInput,
    MessageTextInput,
    Output,
    SecretStrInput,
)
from langflow.schema import Message
from langflow.schema.dotdict import dotdict


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


class MiniMaxLLM(CustomComponent):
    """MiniMax LLM via Anthropic-kompatiblen Endpunkt.

    Wrapper fuer ChatAnthropic mit MiniMax Base URL.
    Erscheint in der Langflow Sidebar als Custom Component.
    """

    display_name = "MiniMax LLM"
    description = (
        "MiniMax LLMs via Anthropic-kompatiblen Endpunkt. "
        "Nutzt ChatAnthropic mit MiniMax Base URL."
    )
    documentation: str = "https://platform.minimax.io/docs/api-reference/text-anthropic-api"
    icon = "Bot"  # Lucide Icon Name
    name = "MiniMaxLLM"

    inputs = [
        SecretStrInput(
            name="api_key",
            display_name="API Key",
            info="MiniMax API Key von https://platform.minimax.io",
            required=True,
            real_time_refresh=True,
        ),
        DropdownInput(
            name="model_name",
            display_name="Model",
            options=MINIMAX_MODELS,
            value="MiniMax-M3",
            real_time_refresh=True,
        ),
        IntInput(
            name="max_tokens",
            display_name="Max Tokens",
            value=4096,
            info="Max tokens to generate. 0 = unlimited.",
        ),
        FloatInput(
            name="temperature",
            display_name="Temperature",
            value=1.0,
            info="Controls randomness. Range [0, 2]. Recommended: 1.",
        ),
        FloatInput(
            name="top_p",
            display_name="Top P",
            value=0.95,
            info="Nucleus sampling. Default 0.95 for M3, 0.9 for M2.x.",
        ),
        MessageTextInput(
            name="base_url",
            display_name="Base URL",
            value=MINIMAX_API_BASE,
            info="Anthropic-kompatibler Endpunkt.",
            advanced=True,
            real_time_refresh=True,
        ),
        BoolInput(
            name="streaming",
            display_name="Streaming",
            value=False,
            info="Enable streaming responses.",
            advanced=True,
        ),
        DictInput(
            name="model_kwargs",
            display_name="Model Kwargs",
            info="Zusaetzliche Parameter fuer das Modell.",
            advanced=True,
        ),
    ]

    outputs = [
        Output(
            display_name="Language Model",
            name="language_model",
            method="build_language_model",
        ),
        Output(
            display_name="Text Response",
            name="text_response",
            method="build_text_response",
        ),
    ]

    def build_language_model(self) -> ChatAnthropic:
        """Baut das ChatAnthropic Modell fuer die LanguageModel Ausgabe."""
        api_key = SecretStr(self.api_key).get_secret_value() if self.api_key else None
        max_tokens = int(self.max_tokens) if self.max_tokens else 4096

        llm = ChatAnthropic(
            model=self.model_name or "MiniMax-M3",
            anthropic_api_key=api_key,
            anthropic_api_url=self.base_url or MINIMAX_API_BASE,
            max_tokens=max_tokens,
            temperature=self.temperature if self.temperature is not None else 1.0,
            top_p=self.top_p if self.top_p is not None else 0.95,
            model_kwargs=self.model_kwargs or {},
            streaming=getattr(self, "streaming", False),
            stream_usage=True,
        )
        return llm

    def build_text_response(self) -> Message:
        """Build- Methode fuer Text-Ausgabe (Legacy)."""
        # Diese Methode wird nicht genutzt wenn Language Model Output
        # mit einem Agent verbunden wird
        return Message(text="MiniMax LLM Component ready")

    def build_config(self):
        return dotdict()

    def get_model_name(self) -> str:
        return self.model_name or "MiniMax-M3"

    def get_api_key(self) -> str:
        return self.api_key or ""

    def get_base_url(self) -> str:
        return self.base_url or MINIMAX_API_BASE
