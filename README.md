# st-langflow-aio

**Langflow all-in-one** mit voll integriertem MiniMax Provider (im Agent Dropdown).

## Was ist drin

| Tool | Zweck |
|------|--------|
| Langflow | UI/Framework |
| ffmpeg | Video/Audio |
| Chromium | Browser Automation (puppeteer) |
| Node.js 20 | JavaScript Tooling |
| yt-dlp | Media Download |
| puppeteer-core | Browser Control |
| **MiniMax LLM** | **Voll integrierter Global Model Provider** |

## MiniMax als Global Model Provider

MiniMax ist **vollwertig** wie OpenAI, Anthropic oder Ollama integriert:

- **Settings → Model Providers** → "MiniMax" mit API-Key Feld
- **Agent "Model Provider" Dropdown** → "MiniMax" direkt auswaehlbar
- **Agent "Model" Feld** → alle MiniMax-Modelle auswaehlbar

### Setup

```bash
# 1. Volume weg (DB Cache loeschen!)
docker compose down -v

# 2. Bauen
docker build --no-cache -t st-langflow-aio .

# 3. .env erstellen
cat > .env << 'EOF'
LANGFLOW_SECRET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
LANGFLOW_SUPERUSER=alephtex@gmail.com
LANGFLOW_SUPERUSER_PASSWORD=changeme
MINIMAX_API_KEY=your_key
EOF

# 4. Starten
docker compose up -d
```

### Verwendung

1. **http://localhost:7860** → einloggen
2. **Settings → Model Providers** → **MiniMax** → API Key eintragen → Save
3. Neuer Flow → **Agent** → **Model Provider: MiniMax** → **Model: MiniMax-M3**
4. Chatten!

## Unterstuetzte Modelle

| Model | Context | Tool Calling | Besonderes |
|-------|---------|-------------|------------|
| MiniMax-M3 | 1M | ✅ | Bild/Video/Thinking |
| MiniMax-M2.7 | 200k | ✅ | highspeed ~100 tps |
| MiniMax-M2.5 | 200k | ✅ | highspeed ~100 tps |
| MiniMax-M2.1 | 200k | ✅ | highspeed ~100 tps |
| MiniMax-M2 | 200k | ✅ | Agentic/Reasoning |

## Wie die Integration funktioniert (technisch)

Der Provider wird **nicht** als Custom Component in die Sidebar gelegt, sondern
direkt in Langflow's Global Model Provider System registriert. Dafuer patchen wir
4 Backend-Dateien:

```
lfx/base/models/minimax_constants.py            NEU - Modelliste
lfx/base/models/model_metadata.py              MODEL_PROVIDER_METADATA["MiniMax"]
lfx/base/models/unified_models/provider_queries.py   MINIMAX_MODELS_DETAILED
lfx/base/models/model_input_constants.py       MODEL_PROVIDERS_DICT + LIST
```

Zusaetzlich wird `MiniMaxModelComponent` (LCModelComponent) in `lfx/components/`
installiert, damit das Frontend das Component-Template rendern kann.

Wichtig: nach Aenderungen **immer** `--no-cache` und Volume loeschen,
weil Langflow die Component-Templates in der DB cached.

---

## Hinweis zur KI-Unterstuetzung

Bei der Entwicklung dieses Projekts wurden teilweise oder vollstaendig KI-gestuetzte Tools und Technologien eingesetzt.
