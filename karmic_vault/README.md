# karmic_vault/ — Doctrine Engine pour Gemma 4 Mini

## Structure

```
karmic_vault/
├── 00_MASTER_CONTEXT.md   ← TOUJOURS injecté (piliers + règles core)
├── 01_output_rules.md     ← TOUJOURS injecté (format + interdits)
└── 02_planet_keywords.md  ← Injecté SI transit actif détecté
```

## Injection dans le prompt

```python
def load_vault(include_keywords: bool = False) -> str:
    base = open("karmic_vault/00_MASTER_CONTEXT.md").read()
    rules = open("karmic_vault/01_output_rules.md").read()
    vault = base + "\n\n---\n\n" + rules
    if include_keywords:
        kw = open("karmic_vault/02_planet_keywords.md").read()
        vault += "\n\n---\n\n" + kw
    return vault
```

## Budget tokens estimé

| Fichiers injectés | Tokens estimés |
|---|---|
| 00 + 01 | ~800 |
| 00 + 01 + 02 | ~1300 |
| Payload JSON (pre_processor) | ~300 |
| **Total prompt Gemma** | **~1100–1600** |

Fenêtre context Gemma 4 Mini = 8192 tokens → largement suffisant.

## Règle de mise à jour

Toute modification doctrinale se fait D'ABORD dans `doctrine.py` (source de vérité),
puis se répercute manuellement dans ce vault.
Ne jamais modifier le vault sans valider avec la doctrine principale.

## Test de référence

Natal Jérôme : 31 Oct 1974, 08h25, Athis-Mons
- Chandra Lagna : Bélier H1
- Ketu (ROM) : Gémeaux H3
- Chiron (RAM) : Poissons H12
- Stage : Capricorne H10
- Porte Visible : Lion H5
- Porte Invisible : Verseau H11
