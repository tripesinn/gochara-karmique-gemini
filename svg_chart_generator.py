
import math

# ── Constantes pour la génération SVG ─────────────────────────────────────────
SVG_SIZE = 500
CENTER = SVG_SIZE / 2
HOUSE_RADIUS = 200
PLANET_RADIUS = 165  # Un peu plus loin pour la clarté
ZODIAC_RADIUS = 230
AXIS_RADIUS = 200

# ── Palette de symboles et couleurs ──────────────────────────────────────────
PLANET_INFO = {
    # Planètes traditionnelles
    "Soleil ☀":      {"symbol": "☉", "color": "#FFD700"},
    "Lune ☽":        {"symbol": "☽", "color": "#C0C0C0"},
    "Mercure ☿":     {"symbol": "☿", "color": "#808080"},
    "Vénus ♀":       {"symbol": "♀", "color": "#FF69B4"},
    "Mars ♂":        {"symbol": "♂", "color": "#FF4500"},
    "Jupiter ♃":     {"symbol": "♃", "color": "#4169E1"},
    "Saturne ♄":     {"symbol": "♄", "color": "#2F4F4F"},
    # Trans-saturniennes
    "Uranus ♅":      {"symbol": "♅", "color": "#00FFFF"},
    "Neptune ♆":     {"symbol": "♆", "color": "#0000FF"},
    "Pluton ♇":      {"symbol": "♇", "color": "#A9A9A9"},
    # Axes et points karmiques
    "Nœud Nord ☊":   {"symbol": "☊", "color": "#008000"},
    "Nœud Sud ☋":   {"symbol": "☋", "color": "#008000"},
    "Chiron ⚷":      {"symbol": "⚷", "color": "#9400D3"}, # Violet
    "Lilith ⚸":      {"symbol": "⚸", "color": "#4B0082"}, # Indigo
    "Porte Visible ⊙": {"symbol": "⊙", "color": "#FF8C00"}, # Orange foncé
    "Porte Invisible ⊗": {"symbol": "⊗", "color": "#FF8C00"},
    # Points cardinaux
    "ASC ↑":         {"symbol": "As", "color": "#DC143C"},
    "MC ↑":          {"symbol": "Mc", "color": "#DC143C"},
}

SIGNS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]

def _get_coords(lon, radius):
    """Calcule les coordonnées x, y pour une longitude donnée."""
    angle = math.radians(360 - lon)
    x = CENTER + radius * math.cos(angle)
    y = CENTER + radius * math.sin(angle)
    return x, y

def generate_karmic_chart_svg(natal_positions, lang="fr"):
    """
    Génère une carte du ciel SVG améliorée avec les axes karmiques.
    """
    svg_parts = [
        f'<svg width="{SVG_SIZE}" height="{SVG_SIZE}" viewBox="0 0 {SVG_SIZE} {SVG_SIZE}" xmlns="http://www.w3.org/2000/svg" style="background-color:#1a1a1a; font-family: sans-serif;">'
    ]

    # Cercle extérieur des signes
    svg_parts.append(f'<circle cx="{CENTER}" cy="{CENTER}" r="{ZODIAC_RADIUS + 10}" fill="none" stroke="#444" stroke-width="1"/>')
    svg_parts.append(f'<circle cx="{CENTER}" cy="{CENTER}" r="{HOUSE_RADIUS}" fill="none" stroke="#444" stroke-width="1"/>')


    # Dessiner les signes du zodiaque
    for i in range(12):
        angle_deg = 360 - (i * 30 + 15)
        x, y = _get_coords(angle_deg, ZODIAC_RADIUS)
        svg_parts.append(f'<text x="{x}" y="{y}" font-size="20" fill="#888" text-anchor="middle" alignment-baseline="middle">{SIGNS[i]}</text>')

    # Dessiner les maisons (lignes et numéros)
    for i in range(12):
        angle_deg = i * 30
        x2, y2 = _get_coords(angle_deg, HOUSE_RADIUS)
        svg_parts.append(f'<line x1="{CENTER}" y1="{CENTER}" x2="{x2}" y2="{y2}" stroke="#444" stroke-width="1"/>')
        
        lx, ly = _get_coords(angle_deg + 15, HOUSE_RADIUS - 20)
        svg_parts.append(f'<text x="{lx}" y="{ly}" font-size="12" fill="#666" text-anchor="middle" alignment-baseline="middle">{i + 1}</text>')

    if not natal_positions:
        svg_parts.append('</svg>')
        return "".join(svg_parts)

    # ── Dessiner les Axes Karmiques ───────────────────────────────────────────
    
    # 1. Axe des Nœuds Lunaires (Rahu/Ketu)
    nn_pos = natal_positions.get("Nœud Nord ☊")
    sn_pos = natal_positions.get("Nœud Sud ☋")
    if nn_pos and sn_pos and 'lon_raw' in nn_pos:
        x1, y1 = _get_coords(nn_pos['lon_raw'], AXIS_RADIUS)
        x2, y2 = _get_coords(sn_pos['lon_raw'], AXIS_RADIUS)
        svg_parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{PLANET_INFO["Nœud Nord ☊"]["color"]}" stroke-width="1.5" stroke-dasharray="4, 4"/>')

    # 2. Axe des Portes (Visible/Invisible)
    pv_pos = natal_positions.get("Porte Visible ⊙")
    pi_pos = natal_positions.get("Porte Invisible ⊗")
    if pv_pos and pi_pos and 'lon_raw' in pv_pos:
        x1, y1 = _get_coords(pv_pos['lon_raw'], AXIS_RADIUS)
        x2, y2 = _get_coords(pi_pos['lon_raw'], AXIS_RADIUS)
        svg_parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{PLANET_INFO["Porte Visible ⊙"]["color"]}" stroke-width="1.5"/>')

    # ── Dessiner les Planètes et Points ───────────────────────────────────────
    for name, data in natal_positions.items():
        if not data or 'lon_raw' not in data:
            continue
            
        info = PLANET_INFO.get(name)
        if not info:
            continue

        lon = data['lon_raw']
        x, y = _get_coords(lon, PLANET_RADIUS)
        
        # Ajoute un cercle derrière les symboles pour une meilleure lisibilité
        svg_parts.append(f'<circle cx="{x}" cy="{y}" r="12" fill="#1a1a1a" />')

        # Le symbole avec une infobulle
        retro = " (R)" if data.get('retrograde', False) else ""
        tooltip = f"{name.split(' ')[0]}{retro}: {data.get('display', '')}"
        
        svg_parts.append(
            f'<text x="{x}" y="{y}" font-size="16" fill="{info["color"]}" text-anchor="middle" alignment-baseline="middle">'
            f'<title>{tooltip}</title>'
            f'{info["symbol"]}'
            f'</text>'
        )

    svg_parts.append('</svg>')
    return "".join(svg_parts)
