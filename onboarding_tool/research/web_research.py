"""
Web-Recherche via DuckDuckGo:
- Foren & Reddit (echte Sprache der Zielgruppe)
- Kaufnahe Suchanfragen
- Branchennews & aktuelle Diskussionen
"""

from duckduckgo_search import DDGS


def _ddg_search(query: str, max_results: int = 8) -> list[dict]:
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", "")[:400],
                })
    except Exception as e:
        print(f"    ⚠️  DDG Fehler: {e}")
    return results


def research_target_audience_language(client: dict) -> list[dict]:
    """Sucht echte Diskussionen der Zielgruppe in Foren & Reddit."""
    print("    → Zielgruppen-Sprache & Foren...")
    results = []
    queries = [
        f'{client["niche"]} Forum Erfahrungen',
        f'{client["niche"]} Reddit',
        f'Fragen {client["niche"]} Unternehmer',
        f'Nachteile {client["niche"]}',
        f'Kosten {client["niche"]}',
    ]
    for q in queries:
        results.extend(_ddg_search(q, max_results=5))
    return results


def research_purchase_intent(client: dict) -> list[dict]:
    """Sucht kaufnahe Keywords und Suchmuster."""
    print("    → Kaufintent-Signale...")
    results = []
    queries = [
        f'{client["niche"]} Beratung Kosten',
        f'{client["niche"]} Anbieter Vergleich',
        f'{client["niche"]} empfehlenswert seriös',
        f'wann lohnt sich {client["niche"]}',
        f'{client["niche"]} Erfahrungsberichte',
    ]
    for q in queries:
        results.extend(_ddg_search(q, max_results=5))
    return results


def research_industry_news(client: dict) -> list[dict]:
    """Recherchiert aktuelle Branchennews und Gesetzesänderungen."""
    print("    → Branchennews & Gesetze...")
    results = []
    queries = [
        f'{client["niche"]} aktuell 2024 2025',
        f'Steuerrecht {client["niche"]} Änderungen',
        f'{client["niche"]} Gesetz Bundesfinanzhof',
    ]
    for q in queries:
        results.extend(_ddg_search(q, max_results=5))
    return results


def research_seo_keywords(client: dict) -> list[dict]:
    """Sucht weitere SEO-relevante Keywords über AnswerThePublic-ähnliche Abfragen."""
    print("    → SEO Keywords & Fragen...")
    results = []
    base = client["keywords_de"][0]
    questions = [
        f"wie {base}",
        f"was kostet {base}",
        f"warum {base}",
        f"welche Vorteile {base}",
        f"wann {base} sinnvoll",
        f"{base} Risiken",
    ]
    for q in questions:
        results.extend(_ddg_search(q, max_results=4))
    return results


def research_web(client: dict) -> dict:
    """Hauptfunktion: Führt alle Web-Recherchen durch."""
    print("  🌐 Web-Recherche läuft...")
    results = {
        "audience_language": research_target_audience_language(client),
        "purchase_intent": research_purchase_intent(client),
        "industry_news": research_industry_news(client),
        "seo_questions": research_seo_keywords(client),
    }
    total = sum(len(v) for v in results.values())
    print(f"  ✅ Web: {total} Quellen gesammelt")
    return results
