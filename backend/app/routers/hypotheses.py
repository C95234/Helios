from __future__ import annotations

import asyncio

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from ..connectors.insee import InseeBdmConnector
from ..connectors.wikipedia import WikipediaPageviewsConnector
from ..connectors.wikipedia_edits import WikipediaEditActivityConnector
from ..phenomena import PHENOMENA
from ..schemas import H1AggregateResponse, H1Response, IndicatorSeriesOut, PhenomenonEntry, SeriesAnalysisOut, SignificanceOut
from ..stats.indicators import rolling_ac1, rolling_variance
from ..stats.surrogates import surrogate_test

router = APIRouter(prefix="/api/hypotheses", tags=["hypotheses"])

_insee = InseeBdmConnector()
_wiki = WikipediaPageviewsConnector()
_wiki_edits = WikipediaEditActivityConnector()


def _series_out(dates: list[str], values: pd.Series) -> IndicatorSeriesOut:
    return IndicatorSeriesOut(dates=dates, values=[None if pd.isna(v) else round(float(v), 6) for v in values])


def _analyze(dates: list[str], values: pd.Series, title: str, source: str, window: int, n_surrogates: int, seed_offset: int) -> SeriesAnalysisOut:
    variance = rolling_variance(values, window)
    ac1 = rolling_ac1(values, window)
    variance_sig = surrogate_test(values, window, "variance", n_surrogates=n_surrogates, seed=seed_offset)
    ac1_sig = surrogate_test(values, window, "ac1", n_surrogates=n_surrogates, seed=seed_offset + 1)

    peak_date = None
    if ac1.notna().any():
        peak_date = dates[ac1.idxmax()]
    elif variance.notna().any():
        peak_date = dates[variance.idxmax()]

    return SeriesAnalysisOut(
        title=title,
        source=source,
        window=window,
        n_observations=len(values),
        raw=_series_out(dates, values),
        variance=_series_out(dates, variance),
        ac1=_series_out(dates, ac1),
        variance_significance=SignificanceOut(**variance_sig),
        ac1_significance=SignificanceOut(**ac1_sig),
        peak_date=peak_date,
    )


def _is_significant(s: SeriesAnalysisOut) -> bool:
    return s.variance_significance.significant_at_0_05 or s.ac1_significance.significant_at_0_05


def _earliest_peak(signals: list[SeriesAnalysisOut]) -> str | None:
    sig_peaks = [s.peak_date for s in signals if _is_significant(s) and s.peak_date]
    return min(sig_peaks) if sig_peaks else None


def _verdict(n_official: int, n_official_sig: int, n_social: int, n_social_sig: int, decalage: int | None) -> str:
    if n_official == 0 or n_social == 0:
        return "Pas assez de signaux exploitables sur cette période pour évaluer H1."
    if n_official_sig == 0 and n_social_sig == 0:
        return (
            f"Aucun des {n_official} signaux officiels ni des {n_social} signaux sociaux ne devient "
            "significatif sur cette période : elle ne fournit pas d'épisode candidat pour tester H1."
        )
    if n_official_sig > 0 and n_social_sig == 0:
        return (
            f"{n_official_sig}/{n_official} signaux officiels deviennent significatifs, mais aucun des "
            f"{n_social} signaux sociaux -- H1 n'est pas soutenue par ce cas."
        )
    if n_social_sig > 0 and n_official_sig == 0:
        return (
            f"{n_social_sig}/{n_social} signaux sociaux deviennent significatifs, mais aucun des "
            f"{n_official} signaux officiels -- cohérent avec H1 (signal précoce sans confirmation "
            "officielle immédiate), sans le prouver."
        )
    if decalage is not None and decalage > 0:
        return (
            f"{n_official_sig}/{n_official} signaux officiels et {n_social_sig}/{n_social} signaux sociaux "
            f"deviennent significatifs, et le plus précoce des pics sociaux précède le plus précoce des pics "
            f"officiels de {decalage} jour(s) -- cohérent avec H1 sur ce cas isolé."
        )
    if decalage is not None and decalage < 0:
        return (
            f"{n_official_sig}/{n_official} signaux officiels et {n_social_sig}/{n_social} signaux sociaux "
            f"deviennent significatifs, mais le plus précoce des pics officiels précède celui des pics sociaux "
            f"de {-decalage} jour(s) -- ce cas isolé va à l'encontre de H1."
        )
    return (
        f"{n_official_sig}/{n_official} signaux officiels et {n_social_sig}/{n_social} signaux sociaux "
        "deviennent significatifs, sans écart de calendrier net entre eux."
    )


