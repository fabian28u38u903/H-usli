"""
Claude API Analyzer – verarbeitet alle Research-Daten und generiert
die strukturierte Onboarding-Analyse.
"""

import json
import anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL


def _format_research_for_prompt(research: dict) -> str:
    """Bereitet alle Recherche-Daten als lesbaren Text auf."""
    parts = []

    # YouTube DE
    yt_de = research.get("youtube", {}).get("de", [])
    if yt_de:
        parts.append("=== YouTube Wettbewerber (Deutschland) ===")
        for item in yt_de[:15]:
            title = item.get("title", "")
            desc = item.get("description", "")[:150]
            parts.append(f"- {title}: {desc}")

    # YouTube US
    yt_us = research.get("youtube", {}).get("us", [])
    if yt_us:
        parts.append("\n=== YouTube Wettbewerber (USA/International) ===")
        for item in yt_us[:15]:
            title = item.get("title", "")
            desc = item.get("description", "")[:150]
            parts.append(f"- {title}: {desc}")

    # Google Trends
    trends = research.get("trends", {}).get("interest_over_time", {})
    if trends:
        parts.append("\n=== Google Trends (Suchinteresse) ===")
        for kw, data in trends.items():
            parts.append(
                f"- '{kw}': Ø {data.get('average_interest', 'N/A')}/100, "
                f"Peak: {data.get('peak_interest', 'N/A')}, "
                f"Trend: {data.get('trend', 'N/A')}"
            )

    # Top Suchanfragen
    top_q = research.get("trends", {}).get("top_queries", {})
    if top_q:
        parts.append("\n=== Verwandte Top-Suchanfragen (Google) ===")
        for kw, queries in list(top_q.items())[:2]:
            parts.append(f"Für '{kw}':")
            for q in queries[:8]:
                parts.append(f"  - {q.get('query', '')} (Wert: {q.get('value', '')})")

    # Steigende Suchanfragen
    rising_q = research.get("trends", {}).get("rising_queries", {})
    if rising_q:
        parts.append("\n=== Steigende Suchanfragen (Kaufsignale) ===")
        for kw, queries in list(rising_q.items())[:2]:
            parts.append(f"Für '{kw}':")
            for q in queries[:8]:
                parts.append(f"  - {q.get('query', '')} (+{q.get('value', '')}%)")

    # Reddit
    reddit = research.get("web", {}).get("reddit", [])
    if reddit:
        parts.append("\n=== Reddit Diskussionen (echte Zielgruppen-Sprache) ===")
        for item in reddit[:15]:
            score = item.get("score", "")
            comments = item.get("num_comments", "")
            sub = item.get("subreddit", "")
            meta = f" [r/{sub}, {score} Upvotes, {comments} Kommentare]" if sub else ""
            parts.append(f"- {item.get('title', '')}{meta}: {item.get('snippet', '')[:300]}")

    # Web: Zielgruppen-Sprache
    audience = research.get("web", {}).get("audience_language", [])
    if audience:
        parts.append("\n=== Foren & Diskussionen (Zielgruppen-Sprache) ===")
        for item in audience[:10]:
            parts.append(f"- {item.get('title', '')}: {item.get('snippet', '')[:200]}")

    # Web: Kaufintent
    purchase = research.get("web", {}).get("purchase_intent", [])
    if purchase:
        parts.append("\n=== Kaufintent-Signale (Web) ===")
        for item in purchase[:10]:
            parts.append(f"- {item.get('title', '')}: {item.get('snippet', '')[:200]}")

    # Web: SEO-Fragen
    seo = research.get("web", {}).get("seo_questions", [])
    if seo:
        parts.append("\n=== SEO-Fragen der Zielgruppe ===")
        for item in seo[:10]:
            parts.append(f"- {item.get('title', '')}: {item.get('snippet', '')[:150]}")

    # Branchennews
    news = research.get("web", {}).get("industry_news", [])
    if news:
        parts.append("\n=== Aktuelle Branchennews & Gesetze ===")
        for item in news[:8]:
            parts.append(f"- {item.get('title', '')}: {item.get('snippet', '')[:150]}")

    return "\n".join(parts)


