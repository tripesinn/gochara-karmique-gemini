package com.karmicgochara.app.astro;

/**
 * NakshatraCalc — Port Java de astro_calc.py (partie maths pures)
 * Calculs : nakshatra, D9, D10, D60, display, Porte Visible/Invisible.
 * Aucune dépendance externe.
 */
public final class NakshatraCalc {

    // ── Signes ───────────────────────────────────────────────────────────────
    public static final String[] SIGNS = {
        "Bélier", "Taureau", "Gémeaux", "Cancer",
        "Lion", "Vierge", "Balance", "Scorpion",
        "Sagittaire", "Capricorne", "Verseau", "Poissons"
    };

    public static final String[] SIGN_SYMBOLS = {
        "♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"
    };

    // ── Nakshatras (27 × 13°20′) ─────────────────────────────────────────────
    public static final String[] NAKSHATRAS = {
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
        "Ardra", "Punarvasu", "Pushya", "Ashlesha",
        "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
        "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
        "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
        "Dhanishtha", "Shatabhisha", "Purva Bhadrapada",
        "Uttara Bhadrapada", "Revati"
    };

    // Régents Vimshotari
    public static final String[] NAKSHATRA_LORDS = {
        "Ketu", "Vénus", "Soleil", "Lune", "Mars", "Rahu", "Jupiter", "Saturne", "Mercure",
        "Ketu", "Vénus", "Soleil", "Lune", "Mars", "Rahu", "Jupiter", "Saturne", "Mercure",
        "Ketu", "Vénus", "Soleil", "Lune", "Mars", "Rahu", "Jupiter", "Saturne", "Mercure"
    };

    // ── D9 — Navamsha ─────────────────────────────────────────────────────────
    private static final int[] D9_START = { 0, 9, 6, 3, 0, 9, 6, 3, 0, 9, 6, 3 };

    // ── D60 — Shashtyamsha seigneurs ──────────────────────────────────────────
    public static final String[] D60_LORDS = {
        "Ghora", "Rakshasa", "Deva", "Kubera",
        "Yaksha", "Kinnara", "Bhrashta", "Kulaghna",
        "Garuda", "Agni", "Maya", "Apampathi",
        "Marut", "Kaala", "Sarpa", "Amrita",
        "Indu", "Mridu", "Komala", "Heramba",
        "Brahma", "Vishnu", "Maheshwara", "Deva",
        "Ardra", "Kalinasa", "Kshiteesh", "Kamalakara",
        "Gulika", "Mrityu", "Kaala", "Davagni",
        "Ghora", "Yama", "Kantaka", "Suddha",
        "Amrita", "Poorna Chandra", "Vishhadagdha", "Kulanasha",
        "Vamshakshaya", "Utpata", "Kaala", "Saumya",
        "Komala", "Sheetala", "Karaladamshtra", "Chandramukhi",
        "Praveena", "Kaala Pavaka", "Dandayudha", "Nirmala",
        "Saumya", "Krura", "Atisheetala", "Amrita",
        "Payodhi", "Brahma", "Vishnu", "Maheshwara"
    };

    private NakshatraCalc() {}

    // ── lonToNakshatra ────────────────────────────────────────────────────────
    public static NakshatraResult lonToNakshatra(double lon) {
        lon = lon % 360;
        double nakSize  = 360.0 / 27.0;   // 13.3333°
        double padaSize = nakSize / 4.0;   // 3.3333°
        int nakIdx  = (int)(lon / nakSize);
        int padaIdx = (int)((lon % nakSize) / padaSize) + 1;
        double degInNak = lon - (nakIdx * nakSize);
        return new NakshatraResult(
            NAKSHATRAS[nakIdx],
            padaIdx,
            NAKSHATRA_LORDS[nakIdx],
            Math.round(degInNak * 100.0) / 100.0
        );
    }

    // ── lonToD9 ───────────────────────────────────────────────────────────────
    public static DivisionalResult lonToD9(double lon) {
        lon = lon % 360;
        int signIdx = (int)(lon / 30);
        double pos  = lon % 30;
        int navNum  = (int)(pos / (30.0 / 9));   // 0-8
        int d9Sign  = (D9_START[signIdx] + navNum) % 12;
        return new DivisionalResult(SIGNS[d9Sign], SIGN_SYMBOLS[d9Sign], navNum + 1, null);
    }

