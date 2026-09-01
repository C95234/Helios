"""Phenomenes reels curates pour tester l'hypothese H1 -- cahier des charges Helios §5.5, §5.7.

Chaque phenomene combine PLUSIEURS signaux officiels (INSEE, lents et fiables)
et PLUSIEURS signaux sociaux (Wikipedia, rapides et bruites) sur la meme
periode. Retour utilisateur explicite : "un maximum de sources par
phenomene, pas juste 2 ou 4" -- ce fichier reflete cette exigence plutot
que d'ajouter des sources inventees.

- insee_idbanks : la totalite des composantes publiees de l'enquete
  mensuelle de conjoncture aupres des menages de l'Insee (CAMME) que nous
  avons pu verifier en direct -- confiance globale, climat des affaires,
  chomage, niveau de vie, prix, epargne. Ce sont des series DISTINCTES
  (chacune a son propre idbank, sa propre question posee aux menages),
  pas des duplications d'un meme indicateur sous des noms differents.
- wiki_articles : plusieurs articles Wikipedia lies au phenomene, dont les
  vues quotidiennes sont SOMMEES pour former un signal d'attention moins
  arbitraire qu'un article choisi seul.
- wiki_edit_article : l'article dont on suit aussi l'ACTIVITE D'EDITION --
  a la fois le nombre de modifications/jour ET le nombre de contributeurs
  DIFFERENTS/jour (deux lectures distinctes de la meme donnee brute :
  beaucoup de monde s'y met, ou une poignee de gens editent beaucoup ?).

Le protocole de validation (§5.7) exige au moins 5 episodes independants
avant toute conclusion ferme : ces phenomenes ne constituent qu'un point de
depart, jamais une preuve -- et plus de sources par episode ne remplace
pas plus d'episodes independants (une nuance rappelee dans l'interface).

Limites techniques assumees :
- L'API Wikimedia Pageviews ne couvre que juillet 2015 et apres (verifie en
  direct) -- aucun phenomene anterieur (ex. crise de 2008) n'est inclus.
- Certains articles Wikipedia pourtant existants n'ont aucune donnee de vues
  indexee (verifie en direct sur deux candidats) ; ils sont exclus plutot
  que devines.
- Les 7 series INSEE ci-dessous sont toutes verifiees en direct avec une
  couverture mensuelle continue depuis janvier 2015 au minimum.
"""
from __future__ import annotations

import json
from pathlib import Path

# Batterie complete des indicateurs officiels INSEE : la composante menages
# verifiee a la main (confiance, chomage, niveau de vie, prix, epargne) PLUS
# la batterie decouverte automatiquement dans scripts/discover_insee_battery.py
# (climat des affaires par secteur -- industrie, services, batiment, commerce
# -- verifiee en direct : mensuelle, CVS, indicateur synthetique actif, pas
# une question granulaire par sous-secteur). Retour utilisateur : "un maximum
# de sources par phenomene" -- 39 series officielles distinctes plutot que
# des doublons ajoutes pour gonfler un chiffre.
_MANUAL_MENAGES = [
    ("001587668", "Confiance des ménages (indice composite)"),
    ("001565530", "Climat des affaires (tous secteurs)"),
    ("001688527", "Taux de chômage (BIT)"),
    ("000857190", "Anticipation de chômage"),
    ("000857189", "Niveau de vie futur anticipé"),
    ("000857192", "Prix futurs anticipés"),
    ("011818470", "Climat de l'épargne"),
]

_DISCOVERED_BATTERY_PATH = Path(__file__).resolve().parent / "data" / "insee_battery.json"


def _load_insee_battery() -> list[tuple[str, str]]:
    battery: list[tuple[str, str]] = []
    seen: set[str] = set()
    for idbank, label in _MANUAL_MENAGES:
        battery.append((idbank, label))
        seen.add(idbank)

    if _DISCOVERED_BATTERY_PATH.exists():
        discovered = json.loads(_DISCOVERED_BATTERY_PATH.read_text(encoding="utf-8"))
        for entry in discovered:
            if entry["idbank"] in seen:
                continue
            # Titre INSEE type : "Enquête ... dans {secteur} - {sous-secteur} - {indicateur} - Série CVS".
            # On garde le sous-secteur + le type d'indicateur, jamais le prefixe/suffixe generiques.
            parts = [p.strip() for p in entry["title"].split(" - ")]
            middle = [p for p in parts[1:] if p and "série" not in p.lower() and "serie" not in p.lower()]
            detail = " — ".join(middle) if middle else entry["title"]
            label = f"{entry['sector']} : {detail}"
            battery.append((entry["idbank"], label))
            seen.add(entry["idbank"])

    return battery


