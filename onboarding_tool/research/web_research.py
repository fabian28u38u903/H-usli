"""
Web-Recherche via DuckDuckGo:
- Reddit (echte Sprache der Zielgruppe, Fragen, Diskussionen)
- Foren & Communities
- Kaufnahe Suchanfragen
- Branchennews & aktuelle Diskussionen
"""

import time
import requests
from duckduckgo_search import DDGS

REDDIT_HEADERS = {"User-Agent": "OnboardingResearchBot/1.0"}

# Deutsche & englische Subreddits je Themenbereich
REDDIT_SUBREDDITS_DE = [
    "Finanzen", "Unternehmertum", "Steuern", "Recht",
    "Vermögensaufbau", "personalfinance", "germany"
]
REDDIT_SUBREDDITS_EN = [
    "personalfinance", "legaladvice", "Entrepreneur",
    "smallbusiness", "investing", "fatFIRE"
]


def _ddg_search(query: str, max_results: int = 8) -> list[dict]:
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", "")[:400],
                    "source": "web",
                })
    except Exception as e:
        print(f"    ⚠️  DDG Fehler: {e}")
    return results


def _reddit_search_ddg(keyword: str, subreddit: str = None, max_results: int = 6) -> list[dict]:
    """Sucht Reddit-Posts via DuckDuckGo (kein API Key nötig)."""
    if subreddit:
        query = f"site:reddit.com/r/{subreddit} {keyword}"
    else:
        query = f"site:reddit.com {keyword}"
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", "")[:500],
                    "source": "reddit",
                })
    except Exception as e:
        print(f"    ⚠️  Reddit DDG Fehler: {e}")
    return results


def _reddit_api_search(keyword: str, subreddit: str = None, limit: int = 10) -> list[dict]:
    """Sucht Reddit-Posts direkt via Reddit JSON API (kein Key nötig)."""
    results = []
    try:
        if subreddit:
            url = f"https://www.reddit.com/r/{subreddit}/search.json"
            params = {"q": keyword, "restrict_sr": 1, "sort": "top", "limit": limit, "t": "year"}
        else:
            url = "https://www.reddit.com/search.json"
            params = {"q": keyword, "sort": "top", "limit": limit, "t": "year"}

        resp = requests.get(url, params=params, headers=REDDIT_HEADERS, timeout=10)
        if resp.status_code != 200:
            return results

        posts = resp.json().get("data", {}).get("children", [])
        for post in posts:
            d = post.get("data", {})
            results.append({
                "title": d.get("title", ""),
                "url": f"https://reddit.com{d.get('permalink', '')}",
                "snippet": d.get("selftext", "")[:500] or d.get("title", ""),
                "score": d.get("score", 0),
                "num_comments": d.get("num_comments", 0),
                "subreddit": d.get("subreddit", ""),
                "source": "reddit_api",
            })
        time.sleep(0.5)
    except Exception as e:
        print(f"    ⚠️  Reddit API Fehler: {e}")
    return results


def research_reddit(client: dict) -> list[dict]:
    """
    Recherchiert Reddit gezielt nach:
    - Fragen der Zielgruppe
    - Erfahrungsberichte
    - Kritik & Einwände
    - Kaufentscheidungen
    """
    print("    → Reddit-Recherche läuft...")
    results = []

    # Direkte Reddit API Suche (Top-Posts, letztes Jahr)
    for keyword in client["keywords_de"][:3]:
        # Allgemeine Reddit-Suche auf Deutsch
        hits = _reddit_api_search(keyword, limit=8)
        results.extend(hits)

        # Spezifische deutsche Subreddits
        for sub in ["Finanzen", "Steuern", "Unternehmertum", "Vermögensaufbau"]:
            hits = _reddit_api_search(keyword, subreddit=sub, limit=5)
            results.extend(hits)
            time.sleep(0.3)

    # Englische Suche für US-Markt-Insights
    for keyword in client["keywords_en"][:2]:
        for sub in ["personalfinance", "Entrepreneur", "fatFIRE"]:
            hits = _reddit_api_search(keyword, subreddit=sub, limit=5)
            results.extend(hits)
            time.sleep(0.3)

    # Fallback via DDG falls Reddit API wenig liefert
    if len(results) < 5:
        print("    → Reddit Fallback via DuckDuckGo...")
        for keyword in client["keywords_de"][:2]:
            results.extend(_reddit_search_ddg(keyword, max_results=6))

    # Duplikate entfernen & nach Score sortieren
    seen = set()
    unique = []
    for r in results:
        key = r.get("url", "") + r.get("title", "")
        if key not in seen and r.get("title"):
            seen.add(key)
            unique.append(r)

    unique.sort(key=lambda x: x.get("score", 0), reverse=True)

    print(f"    ✅ Reddit: {len(unique)} Posts gefunden")
    return unique


