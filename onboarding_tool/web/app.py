"""
Flask Web-Interface für das Onboarding Analyse Tool.
Starten: python web/app.py
"""

import sys
import os
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from database import (
    create_customer, get_customer, list_customers, update_customer,
    delete_customer, create_analysis, update_analysis_status,
    get_latest_analysis, list_analyses
)
from email_sender import send_report

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "change-me-in-production")


def _run_analysis_bg(customer_id: int, analysis_id: int):
    """Führt die Analyse im Hintergrund aus."""
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    from main import run
    from database import get_customer

    update_analysis_status(analysis_id, "running")
    try:
        customer = get_customer(customer_id)
        pdf_path = run(customer)
        update_analysis_status(analysis_id, "done", report_path=pdf_path)

        # Automatisch E-Mail senden falls Adresse vorhanden
        if customer.get("contact_email"):
            send_report(customer, pdf_path)

    except Exception as e:
        update_analysis_status(analysis_id, "error", error=str(e))


# ── Routen ──────────────────────────────────────────────────────────────────

@app.route("/")
def dashboard():
    customers = list_customers()
    # Letzten Analyse-Status je Kunde anhängen
    for c in customers:
        c["latest_analysis"] = get_latest_analysis(c["id"])
    return render_template("dashboard.html", customers=customers)


@app.route("/customers/new", methods=["GET", "POST"])
def new_customer():
    if request.method == "POST":
        data = {
            "name": request.form["name"],
            "niche": request.form["niche"],
            "service": request.form["service"],
            "target_audience": request.form.get("target_audience", ""),
            "contact_email": request.form.get("contact_email", ""),
            "contact_name": request.form.get("contact_name", ""),
            "benefits": [b.strip() for b in request.form.get("benefits", "").splitlines() if b.strip()],
            "keywords_de": [k.strip() for k in request.form.get("keywords_de", "").splitlines() if k.strip()],
            "keywords_en": [k.strip() for k in request.form.get("keywords_en", "").splitlines() if k.strip()],
        }
        customer_id = create_customer(data)
        flash("Kunde erfolgreich angelegt.", "success")
        return redirect(url_for("customer_detail", customer_id=customer_id))
    return render_template("customer_form.html", customer=None)


@app.route("/customers/<int:customer_id>")
def customer_detail(customer_id):
    customer = get_customer(customer_id)
    if not customer:
        flash("Kunde nicht gefunden.", "error")
        return redirect(url_for("dashboard"))
    analyses = list_analyses(customer_id)
    return render_template("customer_detail.html", customer=customer, analyses=analyses)


@app.route("/customers/<int:customer_id>/edit", methods=["GET", "POST"])
def edit_customer(customer_id):
    customer = get_customer(customer_id)
    if not customer:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        data = {
            "name": request.form["name"],
            "niche": request.form["niche"],
            "service": request.form["service"],
            "target_audience": request.form.get("target_audience", ""),
            "contact_email": request.form.get("contact_email", ""),
            "contact_name": request.form.get("contact_name", ""),
            "benefits": [b.strip() for b in request.form.get("benefits", "").splitlines() if b.strip()],
            "keywords_de": [k.strip() for k in request.form.get("keywords_de", "").splitlines() if k.strip()],
            "keywords_en": [k.strip() for k in request.form.get("keywords_en", "").splitlines() if k.strip()],
        }
        update_customer(customer_id, data)
        flash("Kunde aktualisiert.", "success")
        return redirect(url_for("customer_detail", customer_id=customer_id))
    return render_template("customer_form.html", customer=customer)


@app.route("/customers/<int:customer_id>/delete", methods=["POST"])
def delete_customer_route(customer_id):
    delete_customer(customer_id)
    flash("Kunde gelöscht.", "success")
    return redirect(url_for("dashboard"))


@app.route("/customers/<int:customer_id>/analyze", methods=["POST"])
def start_analysis(customer_id):
    customer = get_customer(customer_id)
    if not customer:
        return jsonify({"error": "Kunde nicht gefunden"}), 404

    analysis_id = create_analysis(customer_id)
    thread = threading.Thread(
        target=_run_analysis_bg,
        args=(customer_id, analysis_id),
        daemon=True
    )
    thread.start()

    flash("Analyse gestartet! Sie läuft im Hintergrund.", "success")
    return redirect(url_for("customer_detail", customer_id=customer_id))


@app.route("/analysis/<int:analysis_id>/status")
def analysis_status(analysis_id):
    from database import get_conn
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM analyses WHERE id=?", (analysis_id,)
        ).fetchone()
    if not row:
        return jsonify({"error": "Nicht gefunden"}), 404
    return jsonify(dict(row))


@app.route("/analysis/<int:analysis_id>/download")
def download_report(analysis_id):
    from database import get_conn
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM analyses WHERE id=?", (analysis_id,)
        ).fetchone()
    if not row or not row["report_path"] or not os.path.exists(row["report_path"]):
        flash("Report nicht verfügbar.", "error")
        return redirect(url_for("dashboard"))
    return send_file(row["report_path"], as_attachment=True)


@app.route("/analysis/<int:analysis_id>/send-email", methods=["POST"])
def send_email_route(analysis_id):
    from database import get_conn
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM analyses WHERE id=?", (analysis_id,)
        ).fetchone()
    if not row:
        flash("Analyse nicht gefunden.", "error")
        return redirect(url_for("dashboard"))

    customer = get_customer(row["customer_id"])
    override_email = request.form.get("email") or None
    ok = send_report(customer, row["report_path"], recipient_email=override_email)

    if ok:
        flash("E-Mail erfolgreich gesendet.", "success")
    else:
        flash("E-Mail konnte nicht gesendet werden. SMTP-Daten prüfen.", "error")
    return redirect(url_for("customer_detail", customer_id=row["customer_id"]))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
