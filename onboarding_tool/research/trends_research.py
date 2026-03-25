"""
Google Trends Recherche – Suchvolumen, Saisonalität, steigende Begriffe.
"""

import time
from pytrends.request import TrendReq


def research_trends(client: dict) -> dict:
    """
    Analysiert Google Trends für die Keywords des Kunden.
    Gibt Interesse-Werte, saisonale Muster und verwandte Suchanfragen zurück.
    """
    print("  📈 Google Trends-Recherche läuft...")
    results = {
        "interest_over_time": {},
        "related_queries": {},
        "rising_queries": {},
        "top_queries": {},
    }

    try:
        pytrends = TrendReq(hl="de-DE", tz=60)

        keywords_de = client["keywords_de"][:5]

        # Interesse über Zeit (letzte 12 Monate, Deutschland)
        pytrends.build_payload(keywords_de, cat=0, timeframe="today 12-m", geo="DE")
        time.sleep(1)

        interest_df = pytrends.interest_over_time()
        if not interest_df.empty:
            for kw in keywords_de:
                if kw in interest_df.columns:
                    avg = round(interest_df[kw].mean(), 1)
                    peak = int(interest_df[kw].max())
                    results["interest_over_time"][kw] = {
                        "average_interest": avg,
                        "peak_interest": peak,
                        "trend": "steigend" if interest_df[kw].iloc[-1] > interest_df[kw].iloc[0] else "fallend",
                    }

        time.sleep(2)

        # Verwandte Suchanfragen
        related = pytrends.related_queries()
        for kw in keywords_de:
            if kw in related:
                top = related[kw].get("top")
                rising = related[kw].get("rising")
                if top is not None and not top.empty:
                    results["top_queries"][kw] = top.head(10).to_dict("records")
                if rising is not None and not rising.empty:
                    results["rising_queries"][kw] = rising.head(10).to_dict("records")

        time.sleep(1)

        # Englische Keywords für US-Vergleich
        keywords_en = client["keywords_en"][:3]
        pytrends.build_payload(keywords_en, cat=0, timeframe="today 12-m", geo="US")
        time.sleep(1)

        interest_en = pytrends.interest_over_time()
        if not interest_en.empty:
            for kw in keywords_en:
                if kw in interest_en.columns:
                    avg = round(interest_en[kw].mean(), 1)
                    results["interest_over_time"][f"{kw} (US)"] = {
                        "average_interest": avg,
                        "peak_interest": int(interest_en[kw].max()),
                        "trend": "steigend" if interest_en[kw].iloc[-1] > interest_en[kw].iloc[0] else "fallend",
                    }

        print(f"  ✅ Trends: {len(results['interest_over_time'])} Keywords analysiert")

    except Exception as e:
        print(f"  ⚠️  Trends-Fehler: {e}")

    return results
