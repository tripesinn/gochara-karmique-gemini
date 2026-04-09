"""
ai_interpret.py — Gochara Karmique
Intelligence siderealAstro13 | Astrologie védique sidérale (Chandra Lagna)
Doctrine centralisée dans doctrine.py — ce fichier ne contient que la logique d'appel API.

Vault Karpathy (karmic_vault/) injecté dans _build_system_prompt() en remplacement
du SYSTEM_PROMPT_FR/EN de doctrine.py. Plus compact (~800 tokens vs ~2000),
structuré pour Claude ET Gemma 4 Mini (migration progressive).
"""

import anthropic
import os

# ── Import doctrine centralisée ───────────────────────────────────────────────
from doctrine import (
    get_system_prompt,
    _detect_friction_axis,
    NAKSHATRA_KARMA,
    NODAL_CYCLES,
    HOUSE_MEANINGS,
)


# ══════════════════════════════════════════════════════════════════════════════
# VAULT KARPATHY — chargement des fichiers Markdown doctrinaux
# ══════════════════════════════════════════════════════════════════════════════

_VAULT_DIR = os.path.join(os.path.dirname(__file__), "karmic_vault")

def _load_vault(include_keywords: bool = True) -> str:
    """
    Charge le vault doctrinal Markdown compressé (~800-1300 tokens).
    Remplace get_system_prompt() de doctrine.py dans _build_system_prompt().
    Fallback silencieux vers get_system_prompt() si le vault est absent.

    include_keywords=True  → injecte 02_planet_keywords.md (transits actifs)
    include_keywords=False → 00 + 01 seulement (hook freemium léger)
    """
    try:
        master = open(os.path.join(_VAULT_DIR, "00_MASTER_CONTEXT.md"), encoding="utf-8").read()
        rules  = open(os.path.join(_VAULT_DIR, "01_output_rules.md"),   encoding="utf-8").read()
        vault  = master + "\n\n---\n\n" + rules
        if include_keywords:
            kw_path = os.path.join(_VAULT_DIR, "02_planet_keywords.md")
            if os.path.exists(kw_path):
                vault += "\n\n---\n\n" + open(kw_path, encoding="utf-8").read()
        return vault
    except FileNotFoundError:
        # Vault absent → fallback doctrine.py (comportement identique à avant)
        return None

# ── Client singleton ──────────────────────────────────────────────────────────
_client = None

def _get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    return _client


# ══════════════════════════════════════════════════════════════════════════════
# PROMPT SYSTÈME — personnalisé par utilisateur, doctrine centralisée
# ══════════════════════════════════════════════════════════════════════════════

