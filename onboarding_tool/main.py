"""
Onboarding Marktanalyse Tool
============================
Automatisierte Markt-, Zielgruppen- & SEO-Analyse für YouTube-Kanäle.

Verwendung:
    python main.py
    python main.py --client "Mein Kunde GmbH" --niche "Finanzberatung" --output report.pdf
"""

import sys
import os
import json
import argparse
from datetime import datetime

# Sicherstellen, dass das Tool-Verzeichnis im Pfad ist
sys.path.insert(0, os.path.dirname(__file__))

from config import DEFAULT_CLIENT
from research.youtube_research import research_competitors
from research.trends_research import research_trends
from research.web_research import research_web
from analysis.claude_analyzer import analyze
from report.pdf_report import generate_pdf


def run(client: dict, output_path: str = None, skip_research: bool = False, research_file: str = None):
    """
    Führt die komplette Onboarding-Analyse durch.

    Args:
        client: Kunden-Konfiguration (dict)
        output_path: Pfad für den PDF-Report
        skip_research: Falls True, wird gecachte Recherche aus research_file geladen
        research_file: Pfad zu gecachter Recherche (JSON)
    """
    print(f"\n{'='*60}")
    print(f"  ONBOARDING ANALYSE")
    print(f"  Kunde: {client['name']}")
    print(f"  Nische: {client['niche']}")
    print(f"{'='*60}\n")

    # ── Phase 1: Recherche ────────────────────────────────────────────────
    if skip_research and research_file and os.path.exists(research_file):
        print("📂 Lade gecachte Recherche-Daten...")
        with open(research_file, "r", encoding="utf-8") as f:
            research = json.load(f)
        print("✅ Recherche geladen\n")
    else:
        print("🔍 Phase 1: Recherche läuft...\n")
        research = {}

        research["youtube"] = research_competitors(client)
        research["trends"] = research_trends(client)
        research["web"] = research_web(client)

        # Recherche cachen
        cache_file = f"research_cache_{client['name'].replace(' ', '_')}.json"
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(research, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Recherche gecacht: {cache_file}")

    # ── Phase 2: Analyse via Claude API ───────────────────────────────────
    print("\n🤖 Phase 2: KI-Analyse...")
    analysis = analyze(client, research)

    # Analyse speichern
    analysis_file = f"analysis_{client['name'].replace(' ', '_')}.json"
    with open(analysis_file, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    print(f"💾 Analyse gespeichert: {analysis_file}")

    # ── Phase 3: PDF Report ───────────────────────────────────────────────
    print("\n📄 Phase 3: PDF-Report wird erstellt...")
    if output_path is None:
        safe_name = client["name"].replace(" ", "_").replace("/", "-")
        date_str = datetime.now().strftime("%Y%m%d")
        output_path = f"report_{safe_name}_{date_str}.pdf"

    pdf_path = generate_pdf(client, analysis, output_path)

    print(f"\n{'='*60}")
    print(f"  ✅ FERTIG!")
    print(f"  📄 Report: {pdf_path}")
    print(f"{'='*60}\n")

    return pdf_path


def main():
    parser = argparse.ArgumentParser(description="Onboarding Marktanalyse Tool")
    parser.add_argument("--client", type=str, help="Kundenname", default=None)
    parser.add_argument("--niche", type=str, help="Nische/Branche", default=None)
    parser.add_argument("--service", type=str, help="Dienstleistungsbeschreibung", default=None)
    parser.add_argument("--output", type=str, help="PDF-Ausgabepfad", default=None)
    parser.add_argument(
        "--use-cache", type=str, metavar="CACHE_FILE",
        help="Gecachte Recherche laden statt neu recherchieren",
        default=None
    )
    args = parser.parse_args()

    client = dict(DEFAULT_CLIENT)
    if args.client:
        client["name"] = args.client
    if args.niche:
        client["niche"] = args.niche
    if args.service:
        client["service"] = args.service

    skip = bool(args.use_cache)
    run(client, output_path=args.output, skip_research=skip, research_file=args.use_cache)


if __name__ == "__main__":
    main()
