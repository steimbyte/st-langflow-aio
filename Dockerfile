# syntax=docker/dockerfile:1.7
# Langflow + MiniMax Bundle (Anthropic-kompatibel)
# Build:  docker build -t langflow-minimax .
# Run:    docker run -d -p 7860:7860 \
#            -e MINIMAX_API_KEY=your_key \
#            langflow-minimax

FROM langflowai/langflow:latest

USER root

ENV DEBIAN_FRONTEND=noninteractive \
    PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium \
    # Hier landen unsere Custom Components
    LANGFLOW_COMPONENTS_PATH=/app/custom_components

# ---------- System: ffmpeg + Chromium + Node.js ----------
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

# ---------- Python: yt-dlp + langchain-anthropic ----------
RUN pip install --no-cache-dir --break-system-packages yt-dlp langchain-anthropic

# ---------- Node: puppeteer-core + yt-dlp-wrap ----------
WORKDIR /opt/tools
RUN npm init -y >/dev/null \
 && npm install --no-audit --no-fund puppeteer-core yt-dlp-wrap \
 && npm cache clean --force \
 && rm -rf /tmp/*

ENV PATH="/opt/tools/node_modules/.bin:${PATH}"

# ============================================================
# MiniMax Bundle — sauber als Custom Component injectiert
# LANGFLOW_COMPONENTS_PATH = /app/custom_components
# ============================================================

WORKDIR /app/custom_components
COPY bundle/src/lfx/src/lfx/components/minimax/__init__.py ./minimax/__init__.py
COPY bundle/src/lfx/src/lfx/components/minimax/minimax.py      ./minimax/minimax.py

# Frontend-Icon: Copy in die existierende icons-Struktur (optional, 
# Fallback-Icon wird genutzt wenn nicht vorhanden)
# COPY src/frontend/src/icons/MiniMax /app/langext/icons/MiniMax

WORKDIR /app/langflow

EXPOSE 7860

CMD ["langflow", "run", "--host", "0.0.0.0", "--port", "7860"]