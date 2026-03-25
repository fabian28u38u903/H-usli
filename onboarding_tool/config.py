import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

CLAUDE_MODEL = "claude-sonnet-4-6"

# Standard Kunden-Template – wird in main.py überschrieben
DEFAULT_CLIENT = {
    "name": "Michel Stiftung Beratung",
    "niche": "Familienstiftung & Vermögensschutz",
    "service": "Beratung zur Gründung von Familienstiftungen in Deutschland",
    "benefits": [
        "Steuern sparen (Erbschaftsteuer, Schenkungsteuer)",
        "Lebenswerk sichern",
        "Unternehmensnachfolge regeln",
        "Vermögensschutz für die Familie",
    ],
    "keywords_de": [
        "Familienstiftung gründen",
        "Stiftung Steuern sparen",
        "Erbschaftsteuer vermeiden",
        "Unternehmensnachfolge Stiftung",
        "Familienstiftung Vorteile",
        "Vermögensschutz Deutschland",
    ],
    "keywords_en": [
        "family foundation Germany",
        "asset protection foundation",
        "inheritance tax avoidance Germany",
        "business succession foundation",
    ],
    "target_audience": "Unternehmer ab 45 Jahren mit erfolgreichem Unternehmen",
    "competitor_markets": ["DE", "US"],
}