def analyze(client: dict, research: dict) -> dict:
    """
    Schickt alle Recherche-Daten an Claude und erhält die strukturierte Analyse.
    Gibt ein Dict mit allen Report-Sektionen zurück.
    """
    print("  🤖 Claude API Analyse läuft...")

    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY nicht gesetzt. Bitte in .env eintragen.")

    client_ai = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    research_text = _format_research_for_prompt(research)

    system_prompt = """Du bist ein erfahrener Marketing- und YouTube-Stratege für deutschsprachige Unternehmen.
Du analysierst Märkte, Zielgruppen und Wettbewerber und erstellst präzise, umsetzbare Onboarding-Analysen.
Antworte immer auf Deutsch. Sei konkret, praxisnah und direkt umsetzbar.
Vermeide generische Aussagen – jede Empfehlung soll spezifisch für diese Nische sein."""

    user_prompt = f"""Erstelle eine vollständige Onboarding-Marktanalyse für folgenden Kunden:

KUNDE: {client['name']}
NISCHE: {client['niche']}
DIENSTLEISTUNG: {client['service']}
NUTZENVERSPRECHEN:
{chr(10).join(f'- {b}' for b in client.get('benefits', []))}
ZIELGRUPPE: {client.get('target_audience', '')}

RECHERCHE-DATEN:
{research_text}

Erstelle die Analyse als JSON mit folgender Struktur:

{{
  "demographics": {{
    "primary_audience": "...",
    "age_range": "...",
    "gender": "...",
    "profession": "...",
    "income": "...",
    "education": "...",
    "key_characteristics": ["...", "...", "..."]
  }},
  "psychographics": {{
    "values": ["...", "..."],
    "fears": ["...", "..."],
    "desires": ["...", "..."],
    "self_image": "...",
    "worldview": "..."
  }},
  "language_tonality": {{
    "own_words": ["...", "...", "..."],
    "preferred_tone": "...",
    "du_or_sie": "...",
    "emotional_vs_rational": "...",
    "taboo_words": ["...", "..."],
    "power_phrases": ["...", "..."]
  }},
  "purchase_behavior": {{
    "trigger_moments": ["...", "...", "..."],
    "decision_duration": "...",
    "buying_signals": ["...", "...", "..."],
    "main_objections": ["...", "...", "..."],
    "trust_factors": ["...", "...", "..."],
    "seasonal_patterns": "..."
  }},
  "seo_analysis": {{
    "top_keywords": [
      {{"keyword": "...", "intent": "informational|navigational|commercial|transactional", "priority": "hoch|mittel|niedrig"}},
      {{"keyword": "...", "intent": "...", "priority": "..."}}
    ],
    "purchase_intent_keywords": ["...", "...", "..."],
    "rising_keywords": ["...", "..."],
    "content_gaps": ["...", "..."],
    "seo_recommendations": ["...", "..."]
  }},
  "competitor_analysis": {{
    "de_market": {{
      "top_channels": [
        {{"name": "...", "strength": "...", "weakness": "..."}},
        {{"name": "...", "strength": "...", "weakness": "..."}}
      ],
      "market_gaps": ["...", "..."],
      "dominant_formats": ["...", "..."]
    }},
    "us_market": {{
      "top_channels": [
        {{"name": "...", "strength": "...", "angle": "..."}}
      ],
      "transferable_concepts": ["...", "...", "..."],
      "successful_hooks": ["...", "..."]
    }}
  }},
  "content_strategy": {{
    "unique_positioning": "...",
    "channel_angle": "...",
    "awareness_content": [
      {{"title": "...", "format": "...", "hook": "..."}},
      {{"title": "...", "format": "...", "hook": "..."}}
    ],
    "trust_content": [
      {{"title": "...", "format": "...", "hook": "..."}},
      {{"title": "...", "format": "...", "hook": "..."}}
    ],
    "conversion_content": [
      {{"title": "...", "format": "...", "hook": "..."}},
      {{"title": "...", "format": "...", "hook": "..."}}
    ],
    "posting_frequency": "...",
    "ideal_video_length": "...",
    "thumbnail_style": "...",
    "cta_recommendation": "..."
  }},
  "executive_summary": "Ein prägnanter Überblick über die wichtigsten Erkenntnisse und Handlungsempfehlungen (3-5 Sätze)."
}}

Gib NUR das JSON zurück, ohne Markdown-Codeblöcke oder zusätzlichen Text."""

    message = client_ai.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": user_prompt}],
        system=system_prompt,
    )

    raw = message.content[0].text.strip()

    # JSON bereinigen falls Markdown-Blöcke enthalten sind
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        analysis = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: rohen Text zurückgeben
        analysis = {"raw": raw}

    print("  ✅ Analyse abgeschlossen")
    return analysis
