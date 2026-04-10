"""
transit_alerts.py — Détection et envoi des alertes de transit important
Gochara Karmique

Logique :
  - Planètes lentes en transit : Jupiter, Saturne, Uranus, Neptune, Pluton, Chiron, Nœuds
  - Points natals cibles : Ketu (Nœud Sud), Chiron, Rahu (Nœud Nord), Soleil, Lune
  - Aspect : Conjonction (orbe < 3°)
  - Alerte si un transit entre ou sort de l'orbe entre J-1 et aujourd'hui
"""

import os
from datetime import date, timedelta

import requests as req

from astro_calc import get_julian_day, _calc_positions, ORB

# Planètes lentes en transit — celles qui déclenchent des alertes
SLOW_PLANETS = {
    "Jupiter ♃", "Saturne ♄", "Uranus ♅", "Neptune ♆", "Pluton ♇",
    "Chiron ⚷", "Nœud Nord ☊", "Nœud Sud ☋",
}

# Points natals surveillés
TARGET_NATAL = {
    "Nœud Sud ☋",   # Ketu — ROM — Mémoire karmique
    "Chiron ⚷",     # RAM — Porte Invisible
    "Nœud Nord ☊",  # Rahu — Stage
    "Soleil ☀",
    "Lune ☽",
}

# Labels lisibles pour l'email
PLANET_LABELS = {
    "Jupiter ♃":   "Jupiter",
    "Saturne ♄":   "Saturne",
    "Uranus ♅":    "Uranus",
    "Neptune ♆":   "Neptune",
    "Pluton ♇":    "Pluton",
    "Chiron ⚷":    "Chiron",
    "Nœud Nord ☊": "Rahu (Nœud Nord)",
    "Nœud Sud ☋":  "Ketu (Nœud Sud)",
}

NATAL_LABELS = {
    "Nœud Sud ☋":  "ton Ketu natal (Mémoire karmique)",
    "Chiron ⚷":    "ton Chiron natal (Porte Invisible)",
    "Nœud Nord ☊": "ton Rahu natal (Stage / Dharma)",
    "Soleil ☀":    "ton Soleil natal",
    "Lune ☽":      "ta Lune natale",
}


def _add_south_node(positions: dict) -> dict:
    """Ajoute Nœud Sud si Nœud Nord présent."""
    nn = positions.get("Nœud Nord ☊")
    if nn:
        ks_lon = (nn["lon"] + 180) % 360
        positions["Nœud Sud ☋"] = {
            "lon": ks_lon,
            "speed": 0,
            "retrograde": False,
        }
    return positions


def _active_conjunctions(natal_pos: dict, transit_pos: dict) -> set[tuple]:
    """Retourne l'ensemble des paires (transit_planet, natal_point) en conjonction < 3°."""
    active = set()
    for t_name, t_data in transit_pos.items():
        if t_data is None or t_name not in SLOW_PLANETS:
            continue
        t_lon = t_data["lon"]
        for n_name, n_data in natal_pos.items():
            if n_data is None or n_name not in TARGET_NATAL:
                continue
            n_lon = n_data["lon"]
            diff = abs(t_lon - n_lon) % 360
            if diff > 180:
                diff = 360 - diff
            if diff <= ORB:
                active.add((t_name, n_name))
    return active


def _positions_for_day(profile: dict, target_date: date) -> tuple[dict, dict]:
    """Calcule positions natales et de transit (à midi) pour une date donnée."""
    natal_jd = get_julian_day(
        profile["year"], profile["month"], profile["day"],
        profile["hour"], profile["minute"], profile["tz"],
    )
    transit_jd = get_julian_day(
        target_date.year, target_date.month, target_date.day,
        12, 0, profile.get("transit_tz") or profile["tz"],
    )
    nat_lat = float(profile["lat"])
    nat_lon = float(profile["lon"])
    tr_lat  = float(profile.get("transit_lat") or profile["lat"])
    tr_lon  = float(profile.get("transit_lon") or profile["lon"])

    natal_pos   = _add_south_node(_calc_positions(natal_jd,   nat_lat, nat_lon))
    transit_pos = _add_south_node(_calc_positions(transit_jd, tr_lat,  tr_lon))
    return natal_pos, transit_pos


