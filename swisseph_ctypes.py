"""
swisseph_ctypes.py — Drop-in replacement for pyswisseph via ctypes.

Expose la même API que le module pyswisseph, en wrappant directement
la DLL C officielle (Swiss Ephemeris ≥ 2.10) — aucune compilation requise.

Installation :
  Windows : télécharger swedll64.dll depuis https://www.astro.com/swisseph/swephdll.htm
            et le placer dans le même dossier que ce fichier (ou dans PATH).
  Linux   : sudo apt install libswe-dev
  macOS   : brew install swiss-ephemeris

Utilisation dans astro_calc.py :
  Remplacer « import swisseph as swe »
  par       « import swisseph_ctypes as swe »
"""

import ctypes
import ctypes.util
import os
import sys
from pathlib import Path

# ── Constantes (identiques à pyswisseph) ─────────────────────────────────────

SUN       = 0
MOON      = 1
MERCURY   = 2
VENUS     = 3
MARS      = 4
JUPITER   = 5
SATURN    = 6
URANUS    = 7
NEPTUNE   = 8
PLUTO     = 9
TRUE_NODE = 11
CHIRON    = 15
OSCU_APOG = 17  # Lilith vraie (Osculating Apogee)

FLG_SPEED    = 256
FLG_SIDEREAL = 65536

SIDM_USER = 255   # Ayanamsa personnalisé

_SE_GREG_CAL = 1  # Calendrier grégorien

# ── Chargement de la bibliothèque ─────────────────────────────────────────────

def _load_library() -> ctypes.CDLL:
    here = Path(__file__).parent

    if sys.platform == "win32":
        candidates = [
            here / "swedll64.dll",
            Path(os.environ.get("SWISSEPH_PATH", ".")) / "swedll64.dll",
        ]
        system_name = "swedll64"
    elif sys.platform == "darwin":
        candidates = [here / "libswe.dylib"]
        system_name = "swe"
    else:
        candidates = [here / "libswe.so.2", here / "libswe.so"]
        system_name = "swe"

    for path in candidates:
        if path.exists():
            return ctypes.CDLL(str(path))

    lib_path = ctypes.util.find_library(system_name)
    if lib_path:
        return ctypes.CDLL(lib_path)

    raise OSError(
        "Swiss Ephemeris C library introuvable.\n"
        "  Windows : placer swedll64.dll à côté de ce fichier\n"
        "            ou définir SWISSEPH_PATH=<dossier>\n"
        "            Téléchargement : https://www.astro.com/swisseph/swephdll.htm\n"
        "  Linux   : sudo apt install libswe-dev\n"
        "  macOS   : brew install swiss-ephemeris\n"
    )


_lib = _load_library()

# ── Signatures des fonctions C ────────────────────────────────────────────────

_lib.swe_julday.restype  = ctypes.c_double
_lib.swe_julday.argtypes = [
    ctypes.c_int, ctypes.c_int, ctypes.c_int,   # year, month, day
    ctypes.c_double,                              # hour (décimal)
    ctypes.c_int,                                 # gregflag
]

_lib.swe_set_sid_mode.restype  = None
_lib.swe_set_sid_mode.argtypes = [
    ctypes.c_int32,    # sid_mode
    ctypes.c_double,   # t0  (JD de référence pour SIDM_USER)
    ctypes.c_double,   # ayan_t0 (valeur ayanamsa à t0)
]

_lib.swe_calc_ut.restype  = ctypes.c_int32
_lib.swe_calc_ut.argtypes = [
    ctypes.c_double,                      # tjd_ut
    ctypes.c_int32,                       # ipl  (numéro de planète)
    ctypes.c_int32,                       # iflag
    ctypes.POINTER(ctypes.c_double),      # xx[6] — résultat
    ctypes.c_char_p,                      # serr[256] — message d'erreur
]

_lib.swe_houses_ex.restype  = ctypes.c_int
_lib.swe_houses_ex.argtypes = [
    ctypes.c_double,                      # tjd_ut
    ctypes.c_int32,                       # iflag (FLG_SIDEREAL etc.)
    ctypes.c_double,                      # geolat
    ctypes.c_double,                      # geolon
    ctypes.c_int,                         # hsys  ('P' = Placidus → ord(80))
    ctypes.POINTER(ctypes.c_double),      # cusps[13]
    ctypes.POINTER(ctypes.c_double),      # ascmc[10]
]

# swe_set_ephe_path — optionnel, pour pointer vers des fichiers .se1
_lib.swe_set_ephe_path.restype  = None
_lib.swe_set_ephe_path.argtypes = [ctypes.c_char_p]

# ── API publique (identique à pyswisseph) ─────────────────────────────────────

def julday(year: int, month: int, day: int, hour: float) -> float:
    """Calcule le Jour Julien (UTC)."""
    return _lib.swe_julday(year, month, day, hour, _SE_GREG_CAL)


def set_sid_mode(sid_mode: int, t0: float = 0.0, ayan_t0: float = 0.0) -> None:
    """Définit le mode sidéral (ayanamsa).
    Utiliser SIDM_USER pour un ayanamsa personnalisé (ex. Centre Galactique DK).
    """
    _lib.swe_set_sid_mode(sid_mode, t0, ayan_t0)


def calc_ut(tjd_ut: float, ipl: int, iflag: int):
    """Calcule la position d'une planète en Jour Julien UT.

    Retourne (xx, retflag) :
      xx[0] = longitude écliptique
      xx[1] = latitude
      xx[2] = distance (UA)
      xx[3] = vitesse en longitude (°/jour)
      xx[4] = vitesse en latitude
      xx[5] = vitesse en distance
    """
    xx   = (ctypes.c_double * 6)()
    serr = ctypes.create_string_buffer(256)
    ret  = _lib.swe_calc_ut(tjd_ut, ipl, iflag, xx, serr)
    if ret < 0:
        msg = serr.value.decode(errors="replace")
        raise RuntimeError(f"swe_calc_ut({ipl}) — {msg}")
    return list(xx), ret


def houses_ex(tjd_ut: float, geolat: float, geolon: float,
              hsys: bytes, iflag: int):
    """Calcule les maisons astrologiques.

    Retourne (cusps, ascmc) :
      cusps[1..12] = cuspides des 12 maisons
      ascmc[0]     = Ascendant
      ascmc[1]     = MC
      ascmc[2]     = ARMC
      ascmc[3]     = Vertex
    """
    cusps = (ctypes.c_double * 13)()
    ascmc = (ctypes.c_double * 10)()
    _lib.swe_houses_ex(
        tjd_ut, iflag, geolat, geolon,
        ord(hsys[0]),   # b"P"[0] → 80
        cusps, ascmc,
    )
    return list(cusps), list(ascmc)


def set_ephe_path(path: str) -> None:
    """Optionnel — pointer vers un dossier contenant des fichiers .se1."""
    _lib.swe_set_ephe_path(path.encode())
