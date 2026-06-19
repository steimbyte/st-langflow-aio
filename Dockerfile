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
# Verify: docker exec -it <container> python3 /tmp/verify_inplace.py
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
# 4. MiniMax Component (LCModelComponent) installieren
#    -> Direkt nach site-packages/lfx/components/minimax/
# =============================================================================
# __init__.py
RUN python3 -c "import site; d=site.getsitepackages()[0]; \
    import os; os.makedirs(f'{d}/lfx/components/minimax', exist_ok=True); \
    open(f'{d}/lfx/components/minimax/__init__.py','w').write('''from __future__ import annotations\nfrom typing import TYPE_CHECKING, Any\nfrom lfx.components._importing import import_mod\nif TYPE_CHECKING:\n    from lfx.components.minimax.minimax import MiniMaxModelComponent\n_dynamic_imports = {\"MiniMaxModelComponent\": \"minimax\"}\n__all__ = [\"MiniMaxModelComponent\"]\ndef __getattr__(attr_name: str) -> Any:\n    if attr_name not in _dynamic_imports:\n        raise AttributeError(attr_name)\n    try:\n        result = import_mod(attr_name, _dynamic_imports[attr_name], __spec__.parent)\n    except (ModuleNotFoundError, ImportError, AttributeError) as e:\n        raise AttributeError(str(e)) from e\n    globals()[attr_name] = result\n    return result\n'''); \
    print('init.py OK')"

# minimax.py
COPY inject/lfx_components/lfx/components/minimax/minimax.py /tmp/minimax_component.py
RUN SITE=$(python3 -c "import site; print(site.getsitepackages()[0])") && \
    cp /tmp/minimax_component.py "$SITE/lfx/components/minimax/minimax.py" && \
    rm /tmp/minimax_component.py && \
    echo "minimax.py installed to $SITE/lfx/components/minimax/"

# =============================================================================
# 5. Patch Langflow Backend — MiniMax als Global Model Provider
# =============================================================================
COPY inject/patch_full_provider.py /tmp/patch.py
RUN python3 /tmp/patch.py && rm /tmp/patch.py

# =============================================================================
# 6. Verify-Tool in /tmp/ ablegen (funktioniert IMMER)
#    Hier nicht via COPY — direkt in den Layer gebaked
# =============================================================================
COPY inject/verify_inplace.py /tmp/verify_inplace.py
RUN chmod +x /tmp/verify_inplace.py

# =============================================================================
# 7. Auto-Patch beim Start — verifiziert + patcht beim Container-Start
#    Falls Dateien nicht gefunden werden (z.B. Image anders), werden sie
#    hier direkt erstellt/gepatcht
# =============================================================================
COPY inject/verify_inplace.py /tmp/auto_patch.py
RUN SITE=$(python3 -c "import site; print(site.getsitepackages()[0])") && \
    echo "=== AUTO-PATCH START ===" && \
    python3 /tmp/auto_patch.py 2>&1 | tee /tmp/auto_patch.log && \
    echo "=== AUTO-PATCH END ==="

# =============================================================================
# Final
# =============================================================================
WORKDIR /app/langflow

EXPOSE 7860

CMD ["langflow", "run", "--host", "0.0.0.0", "--port", "7860"]
