# st-langflow-aio

**Langflow all-in-one** mit voll integriertem MiniMax Provider (im Agent Dropdown).

> **v0.1.5** - Verifiziert funktionsfaehig. MiniMax ist Global Model Provider mit vollstaendiger Anthropic-SDK-Integration.

## Quickstart

```bash
# 1. .env anlegen
cat > .env << 'EOF'
LANGFLOW_SECRET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
LANGFLOW_SUPERUSER=alephtex@gmail.com
LANGFLOW_SUPERUSER_PASSWORD=changeme
MINIMAX_API_KEY=your_key_from_platform_minimax_io
EOF

# 2. Bauen
docker build --no-cache -t st-langflow-aio .

# 3. Starten
docker compose up -d

# 4. Browser: http://localhost:7860
#    Settings -> Model Providers -> MiniMax -> API Key eintragen
#    Neuer Flow -> Agent -> Model Provider: MiniMax -> Model: MiniMax-M3
```

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

1. Hole dir einen Key auf https://platform.minimax.io/
2. In Langflow: **Settings → Model Providers** → **MiniMax** → API Key eintragen → Save
3. Neuer Flow → **Agent** → **Model Provider: MiniMax** → **Model: MiniMax-M3**

### Unterstuetzte Modelle

| Model | Context | Tool Calling | Besonderes |
|-------|---------|-------------|------------|
| MiniMax-M3 | 1M | ✅ | Bild/Video/Thinking |
| MiniMax-M2.7 | 200k | ✅ | highspeed ~100 tps |
| MiniMax-M2.5 | 200k | ✅ | highspeed ~100 tps |
| MiniMax-M2.1 | 200k | ✅ | highspeed ~100 tps |
| MiniMax-M2 | 200k | ✅ | Agentic/Reasoning |

## Verifikation nach dem Build

```bash
# Verifiziert alle 5 Patches
docker exec -it $(docker ps -qf name=langflow) python3 /tmp/verify_inplace.py

# Testet die echte API-Verbindung
docker exec -it $(docker ps -qf name=langflow) python3 /tmp/smoke_test.py <dein_key>
```

## Troubleshooting

| Problem | Loesung |
|---------|--------|
| MiniMax nicht in Settings sichtbar | `docker compose down -v` (DB-Cache loeschen) |
| `invalid x-api-key` Fehler | Key direkt im [MiniMax Console](https://platform.minimax.io/) pruefen |
| Provider im Agent nicht waehlbar | Browser-Hard-Refresh (Strg+Shift+R) |
| Build dauert ewig | `docker build --no-cache` verwenden |

## Wie die Integration funktioniert

Detaillierte technische Dokumentation: [docs/INTEGRATION.md](docs/INTEGRATION.md)

Kurzfassung: 5 Backend-Files in `site-packages/lfx/` werden beim Build gepatcht:

```
lfx/base/models/minimax_constants.py            NEU - Modelliste
lfx/base/models/model_metadata.py              MODEL_PROVIDER_METADATA["MiniMax"]
lfx/base/models/unified_models/provider_queries.py   MINIMAX_MODELS_DETAILED
lfx/base/models/model_input_constants.py       MODEL_PROVIDERS_DICT + LIST
lfx/base/models/unified_models/instantiation.py     get_llm() MiniMax base_url Special-Case
lfx/components/minimax/minimax.py              LCModelComponent (Component Class)
```

Wichtig: nach Aenderungen **immer** `--no-cache` und Volume loeschen,
weil Langflow die Component-Templates in der DB cached.

## Projekt-Struktur

```
st-langflow-aio/
├── Dockerfile                  # Build mit allen Patches
├── docker-compose.yml          # Postgres + Langflow
├── README.md                   # Diese Datei
├── docs/
│   └── INTEGRATION.md          # Technische Doku
└── inject/
    ├── lfx_components/          # MiniMax Component Source
    │   └── lfx/components/minimax/
    │       ├── __init__.py
    │       └── minimax.py
    ├── patch_full_provider.py   # Hauptpatch-Script
    ├── verify_inplace.py        # Verifiziert die Patches
    └── smoke_test.py            # Testet API-Verbindung
```

## Releases

| Version | Datum | Notizen |
|---------|-------|--------|
| v0.1.5 | 2026-06-19 | `get_llm()` base_url Fix |
| v0.1.1 | 2026-06-19 | SecretStr Bug-Fix |
| v0.1.0 | 2026-06-19 | Erste main Release |
| v0.0.x | 2026-06-19 | Pre-main Entwicklungs-Iterationen |

---

## Hinweis zur KI-Unterstuetzung

Bei der Entwicklung dieses Projekts wurden teilweise oder vollstaendig KI-gestuetzte Tools und Technologien eingesetzt.
