# st-langflow-aio

**Langflow all-in-one** — Custom Docker Image mit extras.

## Was ist drin

| Tool | Version | Zweck |
|------|---------|--------|
| Langflow | latest | UI/Framework |
| ffmpeg | apt | Video/Audio Processing |
| Chromium | apt | Browser Automation (puppeteer) |
| Node.js | 20.x | JavaScript Tooling |
| yt-dlp | pip | YouTube/Media Download |
| yt-dlp-wrap | npm | JS-Wrapper für yt-dlp |
| puppeteer-core | npm | Browser Control (ohne Download) |
| langchain-anthropic | pip | MiniMax LLM Provider |

## Enthaltene Custom Components

- **MiniMax LLM** — Anthropic-kompatibler MiniMax Provider

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
└── bundle/
    ├── README.md          # MiniMax Bundle Docs
    ├── frontend/          # Frontend-Snippets (lazyIcons, styleUtils)
    └── src/
        ├── lfx/          # Backend Components
        └── frontend/      # Frontend Icons
```

---

## Hinweis zur KI-Unterstützung

Bei der Entwicklung dieses Projekts wurden teilweise oder vollständig KI-gestützte Tools und Technologien eingesetzt.
