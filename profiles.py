"""
profiles.py — Gestion des profils utilisateurs via Google Sheets
Gochara Karmique — Architecture multi-utilisateurs
"""

import os
import json
from datetime import date
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Colonnes du Google Sheet (ordre fixe)
COLS = [
    "pseudo",               # A
    "email",                # B
    "name",                 # C
    "year",                 # D
    "month",                # E
    "day",                  # F
    "hour",                 # G
    "minute",               # H
    "lat",                  # I
    "lon",                  # J
    "tz",                   # K
    "city",                 # L
    "transit_city",         # M
    "transit_lat",          # N
    "transit_lon",          # O
    "transit_tz",           # P
    "syntheses_count",      # Q
    "syntheses_reset_date", # R
    "alerts_enabled",       # S
    # ── Natal calculé — stocké à l'inscription ──────────────────────────────
    "chandra_lagna_sign",   # T
    "chandra_lagna_deg",    # U
    "ketu_sign",            # V
    "ketu_house",           # W
    "ketu_nakshatra",       # X
    "rahu_sign",            # Y
    "rahu_house",           # Z
    "rahu_nakshatra",       # AA
    "chiron_sign",          # AB
    "chiron_house",         # AC
    "chiron_nakshatra",     # AD
    "lilith_sign",          # AE
    "lilith_house",         # AF
    "saturn_sign",          # AG
    "saturn_house",         # AH
    "jupiter_sign",         # AI
    "jupiter_house",        # AJ
    "porte_visible_sign",   # AK
    "porte_visible_house",  # AL
    "porte_visible_deg",    # AM
    "porte_invisible_sign", # AN
    "porte_invisible_house",# AO
]

# Champs nataux — sous-ensemble de COLS pour update ciblé
NATAL_COLS = COLS[19:]  # de T à AO

SYNTHESIS_QUOTA = 3  # max synthèses par mois (plan free)

_sheet = None


def _current_month_str() -> str:
    """Retourne le 1er du mois courant au format YYYY-MM-01."""
    today = date.today()
    return f"{today.year}-{today.month:02d}-01"


def _get_sheet():
    global _sheet
    if _sheet is not None:
        return _sheet

    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    sheet_id   = os.environ.get("SHEET_ID")

    if not creds_json or not sheet_id:
        raise RuntimeError("GOOGLE_CREDENTIALS_JSON ou SHEET_ID manquant dans les variables d'environnement.")

    creds_data = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_data, scopes=SCOPES)
    gc = gspread.authorize(creds)
    spreadsheet = gc.open_by_key(sheet_id)

    try:
        ws = spreadsheet.sheet1
    except Exception:
        ws = spreadsheet.add_worksheet(title="profiles", rows=1000, cols=20)

    # Créer l'en-tête si la feuille est vide
    if not ws.row_values(1):
        ws.append_row(COLS)

    _sheet = ws
    return _sheet


def _row_to_profile(row: list) -> dict:
    """Convertit une ligne Sheets en dict profil."""
    def _safe(i, cast=str, default=""):
        try:
            v = row[i].strip() if isinstance(row[i], str) else str(row[i])
            return cast(v) if v else default
        except (IndexError, ValueError):
            return default

    return {
        "pseudo":               _safe(0),
        "email":                _safe(1),
        "name":                 _safe(2),
        "year":                 _safe(3, int, 1990),
        "month":                _safe(4, int, 1),
        "day":                  _safe(5, int, 1),
        "hour":                 _safe(6, int, 12),
        "minute":               _safe(7, int, 0),
        "lat":                  _safe(8, float, 48.8566),
        "lon":                  _safe(9, float, 2.3522),
        "tz":                   _safe(10) or "Europe/Paris",
        "city":                 _safe(11) or "Paris, France",
        "transit_city":         _safe(12) or "Paris, France",
        "transit_lat":          _safe(13, float, 48.8566),
        "transit_lon":          _safe(14, float, 2.3522),
        "transit_tz":           _safe(15) or "Europe/Paris",
        # Quota — fallback 0 / mois courant pour anciens profils
        "syntheses_count":      _safe(16, int, 0),
        "syntheses_reset_date": _safe(17) or _current_month_str(),
        "alerts_enabled":       _safe(18, int, 0),
        # ── Natal calculé ────────────────────────────────────────────────────
        "chandra_lagna_sign":   _safe(19),
        "chandra_lagna_deg":    _safe(20),
        "ketu_sign":            _safe(21),
        "ketu_house":           _safe(22),
        "ketu_nakshatra":       _safe(23),
        "rahu_sign":            _safe(24),
        "rahu_house":           _safe(25),
        "rahu_nakshatra":       _safe(26),
        "chiron_sign":          _safe(27),
        "chiron_house":         _safe(28),
        "chiron_nakshatra":     _safe(29),
        "lilith_sign":          _safe(30),
        "lilith_house":         _safe(31),
        "saturn_sign":          _safe(32),
        "saturn_house":         _safe(33),
        "jupiter_sign":         _safe(34),
        "jupiter_house":        _safe(35),
        "porte_visible_sign":   _safe(36),
        "porte_visible_house":  _safe(37),
        "porte_visible_deg":    _safe(38),
        "porte_invisible_sign": _safe(39),
        "porte_invisible_house":_safe(40),
    }


