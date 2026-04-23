import math

def generate_karmic_chart_svg(natal_positions, lang='fr'):
    """
    Génère une carte astrologique karmique en SVG.
    Style : Gold sur fond sombre, Zodiaque Sidéral (Chandra Lagna).
    """
    
    # Couleurs du thème
    BG_COLOR = "#0a0a1a"
    GOLD_COLOR = "#d4a017"
    GOLD_DIM = "rgba(212, 160, 23, 0.3)"
    PURPLE_COLOR = "#c090e0"
    TEXT_COLOR = "#e8e0d0"
    
    # Dimensions
    SIZE = 500
    CENTER = SIZE / 2
    RADIUS = 200
    INNER_RADIUS = 140
    PLANET_RADIUS = 170
    
    # Récupération de l'ascendant (Chandra Lagna) pour la rotation
    # L'ascendant est à 9h (180 degrés)
    asc_data = natal_positions.get("ASC ↑")
    asc_lon = asc_data.get("lon_raw", 0) if asc_data else 0
    
    def get_coords(lon, radius):
        # Rotation pour que l'ASC soit à 180° (à gauche)
        # En SVG, 0° est à 3h, on tourne dans le sens horaire
        angle_deg = (lon - asc_lon + 180) % 360
        angle_rad = math.radians(angle_deg)
        x = CENTER + radius * math.cos(angle_rad)
        y = CENTER + radius * math.sin(angle_rad)
        return x, y

    # Symboles des signes
    SIGNS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
    
    svg = [
        f'<svg width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}" xmlns="http://www.w3.org/2000/svg">',
        f'<rect width="100%" height="100%" fill="{BG_COLOR}" rx="8"/>',
        
        # Cercles concentriques
        f'<circle cx="{CENTER}" cy="{CENTER}" r="{RADIUS}" fill="none" stroke="{GOLD_COLOR}" stroke-width="2"/>',
        f'<circle cx="{CENTER}" cy="{CENTER}" r="{INNER_RADIUS}" fill="none" stroke="{GOLD_DIM}" stroke-width="1"/>',
    ]
    
    # 1. Dessin des 12 maisons (segments)
    for i in range(12):
        angle = i * 30
        x1, y1 = get_coords(angle, INNER_RADIUS)
        x2, y2 = get_coords(angle, RADIUS)
        svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{GOLD_DIM}" stroke-width="1"/>')
        
        # Texte des signes au milieu de chaque segment
        sign_angle = angle + 15
        sx, sy = get_coords(sign_angle, RADIUS + 15)
        svg.append(f'<text x="{sx}" y="{sy}" fill="{GOLD_COLOR}" font-size="14" text-anchor="middle" alignment-baseline="middle" font-family="serif">{SIGNS[i % 12]}</text>')

    # 2. Dessin des planètes
    planet_symbols = {
        "Soleil ☀": "☉", "Lune ☽": "☽", "Mercure ☿": "☿", "Vénus ♀": "♀", "Mars ♂": "♂",
        "Jupiter ♃": "♃", "Saturne ♄": "♄", "Uranus ♅": "♅", "Neptune ♆": "♆", "Pluton ♇": "♇",
        "Chiron ⚷": "⚷", "Nœud Nord ☊": "☊", "Nœud Sud ☋": "☋", "Lilith ⚸": "⚸",
        "Porte Visible ⊙": "⊙", "Porte Invisible ⊗": "⊗"
    }
    
    # On filtre pour ne pas surcharger et on place les symboles
    important_planets = [
        "Lune ☽", "Soleil ☀", "Nœud Nord ☊", "Nœud Sud ☋", "Chiron ⚷", 
        "Saturne ♄", "Jupiter ♃", "Porte Visible ⊙", "Porte Invisible ⊗"
    ]
    
    for p_name in important_planets:
        p_data = natal_positions.get(p_name)
        if not p_data: continue
        
        lon = p_data.get("lon_raw")
        if lon is None: continue
        
        px, py = get_coords(lon, PLANET_RADIUS)
        symbol = planet_symbols.get(p_name, "?")
        
        # Couleur spéciale pour Chiron / Portes
        color = PURPLE_COLOR if "Chiron" in p_name or "Porte" in p_name else GOLD_COLOR
        
        svg.append(f'<text x="{px}" y="{py}" fill="{color}" font-size="18" text-anchor="middle" alignment-baseline="middle">{symbol}</text>')

    # 3. Centre et Ascendant
    svg.append(f'<circle cx="{CENTER}" cy="{CENTER}" r="3" fill="{GOLD_COLOR}"/>')
    # Ligne d'horizon (ASC-DSC)
    x_asc, y_asc = get_coords(asc_lon, RADIUS)
    x_dsc, y_dsc = get_coords(asc_lon + 180, RADIUS)
    svg.append(f'<line x1="{x_asc}" y1="{y_asc}" x2="{x_dsc}" y2="{y_dsc}" stroke="{GOLD_COLOR}" stroke-width="1" stroke-dasharray="4"/>')
    
    # Label ASC
    lx, ly = get_coords(asc_lon, RADIUS + 30)
    svg.append(f'<text x="{lx}" y="{ly}" fill="{GOLD_COLOR}" font-size="10" font-weight="bold" text-anchor="middle" font-family="monospace">ASC</text>')

    svg.append('</svg>')
    return "\n".join(svg)
