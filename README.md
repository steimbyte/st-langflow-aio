# st-langflow-aio

**Langflow all-in-one** — Custom Docker Image mit Extras.

## Was ist drin

| Tool | Version | Zweck |
|------|---------|--------|
| Langflow | latest | UI/Framework |
| ffmpeg | apt | Video/Audio Processing |
| Chromium | apt | Browser Automation (puppeteer) |
| Node.js | 20.x | JavaScript Tooling |
| yt-dlp | pip | YouTube/Media Download |
| yt-dlp-wrap | npm | JS-Wrapper fuer yt-dlp |
| puppeteer-core | npm | Browser Control (ohne Download) |
| langchain-anthropic | pip | MiniMax LLM Provider |

## Enthaltene Custom Components

- **MiniMax LLM** — Anthropic-kompatibler MiniMax Provider

### MiniMax Global Model Provider Integration

MiniMax ist als **Global Model Provider** integriert:

1. **Settings → Model Providers** — MiniMax erscheint als konfigurierbarer Provider
2. **Agent "Model Provider" Dropdown** — "MiniMax" ist direkt auswaehlbar
3. **Custom Component** — Manuelles Verdrahten ueber "Custom" + Language Model Port

Unterstuetzte Modelle:
- MiniMax-M3 (1M context, Bild/Video, Thinking)
- MiniMax-M2.7 / M2.7-highspeed (~100 tps)
- MiniMax-M2.5 / M2.5-highspeed (~100 tps)
- MiniMax-M2.1 / M2.1-highspeed (~100 tps)
- MiniMax-M2

API-Docs: https://platform.minimax.io/docs/api-reference/text-anthropic-api

## Build

```bash
docker build -t st-langflow-aio .
```

## Run

```bash
docker run -d \
  --name langflow \
  -p 7860:7860 \
  -v ./data:/app/langflow \
  -e LANGFLOW_SECRET_KEY=<fernet-key> \
  -e LANGFLOW_SUPERUSER=admin@example.com \
  -e LANGFLOW_SUPERUSER_PASSWORD=changeme \
  -e MINIMAX_API_KEY=your_key \
  st-langflow-aio
```

Fernet Key generieren:
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## MiniMax API Key

Hole dir einen Key unter: https://platform.minimax.io/

## Ordnerstruktur

```
.
├── Dockerfile
├── README.md
├── bundle/                          # Original Bundle-Source (Frontend-Icons etc.)
│   ├── frontend/                    # Frontend-Snippets
│   └── src/
│       ├── lfx/                    # Backend Components
│       └── frontend/                 # Frontend Icons
└── inject/                          # Injection fuer Runtime-Image
    ├── components/                  # Custom Components -> /app/custom_components/
    │   └── lfx/components/minimax/
    ├── lfx/                         # Backend-Patches -> site-packages/lfx/
    │   └── base/models/minimax_constants.py
    ├── inject_startup.py            # sitecustomize.py (sys.path Patch)
    └── patch_model_providers.py     # model_input_constants.py Patch
```

## Wie die Integration funktioniert

```
sitecustomize.py                    -> sys.path Manipulation
  -> /app/custom_components zu sys.path hinzugefuegt

model_input_constants.py           -> Patched bei Build-Zeit
  -> _get_minimax_inputs_and_fields()
  -> MODEL_PROVIDERS_DICT["MiniMax"]  = {...}
  -> MODEL_PROVIDERS_LIST += "MiniMax"

Ergebnis:
  1. Settings -> Model Providers -> MiniMax (mit API-Key-Feld)
  2. Agent "Model Provider" Dropdown -> "MiniMax" auswaehlbar
  3. Custom Component in Sidebar -> MiniMax
```

---

## Hinweis zur KI-Unterstuetzung

Bei der Entwicklung dieses Projekts wurden teilweise oder vollstaendig KI-gestuetzte Tools und Technologien eingesetzt.
