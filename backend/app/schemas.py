from __future__ import annotations

from pydantic import BaseModel, Field


class IndicatorSeriesOut(BaseModel):
    dates: list[str]
    values: list[float | None]


class SignificanceOut(BaseModel):
    indicator: str
    observed_tau: float | None
    p_value: float | None
    n_surrogates: int
    n_points: int
    significant_at_0_05: bool


class AnalysisResponse(BaseModel):
    source_title: str
    source: str
    window: int
    n_observations: int
    raw: IndicatorSeriesOut
    variance: IndicatorSeriesOut
    ac1: IndicatorSeriesOut
    variance_significance: SignificanceOut
    ac1_significance: SignificanceOut
    n_episodes_tested: int = Field(
        1, description="Nombre d'episodes independants testes -- §7 : jamais < 5 pour un verdict ferme."
    )
    preliminary_result: bool = True
    causal_disclaimer: str = (
        "Un signal precurseur indique une perte de resilience statistique, "
        "pas une prediction certaine ni une cause identifiee."
    )


class SeriesCatalogEntry(BaseModel):
    idbank: str
    title: str


class DemoResponse(BaseModel):
    seed: int
    dates: list[str]
    values: list[float]
    tipping_index: int
    variance: IndicatorSeriesOut
    ac1: IndicatorSeriesOut


class SeriesAnalysisOut(BaseModel):
    title: str
    source: str
    window: int
    n_observations: int
    raw: IndicatorSeriesOut
    variance: IndicatorSeriesOut
    ac1: IndicatorSeriesOut
    variance_significance: SignificanceOut
    ac1_significance: SignificanceOut
    peak_date: str | None = Field(None, description="Date du pic d'AC1 dans la fenetre -- proxy simple, pas un test formel.")


class MoranTestOut(BaseModel):
    observed_i: float | None
    p_value: float | None
    n_permutations: int
    null_mean: float | None
    null_std: float | None
    significant_at_0_05: bool


class DepartmentValueOut(BaseModel):
    code: str
    name: str
    value: float


class TrendTestOut(BaseModel):
    observed_tau: float | None
    p_value: float | None
    n_surrogates: int
    n_points: int
    significant_at_0_05: bool


class MoranSeriesOut(BaseModel):
    moran_series: IndicatorSeriesOut
    trend: TrendTestOut
    latest_snapshot: MoranTestOut


class H2Response(BaseModel):
    n_units: int
    n_quarters: int
    period_start: str
    period_end: str
    grid_shape: tuple[int, int]
    n_edges_real_network: int
    real_network: MoranSeriesOut
    control_grid: MoranSeriesOut
    values_latest: list[DepartmentValueOut]
    verdict_simple: str
    n_episodes_tested: int = 1
    preliminary_result: bool = True
    causal_disclaimer: str = (
        "Un indice de Moran élevé indique une synchronisation spatiale, pas une prédiction certaine "
        "ni une cause identifiée. 105 trimestres d'une même série longue rendent le test de tendance "
        "robuste, mais restent une seule série -- pas 5 épisodes indépendants au sens du §5.7."
    )


class ConnectorInfo(BaseModel):
    name: str
    label: str
    description: str
    access_type: str
    terms_of_use_url: str
    ethical_notes: list[str]


class PhenomenonEntry(BaseModel):
    code: str
    label: str
    description: str


class H1Response(BaseModel):
    phenomenon_label: str
    phenomenon_description: str
    official_signals: list[SeriesAnalysisOut]
    social_signals: list[SeriesAnalysisOut]
    n_official_significant: int
    n_social_significant: int
    earliest_official_peak: str | None = None
    earliest_social_peak: str | None = None
    decalage_jours: int | None = Field(
        None,
        description="earliest_official_peak - earliest_social_peak en jours, calcule seulement parmi les signaux significatifs. Positif = le social a culmine avant l'officiel.",
    )
    verdict_simple: str
    n_episodes_tested: int = 1
    preliminary_result: bool = True
    causal_disclaimer: str = (
        "Un signal precurseur indique une perte de resilience statistique, "
        "pas une prediction certaine ni une cause identifiee. Le decalage en jours "
        "est un indice descriptif (date des pics), pas un test statistique de decalage."
    )


class HistoricalPointOut(BaseModel):
    date: str
    national_tau: float | None
    spatial_i: float | None


class H3Response(BaseModel):
    phenomenon_label: str
    phenomenon_description: str
    window_months: int
    observed_national_tau: float | None
    observed_spatial_i: float | None
    nearest_spatial_quarter: str | None
    p_temporal_rank: float | None
    p_spatial_rank: float | None
    t_observed: float | None
    p_joint: float | None
    n_historical_windows: int
    significant_at_0_05: bool
    historical_points: list[HistoricalPointOut]
    verdict_simple: str
    n_episodes_tested: int = 1
    preliminary_result: bool = True
    causal_disclaimer: str = (
        "p_joint est calibré par bootstrap sur l'historique réel 2000-2026, pas par surrogates "
        "synthétiques -- il mesure si CE phénomène est plus inhabituel (sur les deux axes à la fois) "
        "que les autres périodes de même longueur dans les 26 dernières années. Ce n'est ni une "
        "prédiction ni une preuve de cause commune."
    )


