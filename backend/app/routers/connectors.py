"""Documentation programmatique des connecteurs -- cahier des charges Helios §9.3 et §11.

« Aucun connecteur n'est intégré sans documentation de conformité » : ce
module rend cette documentation consultable par l'API (donc par l'interface),
plutôt que de la laisser uniquement dans le code ou ce fichier de specs.
"""
from __future__ import annotations

from fastapi import APIRouter

from ..connectors.google_trends import TERMS_OF_USE_URL as TRENDS_TERMS
from ..connectors.insee import TERMS_OF_USE_URL as INSEE_TERMS
from ..connectors.wikipedia import TERMS_OF_USE_URL as WIKI_TERMS
from ..connectors.wikipedia_edits import TERMS_OF_USE_URL as WIKI_EDITS_TERMS
from ..guardrails import MIN_COMMUNE_POPULATION, MIN_K_ANONYMITY
from ..schemas import ConnectorInfo

router = APIRouter(prefix="/api/connectors", tags=["connectors"])

CONNECTORS: list[ConnectorInfo] = [
    ConnectorInfo(
        name="insee_bdm",
        label="Insee -- Banque de données macroéconomiques (BDM)",
        description=(
            "Séries chronologiques officielles (chômage, confiance des ménages, climat des affaires, "
            "prix...), publiées mensuellement ou trimestriellement par l'Insee au niveau national. "
            "Plusieurs séries indépendantes sont combinées par phénomène testé (H1) plutôt qu'une seule."
        ),
        access_type="Ouvert, sans clé (service web SDMX 2.1)",
        terms_of_use_url=INSEE_TERMS,
        ethical_notes=[
            "Données déjà agrégées au niveau national par l'Insee -- aucune donnée individuelle n'existe dans ce service.",
            "Aucun scraping : appel direct au service web officiel documenté par l'Insee.",
        ],
    ),
    ConnectorInfo(
        name="wikipedia_pageviews",
        label="Wikimedia -- vues quotidiennes d'articles (Pageviews)",
        description=(
            "Nombre de vues par jour d'un article Wikipédia francophone donné -- utilisé comme proxy "
            "de l'attention publique portée à un sujet. Complété depuis par Google Trends (voir plus bas, "
            "accès non officiel documenté) et non par GDELT (API de timeline rate-limitée depuis cet "
            "environnement, fichiers bruts trop volumineux pour une requête interactive)."
        ),
        access_type="Ouvert, sans clé, licence CC0 (domaine public)",
        terms_of_use_url=WIKI_TERMS,
        ethical_notes=[
            "Comptage agrégé par jour et par article -- aucune donnée de visiteur individuelle n'est exposée par cette API.",
            "Filtré sur le trafic humain (« user »), pas les robots d'indexation.",
            "Aucun scraping : appel direct à l'API REST officielle de la Wikimedia Foundation.",
            "Limite technique assumée : cette API ne couvre que juillet 2015 et après -- aucun phénomène antérieur n'est proposé tant qu'aucune autre source sociale historique n'est disponible.",
            "Pour chaque phénomène, plusieurs articles thématiquement liés sont sommés plutôt qu'un seul choisi à la main.",
        ],
    ),
    ConnectorInfo(
        name="wikipedia_edit_activity",
        label="Wikimedia -- activité d'édition d'un article",
        description=(
            "Historique des révisions d'un article Wikipédia, utilisé pour produire DEUX signaux : le "
            "nombre de modifications par jour (intensité) et le nombre de contributeurs différents par "
            "jour (est-ce qu'une seule personne édite beaucoup, ou beaucoup de monde s'y met ?). "
            "Engagement actif, différent de la fréquentation passive des vues."
        ),
        access_type="Ouvert, sans clé (MediaWiki Action API)",
        terms_of_use_url=WIKI_EDITS_TERMS,
        ethical_notes=[
            "Comptage agrégé de modifications par jour -- les comptes ou IP des contributeurs ne sont ni récupérés ni exposés.",
            "Aucun scraping : appel direct à l'API officielle de MediaWiki.",
            "Signal plus rare que les vues (tous les articles ne sont pas édités tous les jours) -- traité comme secondaire, jamais comme substitut au signal de fréquentation.",
        ],
    ),
    ConnectorInfo(
        name="insee_taux_chomage_departements",
        label="Insee -- Taux de chômage localisé par département (dataflow TAUX-CHOMAGE)",
        description=(
            "Taux de chômage trimestriel des 96 départements de métropole en une seule requête -- "
            "utilisé pour la coupe spatiale de l'hypothèse H2 (indice de Moran)."
        ),
        access_type="Ouvert, sans clé (service web SDMX 2.1, même service que la BDM)",
        terms_of_use_url=INSEE_TERMS,
        ethical_notes=[
            "Données déjà agrégées au niveau départemental par l'Insee -- aucune donnée individuelle.",
            "Aucun scraping : appel direct au service web officiel documenté par l'Insee.",
        ],
    ),
    ConnectorInfo(
        name="google_trends",
        label="Google Trends -- intérêt de recherche quotidien (accès non officiel)",
        description=(
            "Volume de recherche relatif par jour pour un terme donné, France. Ajouté en complément de "
            "Wikipédia comme troisième signal social, avec un terme direct par phénomène et un panier "
            "fixe de 5 termes « obliques » (recherche emploi, assurance chômage, anxiété, vente maison, "
            "prêt personnel) — identiques pour tous les phénomènes, choisis avant tout résultat pour "
            "éviter le biais de sélection a posteriori."
        ),
        access_type="Point d'entrée interne non documenté (pas l'API officielle, en accès alpha restreint)",
        terms_of_use_url=TRENDS_TERMS,
        ethical_notes=[
            "DÉROGATION ASSUMÉE au §6 du cahier des charges, qui prévoyait Google Trends désactivé « tant "
            "que l'accès officiel n'est pas obtenu ; pas de contournement ». Ce contournement a été fait, "
            "en connaissance de cause, après une évaluation explicite : voir le code du connecteur "
            "(app/connectors/google_trends.py) pour le raisonnement complet.",
            "Ce n'est pas un accès à des données privées : Google Trends affiche déjà ces chiffres "
            "publiquement à quiconque visite le site — c'est l'automatisation de la requête qui n'est pas "
            "couverte par les conditions d'utilisation, pas la donnée elle-même.",
            "Analyse calculée une fois, hors ligne (comme le Journal de recherche), pas en direct à chaque "
            "clic dans l'application -- Google limite agressivement les appels automatisés, ce qui rend un "
            "appel synchrone à chaque test peu fiable.",
        ],
    ),
    ConnectorInfo(
        name="departements_adjacency",
        label="IGN Admin Express COG -- contours et voisinage des départements",
        description=(
            "Réseau de contiguïté (quels départements se touchent) dérivé une fois hors ligne des "
            "contours géographiques officiels IGN, republiés par gregoiredavid/france-geojson sous "
            "Licence Ouverte Etalab. Utilisé pour l'indice de Moran de l'hypothèse H2 -- aucune "
            "requête réseau à l'exécution, le fichier de voisinage est calculé et mis en cache une fois."
        ),
        access_type="Ouvert, Licence Ouverte (Etalab), dérivé hors ligne",
        terms_of_use_url="https://github.com/gregoiredavid/france-geojson",
        ethical_notes=[
            "Données purement géographiques (contours administratifs) -- aucune donnée personnelle.",
            "Calcul de voisinage fait une fois par un script versionné (scripts/build_department_adjacency.py), pas à chaque requête.",
        ],
    ),
]


@router.get("", response_model=list[ConnectorInfo])
def list_connectors():
    return CONNECTORS


@router.get("/guardrails")
def get_guardrails():
    return {
        "min_k_anonymity": MIN_K_ANONYMITY,
        "min_commune_population_for_display": MIN_COMMUNE_POPULATION,
        "schema_commun": ["source", "territoire", "date", "indicateur", "valeur", "metadonnees"],
    }