    // ── lonToD10 ──────────────────────────────────────────────────────────────
    public static DivisionalResult lonToD10(double lon) {
        lon = lon % 360;
        int signIdx  = (int)(lon / 30);
        double pos   = lon % 30;
        int dashaNum = (int)(pos / 3.0);   // 0-9
        int start    = (signIdx % 2 == 0) ? signIdx : (signIdx + 8) % 12;
        int d10Sign  = (start + dashaNum) % 12;
        return new DivisionalResult(SIGNS[d10Sign], SIGN_SYMBOLS[d10Sign], dashaNum + 1, null);
    }

    // ── lonToD60 ──────────────────────────────────────────────────────────────
    public static DivisionalResult lonToD60(double lon) {
        lon = lon % 360;
        int signIdx   = (int)(lon / 30);
        double pos    = lon % 30;
        int shashNum  = (int)(pos / 0.5);   // 0-59
        int start     = (signIdx % 2 == 0) ? 0 : 9;
        int d60Sign   = (start + shashNum) % 12;
        return new DivisionalResult(SIGNS[d60Sign], SIGN_SYMBOLS[d60Sign], shashNum + 1, D60_LORDS[shashNum]);
    }

    // ── lonToDisplay ──────────────────────────────────────────────────────────
    public static String lonToDisplay(double lon) {
        lon = lon % 360;
        int idx     = (int)(lon / 30);
        int deg     = (int)(lon % 30);
        int minutes = (int)(((lon % 30) % 1) * 60);
        return SIGN_SYMBOLS[idx] + " " + SIGNS[idx] + " " + deg + "°" + String.format("%02d", minutes) + "′";
    }

    // ── calcPortes ────────────────────────────────────────────────────────────
    /** PV = mi-point du petit arc Saturne→Uranus. PI = PV + 180°. */
    public static PortesResult calcPortes(double saturnLon, double uranusLon) {
        double diff = (uranusLon - saturnLon) % 360;
        if (diff < 0) diff += 360;
        double midpoint;
        if (diff <= 180) {
            midpoint = (saturnLon + diff / 2.0) % 360;
        } else {
            double diffInv = 360 - diff;
            midpoint = (saturnLon - diffInv / 2.0) % 360;
        }
        double pv = ((midpoint % 360) + 360) % 360;
        double pi = (pv + 180.0) % 360;

        NakshatraResult nakPv = lonToNakshatra(pv);
        NakshatraResult nakPi = lonToNakshatra(pi);

        return new PortesResult(
            new PlanetPosition(pv, lonToDisplay(pv), nakPv.nakshatra, nakPv.pada, nakPv.lord, nakPv.degInNak,
                lonToD9(pv), lonToD10(pv), lonToD60(pv), 0, false),
            new PlanetPosition(pi, lonToDisplay(pi), nakPi.nakshatra, nakPi.pada, nakPi.lord, nakPi.degInNak,
                lonToD9(pi), lonToD10(pi), lonToD60(pi), 0, false)
        );
    }

    // ── Value objects ─────────────────────────────────────────────────────────

    public static class NakshatraResult {
        public final String nakshatra;
        public final int    pada;
        public final String lord;
        public final double degInNak;
        NakshatraResult(String nakshatra, int pada, String lord, double degInNak) {
            this.nakshatra = nakshatra; this.pada = pada;
            this.lord = lord; this.degInNak = degInNak;
        }
    }

    public static class DivisionalResult {
        public final String sign;
        public final String symbol;
        public final int    part;
        public final String lord;  // null sauf D60
        DivisionalResult(String sign, String symbol, int part, String lord) {
            this.sign = sign; this.symbol = symbol; this.part = part; this.lord = lord;
        }
    }

    public static class PlanetPosition {
        public final double          lon;
        public final String          display;
        public final String          nakshatra;
        public final int             pada;
        public final String          nakLord;
        public final double          degInNak;
        public final DivisionalResult d9, d10, d60;
        public final double          speed;
        public final boolean         retrograde;

        public PlanetPosition(double lon, String display, String nakshatra, int pada,
                              String nakLord, double degInNak,
                              DivisionalResult d9, DivisionalResult d10, DivisionalResult d60,
                              double speed, boolean retrograde) {
            this.lon = lon; this.display = display;
            this.nakshatra = nakshatra; this.pada = pada;
            this.nakLord = nakLord; this.degInNak = degInNak;
            this.d9 = d9; this.d10 = d10; this.d60 = d60;
            this.speed = speed; this.retrograde = retrograde;
        }
    }

    public static class PortesResult {
        public final PlanetPosition porteVisible;
        public final PlanetPosition porteInvisible;
        PortesResult(PlanetPosition pv, PlanetPosition pi) {
            this.porteVisible = pv; this.porteInvisible = pi;
        }
    }
}
