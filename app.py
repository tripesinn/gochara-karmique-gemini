"""
app.py — Gochara Karmique
Application Flask — Multi-utilisateur
Toutes les données natal/transit viennent du profil envoyé par le frontend.
"""

import os
from datetime import datetime

import pytz
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    tz  = pytz.timezone("Europe/Paris")
    now = datetime.now(tz)
    return render_template(
        "index.html",
        today_iso=now.strftime("%Y-%m-%d"),
        now_hour=now.hour,
        now_minute=now.minute,
    )


@app.route("/geocode", methods=["POST"])
def geocode():
    """Proxy géocodage Nominatim (évite CORS + rate limiting côté serveur)."""
    import time
    import urllib.request
    import urllib.parse
    import json as _json

    data = request.get_json()
    city = (data.get("city") or "").strip()
    if not city:
        return jsonify({"error": "Ville vide"}), 400

    query = urllib.parse.urlencode({"q": city, "format": "json", "limit": 1})
    url   = f"https://nominatim.openstreetmap.org/search?{query}"
    req   = urllib.request.Request(url, headers={"User-Agent": "GocharaKarmique/1.0"})

    try:
        time.sleep(1)  # respect rate limit Nominatim
        with urllib.request.urlopen(req, timeout=10) as resp:
            results = _json.loads(resp.read().decode())
        if not results:
            return jsonify({"error": f"Ville introuvable : {city}"}), 404
        r = results[0]
        return jsonify({
            "lat":     float(r["lat"]),
            "lon":     float(r["lon"]),
            "display": r.get("display_name", city)[:80],
        })
    except Exception as exc:
        app.logger.error("Geocode error: %s", exc)
        return jsonify({"error": str(exc)}), 500


@app.route("/calculate", methods=["POST"])
def calculate():
    from astro_calc import calculate_transits
    from ai_interpret import get_synthesis, build_chart_context

    data = request.get_json()

    # ── Données natal depuis le profil utilisateur ──
    natal = {
        "name":   data.get("name", "Inconnu"),
        "year":   int(data.get("birth_year",   2000)),
        "month":  int(data.get("birth_month",  1)),
        "day":    int(data.get("birth_day",    1)),
        "hour":   int(data.get("birth_hour",   12)),
        "minute": int(data.get("birth_minute", 0)),
        "lat":    float(data.get("natal_lat",  48.85)),
        "lon":    float(data.get("natal_lon",  2.35)),
        "tz":     "Europe/Paris",   # TODO: déduire du natal_lon si nécessaire
        "city":   data.get("birthCity", ""),
    }

    # ── Données transit depuis le formulaire ──
    transit_loc = {
        "city": data.get("transit_city", ""),
        "lat":  float(data.get("transit_lat", natal["lat"])),
        "lon":  float(data.get("transit_lon", natal["lon"])),
        "tz":   "Europe/Paris",
    }

    date_str = data.get("date", "")
    hour     = int(data.get("hour",   12))
    minute   = int(data.get("minute", 0))

    if not date_str:
        return jsonify({"error": "Date manquante"}), 400

    try:
        year, month, day = map(int, date_str.split("-"))
        result = calculate_transits(natal, transit_loc, year, month, day, hour, minute)
        result["name"]          = natal["name"]
        result["synthesis"]     = get_synthesis(result)
        result["chart_context"] = build_chart_context(result)
        return jsonify(result)
    except Exception as exc:
        app.logger.error("Erreur calcul : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


@app.route("/chat", methods=["POST"])
def chat():
    from ai_interpret import chat_response

    data          = request.get_json()
    message       = data.get("message", "").strip()
    history       = data.get("history", [])
    chart_context = data.get("chart_context", "")
    name          = data.get("name", "l'utilisateur")

    if not message:
        return jsonify({"error": "Message vide"}), 400

    try:
        response = chat_response(message, history, chart_context, name)
        return jsonify({"response": response})
    except Exception as exc:
        app.logger.error("Erreur chat : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


# ── Lancement ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
