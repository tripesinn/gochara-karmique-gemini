"""
app.py — Gochara Karmique
Application Flask — Astrologie védique karmique multi-utilisateurs
Login par email → Google Sheets (profiles.py)
"""

import os
from datetime import datetime

import pytz
from flask import (
    Flask, jsonify, render_template, request,
    redirect, url_for, session
)
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "gochara-secret-change-me")
app.config["JSON_AS_ASCII"] = False


# ── Helpers session ───────────────────────────────────────────────────────────
def _current_user() -> dict | None:
    """Retourne le profil stocké en session, ou None."""
    return session.get("user")


def _natal_from_user(user: dict) -> dict:
    """Construit le dict NATAL depuis le profil utilisateur."""
    date_parts = user["birth_date"].split("-")
    return {
        "name":   user["prenom"],
        "year":   int(date_parts[0]),
        "month":  int(date_parts[1]),
        "day":    int(date_parts[2]),
        "hour":   int(user["birth_hour"]),
        "minute": int(user["birth_minute"]),
        "lat":    float(user["birth_lat"]),
        "lon":    float(user["birth_lon"]),
        "tz":     user["birth_tz"],
        "city":   user["birth_city"],
    }


def _transit_from_user(user: dict) -> dict:
    return {
        "city": user["transit_city"],
        "lat":  float(user["transit_lat"]),
        "lon":  float(user["transit_lon"]),
        "tz":   user["transit_tz"],
    }


# ── Page d'accueil / login ────────────────────────────────────────────────────
@app.route("/")
def index():
    user = _current_user()
    if not user:
        return redirect(url_for("login"))

    tz = pytz.timezone("Europe/Paris")
    now = datetime.now(tz)
    natal = _natal_from_user(user)
    transit = _transit_from_user(user)

    return render_template(
        "index.html",
        user=user,
        natal=natal,
        transit_city=transit["city"],
        today_iso=now.strftime("%Y-%m-%d"),
        now_hour=now.hour,
        now_minute=now.minute,
    )


# ── Login ─────────────────────────────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    data = request.get_json() or request.form
    email = (data.get("email") or "").strip().lower()

    if not email:
        return jsonify({"error": "Email requis"}), 400

    try:
        from profiles import get_profile_by_email
        user = get_profile_by_email(email)
        if not user:
            return jsonify({"error": "Aucun compte trouvé pour cet email. Inscris-toi d'abord."}), 404

        session["user"] = user
        session.permanent = True
        return jsonify({"ok": True, "prenom": user["prenom"]})

    except Exception as exc:
        app.logger.error("Erreur login : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


# ── Inscription ───────────────────────────────────────────────────────────────
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Données manquantes"}), 400

    required = ["email", "prenom", "birth_date", "birth_hour", "birth_minute",
                "birth_city", "birth_lat", "birth_lon", "birth_tz",
                "transit_city", "transit_lat", "transit_lon"]
    missing = [f for f in required if not data.get(f) and data.get(f) != 0]
    if missing:
        return jsonify({"error": f"Champs manquants : {', '.join(missing)}"}), 400

    try:
        from profiles import create_profile, get_profile_by_email

        email = data["email"].strip().lower()
        if get_profile_by_email(email):
            return jsonify({"error": "Un compte existe déjà pour cet email."}), 409

        user = create_profile(
            email=email,
            prenom=data["prenom"],
            birth_date=data["birth_date"],
            birth_hour=int(data["birth_hour"]),
            birth_minute=int(data["birth_minute"]),
            birth_city=data["birth_city"],
            birth_lat=float(data["birth_lat"]),
            birth_lon=float(data["birth_lon"]),
            birth_tz=data.get("birth_tz", "Europe/Paris"),
            transit_city=data["transit_city"],
            transit_lat=float(data["transit_lat"]),
            transit_lon=float(data["transit_lon"]),
            transit_tz=data.get("transit_tz", "Europe/Paris"),
        )
        session["user"] = user
        session.permanent = True
        return jsonify({"ok": True, "prenom": user["prenom"]})

    except ValueError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as exc:
        app.logger.error("Erreur inscription : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


# ── Logout ────────────────────────────────────────────────────────────────────
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ── API profil courant ────────────────────────────────────────────────────────
@app.route("/me")
def me():
    user = _current_user()
    if not user:
        return jsonify({"error": "Non connecté"}), 401
    return jsonify(user)


# ── Calcul des transits ───────────────────────────────────────────────────────
@app.route("/calculate", methods=["POST"])
def calculate():
    user = _current_user()
    if not user:
        return jsonify({"error": "Non connecté"}), 401

    from astro_calc import calculate_transits
    from ai_interpret import get_synthesis, build_chart_context

    data = request.get_json()
    date_str = data.get("date", "")
    hour = int(data.get("hour", 12))
    minute = int(data.get("minute", 0))

    try:
        year, month, day = map(int, date_str.split("-"))
        natal = _natal_from_user(user)
        transit = _transit_from_user(user)

        result = calculate_transits(natal, transit, year, month, day, hour, minute)
        result["synthesis"] = get_synthesis(result)
        result["chart_context"] = build_chart_context(result)
        return jsonify(result)

    except Exception as exc:
        app.logger.error("Erreur calcul : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


# ── Chat karmique ─────────────────────────────────────────────────────────────
@app.route("/chat", methods=["POST"])
def chat():
    user = _current_user()
    if not user:
        return jsonify({"error": "Non connecté"}), 401

    from ai_interpret import chat_response

    data = request.get_json()
    message = data.get("message", "").strip()
    history = data.get("history", [])
    chart_context = data.get("chart_context", "")

    if not message:
        return jsonify({"error": "Message vide"}), 400

    try:
        response = chat_response(message, history, chart_context, prenom=user["prenom"])
        return jsonify({"response": response})
    except Exception as exc:
        app.logger.error("Erreur chat : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


# ── Géocodage Nominatim (pour l'inscription) ──────────────────────────────────
@app.route("/geocode")
def geocode():
    """Proxy Nominatim pour éviter les CORS côté client."""
    import urllib.request, urllib.parse, json as _json

    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({"error": "Ville manquante"}), 400

    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode({
        "q": city, "format": "json", "limit": 1, "addressdetails": 1
    })
    req = urllib.request.Request(url, headers={"User-Agent": "GocharaKarmique/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            results = _json.loads(resp.read())
        if not results:
            return jsonify({"error": "Ville non trouvée"}), 404
        r = results[0]
        # Timezone approx par pays (à améliorer si besoin)
        cc = r.get("address", {}).get("country_code", "fr").lower()
        tz_map = {"fr": "Europe/Paris", "be": "Europe/Brussels",
                  "ch": "Europe/Zurich", "ca": "America/Toronto",
                  "us": "America/New_York", "gb": "Europe/London"}
        return jsonify({
            "lat": float(r["lat"]),
            "lon": float(r["lon"]),
            "display": r["display_name"],
            "tz": tz_map.get(cc, "Europe/Paris"),
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# ── Lancement ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
