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


class H1AggregateResponse(BaseModel):
    n_phenomena_tested: int
    n_favorable_to_h1: int
    n_against_h1: int
    n_neutral: int
    results: list[H1Response]
    errors: list[str]