def research_target_audience_language(client: dict) -> list[dict]:
    """Sucht echte Diskussionen der Zielgruppe in Foren (ohne Reddit – separat)."""
    print("    → Foren & Communities...")
    results = []
    queries = [
        f'{client["niche"]} Forum Erfahrungen',
        f'Fragen {client["niche"]} Unternehmer',
        f'Nachteile {client["niche"]}',
        f'Kosten {client["niche"]}',
        f'{client["niche"]} lohnt sich',
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


def _detect_relevant_subreddits(client: dict) -> list[str]:
    """
    Erkennt automatisch passende Subreddits basierend auf Nische & Keywords.
    Claude API analysiert später diese Posts – daher möglichst breit suchen.
    """
    niche_lower = (client.get("niche", "") + " " + client.get("service", "")).lower()

    subreddits = []

    # Finanzen & Steuern
    if any(w in niche_lower for w in ["steuer", "stiftung", "erbschaft", "vermögen", "finanz"]):
        subreddits += ["Finanzen", "Steuern", "Vermögensaufbau", "personalfinance", "fatFIRE"]

    # Unternehmertum & Business
    if any(w in niche_lower for w in ["unternehm", "business", "gründ", "selbstständig", "startup"]):
        subreddits += ["Unternehmertum", "Entrepreneur", "smallbusiness", "de_IAmA"]

    # Immobilien
    if any(w in niche_lower for w in ["immobil", "real estate", "wohnung", "miete"]):
        subreddits += ["immobilieninvestments", "realestateinvesting", "landlord"]

    # Marketing & Social Media
    if any(w in niche_lower for w in ["marketing", "youtube", "social media", "content"]):
        subreddits += ["marketing", "youtube", "socialmedia", "content_marketing"]

    # Gesundheit & Fitness
    if any(w in niche_lower for w in ["fitness", "gesundheit", "ernährung", "sport", "abnehm"]):
        subreddits += ["fitness", "nutrition", "loseit", "GesundheitDE"]

    # Recht & Compliance
    if any(w in niche_lower for w in ["recht", "legal", "anwalt", "compliance", "datenschutz"]):
        subreddits += ["Recht", "legaladvice", "germany"]

    # Fallback: immer dabei
    subreddits += ["germany", "de"]

    # Duplikate entfernen
    seen = set()
    unique = []
    for s in subreddits:
        if s not in seen:
            seen.add(s)
            unique.append(s)

    return unique


def research_reddit(client: dict) -> list[dict]:
    """
    Recherchiert Reddit gezielt nach:
    - Fragen der Zielgruppe
    - Erfahrungsberichte
    - Kritik & Einwände
    - Kaufentscheidungen

    Subreddits werden automatisch zur Nische erkannt.
    """
    print("    → Reddit-Recherche läuft...")
    results = []

    relevant_subreddits_de = _detect_relevant_subreddits(client)
    relevant_subreddits_en = [s for s in relevant_subreddits_de if not any(
        w in s.lower() for w in ["de", "germany", "steuern", "finanzen", "recht", "unternehmertum"]
    )]

    print(f"    → Subreddits erkannt: {', '.join(relevant_subreddits_de[:6])}")

    # Deutsche Keywords auf relevanten Subreddits
    for keyword in client["keywords_de"][:3]:
        hits = _reddit_api_search(keyword, limit=8)
        results.extend(hits)

        for sub in relevant_subreddits_de[:4]:
            hits = _reddit_api_search(keyword, subreddit=sub, limit=5)
            results.extend(hits)
            time.sleep(0.3)

    # Englische Keywords auf englischen Subreddits
    for keyword in client["keywords_en"][:2]:
        for sub in relevant_subreddits_en[:3]:
            hits = _reddit_api_search(keyword, subreddit=sub, limit=5)
            results.extend(hits)
            time.sleep(0.3)

    # Fallback via DDG
    if len(results) < 5:
        print("    → Reddit Fallback via DuckDuckGo...")
        for keyword in client["keywords_de"][:2]:
            results.extend(_reddit_search_ddg(keyword, max_results=6))

    # Duplikate entfernen & nach Score sortieren
    seen = set()
    unique = []
    for r in results:
        key = r.get("url", "") + r.get("title", "")
        if key not in seen and r.get("title"):
            seen.add(key)
            unique.append(r)

    unique.sort(key=lambda x: x.get("score", 0), reverse=True)
    print(f"    ✅ Reddit: {len(unique)} Posts gefunden")
    return unique


def research_web(client: dict) -> dict:
    """Hauptfunktion: Führt alle Web-Recherchen durch."""
    print("  🌐 Web-Recherche läuft...")
    results = {
        "reddit": research_reddit(client),
        "audience_language": research_target_audience_language(client),
        "purchase_intent": research_purchase_intent(client),
        "industry_news": research_industry_news(client),
        "seo_questions": research_seo_keywords(client),
    }
    total = sum(len(v) for v in results.values())
    print(f"  ✅ Web: {total} Quellen gesammelt")
    return results