def get_profile_by_email(email: str) -> dict | None:
    ws = _get_sheet()
    records = ws.get_all_values()
    email_lower = email.strip().lower()
    for row in records[1:]:
        if len(row) > 1 and row[1].strip().lower() == email_lower:
            return _row_to_profile(row)
    return None


def get_profile_by_pseudo(pseudo: str) -> dict | None:
    ws = _get_sheet()
    records = ws.get_all_values()
    pseudo_lower = pseudo.strip().lower()
    header = records[0] if records else []

    for row in records[1:]:
        if row and row[0].strip().lower() == pseudo_lower:
            return _row_to_profile(row)
    return None


def create_profile(data: dict) -> dict:
    """Crée un nouveau profil et retourne le profil créé."""
    ws = _get_sheet()
    row = [
        data.get("pseudo", ""),
        data.get("email", ""),
        data.get("name", ""),
        str(data.get("year", "")),
        str(data.get("month", "")),
        str(data.get("day", "")),
        str(data.get("hour", "")),
        str(data.get("minute", "")),
        str(data.get("lat", "")),
        str(data.get("lon", "")),
        data.get("tz", "Europe/Paris"),
        data.get("city", ""),
        data.get("transit_city", ""),
        str(data.get("transit_lat", "")),
        str(data.get("transit_lon", "")),
        data.get("transit_tz", "Europe/Paris"),
        "0",                      # syntheses_count
        _current_month_str(),     # syntheses_reset_date
        "0",                      # alerts_enabled
        # Natal — vide à l'inscription, rempli par save_natal_to_sheet()
        "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
    ]
    ws.append_row(row)
    return _row_to_profile(row)


def update_profile(email: str, data: dict) -> dict | None:
    """Met à jour le profil d'un utilisateur existant."""
    ws = _get_sheet()
    records = ws.get_all_values()
    email_lower = email.strip().lower()

    for i, row in enumerate(records[1:], start=2):
        if len(row) > 1 and row[1].strip().lower() == email_lower:
            # Préserve les colonnes quota existantes
            existing_count      = row[16] if len(row) > 16 else "0"
            existing_reset_date = row[17] if len(row) > 17 else _current_month_str()

            existing_alerts = row[18] if len(row) > 18 else "0"

            new_row = [
                data.get("pseudo",       row[0]  if len(row) > 0  else ""),
                row[1],  # email immuable
                data.get("name",         row[2]  if len(row) > 2  else ""),
                str(data.get("year",     row[3]  if len(row) > 3  else "")),
                str(data.get("month",    row[4]  if len(row) > 4  else "")),
                str(data.get("day",      row[5]  if len(row) > 5  else "")),
                str(data.get("hour",     row[6]  if len(row) > 6  else "")),
                str(data.get("minute",   row[7]  if len(row) > 7  else "")),
                str(data.get("lat",      row[8]  if len(row) > 8  else "")),
                str(data.get("lon",      row[9]  if len(row) > 9  else "")),
                data.get("tz",           row[10] if len(row) > 10 else "Europe/Paris"),
                data.get("city",         row[11] if len(row) > 11 else ""),
                data.get("transit_city", row[12] if len(row) > 12 else ""),
                str(data.get("transit_lat", row[13] if len(row) > 13 else "")),
                str(data.get("transit_lon", row[14] if len(row) > 14 else "")),
                data.get("transit_tz",   row[15] if len(row) > 15 else "Europe/Paris"),
                existing_count,       # préservé
                existing_reset_date,  # préservé
                existing_alerts,      # préservé
            ]
            ws.update(f"A{i}:S{i}", [new_row])
            return _row_to_profile(new_row)
    return None


