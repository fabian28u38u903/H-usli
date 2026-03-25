# Onboarding Marktanalyse Tool

Automatisierte Markt-, Zielgruppen- & SEO-Analyse für YouTube-Kanäle.

## Setup

```bash
cd onboarding_tool
pip install -r requirements.txt
cp .env.example .env
# .env bearbeiten und API Keys eintragen
```

## Verwendung

```bash
# Mit Standard-Kunden (Michel Stiftung Beratung)
python main.py

# Mit eigenem Kunden
python main.py --client "Kundenname" --niche "Finanzberatung" --output report.pdf

# Gecachte Recherche verwenden (spart Zeit & API-Kosten)
python main.py --use-cache research_cache_Michel_Stiftung_Beratung.json
```

## Ausgabe

- `report_[Kunde]_[Datum].pdf` – vollständiger PDF-Report
- `research_cache_[Kunde].json` – gecachte Recherche-Daten
- `analysis_[Kunde].json` – Claude API Analyse-Ergebnis

## Report-Inhalt

1. Demografisches Profil
2. Psychografisches Profil
3. Sprache & Tonalität
4. Kaufverhalten & Trigger
5. SEO-Analyse (Keywords, Intent, Lücken)
6. Wettbewerber-Analyse (DE + US)
7. Content-Strategie (Video-Ideen je Funnel-Stufe)

## API Keys

| Key | Pflicht | Wo |
|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ Ja | console.anthropic.com |
| `YOUTUBE_API_KEY` | Optional | console.cloud.google.com |

Ohne YouTube API Key wird DuckDuckGo als Fallback genutzt.