def _build_system_prompt(user: dict, use_vault: bool = True) -> str:
    """
    Construit le prompt système complet.

    use_vault=True (défaut) :
        Base = vault Karpathy (karmic_vault/00_MASTER_CONTEXT.md + 01 + 02)
        ~800-1300 tokens, structuré Markdown, optimal pour Claude ET Gemma.
        Fallback automatique vers get_system_prompt() si vault absent.

    use_vault=False :
        Base = doctrine.get_system_prompt(user) — comportement legacy.

    Dans les deux cas : injection du bloc natal personnalisé + friction (Pilier 6).
    """
    user = user or {}
    lang = user.get("lang", "fr")

    name         = user.get("name", "l'utilisateur")
    cl_sign      = user.get("chandra_lagna_sign", "")
    cl_deg       = user.get("chandra_lagna_deg", "")
    ketu_sign    = user.get("ketu_sign", "")
    ketu_h       = user.get("ketu_house", "")
    rahu_sign    = user.get("rahu_sign", "")
    rahu_h       = user.get("rahu_house", "")
    pv_sign      = user.get("porte_visible_sign", "")
    pv_deg       = user.get("porte_visible_deg", "")
    pv_h         = user.get("porte_visible_house", "")
    pi_sign      = user.get("porte_invisible_sign", "")
    pi_deg       = user.get("porte_invisible_deg", "")
    pi_h         = user.get("porte_invisible_house", "")
    chiron_sign  = user.get("chiron_sign", "")
    chiron_h     = user.get("chiron_house", "")
    lilith_sign  = user.get("lilith_sign", "")
    lilith_h     = user.get("lilith_house", "")
    saturn_sign  = user.get("saturn_sign", "")
    saturn_h     = user.get("saturn_house", "")
    jupiter_sign = user.get("jupiter_sign", "")
    jupiter_h    = user.get("jupiter_house", "")

    # Enrichissement nakshatra via doctrine.py
    ketu_nak   = user.get("ketu_nakshatra", "")
    rahu_nak   = user.get("rahu_nakshatra", "")
    chiron_nak = user.get("chiron_nakshatra", "")
    lilith_nak = user.get("lilith_nakshatra", "")

    def nak_theme(nak_name: str, planet_key: str) -> str:
        if not nak_name:
            return ""
        entry = NAKSHATRA_KARMA.get(nak_name, {})
        theme = entry.get(planet_key, "")
        return f" — {theme}" if theme else ""

    # ── Labels bilingues ──────────────────────────────────────────────────────
    if lang == "en":
        header       = f"NATAL CHART OF {name.upper()} — Base reference for all transits"
        lbl_h1       = "Identity (H1 / Chandra Lagna)"
        lbl_ketu     = "Karmic Memory — Ketu (ROM ☋)"
        lbl_rahu     = "Dharma — Rahu (☊)"
        lbl_pv       = "Liberation Path (Visible Door / Stage)"
        lbl_pi       = "Unconscious Prison (Invisible Door / RAM ⚷)"
        lbl_chiron   = "Core Wound — Chiron (RAM ⚷)"
        lbl_lilith   = "Karmic Trial — Lilith (⚸)"
        lbl_saturn   = "Saturn — Architect (♄)"
        lbl_jupiter  = "Jupiter — Gift-Bearer (♃)"
        lbl_ref      = f"ALWAYS use this natal chart as fixed reference. Never deviate.\nAddress {name} directly."
    else:
        header       = f"THÈME NATAL DE {name.upper()} — Référence de base pour tous les transits"
        lbl_h1       = "Identité (H1 / Chandra Lagna)"
        lbl_ketu     = "Mémoire karmique — Ketu (ROM ☋)"
        lbl_rahu     = "Dharma — Rahu (☊)"
        lbl_pv       = "Voie de libération (Porte Visible / Stage)"
        lbl_pi       = "Prison inconsciente (Porte Invisible / RAM ⚷)"
        lbl_chiron   = "Blessure originelle — Chiron (RAM ⚷)"
        lbl_lilith   = "Épreuve karmique — Lilith (⚸)"
        lbl_saturn   = "Saturne — Architecte (♄)"
        lbl_jupiter  = "Jupiter — Porteur de cadeaux (♃)"
        lbl_ref      = f"Utilise TOUJOURS ce thème natal comme référence fixe. Ne jamais dévier.\nTu t'adresses à {name} en tutoiement direct."

    natal_bloc = ""
    if cl_sign:
        natal_bloc = f"""

═══════════════════════════════════════════════════════════════
{header}
═══════════════════════════════════════════════════════════════

{lbl_h1:<42}: {cl_sign} {cl_deg}
{lbl_ketu:<42}: {ketu_sign} H{ketu_h}{nak_theme(ketu_nak, "ketu")}
{lbl_rahu:<42}: {rahu_sign} H{rahu_h}{nak_theme(rahu_nak, "rahu")}
{lbl_pv:<42}: {pv_sign} {pv_deg} H{pv_h}
{lbl_pi:<42}: {pi_sign} {pi_deg} H{pi_h}
{lbl_chiron:<42}: {chiron_sign} H{chiron_h}{nak_theme(chiron_nak, "chiron")}
{lbl_lilith:<42}: {lilith_sign} H{lilith_h}{nak_theme(lilith_nak, "ketu")}
{lbl_saturn:<42}: {saturn_sign} H{saturn_h}
{lbl_jupiter:<42}: {jupiter_sign} H{jupiter_h}

{lbl_ref}
"""

    # ── Pilier 6 : friction axis depuis profil natal ───────────────────────────
    friction_bloc = ""
    natal_positions = user.get("natal_positions", {})
    if natal_positions:
        friction = _detect_friction_axis(natal_positions, lang=lang)
        friction_bloc = f"\n{friction['prompt_block']}\n"

    # ── Assemblage final ──────────────────────────────────────────────────────
    # Vault Karpathy si disponible, sinon fallback doctrine.py
    if use_vault:
        vault_content = _load_vault(include_keywords=True)
        base_prompt = vault_content if vault_content else get_system_prompt(user)
    else:
        base_prompt = get_system_prompt(user)

    return base_prompt + natal_bloc + friction_bloc


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _aspects_to_text(aspects: list, max_aspects: int = 20) -> str:
    """Formate la liste des aspects transit→natal pour le prompt."""
    if not aspects:
        return "Aucun aspect actif dans l'orbe de 3°."
    lines = []
    for a in aspects[:max_aspects]:
        retro      = " ℞" if a.get("retrograde") else ""
        t_nak      = f" [{a['transit_nakshatra']}]" if a.get("transit_nakshatra") else ""
        n_nak      = f" [{a['natal_nakshatra']}]"   if a.get("natal_nakshatra")   else ""

        t_nak_theme = ""
        n_nak_theme = ""
        t_planet_key = _planet_to_doctrine_key(a.get("transit_planet", ""))
        n_planet_key = _planet_to_doctrine_key(a.get("natal_planet", ""))
        if a.get("transit_nakshatra") and t_planet_key:
            entry = NAKSHATRA_KARMA.get(a["transit_nakshatra"], {})
            if entry.get(t_planet_key):
                t_nak_theme = f" -> {entry[t_planet_key]}"
        if a.get("natal_nakshatra") and n_planet_key:
            entry = NAKSHATRA_KARMA.get(a["natal_nakshatra"], {})
            if entry.get(n_planet_key):
                n_nak_theme = f" -> {entry[n_planet_key]}"

        lines.append(
            f"T.{a['transit_planet']}{retro} ({a.get('transit_display','')}{t_nak}{t_nak_theme}) "
            f"{a['aspect']} "
            f"N.{a['natal_planet']} ({a.get('natal_display','')}{n_nak}{n_nak_theme}) "
            f"[orbe {a['orb']}°]"
        )
    return "\n".join(lines)