def detect_transit_events(profile: dict) -> list[dict]:
    """
    Compare les conjonctions importantes d'hier et d'aujourd'hui.
    Retourne les transits qui commencent ou se terminent aujourd'hui.
    """
    today     = date.today()
    yesterday = today - timedelta(days=1)

    natal_pos, today_transit    = _positions_for_day(profile, today)
    _,         yesterday_transit = _positions_for_day(profile, yesterday)

    today_active     = _active_conjunctions(natal_pos, today_transit)
    yesterday_active = _active_conjunctions(natal_pos, yesterday_transit)

    events = []
    for pair in today_active - yesterday_active:
        events.append({"type": "debut", "transit": pair[0], "natal": pair[1]})
    for pair in yesterday_active - today_active:
        events.append({"type": "fin", "transit": pair[0], "natal": pair[1]})

    return events


def _build_alert_html(profile: dict, events: list[dict]) -> str:
    name      = profile.get("name") or profile.get("pseudo", "")
    today_str = date.today().strftime("%d/%m/%Y")

    rows = ""
    for e in events:
        is_debut = e["type"] == "debut"
        icon     = "▶" if is_debut else "■"
        label    = "Début de transit" if is_debut else "Fin de transit"
        color    = "#6ab56a" if is_debut else "#e57373"
        t_label  = PLANET_LABELS.get(e["transit"], e["transit"])
        n_label  = NATAL_LABELS.get(e["natal"],   e["natal"])
        rows += f"""
        <tr>
          <td style="padding:10px 8px;color:{color};font-size:20px;vertical-align:top;">{icon}</td>
          <td style="padding:10px 8px;vertical-align:top;">
            <div style="color:#d4a017;font-weight:bold;font-size:14px;">{t_label}</div>
            <div style="color:#c090e0;font-size:13px;margin-top:2px;">⊕ {n_label}</div>
            <div style="color:#9090b0;font-size:11px;margin-top:2px;">{label}</div>
          </td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8">
<style>
  body {{ font-family: Georgia, serif; background: #0a0a1a; color: #e8e0d0; margin: 0; padding: 20px; }}
  .container {{ max-width: 620px; margin: 0 auto; background: #0f0f2a;
                border: 1px solid #4b0082; border-radius: 4px; padding: 30px; }}
  h1 {{ color: #d4a017; font-size: 19px; border-bottom: 1px solid #4b0082; padding-bottom: 10px; margin-top: 0; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
  tr {{ border-bottom: 1px solid #1a1a30; }}
  .footer {{ margin-top: 28px; padding-top: 14px; border-top: 1px solid #4b0082;
             font-size: 11px; color: #606080; text-align: center; }}
  .support a {{ background: #d4a017; color: #000; text-decoration: none;
                padding: 7px 18px; border-radius: 4px; font-weight: bold; font-size: 12px; }}
</style>
</head>
<body>
<div class="container">
  <h1>✦ Alerte Transit Karmique</h1>
  <p style="color:#9090b0;font-size:12px;margin-top:0;">{name} · {today_str} · Astrologie Védique Sidérale</p>
  <table>{rows}</table>
  <div class="support" style="margin-top:20px;text-align:center;">
    <a href="https://buymeacoffee.com/jerome6">☕ Soutenir le projet</a>
  </div>
  <div class="footer">
    Karmic Gochara · DK Ayanamsa · Chandra Lagna · True Nodes · Orbe &lt; 3°<br>
    Pour gérer tes alertes, connecte-toi sur l'application.
  </div>
</div>
</body>
</html>"""


def send_alert_email(profile: dict, events: list[dict]) -> bool:
    resend_key = os.environ.get("RESEND_API_KEY", "")
    if not resend_key:
        return False
    email = (profile.get("email") or "").strip()
    if not email:
        return False

    html      = _build_alert_html(profile, events)
    today_str = date.today().strftime("%d/%m/%Y")

    try:
        r = req.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {resend_key}",
                "Content-Type":  "application/json",
            },
            json={
                "from":     "Gochara Karmique <karmic.gochara@astro.jeromemalige.fr>",
                "reply_to": "astro@jeromemalige.fr",
                "to":       [email],
                "subject":  f"✦ Transit Alert — {today_str}",
                "html":     html,
            },
            timeout=10,
        )
        return r.status_code in (200, 201)
    except Exception:
        return False


def run_daily_alerts() -> dict:
    """Point d'entrée principal — appelé par la route /cron/daily."""
    from profiles import get_all_profiles

    profiles = get_all_profiles()
    results  = {"total": len(profiles), "processed": 0, "alerted": 0, "errors": 0}

    for profile in profiles:
        if not profile.get("alerts_enabled"):
            continue
        if not profile.get("email"):
            continue
        results["processed"] += 1
        try:
            events = detect_transit_events(profile)
            if events:
                sent = send_alert_email(profile, events)
                if sent:
                    results["alerted"] += 1
        except Exception:
            results["errors"] += 1

    return results
