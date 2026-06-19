# MiniMax Bundle fuer Langflow

Anthropic-kompatibler MiniMax Provider fuer Langflow.

## Was ist das?

MiniMax bietet einen **Anthropic-SDK-kompatiblen** Endpunkt. Dieses Bundle
bindet die MiniMax-Modelle (M3, M2.7, M2.5, M2.1, M2) direkt in Langflow ein
— mit dem nativen Anthropic-Komponenten-Interface.

API-Docs: https://platform.minimax.io/docs/api-reference/text-anthropic-api

Unterstuetzte Modelle:
- MiniMax-M3        (1M context, Bild/Video, Thinking)
- MiniMax-M2.7     (200k context, highspeed ~100 tps)
- MiniMax-M2.5     (200k context, highspeed ~100 tps)
- MiniMax-M2.1     (200k context, highspeed ~100 tps)
- MiniMax-M2       (200k context, Agentic/Reasoning)


## Installation — 2 Varianten

### Variante A: In bestehendes Langflow-Source-Repo einbauen

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
   // Finde die Zeile mit "MistralAI:" und fuege DAVOR ein:
     MiniMax: () =>
       import("@/icons/MiniMax").then((mod) => ({ default: mod.MiniMaxIcon })),
   ```

4. **Sidebar-Eintrag** — in `src/frontend/src/utils/styleUtils.ts`,
   in `SIDEBAR_BUNDLES` Array, alphabetisch einfuegen:
   ```ts
   { display_name: "MiniMax", name: "minimax", icon: "MiniMax" },
   ```

5. **Neu bauen**
   ```bash
   cd /pfad/zu/langflow
   make install_frontend && make build_frontend && make install_backend
   uv run langflow run --port 7860
   ```

### Variante B: Custom Component (kein Source-Edit noetig)

Speichere `src/lfx/src/lfx/components/minimax/minimax.py` als
Custom Component in deinem `LANGFLOW_COMPONENTS_PATH` Verzeichnis.
Das Icon muss dann separat konfiguriert werden.

**Erforderliches pip-Paket:**
```bash
pip install langchain-anthropic
```

In dein Docker-Image oder Compose eintragen:
```bash
MINIMAX_API_KEY=your_key_here
```


## Verwendung

1. **Settings → Model Providers** oder im Agent: "Model Provider" → MiniMax
2. **API Key** eintragen (von https://platform.minimax.io)
3. **Model** waehlen (MiniMax-M3 empfohlen)
4. Max Tokens, Temperature, Top P wie gewohnt

M3 unterstuetzt Bild- und Video-Input (URL oder Base64).
M2.x unterstuetzen nur Text + Tool Calling.


## Dateistruktur

```
src/lfx/src/lfx/components/minimax/
├── __init__.py           # Lazy-Import Boilerplate
└── minimax.py           # Hauptkomponente (LCModelComponent)

src/frontend/src/icons/MiniMax/
├── index.tsx             # React forwardRef Wrapper
├── MiniMaxIcon.jsx       # JSX SVG Komponente
└── MiniMaxIcon.svg       # Rohes SVG
```