class H1AggregateResponse(BaseModel):
    n_phenomena_tested: int
    n_favorable_to_h1: int
    n_against_h1: int
    n_neutral: int
    results: list[H1Response]
    errors: list[str]


class KuramotoTraceOut(BaseModel):
    time: list[float]
    values: list[float]


class H4Response(BaseModel):
    """Simulateur H4 (§5.8) -- PAS un test statistique. Aucun champ ici ne
    doit jamais etre lu comme "confirme/infirme" : c'est une demonstration
    de principe, toujours accompagnee de `simulation_disclaimer`.
    """

    n_oscillators: int
    coupling_k: float
    critical_coupling: float
    r_threshold: float
    beta: float
    duration: float
    dt: float
    seed: int | None
    network: str = "synthetic"
    n_edges: int | None = None
    r_uncontrolled: KuramotoTraceOut
    r_controlled: KuramotoTraceOut
    mean_coupling_controlled: KuramotoTraceOut
    r_mean_uncontrolled: float
    r_mean_controlled: float
    r_final_uncontrolled: float
    r_final_controlled: float
    is_pedagogical_simulation: bool = True
    simulation_disclaimer: str = (
        "H4 est une simulation pédagogique de principe (modèle de Kuramoto), pas un test statistique "
        "contre des données réelles comme H1, H2 ou H3. Elle illustre un mécanisme possible, elle ne le "
        "prouve pas dans le monde réel. Jamais de verdict « confirmée / infirmée » ici."
    )


class FusionShotResult(BaseModel):
    """Un tir MAST analyse par le pipeline H1/H2 (variance/AC1 + indice de
    Moran, code inchange) -- §7ter. `precursor_before_quench` est le verdict
    par tir : le signal temporel ET/OU spatial devient-il significatif AVANT
    le quench (memes logique de precedence que H1), pas un nouveau type de
    verdict."""

    shot_id: int
    campaign: str | None
    disrupted: bool
    t_quench: float | None
    t_peak: float | None
    peak_current_ka: float
    n_current_points_analyzed: int
    variance_significance: SignificanceOut
    ac1_significance: SignificanceOut
    n_probes: int
    moran_trend: TrendTestOut
    precursor_before_quench: bool
    verdict_simple: str


class FusionAggregateResponse(BaseModel):
    n_shots: int
    n_disrupted: int
    n_stable: int
    n_disrupted_with_precursor: int
    n_stable_false_positive: int
    shots: list[FusionShotResult]
    verdict_simple: str
    quench_disclaimer: str = (
        "La verite terrain de disruption est derivee des donnees MAST elles-memes (chute brutale du courant "
        "plasma, critere simple documente) plutot que d'un jeu de donnees externe -- DisruptionBench "
        "(DIII-D/EAST/Alcator C-Mod) exige des identifiants institutionnels non disponibles. Ce n'est pas un "
        "detecteur de disruption valide cliniquement."
    )
    scope_disclaimer: str = (
        "Détection uniquement -- ce module ne simule, ne conçoit ni ne propose aucun système de contrôle réel "
        "de plasma. Toute mention du RCA (H4) reste une note conceptuelle hors périmètre, jamais une "
        "conception fonctionnelle applicable à un vrai tokamak. Résultats présentés séparément du domaine "
        "socio-territorial, jamais combinés en un verdict unique."
    )


class ModelComparisonOut(BaseModel):
    """Test du rapport de vraisemblance de Vuong entre la loi de puissance et
    un modèle alternatif (§5.9.2 étape 5). `mu`/`sigma` pour la log-normale,
    `rate` pour l'exponentielle -- l'autre champ reste vide selon le modèle."""

    r: float
    z: float | None = None
    p_value: float | None = None
    favors_power_law: bool | None = None
    mu: float | None = None
    sigma: float | None = None
    rate: float | None = None


class H5Response(BaseModel):
    """Loi de puissance / criticité auto-organisée (§5.9) -- hypothèse
    empirique et falsifiable, mais de nature différente de H1-H3 : pas un
    test épisode par épisode, une distribution testée sur un grand nombre de
    chocs. Jamais de verdict fondé sur le seul ajustement visuel (§5.9,
    cadrage honnête) -- toujours accompagné du test de plausibilité ET de la
    comparaison aux modèles alternatifs."""

    alpha: float
    xmin: float
    ks_statistic: float
    n_tail: int
    n_total: int
    n_departments: int
    n_quarters: int
    period_start: str
    period_end: str
    p_plausibility: float | None
    n_synthetic: int
    tail_values: list[float]
    lognormal: ModelComparisonOut
    exponential: ModelComparisonOut
    verdict: str
    data_source_disclaimer: str = (
        "Source réelle : amplitude des chocs trimestriels de chômage départemental (Insee), seule source "
        "disponible parmi celles envisagées au §5.9.3 -- GDELT (rate-limité de façon persistante) et "
        "Reddit/SNAP (aucun connecteur construit) restent indisponibles."
    )
