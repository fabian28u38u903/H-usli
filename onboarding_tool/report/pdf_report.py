"""
PDF-Report Generator via ReportLab.
Erstellt einen professionellen Onboarding-Analyse-Report.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY


# ── Farben ──────────────────────────────────────────────────────────────────
BRAND_DARK = colors.HexColor("#1A1A2E")
BRAND_PRIMARY = colors.HexColor("#16213E")
BRAND_ACCENT = colors.HexColor("#E94560")
BRAND_LIGHT = colors.HexColor("#F5F5F5")
BRAND_GRAY = colors.HexColor("#7F8C8D")
WHITE = colors.white


def _build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        "CoverTitle",
        fontName="Helvetica-Bold",
        fontSize=28,
        textColor=WHITE,
        spaceAfter=10,
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        "CoverSubtitle",
        fontName="Helvetica",
        fontSize=14,
        textColor=colors.HexColor("#BDC3C7"),
        spaceAfter=6,
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        "SectionTitle",
        fontName="Helvetica-Bold",
        fontSize=16,
        textColor=BRAND_DARK,
        spaceBefore=20,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        "SubSectionTitle",
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=BRAND_PRIMARY,
        spaceBefore=12,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        "BodyText2",
        fontName="Helvetica",
        fontSize=10,
        textColor=colors.HexColor("#2C3E50"),
        spaceAfter=4,
        leading=15,
        alignment=TA_JUSTIFY,
    ))
    styles.add(ParagraphStyle(
        "BulletItem",
        fontName="Helvetica",
        fontSize=10,
        textColor=colors.HexColor("#2C3E50"),
        leftIndent=15,
        spaceAfter=3,
        leading=14,
    ))
    styles.add(ParagraphStyle(
        "TagBadge",
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=BRAND_ACCENT,
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        "FooterText",
        fontName="Helvetica",
        fontSize=8,
        textColor=BRAND_GRAY,
        alignment=TA_CENTER,
    ))
    return styles


def _cover_page(elements, client, styles):
    """Deckblatt."""
    # Hintergrund-Farbblock simulieren mit Tabelle
    cover_data = [[""]]
    cover_table = Table(cover_data, colWidths=[17 * cm], rowHeights=[4 * cm])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BRAND_DARK),
        ("TOPPADDING", (0, 0), (-1, -1), 30),
    ]))
    elements.append(cover_table)
    elements.append(Spacer(1, 0.5 * cm))

    elements.append(Paragraph("ONBOARDING", styles["CoverSubtitle"]))
    elements.append(Paragraph("Marktanalyse", styles["CoverTitle"]))
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(HRFlowable(width="100%", thickness=2, color=BRAND_ACCENT))
    elements.append(Spacer(1, 0.5 * cm))

    elements.append(Paragraph(client["name"], ParagraphStyle(
        "ClientName", fontName="Helvetica-Bold", fontSize=22,
        textColor=BRAND_PRIMARY, spaceAfter=6
    )))
    elements.append(Paragraph(client["niche"], ParagraphStyle(
        "Niche", fontName="Helvetica", fontSize=13,
        textColor=BRAND_GRAY, spaceAfter=4
    )))
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(Paragraph(
        f"Erstellt am {datetime.now().strftime('%d. %B %Y')}",
        styles["FooterText"]
    ))
    elements.append(PageBreak())


def _section_header(elements, title, styles):
    elements.append(HRFlowable(width="100%", thickness=1, color=BRAND_ACCENT))
    elements.append(Paragraph(title, styles["SectionTitle"]))


def _bullet_list(elements, items, styles):
    for item in items:
        elements.append(Paragraph(f"▸  {item}", styles["BulletItem"]))


def _keyword_table(elements, keywords, styles):
    """Rendert Keywords als farbige Tabelle."""
    if not keywords:
        return
    data = [["Keyword", "Intent", "Priorität"]]
    for kw in keywords:
        if isinstance(kw, dict):
            intent_color = {
                "transactional": "#E74C3C",
                "commercial": "#E67E22",
                "informational": "#27AE60",
                "navigational": "#2980B9",
            }.get(kw.get("intent", "").lower(), "#7F8C8D")
            data.append([
                kw.get("keyword", ""),
                kw.get("intent", ""),
                kw.get("priority", ""),
            ])
        else:
            data.append([str(kw), "-", "-"])

    t = Table(data, colWidths=[8 * cm, 5 * cm, 4 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BRAND_LIGHT, WHITE]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.4 * cm))


def _video_ideas_table(elements, videos, styles):
    """Rendert Video-Ideen als Tabelle."""
    if not videos:
        return
    data = [["Titel", "Format", "Hook"]]
    for v in videos:
        if isinstance(v, dict):
            data.append([
                v.get("title", "")[:50],
                v.get("format", "")[:20],
                v.get("hook", "")[:60],
            ])
    if len(data) == 1:
        return
    t = Table(data, colWidths=[6 * cm, 3.5 * cm, 7.5 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BRAND_LIGHT, WHITE]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("WORDWRAP", (0, 0), (-1, -1), True),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.4 * cm))


def generate_pdf(client: dict, analysis: dict, output_path: str = None) -> str:
    """
    Generiert den vollständigen PDF-Report.
    Gibt den Pfad zur gespeicherten PDF zurück.
    """
    if output_path is None:
        safe_name = client["name"].replace(" ", "_").replace("/", "-")
        date_str = datetime.now().strftime("%Y%m%d")
        output_path = f"report_{safe_name}_{date_str}.pdf"

    print(f"  📄 PDF wird generiert: {output_path}")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    styles = _build_styles()
    elements = []

    # ── Deckblatt ──────────────────────────────────────────────────────────
    _cover_page(elements, client, styles)

    # ── Executive Summary ──────────────────────────────────────────────────
    if analysis.get("executive_summary"):
        _section_header(elements, "Executive Summary", styles)
        elements.append(Paragraph(analysis["executive_summary"], styles["BodyText2"]))
        elements.append(Spacer(1, 0.5 * cm))

    # ── 1. Demografisches Profil ───────────────────────────────────────────
    demo = analysis.get("demographics", {})
    if demo:
        _section_header(elements, "1. Demografisches Profil", styles)
        info_data = [
            ["Primäre Zielgruppe", demo.get("primary_audience", "-")],
            ["Alter", demo.get("age_range", "-")],
            ["Geschlecht", demo.get("gender", "-")],
            ["Beruf", demo.get("profession", "-")],
            ["Einkommen", demo.get("income", "-")],
            ["Bildung", demo.get("education", "-")],
        ]
        t = Table(info_data, colWidths=[5 * cm, 12 * cm])
        t.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [BRAND_LIGHT, WHITE]),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#E0E0E0")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.3 * cm))
        if demo.get("key_characteristics"):
            elements.append(Paragraph("Hauptmerkmale:", styles["SubSectionTitle"]))
            _bullet_list(elements, demo["key_characteristics"], styles)
        elements.append(Spacer(1, 0.5 * cm))

    # ── 2. Psychografisches Profil ─────────────────────────────────────────
    psycho = analysis.get("psychographics", {})
    if psycho:
        _section_header(elements, "2. Psychografisches Profil", styles)

        elements.append(Paragraph("Werte:", styles["SubSectionTitle"]))
        _bullet_list(elements, psycho.get("values", []), styles)

        elements.append(Paragraph("Ängste & Sorgen:", styles["SubSectionTitle"]))
        _bullet_list(elements, psycho.get("fears", []), styles)

        elements.append(Paragraph("Wünsche & Ziele:", styles["SubSectionTitle"]))
        _bullet_list(elements, psycho.get("desires", []), styles)

        if psycho.get("self_image"):
            elements.append(Paragraph("Selbstbild:", styles["SubSectionTitle"]))
            elements.append(Paragraph(psycho["self_image"], styles["BodyText2"]))

        elements.append(Spacer(1, 0.5 * cm))

    # ── 3. Sprache & Tonalität ─────────────────────────────────────────────
    lang = analysis.get("language_tonality", {})
    if lang:
        _section_header(elements, "3. Sprache & Tonalität", styles)

        info_data = [
            ["Ansprache", lang.get("du_or_sie", "-")],
            ["Tonalität", lang.get("preferred_tone", "-")],
            ["Stil", lang.get("emotional_vs_rational", "-")],
        ]
        t = Table(info_data, colWidths=[5 * cm, 12 * cm])
        t.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [BRAND_LIGHT, WHITE]),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#E0E0E0")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.3 * cm))

        if lang.get("own_words"):
            elements.append(Paragraph("Eigene Worte der Zielgruppe:", styles["SubSectionTitle"]))
            _bullet_list(elements, lang["own_words"], styles)

        if lang.get("power_phrases"):
            elements.append(Paragraph("Power-Phrases (wirken bei dieser Zielgruppe):", styles["SubSectionTitle"]))
            _bullet_list(elements, lang["power_phrases"], styles)

        if lang.get("taboo_words"):
            elements.append(Paragraph("Taboo-Worte (vermeiden):", styles["SubSectionTitle"]))
            _bullet_list(elements, lang["taboo_words"], styles)

        elements.append(Spacer(1, 0.5 * cm))

    # ── 4. Kaufverhalten & Trigger ─────────────────────────────────────────
    purchase = analysis.get("purchase_behavior", {})
    if purchase:
        _section_header(elements, "4. Kaufverhalten & Kauftrigger", styles)

        if purchase.get("trigger_moments"):
            elements.append(Paragraph("Trigger-Momente (wann entsteht Kaufwunsch):", styles["SubSectionTitle"]))
            _bullet_list(elements, purchase["trigger_moments"], styles)

        if purchase.get("buying_signals"):
            elements.append(Paragraph("Kaufsignale erkennen:", styles["SubSectionTitle"]))
            _bullet_list(elements, purchase["buying_signals"], styles)

        if purchase.get("main_objections"):
            elements.append(Paragraph("Häufige Einwände (Content-Ideen!):", styles["SubSectionTitle"]))
            _bullet_list(elements, purchase["main_objections"], styles)

        if purchase.get("trust_factors"):
            elements.append(Paragraph("Vertrauensfaktoren:", styles["SubSectionTitle"]))
            _bullet_list(elements, purchase["trust_factors"], styles)

        info_data = []
        if purchase.get("decision_duration"):
            info_data.append(["Entscheidungsdauer", purchase["decision_duration"]])
        if purchase.get("seasonal_patterns"):
            info_data.append(["Saisonalität", purchase["seasonal_patterns"]])
        if info_data:
            t = Table(info_data, colWidths=[5 * cm, 12 * cm])
            t.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [BRAND_LIGHT, WHITE]),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#E0E0E0")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]))
            elements.append(Spacer(1, 0.2 * cm))
            elements.append(t)

        elements.append(Spacer(1, 0.5 * cm))

    # ── 5. SEO-Analyse ─────────────────────────────────────────────────────
    seo = analysis.get("seo_analysis", {})
    if seo:
        _section_header(elements, "5. SEO-Analyse", styles)

        if seo.get("top_keywords"):
            elements.append(Paragraph("Top-Keywords nach Intent:", styles["SubSectionTitle"]))
            _keyword_table(elements, seo["top_keywords"], styles)

        if seo.get("purchase_intent_keywords"):
            elements.append(Paragraph("Kaufnahe Keywords (hohe Conversion-Chance):", styles["SubSectionTitle"]))
            _bullet_list(elements, seo["purchase_intent_keywords"], styles)

        if seo.get("rising_keywords"):
            elements.append(Paragraph("Steigende Keywords (Frühzeitig besetzen):", styles["SubSectionTitle"]))
            _bullet_list(elements, seo["rising_keywords"], styles)

        if seo.get("content_gaps"):
            elements.append(Paragraph("Content-Lücken im Markt:", styles["SubSectionTitle"]))
            _bullet_list(elements, seo["content_gaps"], styles)

        if seo.get("seo_recommendations"):
            elements.append(Paragraph("SEO-Empfehlungen:", styles["SubSectionTitle"]))
            _bullet_list(elements, seo["seo_recommendations"], styles)

        elements.append(Spacer(1, 0.5 * cm))

    # ── 6. Wettbewerber-Analyse ────────────────────────────────────────────
    comp = analysis.get("competitor_analysis", {})
    if comp:
        _section_header(elements, "6. Wettbewerber-Analyse", styles)
        elements.append(PageBreak())

        # DE Markt
        de = comp.get("de_market", {})
        if de:
            elements.append(Paragraph("Deutschsprachiger Markt", styles["SubSectionTitle"]))
            if de.get("top_channels"):
                ch_data = [["Kanal", "Stärken", "Schwächen"]]
                for ch in de["top_channels"]:
                    ch_data.append([
                        ch.get("name", "")[:30],
                        ch.get("strength", "")[:50],
                        ch.get("weakness", "")[:50],
                    ])
                t = Table(ch_data, colWidths=[5 * cm, 6 * cm, 6 * cm])
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), BRAND_PRIMARY),
                    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BRAND_LIGHT, WHITE]),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("WORDWRAP", (0, 0), (-1, -1), True),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 0.3 * cm))

            if de.get("market_gaps"):
                elements.append(Paragraph("Marktlücken (Chancen):", styles["SubSectionTitle"]))
                _bullet_list(elements, de["market_gaps"], styles)

            if de.get("dominant_formats"):
                elements.append(Paragraph("Dominante Formate:", styles["SubSectionTitle"]))
                _bullet_list(elements, de["dominant_formats"], styles)

        # US/International Markt
        us = comp.get("us_market", {})
        if us:
            elements.append(Spacer(1, 0.3 * cm))
            elements.append(Paragraph("US/Internationaler Markt – Übertragbare Konzepte", styles["SubSectionTitle"]))
            if us.get("top_channels"):
                for ch in us["top_channels"]:
                    elements.append(Paragraph(
                        f"▸  <b>{ch.get('name', '')}</b> – {ch.get('angle', '')} | Stärke: {ch.get('strength', '')}",
                        styles["BulletItem"]
                    ))

            if us.get("transferable_concepts"):
                elements.append(Paragraph("Konzepte für den deutschen Markt adaptieren:", styles["SubSectionTitle"]))
                _bullet_list(elements, us["transferable_concepts"], styles)

            if us.get("successful_hooks"):
                elements.append(Paragraph("Erfolgreiche Hook-Formeln:", styles["SubSectionTitle"]))
                _bullet_list(elements, us["successful_hooks"], styles)

        elements.append(Spacer(1, 0.5 * cm))

    # ── 7. Content-Strategie ───────────────────────────────────────────────
    content = analysis.get("content_strategy", {})
    if content:
        _section_header(elements, "7. Content-Strategie", styles)

        if content.get("unique_positioning"):
            elements.append(Paragraph("Unique Positioning:", styles["SubSectionTitle"]))
            elements.append(Paragraph(content["unique_positioning"], styles["BodyText2"]))

        if content.get("channel_angle"):
            elements.append(Paragraph("Channel Angle:", styles["SubSectionTitle"]))
            elements.append(Paragraph(content["channel_angle"], styles["BodyText2"]))

        channel_info = []
        if content.get("posting_frequency"):
            channel_info.append(["Posting-Frequenz", content["posting_frequency"]])
        if content.get("ideal_video_length"):
            channel_info.append(["Optimale Video-Länge", content["ideal_video_length"]])
        if content.get("thumbnail_style"):
            channel_info.append(["Thumbnail-Stil", content["thumbnail_style"]])
        if content.get("cta_recommendation"):
            channel_info.append(["CTA-Empfehlung", content["cta_recommendation"]])
        if channel_info:
            t = Table(channel_info, colWidths=[5 * cm, 12 * cm])
            t.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [BRAND_LIGHT, WHITE]),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#E0E0E0")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]))
            elements.append(Spacer(1, 0.2 * cm))
            elements.append(t)
            elements.append(Spacer(1, 0.4 * cm))

        if content.get("awareness_content"):
            elements.append(Paragraph("Awareness-Content (Reichweite aufbauen):", styles["SubSectionTitle"]))
            _video_ideas_table(elements, content["awareness_content"], styles)

        if content.get("trust_content"):
            elements.append(Paragraph("Trust-Content (Vertrauen aufbauen):", styles["SubSectionTitle"]))
            _video_ideas_table(elements, content["trust_content"], styles)

        if content.get("conversion_content"):
            elements.append(Paragraph("Conversion-Content (Kaufimpuls auslösen):", styles["SubSectionTitle"]))
            _video_ideas_table(elements, content["conversion_content"], styles)

    # ── Footer ─────────────────────────────────────────────────────────────
    elements.append(Spacer(1, 1 * cm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=BRAND_GRAY))
    elements.append(Spacer(1, 0.2 * cm))
    elements.append(Paragraph(
        f"Vertraulich · {client['name']} · Erstellt am {datetime.now().strftime('%d.%m.%Y')}",
        styles["FooterText"]
    ))

    doc.build(elements)
    print(f"  ✅ PDF gespeichert: {output_path}")
    return output_path