def _planet_to_doctrine_key(planet_name: str) -> str:
    """Mappe le nom de planète vers la clé doctrine NAKSHATRA_KARMA."""
    mapping = {
        "Ketu":    "ketu",
        "Rahu":    "rahu",
        "Saturn":  "saturn",
        "Saturne": "saturn",
        "Chiron":  "chiron",
        "Venus":   "venus",
        "Vénus":   "venus",
        "Jupiter": "jupiter",
        "Mars":    "mars",
    }
    return mapping.get(planet_name, "")


def _build_natal_context(user: dict) -> str:
    """Bloc de contexte natal compact pour le prompt de synthèse."""
    user = user or {}
    lines = []
    fields = [
        ("Chandra Lagna H1",              "chandra_lagna_sign",  "chandra_lagna_deg"),
        ("Ketu (ROM ☋)",                  "ketu_sign",           "ketu_house"),
        ("Rahu (Dharma ☊)",               "rahu_sign",           "rahu_house"),
        ("Porte Visible / Stage",         "porte_visible_sign",  "porte_visible_house"),
        ("Porte Invisible (RAM ⚷)",       "porte_invisible_sign","porte_invisible_house"),
        ("Chiron (RAM ⚷)",                "chiron_sign",         "chiron_house"),
        ("Lilith (⚸)",                    "lilith_sign",         "lilith_house"),
        ("Saturne (♄)",                   "saturn_sign",         "saturn_house"),
        ("Jupiter (♃)",                   "jupiter_sign",        "jupiter_house"),
    ]
    for label, key1, key2 in fields:
        v1 = user.get(key1, "")
        v2 = user.get(key2, "")
        if v1:
            lines.append(f"  {label}: {v1} {'H'+str(v2) if v2 else ''}")
    return "\n".join(lines) if lines else ""


