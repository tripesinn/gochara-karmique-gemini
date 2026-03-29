"""
app.py — Gochara Karmique Multi-Utilisateurs
Géocodage avec rate-limit protection + cache + fallback
"""

import os
import time
import json
import hashlib
from datetime import datetime
from functools import lru_cache

import pytz
import requests
from flask import Flask, jsonify, render_template, request, session
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "gochara-karmique-2025")
app.config["JSON_AS_ASCII"] = False

# ── Cache simple en mémoire pour géocodage ────────────────────────────────────
_GEO_CACHE = {}
_LAST_NOMINATIM_CALL = 0.0
NOMINATIM_DELAY = 1.1  # secondes entre appels (respecte 1 req/s)


def geocode_city(city_name: str) -> dict | None:
    """
    Géocode une ville avec :
    1. Cache mémoire
    2. Rate-limiting respectueux (1 req/s)
    3. Fallback sur photon.komoot.de si Nominatim échoue
    """
    key = city_name.lower().strip()
    if key in _GEO_CACHE:
        return _GEO_CACHE[key]

    global _LAST_NOMINATIM_CALL

    # ── Respecter le rate limit ──
    elapsed = time.time() - _LAST_NOMINATIM_CALL
    if elapsed < NOMINATIM_DELAY:
        time.sleep(NOMINATIM_DELAY - elapsed)

    # ── Tentative Nominatim ──
    try:
        _LAST_NOMINATIM_CALL = time.time()
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": city_name, "format": "json", "limit": 1},
            headers={"User-Agent": "GochareKarmique/1.0 (astrologie-vedique)"},
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data:
                result = {
                    "lat": float(data[0]["lat"]),
                    "lon": float(data[0]["lon"]),
                    "display": data[0].get("display_name", city_name),
                }
                _GEO_CACHE[key] = result
                return result
    except Exception:
        pass

    # ── Fallback Photon (Komoot) ──
    try:
        resp2 = requests.get(
            "https://photon.komoot.io/api/",
            params={"q": city_name, "limit": 1},
            timeout=5,
        )
        if resp2.status_code == 200:
            features = resp2.json().get("features", [])
            if features:
                coords = features[0]["geometry"]["coordinates"]
                props = features[0]["properties"]
                city_display = f"{props.get('name', city_name)}, {props.get('country', '')}"
                result = {
                    "lat": float(coords[1]),
                    "lon": float(coords[0]),
                    "display": city_display,
                }
                _GEO_CACHE[key] = result
                return result
    except Exception:
        pass

    return None


# ── Route géocodage ───────────────────────────────────────────────────────────
@app.route("/geocode", methods=["POST"])
def geocode():
    data = request.get_json()
    city = data.get("city", "").strip()
    if not city:
        return jsonify({"error": "Ville manquante"}), 400

    result = geocode_city(city)
    if result:
        return jsonify(result)
    return jsonify({"error": f"Ville introuvable : {city}"}), 404


# ── Route principale ──────────────────────────────────────────────────────────
@app.route("/")
def index():
    tz = pytz.timezone("Europe/Paris")
    now = datetime.now(tz)
    return render_template(
        "index.html",
        today_iso=now.strftime("%Y-%m-%d"),
        now_hour=now.hour,
        now_minute=now.minute,
    )


# ── Route calcul ──────────────────────────────────────────────────────────────
@app.route("/calculate", methods=["POST"])
def calculate():
    from astro_calc import calculate_transits
    from ai_interpret import get_synthesis, build_chart_context

    data = request.get_json()

    # Données natal dynamiques
    natal = {
        "name":   data.get("name", "Inconnu"),
        "year":   int(data.get("birth_year")),
        "month":  int(data.get("birth_month")),
        "day":    int(data.get("birth_day")),
        "hour":   int(data.get("birth_hour", 12)),
        "minute": int(data.get("birth_minute", 0)),
        "lat":    float(data.get("natal_lat")),
        "lon":    float(data.get("natal_lon")),
        "tz":     "Europe/Paris",
        "city":   data.get("natal_city", ""),
    }

    transit_loc = {
        "city": data.get("transit_city", ""),
        "lat":  float(data.get("transit_lat")),
        "lon":  float(data.get("transit_lon")),
        "tz":   "Europe/Paris",
    }

    date_str = data.get("date", "")
    hour     = int(data.get("hour", 12))
    minute   = int(data.get("minute", 0))

    try:
        year, month, day = map(int, date_str.split("-"))
        result = calculate_transits(natal, transit_loc, year, month, day, hour, minute)
        result["synthesis"]     = get_synthesis(result)
        result["chart_context"] = build_chart_context(result)
        result["natal_name"]    = natal["name"]
        return jsonify(result)
    except Exception as exc:
        app.logger.error("Erreur calcul : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


# ── Route chat ────────────────────────────────────────────────────────────────
@app.route("/chat", methods=["POST"])
def chat():
    from ai_interpret import chat_response

    data          = request.get_json()
    message       = data.get("message", "").strip()
    history       = data.get("history", [])
    chart_context = data.get("chart_context", "")

    if not message:
        return jsonify({"error": "Message vide"}), 400

    try:
        response = chat_response(message, history, chart_context)
        return jsonify({"response": response})
    except Exception as exc:
        app.logger.error("Erreur chat : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
