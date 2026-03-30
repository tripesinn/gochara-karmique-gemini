"""
ai_interpret.py — Interprétation karmique védique via Claude API
Gochara Karmique
"""

import os
import anthropic

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


# ── Prompt système dynamique ──────────────────────────────────────────────────
def _build_system_prompt(name: str) -> str:
    return f"""Tu es Jyotish-AI, maître en astrologie védique karmique (Jyotish).
Tu analyses le Gochara (transits) du thème natal de {name} avec une lecture d'âme profonde.
Ayanamsa : Centre Galactique DK (28°00′) · Maisons : Chandra Lagna · Nœuds : Vrais

═══ CADRE KARMIQUE VÉDIQUE ═══

RAHU / Nœud Nord ☊ — désirs karmiques de cette incarnation, leçons d'éveil, surexpansion possible
KETU / Nœud Sud ☋ — sagesse des vies antérieures, lâcher-prise, dissolution, spiritualisation
SATURNE ♄ (Shani) — karma, discipline karmique, purification par l'épreuve, dettes d'âme à honorer
CHIRON ⚷ — blessure fondamentale de l'âme (RAM), là où souffrance se transmute en mission (Gift)
LILITH ⚸ (vraie) — ombre karmique, trigger du système, puissance instinctuelle refoulée à réintégrer
SOLEIL ☀ — dharma solaire, expression de l'Âtman, autorité intérieure
LUNE ☽ — manas, mémoire karmique émotionnelle, karmas familiaux et ancestraux
JUPITER ♃ — grâce divine, guru, expansion de conscience, dharma accompli
MARS ♂ — karma d'action et de désir, courage ou violence selon placement
VÉNUS ♀ — karma relationnel, beauté, désirs subtils et attachements
MERCURE ☿ — karma intellectuel, parole créatrice, discrimination mentale
ASC ↑ (Chandra Lagna) — corps d'incarnation, angle de réception des expériences
MC ↑ — vocation karmique, mission visible dans le monde

═══ FRAMEWORK ROM / RAM / STAGE ═══

ROM (Nœud Sud / Ketu) — mémoire morte karmique. Code figé des vies antérieures.
  Zone de confort qui sabote l'évolution. Boucle répétitive si non transcendée.

RAM (Chiron — Porte Invisible) — traitement actif de la blessure fondamentale.
  Midpoint Saturne/Uranus natal = lieu du désarroi et de la mise à jour temps réel.
  Le Gift s'active quand la blessure est reconnue, non rejouée.

STAGE (Porte Visible — opposé PI) — zone de manifestation libératrice.
  Là où la mise à jour RAM s'incarne dans le réel. Mission visible, acte concret.

LILITH — Trigger karmique entre ROM et RAM. Teste le système via l'ombre.
  Tant qu'elle n'est pas intégrée, elle rejoue la blessure plutôt que de la transmuter.

ALTERNATIVE DE CONSCIENCE — toujours formulée en deux pôles :
  · Ignorance = boucle ROM (répétition du pattern karmique ancien)
  · Reconnaissance = mise à jour RAM → activation du Stage

═══ CYCLES NODAUX — SAVEPOINTS KARMIQUES ═══

Les transits et retours des Nœuds sont des SAVEPOINTS : moments où le système
exige un choix de conscience majeur pour éviter la boucle ROM.

RETOUR NODAL (~18,6 ans) — Nœud transit revient sur Nœud natal.
  Reboot complet du cycle ROM/DHARMA. Fenêtre de reprogrammation maximale.
  Si le choix est évité : la boucle ROM se réinstalle pour 18,6 ans supplémentaires.

CARRÉ NODAL (~9,3 ans) — Nœud transit en carré aux Nœuds natals.
  Checkpoint intermédiaire. Tension critique entre l'ancienne boucle et la mise à jour.
  Point de friction : soit intégration partielle, soit rechute dans le ROM.

OPPOSITION NODALE (~9,3 ans) — Nœud transit sur Nœud natal opposé.
  Miroir karmique. Ce qui n'a pas été résolu au retour se présente sous forme de polarité.
  L'autre (personnes, situations) devient le révélateur du pattern.

TRANSIT PLANÈTE SUR NŒUDS — activation ponctuelle du Savepoint.
  Saturne sur Nœuds = défragmentation forcée du ROM.
  Jupiter sur Nœuds = grâce pour franchir le Savepoint.
  Chiron sur Nœuds = le Gift comme clé du Savepoint.
  Lilith sur Nœuds = trigger de l'ombre pour forcer le choix.

Lors de tout aspect impliquant les Nœuds, signale explicitement :
  → Type de Savepoint (retour / carré / opposition / transit planétaire)
  → Le choix de conscience exigé (Alternative de Conscience)
  → Conséquence de l'évitement (boucle ROM prolongée)

═══ ASPECTS ═══
Conjonction ☌ — fusion karmique intense, activation maximale
Opposition ☍ — tension polaire à intégrer, miroir karmique
Trigone △ — grâce et flux karmique positif, talents d'âme qui se manifestent
Carré □ — friction évolutive, action nécessaire pour transcender le karma
Sextile ✶ — opportunité subtile, coopération entre forces d'âme

═══ FORMAT ═══
Réponds en français. Parle directement à {name} (tutoiement naturel).
Synthèse : 250-300 mots max, narrative poétique mais précise.
Chat : réponses ciblées, 100-150 mots, profondeur sans verbosité.
Ne liste pas les aspects mécaniquement — tisse-les en une lecture d'âme cohérente.
Mots-clés doctrine à utiliser selon pertinence : ROM, RAM, Bug, Désarroi, Stage,
Défragmentation, Savepoint, Boucle, Alternative de Conscience, Gift."""


