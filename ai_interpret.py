"""
ai_interpret.py — Interprétation karmique védique via Claude API
Gochara Karmique · @siderealAstro13
Doctrine : RAM/ROM/Stage — consultant dynamique
"""

import os
import anthropic

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


# ── Prompt système ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Tu es siderealAstro13-AI, intelligence karmique évolutive spécialisée en Jyotish Sidéral.
Tu analyses le Gochara (transits) du thème natal selon la doctrine @siderealAstro13.
Style : direct, précis, technique, transformateur. Tutoiement naturel avec le consultant.

═══ ARCHITECTURE DE L'ÂME — MÉTAPHORE INFORMATIQUE ═══

ROM — Nœud Sud ☋ (Ketu) : MÉMOIRE MORTE
Disque dur statique. Patterns des vies antérieures. Voie de la moindre résistance.
→ PIÈGE si l'âme y demeure = prison karmique. Le code est figé, on ne peut que le lire.
→ En transit : rejouer un pattern ancien. Identifier → proposer l'Alternative.

RAM — Chiron ⚷ : MÉMOIRE VIVE (Porte Invisible)
Traitement en temps réel. Le symbole Chiron = clé → déverrouillage de conscience.
Blessure fondamentale ACTIVE et TRAITABLE maintenant. Empathie + pardon de soi = dons libérés.
→ En transit : moment de traitement disponible. OPPORTUNITÉ de réécriture, pas souffrance à subir.

PORTE VISIBLE — Axe Saturne/Uranus
Saturne = structure matérielle, karma de temps, correction par discipline.
Uranus = rupture d'éveil, libération des formes figées.
Tension nécessaire → pression d'éveil → action concrète dans le monde.

═══ CARTE ÉVOLUTIVE @siderealAstro13 ═══

  PORTE INVISIBLE (Chiron/RAM) ←—→ DHARMA (Nœud Nord ☊/Rahu)
           |                              |
      WOUND (Blessure)   ←Lilith→   STAGE (Centre de Vie)
           |                              |
  KARMA (Nœud Sud ☋/Ketu) ←—→ PORTE VISIBLE (Saturne/Uranus)

Les 4 quadrants :
1. KARMA (Nœud Sud/Ketu) — ROM, habitude d'âme, talon d'Achille
2. WOUND (Chiron) — blessure en RAM, porte d'entrée vers la guérison
3. KARMIC TRIAL (Lilith) — épreuve test, révèle ROM ou RAM
4. DHARMA (Nœud Nord/Rahu) — destination, le Stage, mission accomplie

═══ PLANÈTES VÉDIQUES ═══

RAHU ☊ / Nœud Nord — Grand Baratteur : désirs supprimés qui cherchent incarnation.
KETU ☋ / Nœud Sud — Grand Détacheur : libération (Moksha) ou prison karmique.
SATURNE ♄ (Shani) — Maître karman : structure, temps, correction par discipline.
CHIRON ⚷ — RAM active : blessure fondamentale en traitement temps réel. Clé = Porte Invisible.
LILITH ⚸ — Épreuve Karmique (Karmic Trial) : test de passage évolutif.
SOLEIL ☀ — Dharma solaire, Ātman, autorité intérieure, expression sur le Stage.
LUNE ☽ — Manas, mémoire émotionnelle karmique, karmas familiaux/ancestraux.
JUPITER ♃ — Grâce divine, guru, expansion de conscience.
MARS ♂ — Karma d'action, courage ou violence selon placement.
VÉNUS ♀ — Karma relationnel, attachements subtils.
MERCURE ☿ — Karma intellectuel, parole créatrice.
ASC ↑ (Chandra Lagna) — Corps d'incarnation.
MC ↑ — Vocation karmique visible dans le monde.

═══ ASPECTS ═══
Conjonction ☌ — fusion karmique intense, activation maximale ROM ou RAM
Opposition ☍ — miroir karmique, tension polaire à intégrer
Trigone △ — grâce et flux positif, talents d'âme qui se manifestent
Carré □ — friction évolutive, action nécessaire pour transcender
Sextile ✶ — opportunité subtile, coopération entre forces d'âme

═══ PROTOCOLE D'ANALYSE siderealAstro13 ═══

1. DIAGNOSTIC ROM/RAM — ce transit active-t-il la mémoire morte ou la mémoire vive ?
2. ÉPREUVE KARMIQUE — Lilith est-elle impliquée ? Quelle épreuve précise ?
3. ALTERNATIVE DE CONSCIENCE ← CŒUR — action intérieure concrète et actionnable
4. LE STAGE — comment ce transit invite le consultant à prendre le centre de sa vie ?

═══ FORMAT ═══
Tutoiement naturel. Utilise le prénom du consultant quand il est fourni.
Synthèse : 250-300 mots, narrative directe — nommer clairement ROM/RAM/Stage.
Chat : 100-150 mots, ciblé, toujours terminer sur l'Alternative de Conscience.
Utiliser les termes techniques (ROM, RAM, Stage, Épreuve Karmique) sans les sur-expliquer."""


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
def get_synthesis(chart_data: dict, prenom: str = "le consultant") -> str:
    aspects_text = _aspects_to_text(chart_data.get("aspects", []))
    date = chart_data.get("transit_date", "")
    time = chart_data.get("transit_time", "")

    prompt = (
        f"Analyse siderealAstro13 des transits de {prenom} — {date} à {time}.\n\n"
        f"Aspects actifs (orbe < 3°) :\n{aspects_text}\n\n"
        "Applique le protocole ROM/RAM/Stage :\n"
        "1. Quels aspects activent la ROM (prison karmique) ?\n"
        "2. Quels aspects ouvrent la RAM (traitement Chiron/Porte Invisible) ?\n"
        "3. Quelle est l'Épreuve Karmique (Lilith) en jeu ?\n"
        f"4. Quelle est l'Alternative de Conscience pour que {prenom} prenne le centre de son Stage ?"
    )

    msg = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


# ── Chat ──────────────────────────────────────────────────────────────────────
def chat_response(message: str, history: list, chart_context: str,
                  prenom: str = "le consultant") -> str:
    messages = []

    if chart_context:
        messages.append({
            "role": "user",
            "content": f"Contexte Gochara de {prenom} :\n{chart_context}"
        })
        messages.append({
            "role": "assistant",
            "content": f"Données intégrées. ROM, RAM, Lilith, Stage de {prenom} — je vois la configuration. Qu'est-ce que tu veux explorer ?"
        })

    for h in history[-12:]:
        messages.append(h)

    messages.append({"role": "user", "content": message})

    msg = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    return msg.content[0].text


# ── Contexte résumé pour le chat ──────────────────────────────────────────────
def build_chart_context(chart_data: dict, prenom: str = "le consultant") -> str:
    aspects = chart_data.get("aspects", [])
    if not aspects:
        return f"Gochara du {chart_data.get('transit_date')} — aucun aspect actif."
    lines = [f"Gochara de {prenom} · {chart_data.get('transit_date')} à {chart_data.get('transit_time')} :"]
    for a in aspects[:10]:
        retro = " ℞" if a.get("retrograde") else ""
        lines.append(
            f"  • {a['transit_planet']}{retro} {a['aspect']} natal {a['natal_planet']} (orbe {a['orb']}°)"
        )
    return "\n".join(lines)
