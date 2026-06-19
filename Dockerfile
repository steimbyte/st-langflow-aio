# syntax=docker/dockerfile:1.7
# =============================================================================
#  st-langflow-aio
#  Langflow + ffmpeg + chromium + yt-dlp + node tools
#  + MiniMax als Global Model Provider
#    (im Agent Model-Provider-Dropdown, in Settings -> Model Providers,
#     UND in der /api/v1/models Liste)
#
# Build:  docker build --no-cache -t st-langflow-aio .
# Run:    docker run -d -p 7860:7860 -v ./data:/app/langflow st-langflow-aio
# Verify: docker exec -it langflow bash /app/inject/verify.sh
# =============================================================================

FROM langflowai/langflow:latest

USER root

ENV DEBIAN_FRONTEND=noninteractive \
    PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium \
    LANGFLOW_CONFIG_DIR=/app/langflow \
    LANGFLOW_DEV=false \
    LFX_DEV=false

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
# 4. MiniMax Component in site-packages
# =============================================================================
# Find the site-packages directory dynamically (any Python 3.x version)
RUN SITE=$(python3 -c "import site; print(site.getsitepackages()[0])") && \
    echo "Detected site-packages: $SITE" && \
    mkdir -p "$SITE/lfx/components/minimax"

COPY inject/lfx_components/lfx/components/minimax/__init__.py \
     /tmp/minimax_init.py
COPY inject/lfx_components/lfx/components/minimax/minimax.py \
     /tmp/minimax_main.py

RUN SITE=$(python3 -c "import site; print(site.getsitepackages()[0])") && \
    cp /tmp/minimax_init.py "$SITE/lfx/components/minimax/__init__.py" && \
    cp /tmp/minimax_main.py "$SITE/lfx/components/minimax/minimax.py" && \
    rm /tmp/minimax_init.py /tmp/minimax_main.py && \
    echo "MiniMax component installed to $SITE/lfx/components/minimax/"

# =============================================================================
# 5. Patch Langflow Backend — MiniMax als Global Model Provider
# =============================================================================
COPY inject/patch_full_provider.py /tmp/patch.py
RUN python3 /tmp/patch.py && rm /tmp/patch.py

# =============================================================================
# 6. Verify-Skript rein
# =============================================================================
COPY inject/verify.sh /app/inject/verify.sh
RUN chmod +x /app/inject/verify.sh

# =============================================================================
# 7. Cache leeren — Langflow speichert component cache in der DB
#    Aber: User muss Volume loeschen (docker compose down -v)
# =============================================================================

WORKDIR /app/langflow

EXPOSE 7860

CMD ["langflow", "run", "--host", "0.0.0.0", "--port", "7860"]
