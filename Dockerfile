# syntax=docker/dockerfile:1.7
# =============================================================================
#  st-langflow-aio
#  Langflow + ffmpeg + chromium/puppeteer + yt-dlp + node tools
#  + MiniMax als Global Model Provider (im Agent Model-Provider-Dropdown)
#
# Build:  docker build -t st-langflow-aio .
# Run:    docker run -d -p 7860:7860 \
#            -v ./data:/app/langflow \
#            -e LANGFLOW_SECRET_KEY=<fernet-key> \
#            -e LANGFLOW_SUPERUSER=admin@example.com \
#            -e LANGFLOW_SUPERUSER_PASSWORD=changeme \
#            st-langflow-aio
# =============================================================================

FROM langflowai/langflow:latest

USER root

ENV DEBIAN_FRONTEND=noninteractive \
    PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium \
    LANGFLOW_CONFIG_DIR=/app/langflow \
    LANGFLOW_COMPONENTS_PATH=/app/custom_components

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
# 4. Custom Components — MiniMax Component
# =============================================================================
COPY inject/components/ /app/custom_components/

# =============================================================================
# 5. sitecustomize.py
#    Wird VOR jedem Import von Python ausgefuehrt.
#    Fuegt /app/custom_components zu sys.path hinzu,
#    damit "from lfx.components.minimax import ..." funktioniert.
# =============================================================================
COPY inject/inject_startup.py /tmp/sitecustomize_src.py
RUN python3 -c "import site; d=site.getsitepackages()[0]; \
    open(f'{d}/sitecustomize.py','w').write(open('/tmp/sitecustomize_src.py').read()); \
    print(f'sitecustomize.py -> {d}')" \
 && rm /tmp/sitecustomize_src.py

# =============================================================================
# 6. MiniMax Model Provider injectieren
#    minimax_constants.py  -> lfx/base/models/  (Modelliste)
#    model_input_constants.py patch -> MiniMax in MODEL_PROVIDERS_DICT
#                                          + MiniMax in MODEL_PROVIDERS_LIST
#    => MiniMax erscheint in Settings -> Model Providers
#       UND im Agent "Model Provider" Dropdown
# =============================================================================
COPY inject/lfx/ /tmp/inject_lfx/
RUN python3 -c "import site; d=site.getsitepackages()[0]; \
    import shutil,os; src='/tmp/inject_lfx'; dst=d; \
    for root,dirs,files in os.walk(src): \
        for f in files: \
            rel=os.path.relpath(os.path.join(root,f),src); \
            target=os.path.join(dst,rel); \
            os.makedirs(os.path.dirname(target),exist_ok=True); \
            shutil.copy2(os.path.join(root,f),target); \
    print(f'Injected lfx/ -> {dst}')" \
 && rm -rf /tmp/inject_lfx

COPY inject/patch_model_providers.py /tmp/patch_model_providers.py
RUN python3 /tmp/patch_model_providers.py \
 && rm /tmp/patch_model_providers.py

WORKDIR /app/langflow

EXPOSE 7860

CMD ["langflow", "run", "--host", "0.0.0.0", "--port", "7860"]