def check_and_increment_synthesis(pseudo: str) -> dict:
    """
    Vérifie le quota mensuel de synthèses pour un utilisateur.
    - Si quota dépassé  → retourne {"allowed": False, "remaining": 0}
    - Sinon             → incrémente le compteur et retourne {"allowed": True, "remaining": N}
    Gère le reset automatique en début de mois.
    """
    ws = _get_sheet()
    records = ws.get_all_values()
    pseudo_lower = pseudo.strip().lower()
    current_month = _current_month_str()

    for i, row in enumerate(records[1:], start=2):
        if not row or row[0].strip().lower() != pseudo_lower:
            continue

        # Lecture quota avec fallback anciens profils
        try:
            count = int(row[16]) if len(row) > 16 and row[16] else 0
        except ValueError:
            count = 0

        reset_date = row[17] if len(row) > 17 and row[17] else ""

        # Reset si nouveau mois
        if reset_date != current_month:
            count = 0
            reset_date = current_month

        if count >= SYNTHESIS_QUOTA:
            return {"allowed": False, "remaining": 0}

        # Incrémenter
        new_count = count + 1
        ws.update(f"Q{i}:R{i}", [[str(new_count), current_month]])

        return {"allowed": True, "remaining": SYNTHESIS_QUOTA - new_count}

    # Pseudo introuvable
    return {"allowed": False, "remaining": 0}


def get_all_profiles() -> list[dict]:
    """Retourne tous les profils utilisateurs (sans la ligne d'en-tête)."""
    ws = _get_sheet()
    records = ws.get_all_values()
    return [_row_to_profile(row) for row in records[1:] if row and row[0].strip()]


def set_alerts(pseudo: str, enabled: bool) -> bool:
    """Active ou désactive les alertes transit pour un utilisateur. Retourne True si trouvé."""
    ws = _get_sheet()
    records = ws.get_all_values()
    pseudo_lower = pseudo.strip().lower()
    for i, row in enumerate(records[1:], start=2):
        if row and row[0].strip().lower() == pseudo_lower:
            ws.update(f"S{i}", [["1" if enabled else "0"]])
            return True
    return False



def save_natal_to_sheet(pseudo: str, natal_data: dict) -> bool:
    """
    Stocke les positions natales calculées dans Google Sheets.
    Appelé une fois à l'inscription (après calculate_transits).
    Aussi utilisable pour mettre à jour un profil existant.

    natal_data = dict issu de _enrich_profile_with_natal() :
        chandra_lagna_sign, chandra_lagna_deg,
        ketu_sign, ketu_house, ketu_nakshatra,
        rahu_sign, rahu_house, rahu_nakshatra,
        chiron_sign, chiron_house, chiron_nakshatra,
        lilith_sign, lilith_house,
        saturn_sign, saturn_house,
        jupiter_sign, jupiter_house,
        porte_visible_sign, porte_visible_house, porte_visible_deg,
        porte_invisible_sign, porte_invisible_house

    Retourne True si le profil a été trouvé et mis à jour.
    """
    ws = _get_sheet()
    records = ws.get_all_values()
    pseudo_lower = pseudo.strip().lower()

    for i, row in enumerate(records[1:], start=2):
        if not row or row[0].strip().lower() != pseudo_lower:
            continue

        natal_row = [
            natal_data.get("chandra_lagna_sign",   ""),
            natal_data.get("chandra_lagna_deg",    ""),
            natal_data.get("ketu_sign",            ""),
            str(natal_data.get("ketu_house",       "")),
            natal_data.get("ketu_nakshatra",       ""),
            natal_data.get("rahu_sign",            ""),
            str(natal_data.get("rahu_house",       "")),
            natal_data.get("rahu_nakshatra",       ""),
            natal_data.get("chiron_sign",          ""),
            str(natal_data.get("chiron_house",     "")),
            natal_data.get("chiron_nakshatra",     ""),
            natal_data.get("lilith_sign",          ""),
            str(natal_data.get("lilith_house",     "")),
            natal_data.get("saturn_sign",          ""),
            str(natal_data.get("saturn_house",     "")),
            natal_data.get("jupiter_sign",         ""),
            str(natal_data.get("jupiter_house",    "")),
            natal_data.get("porte_visible_sign",   ""),
            str(natal_data.get("porte_visible_house", "")),
            natal_data.get("porte_visible_deg",    ""),
            natal_data.get("porte_invisible_sign", ""),
            str(natal_data.get("porte_invisible_house", "")),
        ]
        # Colonnes T→AO = indices 20→41 → plage Sheets T{i}:AO{i}
        ws.update(f"T{i}:AO{i}", [natal_row])
        return True

    return False


def pseudo_exists(pseudo: str) -> bool:
    ws = _get_sheet()
    records = ws.get_all_values()
    pseudo_lower = pseudo.strip().lower()
    for row in records[1:]:
        if row and row[0].strip().lower() == pseudo_lower:
            return True
    return False