INSEE_BATTERY = _load_insee_battery()

PHENOMENA = {
    "gilets_jaunes_2018": {
        "label": "Mouvement social 2018 (« gilets jaunes »)",
        "description": (
            "Mouvement social declenche mi-novembre 2018, a l'origine autour de la taxe carbone. "
            "Toute la batterie de séries officielles (Insee) contre 3 signaux sociaux (attention "
            "Wikipédia sur 2 articles, éditions, contributeurs distincts)."
        ),
        "insee_idbanks": INSEE_BATTERY,
        "wiki_articles": ["Gilets_jaunes", "Taxe_carbone_en_France"],
        "wiki_edit_article": "Gilets_jaunes",
        "start": "2018-06-01",
        "end": "2019-03-01",
    },
    "confinement_2020": {
        "label": "Tension sanitaire 2020 (premier confinement)",
        "description": (
            "Premier confinement en France (mars 2020). Toute la batterie de séries officielles "
            "contre l'attention et l'activité d'édition Wikipédia sur le confinement."
        ),
        "insee_idbanks": INSEE_BATTERY,
        "wiki_articles": ["Confinement_de_2020_en_France"],
        "wiki_edit_article": "Confinement_de_2020_en_France",
        "start": "2019-10-01",
        "end": "2020-08-01",
    },
    "chomage_recent": {
        "label": "Climat social recent (fenetre glissante la plus recente)",
        "description": (
            "Periode recente sans evenement de rupture connu -- sert de comparaison neutre : "
            "on s'attend a ne trouver aucun signal significatif nulle part."
        ),
        "insee_idbanks": INSEE_BATTERY,
        "wiki_articles": ["Ch%C3%B4mage_en_France", "%C3%89conomie_de_la_France"],
        "wiki_edit_article": "Ch%C3%B4mage_en_France",
        "start": "2024-01-01",
        "end": "2026-08-01",
    },
    "attentats_2015": {
        "label": "Attentats du 13 novembre 2015",
        "description": (
            "Choc sécuritaire soudain, pas économique par nature -- bon cas pour vérifier que les "
            "signaux officiels et sociaux ne réagissent pas forcément de la même façon."
        ),
        "insee_idbanks": INSEE_BATTERY,
        "wiki_articles": ["Attentats_du_13_novembre_2015_en_France", "%C3%89tat_d%27urgence_en_France"],
        "wiki_edit_article": "Attentats_du_13_novembre_2015_en_France",
        "start": "2015-08-01",
        "end": "2016-03-01",
    },
    "reforme_retraites_2023": {
        "label": "Mouvement social contre la réforme des retraites 2023",
        "description": "Mobilisation prolongée (janvier-juin 2023).",
        "insee_idbanks": INSEE_BATTERY,
        "wiki_articles": ["Mouvement_social_contre_la_r%C3%A9forme_des_retraites_en_France_de_2023"],
        "wiki_edit_article": "Mouvement_social_contre_la_r%C3%A9forme_des_retraites_en_France_de_2023",
        "start": "2022-10-01",
        "end": "2023-07-01",
    },
    "attentat_nice_2016": {
        "label": "Attentat de Nice, juillet 2016",
        "description": (
            "Choc localisé et soudain, sans rupture économique nationale attendue -- cas de contrôle."
        ),
        "insee_idbanks": INSEE_BATTERY,
        "wiki_articles": ["Attentat_de_Nice_du_14_juillet_2016", "%C3%89tat_d%27urgence_en_France"],
        "wiki_edit_article": "Attentat_de_Nice_du_14_juillet_2016",
        "start": "2016-04-01",
        "end": "2016-11-01",
    },
}
