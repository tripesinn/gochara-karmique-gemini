"""
profiles.py — Gestion des profils utilisateurs via Google Sheets
Gochara Karmique — Login par email

Colonnes :
  A: email | B: prenom | C: birth_date | D: birth_hour | E: birth_minute
  F: birth_city | G: birth_lat | H: birth_lon | I: birth_tz
  J: transit_city | K: transit_lat | L: transit_lon | M: transit_tz
  N: created_at
"""

import os
import json
import logging
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)

COL = {
    "email":        0,
    "prenom":       1,
    "birth_date":   2,
    "birth_hour":   3,
    "birth_minute": 4,
    "birth_city":   5,
    "birth_lat":    6,
    "birth_lon":    7,
    "birth_tz":     8,
    "transit_city": 9,
    "transit_lat":  10,
    "transit_lon":  11,
    "transit_tz":   12,
    "created_at":   13,
}

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

_sheet = None


def _get_sheet():
    global _sheet
    if _sheet is not None:
        try:
            _sheet.get("A1")
            return _sheet
        except Exception:
            _sheet = None

    creds_raw = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if not creds_raw:
        raise EnvironmentError("GOOGLE_CREDENTIALS_JSON manquant.")

    creds_data = json.loads(creds_raw)
    creds = Credentials.from_service_account_info(creds_data, scopes=SCOPES)
    gc = gspread.authorize(creds)

    sheet_id = os.environ.get("SHEET_ID")
    workbook = gc.open_by_key(sheet_id) if sheet_id else gc.open("gochara-profiles")
    _sheet = workbook.sheet1

    if not _sheet.cell(1, 1).value:
        _sheet.append_row(list(COL.keys()))

    logger.info("Google Sheets connecté — %s", _sheet.title)
    return _sheet


def get_profile_by_email(email: str) -> dict | None:
    email = email.strip().lower()
    sheet = _get_sheet()
    rows = sheet.get_all_values()
    for row in rows[1:]:
        if row and row[0].strip().lower() == email:
            return _row_to_dict(row)
    return None


def create_profile(
    email, prenom, birth_date, birth_hour, birth_minute,
    birth_city, birth_lat, birth_lon, birth_tz,
    transit_city, transit_lat, transit_lon,
    transit_tz="Europe/Paris",
) -> dict:
    email = email.strip().lower()
    if get_profile_by_email(email):
        raise ValueError(f"Un compte existe deja pour '{email}'.")

    sheet = _get_sheet()
    row = [
        email, prenom.strip(),
        birth_date, birth_hour, birth_minute,
        birth_city, birth_lat, birth_lon, birth_tz,
        transit_city, transit_lat, transit_lon, transit_tz,
        datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    ]
    sheet.append_row(row, value_input_option="USER_ENTERED")
    logger.info("Profil cree : %s (%s)", email, prenom)
    return _row_to_dict(row)


def _row_to_dict(row: list) -> dict:
    def g(idx, default=""):
        try:
            return row[idx] if idx < len(row) and row[idx] != "" else default
        except IndexError:
            return default

    return {
        "email":        g(COL["email"]),
        "prenom":       g(COL["prenom"]),
        "birth_date":   g(COL["birth_date"], "1990-01-01"),
        "birth_hour":   int(g(COL["birth_hour"],   12)),
        "birth_minute": int(g(COL["birth_minute"],  0)),
        "birth_city":   g(COL["birth_city"]),
        "birth_lat":    float(g(COL["birth_lat"],  48.8566)),
        "birth_lon":    float(g(COL["birth_lon"],   2.3522)),
        "birth_tz":     g(COL["birth_tz"], "Europe/Paris"),
        "transit_city": g(COL["transit_city"]),
        "transit_lat":  float(g(COL["transit_lat"], 48.8566)),
        "transit_lon":  float(g(COL["transit_lon"],  2.3522)),
        "transit_tz":   g(COL["transit_tz"], "Europe/Paris"),
        "created_at":   g(COL["created_at"]),
    }