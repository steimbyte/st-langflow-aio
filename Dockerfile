# syntax=docker/dockerfile:1.7
# =============================================================================
#  st-langflow-aio
#  Langflow + ffmpeg + chromium + yt-dlp + node tools
#  + MiniMax als VOLL FUNKTIONSFAEHIGER Global Model Provider
#    (im Agent Model-Provider-Dropdown, in Settings -> Model Providers)
#
# Build:  docker build --no-cache -t st-langflow-aio .
# Run:    docker run -d -p 7860:7860 -v ./data:/app/langflow st-langflow-aio
# =============================================================================

FROM langflowai/langflow:latest

USER root

ENV DEBIAN_FRONTEND=noninteractive \
    PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium \
    LANGFLOW_CONFIG_DIR=/app/langflow

# =============================================================================
# 1. System packages
# =============================================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        chromium \
        fonts-liberation \
        libasound2t64 \
        libatk-bridge2.0-0t64 \
        libatk1.0-0t64 \
        libcups2t64 \
        libdrm2 \
        libgbm1 \
        libgtk-3-0t64 \
        libnspr4 \
        libnss3 \
        libx11-xcb1 \
        libxcomposite1 \
        libxdamage1 \
        libxrandr2 \
        libxkbcommon0 \
        libxext6 \
        xdg-utils \
        ca-certificates \
        curl \
        gnupg \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
       | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" \
       > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get purge -y --auto-remove gnupg \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# 2. Python packages
# =============================================================================
RUN pip install --no-cache-dir --break-system-packages \
        yt-dlp \
        langchain-anthropic

# =============================================================================
# 3. Node tools
# =============================================================================
WORKDIR /opt/tools
RUN npm init -y >/dev/null \
 && npm install --no-audit --no-fund puppeteer-core yt-dlp-wrap \
 && npm cache clean --force \
 && rm -rf /tmp/*

ENV PATH="/opt/tools/node_modules/.bin:${PATH}"

# =============================================================================
# 4. MiniMax Component (LCModelComponent) in site-packages
#    -> Direkt importierbar als lfx.components.minimax
# =============================================================================
COPY inject/lfx_components/lfx/components/minimax/ \
     /app/.venv/lib/python3.14/site-packages/lfx/components/minimax/

# touch __init__.py im components parent sicherstellen
RUN touch /app/.venv/lib/python3.14/site-packages/lfx/components/__init__.py

# =============================================================================
# 5. Patch Langflow Backend — MiniMax als Global Model Provider registrieren
#    Patched:
#      - lfx/base/models/minimax_constants.py (NEU)
#      - lfx/base/models/model_metadata.py
#      - lfx/base/models/unified_models/provider_queries.py
#      - lfx/base/models/model_input_constants.py
# =============================================================================
COPY inject/patch_full_provider.py /tmp/patch.py
RUN python3 /tmp/patch.py && rm /tmp/patch.py

WORKDIR /app/langflow

EXPOSE 7860

CMD ["langflow", "run", "--host", "0.0.0.0", "--port", "7860"]