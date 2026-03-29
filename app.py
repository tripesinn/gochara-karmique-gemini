"""
app.py — Gochara Karmique · @siderealAstro13
Application Flask — Astrologie védique karmique sidérale
"""

import os
from datetime import datetime

import pytz
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

# ── Données fixes de Jérôme ───────────────────────────────────────────────────
NATAL = {
    "name":  "Jérôme",
    "year":  1974,
    "month": 10,
    "day":   31,
    "hour":  8,
    "minute": 0,
    "lat":   48.7053,
    "lon":   2.3936,
    "tz":    "Europe/Paris",
    "city":  "Athis-Mons, France",
}

TRANSIT_LOC = {
    "city": "Rochechouart, France",
    "lat":  45.8186,
    "lon":  0.8191,
    "tz":   "Europe/Paris",
}

# ── Pseudos autorisés (liste blanche simple) ──────────────────────────────────
ALLOWED_PSEUDOS = {"jero", "jerome", "jérôme", "siderealastro13", "admin"}


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    tz = pytz.timezone("Europe/Paris")
    now = datetime.now(tz)
    return render_template(
        "index.html",
        natal=NATAL,
        transit_city=TRANSIT_LOC["city"],
        today_iso=now.strftime("%Y-%m-%d"),
        now_hour=now.hour,
        now_minute=now.minute,
    )


@app.route("/login", methods=["POST"])
def login():
    """
    Authentification légère par pseudo.
    Retourne JSON {ok: true, pseudo: "..."} ou {ok: false, error: "..."}.
    """
    data = request.get_json(silent=True) or {}
    pseudo = str(data.get("pseudo", "")).strip().lower()

    if not pseudo:
        return jsonify({"ok": False, "error": "Pseudo vide."}), 400

    if len(pseudo) < 2 or len(pseudo) > 32:
        return jsonify({"ok": False, "error": "Pseudo invalide (2–32 caractères)."}), 400

    # Accepter tout pseudo (profil créé automatiquement) ou restreindre :
    # if pseudo not in ALLOWED_PSEUDOS:
    #     return jsonify({"ok": False, "error": "Accès non autorisé."}), 403

    return jsonify({"ok": True, "pseudo": pseudo})


@app.route("/calculate", methods=["POST"])
def calculate():
    from astro_calc import calculate_transits
    from ai_interpret import get_synthesis, build_chart_context

    data = request.get_json()
    date_str = data.get("date", "")
    hour = int(data.get("hour", 12))
    minute = int(data.get("minute", 0))

    try:
        year, month, day = map(int, date_str.split("-"))
        result = calculate_transits(NATAL, TRANSIT_LOC, year, month, day, hour, minute)
        result["synthesis"] = get_synthesis(result)
        result["chart_context"] = build_chart_context(result)
        return jsonify(result)
    except Exception as exc:
        app.logger.error("Erreur calcul : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


@app.route("/chat", methods=["POST"])
def chat():
    from ai_interpret import chat_response

    data = request.get_json()
    message = data.get("message", "").strip()
    history = data.get("history", [])
    chart_context = data.get("chart_context", "")

    if not message:
        return jsonify({"error": "Message vide"}), 400

    try:
        response = chat_response(message, history, chart_context)
        return jsonify({"response": response})
    except Exception as exc:
        app.logger.error("Erreur chat : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


# ── Lancement ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
