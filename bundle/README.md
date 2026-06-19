# MiniMax Component Source

Dieser Ordner enthält die Original-Source-Dateien für das MiniMax Bundle.

**Aktueller Ansatz**: Custom Component (`inject/components/minimax.py`)
wird direkt in `/app/custom_components/` im Docker-Image installiert.

Dieser `bundle/` Ordner ist nur als Referenz für den Fall, dass MiniMax
später als offizieller Global Model Provider in Langflow integriert werden soll.

## Original-Struktur

```
bundle/
├── src/lfx/src/lfx/components/minimax/
│   ├── __init__.py
│   └── minimax.py           # LCModelComponent (Backend)
└── src/frontend/src/icons/MiniMax/
    ├── index.tsx              # React Icon Wrapper
    ├── MiniMaxIcon.jsx        # JSX SVG
    └── MiniMaxIcon.svg        # Roh-SVG
```

## Unterschied Custom Component vs. Global Provider

| | Custom Component | Global Provider |
|---|---|---|
| Sidebar | ✅ Ja, Custom Components | ❌ Nein |
| Settings → Model Providers | ❌ Nein | ✅ Ja |
| Agent "Model Provider" Dropdown | ❌ Nein (→ "Custom" nutzen) | ✅ Ja |
| Aufwand | Niedrig | Hoch (Frontend + Backend + Patch) |

**Empfehlung**: Custom Component reicht fuer 95% der Faelle aus.

---

## Hinweis zur KI-Unterstuetzung

Bei der Entwicklung dieses Projekts wurden teilweise oder vollstaendig KI-gestuetzte Tools und Technologien eingesetzt.