@router.get("/phenomena", response_model=list[PhenomenonEntry])
def list_phenomena():
    return [PhenomenonEntry(code=k, label=v["label"], description=v["description"]) for k, v in PHENOMENA.items()]


async def _fetch_one_insee_series(idbank: str, label: str, start: str, end: str, insee_window: int) -> tuple[str, list[str], pd.Series] | None:
    """Recupere et filtre UNE serie -- isolee pour pouvoir lancer toute la batterie en parallele
    (39+ series -- les recuperer une par une sequentiellement serait beaucoup trop lent)."""
    try:
        raw = await _insee.fetch(idbank=idbank, start_period=start[:7])
        df = _insee.normalize(raw)
    except Exception:
        return None
    df = df[(df["date"] >= start) & (df["date"] <= end)].reset_index(drop=True)
    if len(df) < insee_window + 4:
        return None
    dates = df["date"].dt.strftime("%Y-%m-%d").tolist()
    return label, dates, df["valeur"]


async def _run_h1(phenomenon: str, insee_window: int, wiki_window: int, n_surrogates: int) -> H1Response:
    if phenomenon not in PHENOMENA:
        raise HTTPException(status_code=404, detail=f"Phénomène inconnu : {phenomenon}")
    spec = PHENOMENA[phenomenon]
    start, end = spec["start"], spec["end"]

    # Chaque serie officielle de la batterie est optionnelle individuellement : une serie
    # trop courte ou indisponible sur CETTE periode est ignoree plutot que de faire echouer
    # tout le phenomene (§9.3 : un seul connecteur, plusieurs series independantes). Recuperees
    # EN PARALLELE (asyncio.gather) : avec ~39 series officielles, les recuperer une par une
    # multiplierait le temps de reponse par autant de requetes reseau sequentielles.
    fetch_results = await asyncio.gather(
        *(
            _fetch_one_insee_series(idbank, label, start, end, insee_window)
            for idbank, label in spec["insee_idbanks"]
        )
    )

    official_signals: list[SeriesAnalysisOut] = []
    for result in fetch_results:
        if result is None:
            continue
        label, dates, values = result
        official_signals.append(
            _analyze(dates, values, label, "insee_bdm", insee_window, n_surrogates, seed_offset=10 + len(official_signals) * 2)
        )

    if not official_signals:
        raise HTTPException(status_code=502, detail="Aucune série officielle exploitable sur cette période.")

    social_signals: list[SeriesAnalysisOut] = []

    try:
        combined = await _wiki.fetch_combined(spec["wiki_articles"], start, end)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Connecteur Wikipedia (vues) indisponible : {exc}") from exc
    if combined.empty or len(combined) < wiki_window + 4:
        raise HTTPException(
            status_code=422,
            detail=f"Signal social (vues) trop court ({len(combined)} points) pour une fenêtre de {wiki_window}.",
        )
    n_articles = combined.attrs.get("n_articles", len(spec["wiki_articles"]))
    social_signals.append(
        _analyze(
            combined["date"].dt.strftime("%Y-%m-%d").tolist(),
            combined["valeur"],
            f"Attention Wikipédia ({n_articles} article{'s' if n_articles > 1 else ''} : {combined.attrs.get('title', '')})",
            "wikipedia_pageviews",
            wiki_window,
            n_surrogates,
            seed_offset=30,
        )
    )

    try:
        edit_raw = await _wiki_edits.fetch(article=spec["wiki_edit_article"], start=start, end=end)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Connecteur Wikipedia (éditions) indisponible : {exc}") from exc

    for mode, label, seed_offset in [
        ("edit_count", "Activité d'édition Wikipédia (nombre de modifications)", 40),
        ("unique_editors", "Contributeurs distincts Wikipédia (nombre de personnes)", 50),
    ]:
        edit_df = _wiki_edits.normalize(edit_raw, start=start, end=end, mode=mode)
        if len(edit_df) >= wiki_window + 4:
            social_signals.append(
                _analyze(
                    edit_df["date"].dt.strftime("%Y-%m-%d").tolist(),
                    edit_df["valeur"],
                    label,
                    "wikipedia_edit_activity",
                    wiki_window,
                    n_surrogates,
                    seed_offset=seed_offset,
                )
            )
    # signaux d'edition omis silencieusement s'ils sont trop courts/plats -- secondaires,
    # contrairement aux vues qui sont obligatoires.

    n_official_sig = sum(1 for s in official_signals if _is_significant(s))
    n_social_sig = sum(1 for s in social_signals if _is_significant(s))
    earliest_official = _earliest_peak(official_signals)
    earliest_social = _earliest_peak(social_signals)

    decalage = None
    if earliest_official and earliest_social:
        decalage = (pd.Timestamp(earliest_official) - pd.Timestamp(earliest_social)).days

    return H1Response(
        phenomenon_label=spec["label"],
        phenomenon_description=spec["description"],
        official_signals=official_signals,
        social_signals=social_signals,
        n_official_significant=n_official_sig,
        n_social_significant=n_social_sig,
        earliest_official_peak=earliest_official,
        earliest_social_peak=earliest_social,
        decalage_jours=decalage,
        verdict_simple=_verdict(len(official_signals), n_official_sig, len(social_signals), n_social_sig, decalage),
    )