def _build_amsa_bloc(chart_data: dict, lang: str = "fr", compact: bool = False) -> str:
    """
    Formate les positions divisionnelles D9/D10/D60 des planètes clés
    (natal uniquement — les Amsas décrivent la nature fixe de l'âme).
    compact=True : D60 limité à Lune+Ketu, sans texte d'instruction (mode Gemma).
    Retourne un bloc texte prêt à injecter dans le prompt.
    """
    natal = chart_data.get("natal", {})
    if not natal:
        return ""

    # Planètes clés par Amsa
    D9_PLANETS  = ["Lune ☽", "ASC ↑", "Nœud Nord ☊", "Nœud Sud ☋", "Vénus ♀", "Jupiter ♃"]
    D10_PLANETS = ["Soleil ☀", "Saturne ♄", "Mars ♂", "Jupiter ♃", "MC ↑"]
    D60_PLANETS = ["Lune ☽", "Nœud Sud ☋"] if compact else ["Lune ☽", "Soleil ☀", "Nœud Sud ☋", "Chiron ⚷", "Saturne ♄"]

    def fmt(planet_key: str, amsa: str) -> str:
        p = natal.get(planet_key)
        if not p:
            return None
        data = p.get(amsa)
        if not data:
            return None
        sign    = data.get("sign", "")
        part    = data.get("part", "")
        lord    = data.get("lord", "")   # D60 seulement
        lord_s  = f" [{lord}]" if lord else ""
        return f"  {planet_key:<22} {sign}{lord_s} (part {part})"

    lines_d9  = [r for p in D9_PLANETS  if (r := fmt(p, "d9"))]
    lines_d10 = [r for p in D10_PLANETS if (r := fmt(p, "d10"))]
    lines_d60 = [r for p in D60_PLANETS if (r := fmt(p, "d60"))]

    if not any([lines_d9, lines_d10, lines_d60]):
        return ""

    if lang == "en":
        header  = "DIVISIONAL CHARTS (NATAL AMSAS)"
        d9_lbl  = "D9 — Navamsha (dharma, soul purpose, marriage)"
        d10_lbl = "D10 — Dashamsha (professional karma, public action)"
        d60_lbl = "D60 — Shashtyamsha (karmic specificity, soul imprint)"
        instr   = ("Use these Amsas to deepen the natal reading: "
                   "the Navamsha sign refines the soul's incarnation dharma; "
                   "the Dashamsha reveals the professional mission; "
                   "the Shashtyamsha lord names the karmic sub-color of each planet.")
    else:
        header  = "CHARTS DIVISIONNELS (AMSAS NATAUX)"
        d9_lbl  = "D9 — Navamsha (dharma, vocation de l'âme, mariage)"
        d10_lbl = "D10 — Dashamsha (karma professionnel, action publique)"
        d60_lbl = "D60 — Shashtyamsha (spécificité karmique, empreinte de l'âme)"
        instr   = ("Utilise ces Amsas pour approfondir la lecture natale : "
                   "le signe Navamsha affine le dharma d'incarnation de l'âme ; "
                   "le Dashamsha révèle la mission professionnelle ; "
                   "le seigneur Shashtyamsha nomme la sous-couleur karmique de chaque planète.")

    bloc = f"\n{'─'*62}\n{header}\n{'─'*62}\n"
    if lines_d9:
        bloc += f"\n{d9_lbl}\n" + "\n".join(lines_d9) + "\n"
    if lines_d10:
        bloc += f"\n{d10_lbl}\n" + "\n".join(lines_d10) + "\n"
    if lines_d60:
        bloc += f"\n{d60_lbl}\n" + "\n".join(lines_d60) + "\n"
    if not compact:
        bloc += f"\n{instr}\n"
    return bloc


def _detect_nodal_cycle(user: dict, chart_data: dict) -> str:
    """
    Détecte si un cycle nodal est actif.
    Utilise doctrine.NODAL_CYCLES pour les descriptions.
    """
    nn_transit = chart_data.get("transit_positions", {}).get("true_node_lon")
    nn_natal   = chart_data.get("natal_positions",   {}).get("true_node_lon")
    if nn_transit is None or nn_natal is None:
        return ""

    diff = abs(nn_transit - nn_natal) % 360
    if diff > 180:
        diff = 360 - diff

    if diff <= 10:
        cycle = NODAL_CYCLES["return"]
        return f"\n CYCLE NODAL ACTIF : {cycle['description']} — {cycle['karma']}"
    if abs(diff - 90) <= 10:
        cycle = NODAL_CYCLES["square"]
        return f"\n CYCLE NODAL ACTIF : {cycle['description']} — {cycle['karma']}"
    if abs(diff - 180) <= 10:
        cycle = NODAL_CYCLES["opposition"]
        return f"\n CYCLE NODAL ACTIF : {cycle['description']} — {cycle['karma']}"
    return ""


def _detect_transit_friction(chart_data: dict, lang: str = "fr") -> str:
    """
    Détecte l'axe de friction identitaire sur les positions EN TRANSIT (Pilier 6).
    Retourne le prompt_block prêt à injecter, ou chaîne vide.
    """
    transit_pos = chart_data.get("transit_positions", {})
    if not transit_pos:
        return ""

    # Construire un dict compatible _detect_friction_axis avec préfixe transit_
    positions = {}
    for planet in ("venus", "jupiter", "mars", "saturn"):
        raw = transit_pos.get(f"{planet}_lon") or transit_pos.get(planet, {}).get("lon_raw")
        if raw is not None:
            positions[f"transit_{planet}"] = {"lon_raw": float(raw)}

    if not positions:
        return ""

    friction = _detect_friction_axis(positions, lang=lang)
    if friction["label"] == "low" and not friction["aspects"]:
        return ""
    return f"\n{friction['prompt_block']}\n"


