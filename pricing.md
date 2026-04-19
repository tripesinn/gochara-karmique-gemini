# Karmic Gochara — Pricing Strategy

> Jyotish sidéral DK · Doctrine Évolutive Synthétique · Claude Haiku · IA locale passive

---

## 1. Pricing Tiers

| Produit | Prix | Plateforme | Contenu | Durée |
|---|---|---|---|---|
| **Signal du Jour** | Gratuit | Web + App | Hook nakshatra quotidien généré par Haiku | Illimité |
| **Lecture** | 4,99 € | Web + App | Synthèse karmique complète + 3 questions chatbot | One-time |
| **Illimité** | 9,99 €/mois | Web + App | Chatbot 10 questions/mois · illimité si IA locale présente | Récurrent |

---

## 2. Funnel d'acquisition

```
Signal du Jour gratuit  →  Lecture 4,99 €  →  Illimité 9,99 €/mois
```

### Étape 1 — Signal du Jour (Gratuit · Web + App)

**Why :** Créer l'habitude quotidienne. L'utilisateur découvre la doctrine DK sans friction,
sans compte, sans email. Le hook est suffisamment précis pour créer une dépendance
intellectuelle — pas assez pour répondre aux vraies questions personnelles.

**How :** Nakshatra du jour + transit dominant + Alternative de Conscience en 3 phrases,
générés par Claude Haiku. Disponible via TikTok (@siderealastro13) et directement sur le site.

**Conversion logic :** Le hook fascine sans satisfaire. L'utilisateur veut sa synthèse perso —
il doit créer un profil et passer à la Lecture.

---

### Étape 2 — Lecture (4,99 € · One-time)

**Why :** Lever la barrière d'entrée avec un prix psychologiquement bas.
Prouver la valeur de la doctrine Jyotish DK avant l'abonnement.

**How :** L'utilisateur entre sa date/heure/lieu de naissance. Il reçoit une synthèse karmique
complète (Haiku) + 3 questions de chatbot incluses. Accès immédiat sur web et app.

**Conversion logic :** Après 3 questions, l'utilisateur heurte la limite. Pour continuer
la relation — questions illimitées, chatbot persistant — l'abonnement mensuel est la réponse naturelle.

---

### Étape 3 — Illimité (9,99 €/mois · Récurrent)

**Why :** Monétiser la relation continue, pas le contenu. La valeur n'est pas la synthèse —
c'est le conseiller personnel disponible à tout moment.

**How :** Chatbot 10 questions/mois via Haiku serveur, avec reset mensuel automatique.
Si l'IA locale est présente sur l'appareil (plugin Capacitor natif ou Chrome Built-in AI),
le quota devient illimité automatiquement — sans surcoût serveur, en silence.

**Conversion logic :** Churn limité par la dépendance relationnelle — le thème natal est
sauvegardé, les transits personnalisés, l'historique connu. Recommencer à zéro a un coût perçu réel.

---

## 3. Feature Comparison

| Feature | Gratuit | Lecture 4,99 € | Illimité 9,99 €/mois |
|---|:---:|:---:|:---:|
| Signal du Jour (nakshatra) | ✓ | ✓ | ✓ |
| Synthèse karmique complète | — | ✓ | ✓ |
| Questions chatbot | — | 3 | 10/mois · illimité si IA locale |
| Alertes transit par email | — | — | ✓ |
| Thème natal sauvegardé | — | ✓ | ✓ |
| Alternative de Conscience | Teaser | Complète | Complète |
| IA locale (si présente sur l'appareil) | — | — | ✓ automatique |

---

## 4. Architecture IA

**Modèle principal : Claude Haiku (serveur)**
Toutes les synthèses, hooks et réponses chatbot passent par Haiku par défaut.
Qualité doctrinale garantie. Coût maîtrisé via quotas.

**IA locale : bonus silencieux**
Si l'utilisateur dispose d'un appareil avec IA locale (plugin Capacitor Android natif,
ou Chrome Built-in AI sur desktop), `Gemma.isAvailable()` le détecte automatiquement.
La génération bascule en local — quota illimité, hors ligne, sans frais serveur.
Aucun bouton, aucun téléchargement demandé à l'utilisateur. C'est une surprise.

**Priorité de routage :**
```
Chrome Built-in AI  →  Plugin Capacitor  →  Claude Haiku (défaut)
```

---

## 5. Positioning — Value Proposition

> **Doctrine Jyotish DK. Généré par Claude.**
> L'oracle karmique qui comprend vraiment.
> @siderealastro13
>
> **Précision. Doctrine. Relation continue.**

Ce n'est pas une app de horoscope. C'est Claude Haiku entraîné sur une doctrine
karmique précise (Nœuds/Chiron/Saturne, ayanamsa DK, tutoiement direct),
accessible sur web et mobile, avec thème natal personnel sauvegardé.

**Différenciation concurrentielle :**

- vs. Co-Star / Pattern : générique, pas de doctrine, pas de Jyotish sidéral
- vs. ChatGPT astro : hallucine, pas de DK ayanamsa, pas de profil personnel
- vs. consultants humains : disponible à 3h du matin, pas de biais de projection
- vs. apps Jyotish classiques : pas de synthèse narrative, pas de chatbot, pas d'IA

---

## 6. Roadmap 6 mois

| Jalons | Timing | Contenu |
|---|---|---|
| **T0 — Launch** | Avr 2026 | Web + APK · Haiku par défaut · Stripe Lecture + Illimité |
| **T1 — Stabilisation** | Juin 2026 | Alertes live transit, feedback loop doctrine, métriques churn |
| **T2 — IA locale native** | Déc 2026 | Gemma natif Android (Google AI Core) · quota illimité automatique pour tous les Illimité |

**Note T2 :** Quand Gemma est natif Android sur tous les appareils compatibles, le quota
10/mois devient caduque pour les abonnés Illimité. Le coût serveur chatbot tombe à zéro
pour cette tranche. Opportunité de repositionnement prix ou d'extension de features.

---

## 7. Metrics & KPIs

| Métrique | Cible 3 mois | Cible 6 mois |
|---|---|---|
| Hook → Lecture conversion | 3 % | 6 % |
| Lecture → Illimité conversion | 20 % | 30 % |
| Churn mensuel | < 15 % | < 10 % |
| Alternative de Conscience hit rate | > 90 % | > 95 % |
| Taux IA locale (Illimité) | — | > 15 % |

---

## 8. Notes stratégiques

**Ce qu'on ne fait pas :**

- Pas d'email newsletter — dilue la relation, crée une attente de contenu
- Pas de téléchargement Gemma demandé à l'utilisateur — trop complexe, rendu médiocre (1B)
- Pas de version freemium avec pub — dégrade la perception doctrinale
- Pas de multi-langue au launch — focus FR, communauté TikTok existante

**Ce sur quoi on mise :**

- **TikTok organique** (@siderealastro13) comme canal d'acquisition principal
- **Geek astro FR** comme early adopter : comprend la doctrine, évangéliste naturel
- **Praticiens** (consultants Jyotish, thérapeutes) comme segment B2B latent (à adresser T2+)
- **Claude Haiku** comme garantie de qualité doctrinale — pas de compromis sur le rendu