@router.get("/h1", response_model=H1Response)
async def test_h1(
    phenomenon: str,
    insee_window: int = Query(default=4, ge=4, le=24),
    wiki_window: int = Query(default=14, ge=7, le=60),
    n_surrogates: int = Query(default=60, ge=30, le=1000),
):
    return await _run_h1(phenomenon, insee_window, wiki_window, n_surrogates)


@router.get("/h1/aggregate", response_model=H1AggregateResponse)
async def test_h1_aggregate(n_surrogates: int = Query(default=30, ge=30, le=500)):
    """Lance H1 sur tous les phenomenes curates et resume le nombre qui vont dans le sens de H1.

    §5.7 : au moins 5 episodes independants avant toute conclusion ferme. Meme avec
    plusieurs phenomenes ici, ce ne sont pas des essais aleatoires controles -- le
    resume reste un indice descriptif, jamais une preuve statistique agregee.
    """
    results: list[H1Response] = []
    errors: list[str] = []
    for code in PHENOMENA:
        try:
            results.append(await _run_h1(code, insee_window=4, wiki_window=14, n_surrogates=n_surrogates))
        except HTTPException as exc:
            errors.append(f"{code} : {exc.detail}")

    n_favorable = 0
    n_against = 0
    for r in results:
        peaked_before = r.decalage_jours is not None and r.decalage_jours > 0
        peaked_after = r.decalage_jours is not None and r.decalage_jours < 0
        favorable = peaked_before or (r.n_social_significant > 0 and r.n_official_significant == 0)
        against = peaked_after or (r.n_official_significant > 0 and r.n_social_significant == 0)

        if favorable and not against:
            n_favorable += 1
        elif against and not favorable:
            n_against += 1
    n_neutral = len(results) - n_favorable - n_against

    return H1AggregateResponse(
        n_phenomena_tested=len(results),
        n_favorable_to_h1=n_favorable,
        n_against_h1=n_against,
        n_neutral=n_neutral,
        results=results,
        errors=errors,
    )
