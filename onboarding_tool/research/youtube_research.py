"""
YouTube Wettbewerber-Recherche.
Nutzt YouTube Data API v3 (wenn Key vorhanden) oder DuckDuckGo als Fallback.
"""

import os
import requests
from duckduckgo_search import DDGS

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"


def search_youtube_channels_api(keyword: str, lang: str = "de", max_results: int = 10) -> list[dict]:
    """Sucht YouTube-Kanäle via YouTube Data API v3."""
    params = {
        "part": "snippet",
        "q": keyword,
        "type": "channel",
        "maxResults": max_results,
        "relevanceLanguage": lang,
        "key": YOUTUBE_API_KEY,
    }
    resp = requests.get(f"{YOUTUBE_API_BASE}/search", params=params, timeout=10)
    resp.raise_for_status()
    items = resp.json().get("items", [])
    return [
        {
            "title": i["snippet"]["channelTitle"],
            "channel_id": i["snippet"]["channelId"],
            "description": i["snippet"]["description"],
            "source": "youtube_api",
        }
        for i in items
    ]


def get_channel_stats_api(channel_id: str) -> dict:
    """Holt Statistiken eines Kanals via YouTube Data API v3."""
    params = {
        "part": "statistics,snippet",
        "id": channel_id,
        "key": YOUTUBE_API_KEY,
    }
    resp = requests.get(f"{YOUTUBE_API_BASE}/channels", params=params, timeout=10)
    resp.raise_for_status()
    items = resp.json().get("items", [])
    if not items:
        return {}
    stats = items[0].get("statistics", {})
    snippet = items[0].get("snippet", {})
    return {
        "subscribers": stats.get("subscriberCount", "N/A"),
        "total_views": stats.get("viewCount", "N/A"),
        "video_count": stats.get("videoCount", "N/A"),
        "country": snippet.get("country", "N/A"),
        "description": snippet.get("description", ""),
    }


def search_top_videos_api(keyword: str, lang: str = "de", max_results: int = 5) -> list[dict]:
    """Sucht Top-Videos zu einem Keyword via YouTube Data API v3."""
    params = {
        "part": "snippet,statistics",
        "q": keyword,
        "type": "video",
        "order": "viewCount",
        "maxResults": max_results,
        "relevanceLanguage": lang,
        "key": YOUTUBE_API_KEY,
    }
    resp = requests.get(f"{YOUTUBE_API_BASE}/search", params=params, timeout=10)
    resp.raise_for_status()
    items = resp.json().get("items", [])
    return [
        {
            "title": i["snippet"]["title"],
            "channel": i["snippet"]["channelTitle"],
            "video_id": i["id"].get("videoId", ""),
            "description": i["snippet"]["description"][:200],
            "source": "youtube_api",
        }
        for i in items
    ]


def search_youtube_ddg(keyword: str, market: str = "DE", max_results: int = 8) -> list[dict]:
    """Fallback: Sucht YouTube-Inhalte via DuckDuckGo."""
    query = f"site:youtube.com {keyword} channel"
    if market == "US":
        query = f"site:youtube.com {keyword} channel english"

    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "description": r.get("body", "")[:300],
                "source": "duckduckgo",
            })
    return results


def research_competitors(client: dict) -> dict:
    """
    Hauptfunktion: Recherchiert Wettbewerber-Kanäle für DE und US-Markt.
    """
    print("  🔍 YouTube-Recherche läuft...")
    results = {"de": [], "us": []}

    use_api = bool(YOUTUBE_API_KEY)

    # Deutschsprachige Wettbewerber
    for keyword in client["keywords_de"][:3]:
        print(f"    → DE: '{keyword}'")
        try:
            if use_api:
                channels = search_youtube_channels_api(keyword, lang="de")
                results["de"].extend(channels)
                videos = search_top_videos_api(keyword, lang="de")
                results["de"].extend(videos)
            else:
                hits = search_youtube_ddg(keyword, market="DE")
                results["de"].extend(hits)
        except Exception as e:
            print(f"    ⚠️  Fehler bei '{keyword}': {e}")

    # Englischsprachige / US-Wettbewerber
    for keyword in client["keywords_en"][:3]:
        print(f"    → US: '{keyword}'")
        try:
            if use_api:
                channels = search_youtube_channels_api(keyword, lang="en")
                results["us"].extend(channels)
                videos = search_top_videos_api(keyword, lang="en")
                results["us"].extend(videos)
            else:
                hits = search_youtube_ddg(keyword, market="US")
                results["us"].extend(hits)
        except Exception as e:
            print(f"    ⚠️  Fehler bei '{keyword}': {e}")

    # Duplikate entfernen
    seen = set()
    for market in ["de", "us"]:
        unique = []
        for item in results[market]:
            key = item.get("title", "") + item.get("url", "") + item.get("channel_id", "")
            if key not in seen:
                seen.add(key)
                unique.append(item)
        results[market] = unique

    print(f"  ✅ YouTube: {len(results['de'])} DE-Ergebnisse, {len(results['us'])} US-Ergebnisse")
    return results