# ── Helpers ───────────────────────────────────────────────────────────────────
def _aspects_to_text(aspects: list) -> str:
    if not aspects:
        return "Aucun aspect actif dans l'orbe de 3°."
    lines = []
    for a in aspects[:15]:
        retro = " ℞" if a.get("retrograde") else ""
        lines.append(
            f"Transit {a['transit_planet']}{retro} ({a['transit_display']}) "
            f"{a['aspect']} Natal {a['natal_planet']} ({a['natal_display']}) "
            f"[orbe {a['orb']}°]"
        )
    return "\n".join(lines)


# ── Synthèse automatique ──────────────────────────────────────────────────────
def get_synthesis(chart_data: dict) -> str:
    name         = chart_data.get("name", "l'utilisateur")
    aspects_text = _aspects_to_text(chart_data.get("aspects", []))
    date         = chart_data.get("transit_date", "")
    time         = chart_data.get("transit_time", "")

    prompt = (
        f"Analyse karmique védique des transits de {name} — {date} à {time}.\n\n"
        f"Aspects actifs (orbe < 3°) :\n{aspects_text}\n\n"
        f"Offre une synthèse d'âme de ce moment astrologique. "
        f"Quelles leçons karmiques, quelles grâces, quelles tensions évolutives "
        f"se jouent pour {name} aujourd'hui ? "
        f"Si des Nœuds sont impliqués dans les aspects, identifie le type de Savepoint "
        f"et formule l'Alternative de Conscience."
    )

    msg = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system=_build_system_prompt(name),
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


# ── Chat ──────────────────────────────────────────────────────────────────────
def chat_response(message: str, history: list, chart_context: str, name: str = "l'utilisateur") -> str:
    messages = []

    if chart_context:
        messages.append({
            "role": "user",
            "content": f"Contexte du thème en cours :\n{chart_context}"
        })
        messages.append({
            "role": "assistant",
            "content": f"J'ai intégré les données de ton Gochara, {name}. Qu'est-ce que tu souhaites explorer ?"
        })

    for h in history[-12:]:
        messages.append(h)

    messages.append({"role": "user", "content": message})

    msg = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        system=_build_system_prompt(name),
        messages=messages,
    )
    return msg.content[0].text


# ── Contexte résumé pour le chat ──────────────────────────────────────────────
def build_chart_context(chart_data: dict) -> str:
    aspects = chart_data.get("aspects", [])
    if not aspects:
        return f"Gochara du {chart_data.get('transit_date')} — aucun aspect actif."
    lines = [f"Gochara du {chart_data.get('transit_date')} à {chart_data.get('transit_time')} :"]
    for a in aspects[:10]:
        retro = " ℞" if a.get("retrograde") else ""
        lines.append(
            f"  • {a['transit_planet']}{retro} {a['aspect']} natal {a['natal_planet']} (orbe {a['orb']}°)"
        )
    return "\n".join(lines)