# ══════════════════════════════════════════════════════════════════════════════
# SYNTHÈSE AUTOMATIQUE
# ══════════════════════════════════════════════════════════════════════════════

def get_synthesis(chart_data: dict, user: dict = None, lang: str = "fr") -> str:
    """
    Génère la synthèse karmique automatique (onglet Gochara).
    chart_data : dict retourné par calculate_transits()
    user       : dict du profil utilisateur (session["profile"])
    """
    user = user or {}
    lang = user.get("lang", lang)  # lang du profil prioritaire

    aspects_text   = _aspects_to_text(chart_data.get("aspects", []))
    natal_context  = _build_natal_context(user)
    nodal_cycle    = _detect_nodal_cycle(user, chart_data)
    transit_frict  = _detect_transit_friction(chart_data, lang=lang)
    amsa_bloc      = _build_amsa_bloc(chart_data, lang=lang)
    date           = chart_data.get("transit_date", "")
    time           = chart_data.get("transit_time", "")
    name           = user.get("name", "l'utilisateur")

    # ── Garde-fous : vérification des données essentielles avant envoi ────────
    _NO_ASPECT_FR = "Aucun aspect actif dans l'orbe de 3°."
    if not aspects_text or aspects_text.strip() == _NO_ASPECT_FR:
        return ("⚠️ Synthèse impossible : aucun aspect de transit actif détecté. "
                "Vérifie que `calculate_transits()` retourne bien des aspects avant d'appeler `get_synthesis()`.")
    if not natal_context:
        return ("⚠️ Synthèse impossible : thème natal manquant. "
                "Vérifie que le profil utilisateur contient au minimum `chandra_lagna_sign`.")

    natal_bloc   = f"\nThème natal de référence :\n{natal_context}\n" if natal_context else ""
    nodal_bloc   = nodal_cycle if nodal_cycle else ""
    frict_bloc   = transit_frict if transit_frict else ""

    # Noms de langue pour la règle d'enforcement
    LANG_NAMES = {
        "fr": "français",    "en": "English",
        "es": "español",     "pt": "português",
        "de": "Deutsch",     "nl": "Nederlands",
        "it": "italiano",
    }
    lang_name = LANG_NAMES.get(lang, "English")

    if lang == "fr":
        prompt = f"""Tu ES @siderealAstro13. Ne te comporte pas comme un assistant. Analyse directement les données ci-dessous selon la doctrine karmique.
Interdiction de reformuler le prompt. Tu dois rédiger une analyse basée exclusivement sur les aspects et positions fournis.

LANGUE : français uniquement. Aucun mot anglais. Écris "socialement" pas "socially", "profondément" pas "deeply", etc.
Analyse siderealAstro13 des transits de {name} — {date} à {time}.
CONSIGNE : commence directement par "## 1. LA MÉMOIRE KARMIQUE". Aucune note préalable, aucun récapitulatif des positions natales, aucune introduction.
{natal_bloc}{amsa_bloc}{nodal_bloc}{frict_bloc}

Aspects actifs (données brutes — NE PAS les citer tels quels dans le texte) :
{aspects_text}

STYLE OBLIGATOIRE : tu écris comme un lecteur d'âme, pas comme un astrologue technique.
- Traduis chaque aspect en vécu concret, en pattern comportemental reconnaissable.
- Ne cite jamais les aspects bruts ("T.Saturne conjoint N.Chiron orbe 2°"). Traduis-les en ce que {name} ressent ou fait.
- Parle directement à {name} : "tu", "ton", "ta". Nomme-le dans ce qu'il vit.
- Exemple de ton juste : "C'est la signature de ton Nœud Sud : tu as oublié ta capacité à dire non, à te poser comme premier acteur de ton existence."
- À la fin de chaque section (1, 2, 3), glisse un APERÇU : une phrase courte en italique qui ouvre une porte sans tout révéler. Cet aperçu donne envie d'aller plus loin.

Applique le protocole en 4 étapes :

1. LA MÉMOIRE KARMIQUE (ROM ☋) — Quel piège l'âme de {name} rejoue-t-elle en ce moment ? Décris le comportement automatique, la sensation familière, ce que ça lui coûte. Termine par un aperçu en italique.

2. LA BLESSURE EN TRAITEMENT (RAM ⚷) — Qu'est-ce qui est en train d'être touché, réveillé, bousculé dans la blessure profonde de {name} ? La Porte Invisible est-elle sous pression ? La Voie de libération s'ouvre-t-elle ? Décris le mouvement vécu, pas la mécanique. Termine par un aperçu en italique.

3. L'ÉPREUVE KARMIQUE (⚸) — Qu'est-ce que la période rend insupportable à {name} ? Quel endroit de sa vie frotte le plus fort ? Vers quoi ça le pousse malgré lui ? Termine par un aperçu en italique.

4. ALTERNATIVE DE CONSCIENCE — Formule la bascule en une vision claire. Ce que {name} doit cesser de faire. Ce qu'il doit oser activer. Termine par UNE seule phrase directe, actionnable, qui s'adresse à {name} personnellement.

Développe chaque section en lecture d'âme cohérente, narrative, sans liste mécanique. Minimum 300 mots. Ne pas tronquer.
RÈGLE DE LANGUE : chaque phrase doit être entièrement en français. Aucun mot dans une autre langue."""
    else:
        prompt = f"""You ARE @siderealAstro13. Do not behave as an assistant. Analyse the data below directly according to karmic doctrine.
Forbidden to rephrase the prompt. You must write an analysis based exclusively on the aspects and positions provided.

siderealAstro13 transit analysis for {name} — {date} at {time}.
INSTRUCTION: start directly with "## 1. KARMIC MEMORY". No preamble, no recap of natal positions, no introduction.
{natal_bloc}{amsa_bloc}{nodal_bloc}{frict_bloc}

Active aspects (raw data — do NOT quote them as-is in the text):
{aspects_text}

MANDATORY STYLE: you write as a soul reader, not a technical astrologer.
- Translate each aspect into lived experience, into a recognizable behavioral pattern.
- Never quote raw aspects ("T.Saturn conjunct N.Chiron orb 2°"). Translate them into what {name} feels or does.
- Speak directly to {name}: "you", "your". Name them in what they are living.
- Example of the right tone: "This is the signature of your South Node: you've forgotten your capacity to say no, to place yourself as the first actor of your own existence."
- At the end of each section (1, 2, 3), add an INSIGHT: one short sentence in italics that opens a door without revealing everything. This insight creates desire to go further.

Apply the 4-step protocol:

1. KARMIC MEMORY (ROM ☋) — What trap is {name}'s soul replaying right now? Describe the automatic behavior, the familiar feeling, what it costs them. End with an insight in italics.

2. THE WOUND IN PROCESSING (RAM ⚷) — What is being touched, awakened, shaken in {name}'s core wound right now? Is the Invisible Door under pressure? Is the path of liberation opening? Describe the lived movement, not the mechanics. End with an insight in italics.

3. KARMIC TRIAL (⚸) — What does this period make unbearable for {name}? Which area of their life chafes the hardest? Where does it push them despite themselves? End with an insight in italics.

4. ALTERNATIVE OF CONSCIOUSNESS — Formulate the inner shift as a clear vision. What {name} must stop doing. What they must dare to activate. End with ONE single direct, actionable sentence addressed personally to {name}.

Develop each section as coherent soul-reading, narrative, no mechanical lists. Minimum 300 words. Do not truncate.
LANGUAGE RULE: every single sentence must be in {lang_name}. No French or English words unless they are proper astrological terms (nakshatra names, ROM, RAM, Stage)."""

    synthesis_model = os.environ.get("SYNTHESIS_MODEL", "claude-haiku-4-5-20251001")
    msg = _get_client().messages.create(
        model=synthesis_model,
        max_tokens=4000,
        system=_build_system_prompt(user, use_vault=True),
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def build_prompt_only(chart_data: dict, user: dict = None, lang: str = "fr") -> dict:
    """
    Construit le prompt compact SANS appeler Claude.
    Optimisé pour Gemma3-1B (< 1500 tokens) : system vide, user ultra-direct.
    Retourne {"system": "...", "user": "..."} prêt à injecter dans n'importe quel LLM.
    """
    user = user or {}
    lang = user.get("lang", lang)

    aspects_text = _aspects_to_text(chart_data.get("aspects", []), max_aspects=4)
    date         = chart_data.get("transit_date", "")
    name         = user.get("name", "l'utilisateur")

    # Contexte natal minimal (signes clés seulement)
    cl   = user.get("chandra_lagna_sign", "")
    ketu = user.get("ketu_sign", "")
    rahu = user.get("rahu_sign", "")
    chi  = user.get("chiron_sign", "")
    lil  = user.get("lilith_sign", "")
    natal_mini = f"Chandra Lagna {cl}, Ketu {ketu}, Rahu {rahu}, Chiron {chi}, Lilith {lil}." if cl else ""

    if lang == "en":
        user_prompt = f"""Karmic transit analysis for {name} — {date}.
Natal: {natal_mini}
Active aspects:
{aspects_text}

Write 4 sections directly. No questions. No preamble. Address {name} as "you".

MEMORY (ROM): What karmic trap replays?
WOUND (RAM): What core wound activates?
TRIAL (Lilith): What is unbearable right now?
ACTION: One clear shift — what to stop, what to activate."""
    else:
        user_prompt = f"""Analyse karmique de transit pour {name} — {date}.
Natal : {natal_mini}
Aspects actifs (À UTILISER IMPÉRATIVEMENT) :
{aspects_text}

MISSION : Explique comment ces aspects activent spécifiquement la ROM ou la RAM.
Écris 4 sections : MÉMOIRE, BLESSURE, ÉPREUVE, ACTION.
Interdiction de répéter 'votre volonté'. Sois concret.
INSTRUCTION CRUCIALE : Nomme au moins une planète des 'Aspects actifs' dans chaque section pour justifier ton analyse.
CONSIGNE TECHNIQUE : Tu dois obligatoirement citer au moins un nom de planète issu de la liste 'Aspects actifs' dans chaque section. Explique concrètement comment cette planète influence la ROM ou la RAM de {name}."""

    system = (
        "Tu es @siderealAstro13. Utilise cette légende pour l'analyse : "
        "ROM (Ketu)=Mémoires passées/automatisme. "
        "RAM (Chiron)=Traitement actif de la blessure. "
        "LILITH=Point de rupture/épreuve. "
        "ACTION=Dharma/Bascule. "
        "Tutoie l'utilisateur. Sois direct, pas de blabla. 200 mots max."
    )

    return {
        "system": system,
        "user":   user_prompt,
    }


# ══════════════════════════════════════════════════════════════════════════════
# SYNTHÈSE STREAMING — Server-Sent Events (SSE)
# ══════════════════════════════════════════════════════════════════════════════

def get_synthesis_stream(chart_data: dict, user: dict = None, lang: str = "fr"):
    """
    Version streaming de get_synthesis().
    Génère la synthèse karmique token par token via Server-Sent Events (SSE).

    Usage dans app.py :
    ─────────────────────────────────────────────────────────────────
    from flask import Response, stream_with_context
    from ai_interpret import get_synthesis_stream

    @app.route("/synthesis_stream")
    def synthesis_stream():
        chart_data = session.get("last_chart_data", {})
        user = session.get("profile", {})
        return Response(
            stream_with_context(get_synthesis_stream(chart_data, user)),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )
    ─────────────────────────────────────────────────────────────────

    Côté frontend (JavaScript) :
    ─────────────────────────────────────────────────────────────────
    const evtSource = new EventSource("/synthesis_stream");
    const container = document.getElementById("synthesis");
    container.innerHTML = "";

    evtSource.onmessage = (e) => {
        if (e.data === "[DONE]") { evtSource.close(); return; }
        // Rétablir les vrais sauts de ligne
        container.innerHTML += e.data.replace(/\\n/g, "\n");
    };
    evtSource.onerror = () => evtSource.close();
    ─────────────────────────────────────────────────────────────────

    Yields : chaînes SSE "data: <token>\\n\\n"
    """
    user = user or {}
    lang = user.get("lang", lang)

    aspects_text  = _aspects_to_text(chart_data.get("aspects", []))
    natal_context = _build_natal_context(user)
    nodal_cycle   = _detect_nodal_cycle(user, chart_data)
    transit_frict = _detect_transit_friction(chart_data, lang=lang)
    amsa_bloc     = _build_amsa_bloc(chart_data, lang=lang)
    date          = chart_data.get("transit_date", "")
    time          = chart_data.get("transit_time", "")
    name          = user.get("name", "l'utilisateur")

    # ── Garde-fous ────────────────────────────────────────────────────────────
    _NO_ASPECT_FR = "Aucun aspect actif dans l'orbe de 3°."
    if not aspects_text or aspects_text.strip() == _NO_ASPECT_FR:
        yield "data: ⚠️ Aucun aspect de transit actif détecté.\n\n"
        yield "data: [DONE]\n\n"
        return
    if not natal_context:
        yield "data: ⚠️ Thème natal manquant.\n\n"
        yield "data: [DONE]\n\n"
        return

    natal_bloc = f"\nThème natal de référence :\n{natal_context}\n" if natal_context else ""
    nodal_bloc = nodal_cycle if nodal_cycle else ""
    frict_bloc = transit_frict if transit_frict else ""

    LANG_NAMES = {
        "fr": "français", "en": "English", "es": "español",
        "pt": "português", "de": "Deutsch", "nl": "Nederlands", "it": "italiano",
    }
    lang_name = LANG_NAMES.get(lang, "English")

    if lang == "fr":
        prompt = f"""Tu ES @siderealAstro13. Ne te comporte pas comme un assistant. Analyse directement les données ci-dessous selon la doctrine karmique.
Interdiction de reformuler le prompt. Tu dois rédiger une analyse basée exclusivement sur les aspects et positions fournis.

LANGUE : français uniquement. Aucun mot anglais.
Analyse siderealAstro13 des transits de {name} — {date} à {time}.
CONSIGNE : commence directement par "## 1. LA MÉMOIRE KARMIQUE". Aucune note préalable, aucune introduction.
{natal_bloc}{amsa_bloc}{nodal_bloc}{frict_bloc}

Aspects actifs (NE PAS les citer tels quels) :
{aspects_text}

STYLE OBLIGATOIRE : lecteur d'âme, pas astrologue technique.
- Traduis chaque aspect en vécu concret, pattern comportemental reconnaissable.
- Parle directement à {name} : "tu", "ton", "ta".
- À la fin de chaque section (1, 2, 3), un APERÇU en italique.

1. LA MÉMOIRE KARMIQUE (ROM ☋) — Quel piège rejoue-t-elle ? Décris le comportement automatique, ce que ça coûte. Aperçu en italique.
2. LA BLESSURE EN TRAITEMENT (RAM ⚷) — Qu'est-ce qui est réveillé ? La Porte Invisible est-elle sous pression ? Aperçu en italique.
3. L'ÉPREUVE KARMIQUE (⚸) — Qu'est-ce que la période rend insupportable ? Vers quoi ça pousse malgré lui ? Aperçu en italique.
4. ALTERNATIVE DE CONSCIENCE — Ce que {name} doit cesser. Ce qu'il doit oser. UNE phrase directe, actionnable.

Minimum 300 mots. Ne pas tronquer. Tout en français."""
    else:
        prompt = f"""You ARE @siderealAstro13. Do not behave as an assistant. Analyse the data below directly according to karmic doctrine.

siderealAstro13 transit analysis for {name} — {date} at {time}.
INSTRUCTION: start directly with "## 1. KARMIC MEMORY". No preamble.
{natal_bloc}{amsa_bloc}{nodal_bloc}{frict_bloc}

Active aspects (do NOT quote them as-is):
{aspects_text}

MANDATORY STYLE: soul reader, not technical astrologer.
- Translate each aspect into lived experience.
- Speak directly to {name}: "you", "your".
- End sections 1, 2, 3 with an INSIGHT in italics.

1. KARMIC MEMORY (ROM ☋) — What trap replays? Insight in italics.
2. THE WOUND IN PROCESSING (RAM ⚷) — What is awakened? Insight in italics.
3. KARMIC TRIAL (⚸) — What is unbearable? Insight in italics.
4. ALTERNATIVE OF CONSCIOUSNESS — ONE direct, actionable sentence to {name}.

Minimum 300 words. Do not truncate. Language: {lang_name}."""

    synthesis_model = os.environ.get("SYNTHESIS_MODEL", "claude-haiku-4-5-20251001")

    # ── Streaming Anthropic SDK ───────────────────────────────────────────────
    with _get_client().messages.stream(
        model=synthesis_model,
        max_tokens=4000,
        system=_build_system_prompt(user, use_vault=True),
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text_chunk in stream.text_stream:
            safe = text_chunk.replace("\n", "\\n")
            yield f"data: {safe}\n\n"

    yield "data: [DONE]\n\n"
