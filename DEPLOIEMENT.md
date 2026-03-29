# Déploiement — Gochara Karmique sur Render

## Ce qu'il vous faut
- Un compte **GitHub** (gratuit) — https://github.com
- Un compte **Render** (gratuit) — https://render.com
- Une clé API **Anthropic** — https://console.anthropic.com

---

## Étape 1 — Créer un dépôt GitHub

1. Sur GitHub → **New repository**
2. Nom : `gochara-karmique` (privé recommandé)
3. Copiez tous les fichiers du projet dans ce dépôt :
   ```
   app.py
   astro_calc.py
   ai_interpret.py
   requirements.txt
   Procfile
   render.yaml
   .env.example
   templates/
       index.html
   ```
4. Faites un commit et push.

---

## Étape 2 — Déployer sur Render

1. Sur Render → **New → Web Service**
2. Connectez votre dépôt GitHub `gochara-karmique`
3. Render détecte automatiquement `render.yaml` — vérifiez :
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
   - **Environment** : Python
4. Dans **Environment Variables**, ajoutez :
   - Clé : `ANTHROPIC_API_KEY`
   - Valeur : votre clé `sk-ant-...`
5. Cliquez **Deploy** — le build prend 2-3 minutes.

Votre URL sera du type : `https://gochara-karmique.onrender.com`

---

## Notes importantes

**Démarrage à froid** : Sur le plan gratuit Render, l'app s'endort après 15 min d'inactivité.
Le premier accès peut prendre ~30 secondes. C'est normal.

**Chiron** : Si les calculs de Chiron échouent (fichiers éphémérides manquants),
il sera marqué `N/A` dans les aspects. Les autres planètes calculent sans problème.

**Moonrise Chart** : Implémenté en Chandra Lagna (ASC = début du signe de la Lune natale),
fidèle à la logique védique du système.

**Djwhal Khul** : Ayanamsa natif Swiss Ephemeris (SE_SIDM_DJWHAL_KHUL = constante 6).

---

## Test en local (optionnel)

```bash
pip install -r requirements.txt
cp .env.example .env
# Éditez .env avec votre clé Anthropic
python app.py
# → ouvrez http://localhost:5000
```