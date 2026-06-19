# MiniMax Bundle fuer Langflow

Anthropic-kompatibler MiniMax Provider fuer Langflow.

## Was ist das?

MiniMax bietet einen **Anthropic-SDK-kompatiblen** Endpunkt. Dieses Bundle
bindet die MiniMax-Modelle (M3, M2.7, M2.5, M2.1, M2) ein.

API-Docs: https://platform.minimax.io/docs/api-reference/text-anthropic-api

Unterstuetzte Modelle:
- MiniMax-M3        (1M context, Bild/Video, Thinking)
- MiniMax-M2.7     (200k context, highspeed ~100 tps)
- MiniMax-M2.5     (200k context, highspeed ~100 tps)
- MiniMax-M2.1     (200k context, highspeed ~100 tps)
- MiniMax-M2       (200k context, Agentic/Reasoning)

## Installation

### Im st-langflow-aio Docker Image (empfohlen)

Bereits integriert. Einfach bauen und starten.

### Variante: In bestehendes Langflow-Source-Repo einbauen

1. **Backend-Komponente kopieren**
   ```bash
   cp -r src/lfx/src/lfx/components/minimax \
         /pfad/zu/langflow/src/lfx/src/lfx/components/
   ```

2. **Frontend-Icon kopieren**
   ```bash
   cp -r src/frontend/src/icons/MiniMax \
         /pfad/zu/langflow/src/frontend/src/icons/
   ```

3. **Frontend-Registrierung** — in `src/frontend/src/icons/lazyIconImports.ts`:
   ```ts
     MiniMax: () =>
       import("@/icons/MiniMax").then((mod) => ({ default: mod.MiniMaxIcon })),
   ```

4. **Sidebar-Eintrag** — in `src/frontend/src/utils/styleUtils.ts`,
   in `SIDEBAR_BUNDLES` Array:
   ```ts
   { display_name: "MiniMax", name: "minimax", icon: "MiniMax" },
   ```

5. **Neu bauen**
   ```bash
   cd /pfad/zu/langflow
   make install_frontend && make build_frontend && make install_backend
   uv run langflow run --port 7860
   ```

## Verwendung

### Weg 1: Global Model Provider (neu)
1. **Settings → Model Providers** → MiniMax auswaehlen
2. API Key eintragen
3. Model waehlen
4. Im Agent: "Model Provider" → "MiniMax"

### Weg 2: Custom Component verdrahten
1. Agent: "Model Provider" → "Custom"
2. MiniMax Component in Flow ziehen
3. LanguageModel Output → Agent Language Model Input verbinden

## Dateistruktur

```
src/lfx/src/lfx/components/minimax/
├── __init__.py           # Lazy-Import Boilerplate
└── minimax.py           # Hauptkomponente (LCModelComponent)

src/frontend/src/icons/MiniMax/
├── index.tsx             # React forwardRef Wrapper
├── MiniMaxIcon.jsx        # JSX SVG Komponente
└── MiniMaxIcon.svg       # Rohes SVG
```

---

## Hinweis zur KI-Unterstuetzung

Bei der Entwicklung dieses Projekts wurden teilweise oder vollstaendig KI-gestuetzte Tools und Technologien eingesetzt.
