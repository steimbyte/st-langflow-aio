# st-langflow-aio

**Langflow all-in-one** — Custom Docker Image mit Extras.

## Was ist drin

| Tool | Art | Zweck |
|------|------|--------|
| Langflow | latest | UI/Framework |
| ffmpeg | apt | Video/Audio Processing |
| Chromium | apt | Browser Automation (puppeteer) |
| Node.js | 20.x | JavaScript Tooling |
| yt-dlp | pip | YouTube/Media Download |
| yt-dlp-wrap | npm | JS-Wrapper fuer yt-dlp |
| puppeteer-core | npm | Browser Control (ohne Download) |
| langchain-anthropic | pip | MiniMax LLM Provider |
| **MiniMax LLM** | Custom Component | Anthropic-kompatibel |

## MiniMax Custom Component

Der MiniMax LLM Component erscheint in der **Sidebar → Custom Components** als **"MiniMax LLM"**.

### Verwendung mit dem Agent

1. **Simple Agent** Flow oeffnen (oder neuen erstellen)
2. Agent: **"Model Provider"** → **"Custom"** auswaehlen
3. **MiniMax LLM** Component aus der Sidebar in den Flow ziehen
4. MiniMax LLM: API Key + Model konfigurieren
5. MiniMax LLM **Language Model** Output → Agent **Language Model** Input verbinden
6. **Playground** — chatten mit MiniMax

### Unterstuetzte Modelle

| Model | Context | Besonderes |
|-------|---------|------------|
| MiniMax-M3 | 1M | Bild/Video/Thinking |
| MiniMax-M2.7 | 200k | highspeed ~100 tps |
| MiniMax-M2.5 | 200k | highspeed ~100 tps |
| MiniMax-M2.1 | 200k | highspeed ~100 tps |
| MiniMax-M2 | 200k | Agentic/Reasoning |

API-Docs: https://platform.minimax.io/docs/api-reference/text-anthropic-api

## Build & Start

```bash
# .env Datei erstellen
cat > .env << 'EOF'
LANGFLOW_SECRET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
LANGFLOW_SUPERUSER=alephtex@gmail.com
LANGFLOW_SUPERUSER_PASSWORD=changeme
MINIMAX_API_KEY=dein_key_von_platform.minimax.io
EOF

# Bauen (--no-cache wichtig nach Aenderungen)
docker build --no-cache -t st-langflow-aio .

# Starten (Volume wird geloescht = frischer DB-Start)
docker compose up -d
```

Oder mit Docker Compose und bestehendem Netzwerk `npm`:

```bash
# Netzwerk erstellen falls noetig
docker network create npm 2>/dev/null || true

docker build --no-cache -t st-langflow-aio .
docker run -d \
  --name langflow \
  --network npm \
  -p 7860:7860 \
  -v $(pwd)/data:/app/langflow \
  -e LANGFLOW_SECRET_KEY=<fernet-key> \
  -e LANGFLOW_SUPERUSER=alephtex@gmail.com \
  -e LANGFLOW_SUPERUSER_PASSWORD=<pwd> \
  -e LANGFLOW_DATABASE_URL=postgresql://langflow:langflow@postgres:5432/langflow \
  st-langflow-aio
```

Fernet Key generieren:
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Ordnerstruktur

```
.
├── Dockerfile
├── docker-compose.yml
├── README.md
└── inject/
    └── components/
        ├── __init__.py
        └── minimax.py      # Custom Component -> Sidebar
```

## Bekannte Probleme

**"Component nicht in der Sidebar"** nach Update:
- `docker build --no-cache -t st-langflow-aio .`
- Docker Compose: `docker compose down -v && docker compose up -d` (loescht Volume)

---

## Hinweis zur KI-Unterstuetzung

Bei der Entwicklung dieses Projekts wurden teilweise oder vollstaendig KI-gestuetzte Tools und Technologien eingesetzt.
