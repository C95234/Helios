"""Exécution du pré-enregistrement du banc « épidémies » (docs/vulnerabilite/preenregistrement.md, étiquette `preenregistrement-v1`).

Ce module applique, sans les modifier, les définitions du pré-enregistrement :
- C1′ : corrélation de rang entre R̂ (croisé, urgences seules, SOS seul ; effets d'unité) et la croissance de l'indicateur national d'eaux
  usées sur des fenêtres glissantes de 12 semaines ; intervalles à 90 % par bootstrap par blocs de 12 fenêtres consécutives ;
- C2′ : tendances de Kendall avant les démarrages de vague exploitables, comparées aux fenêtres témoins (descriptif) ;
- C3 : placebos (canaux SOS permutés entre départements ; dates fictives) ;
- sensibilités du §6.

Toute fonction prend un `DonneesBanc` : le même code tourne sur les données réelles et sur des données simulées (tests).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from . import calendrier as cal
from .evaluation import tendance_kendall
from .multicanal import pente_croisee, pente_naive
from .vagues import detecter_demarrages

# --- constantes du pré-enregistrement -----------------------------------------------------------------
TAILLE_C1 = 12
PRE_FENETRE = 16
SOUS_FENETRE = 8
BLOC_BOOTSTRAP = 12
N_BOOTSTRAP = 2000
N_PERMUTATIONS = 200
N_TIRAGES_PLACEBO_DATES = 2000
DECALAGE_SOS_JOURS = 4
DEBUT = pd.Timestamp("2022-12-26")
N_SEMAINES = 105
SEMAINE_STATIONS = pd.Timestamp("2024-02-19")  # première semaine avec au moins 20 stations renseignées


@dataclass
class DonneesBanc:
    """Données hebdomadaires (T, N) et, si disponibles, quotidiennes (D, N) ; `eaux` : indicateur national hebdomadaire (T,)."""

    semaines: pd.DatetimeIndex
    departements: list[str]
    urgences: np.ndarray
    sos: np.ndarray
    eaux: np.ndarray
    controles: np.ndarray | None = None  # (T, N, 2) : férié, vacances
    urgences_j: np.ndarray | None = None  # (7·T, N)
    sos_j: np.ndarray | None = None
    controles_j: np.ndarray | None = None  # (7·T, N, 8)
    eaux_stations: pd.DataFrame | None = None  # index = semaines, colonnes = stations
    stations_departement: dict[str, str] | None = None


# ---------------------------------------------------------------------------------------------------------
# Chargement
# ---------------------------------------------------------------------------------------------------------
def _semaine_iso_vers_lundi(etiquette: str) -> pd.Timestamp:
    annee, sem = etiquette.split("-S")
    return pd.Timestamp(pd.Timestamp.fromisocalendar(int(annee), int(sem), 1))


def charger_donnees(racine: Path, couverture: str = "complete") -> DonneesBanc:
    """Charge les fichiers bruts de `racine`/raw. `couverture` : « complete » (37 départements) ou « partielle » (tous ceux avec SOS)."""
    brut = racine / "raw"
    s = pd.read_csv(brut / "sursaud-covid-quot-dep-2025-01-01-18h00.csv", sep=";", dtype={"dep": str, "sursaud_cl_age_corona": str},
                    parse_dates=["date_de_passage"])
    t = s[s.sursaud_cl_age_corona == "0"]
    jours = pd.date_range(DEBUT, periods=7 * N_SEMAINES, freq="D")
    sos_non_nul = t.dropna(subset=["nbre_acte_tot"]).groupby("dep").date_de_passage.count()
    n_jours_total = t.date_de_passage.nunique()
    if couverture == "complete":
        deps = sorted(sos_non_nul[sos_non_nul == n_jours_total].index)
    elif couverture == "partielle":
        deps = sorted(d for d in sos_non_nul.index if not d.startswith("97"))
    else:
        raise ValueError("couverture doit valoir « complete » ou « partielle ».")

    def pivot(col):
        return t.pivot(index="date_de_passage", columns="dep", values=col).reindex(jours)[deps].to_numpy(float)

    urg_j, sos_j = pivot("nbre_pass_corona"), pivot("nbre_acte_corona")
    semaines = pd.date_range(DEBUT, periods=N_SEMAINES, freq="7D")
    eau = pd.read_csv(brut / "sumeau-indicateurs-2026-01-21-14h00.csv", sep=";", decimal=",", na_values=["NA"])
    eau.index = [_semaine_iso_vers_lundi(x) for x in eau["semaine"]]
    feries = cal.charger_jours_feries(brut / "jours_feries_metropole.csv")
    vacances = cal.charger_vacances(brut / "fr-en-calendrier-scolaire.csv")
    stations = eau.drop(columns=["semaine", "National_12", "National_54"])
    chemin_st = racine / "stations_departements.json"
    st_dep = ({k: v["departement"] for k, v in json.loads(chemin_st.read_text(encoding="utf-8"))["stations"].items()} if chemin_st.exists() else None)
    return DonneesBanc(
        semaines=semaines, departements=deps,
        urgences=semaines_depuis_jours(urg_j), sos=semaines_depuis_jours(sos_j),
        eaux=eau["National_12"].reindex(semaines).to_numpy(float),
        controles=cal.controles_hebdomadaires(semaines, deps, feries, vacances),
        urgences_j=urg_j, sos_j=sos_j, controles_j=cal.controles_quotidiens(jours, deps, feries, vacances),
        eaux_stations=stations.reindex(semaines), stations_departement=st_dep,
    )


def semaines_depuis_jours(X_j: np.ndarray) -> np.ndarray:
    """Somme des 7 jours de chaque semaine ; NaN si l'un des jours manque."""
    return X_j.reshape(-1, 7, X_j.shape[1]).sum(axis=1)


# ---------------------------------------------------------------------------------------------------------
# Briques
# ---------------------------------------------------------------------------------------------------------
def fenetres(n: int, taille: int, pas: int = 1) -> list[slice]:
    return [slice(i, i + taille) for i in range(0, n - taille + 1, pas)]


def croissance_eaux(eaux: np.ndarray, taille: int) -> np.ndarray:
    """g pour chaque fenêtre : moyenne des log(E_{t+1}/E_t) sur les paires de la fenêtre ; NaN si une valeur manque."""
    with np.errstate(divide="ignore", invalid="ignore"):
        d = np.log(eaux[1:] / eaux[:-1])
    return np.array([np.mean(d[i:i + taille - 1]) if not np.isnan(d[i:i + taille - 1]).any() else np.nan for i in range(len(eaux) - taille + 1)])


def r_par_fenetre(urg, sos, taille: int, pas: int = 1, *, effets_temporels: bool = False, controles=None) -> dict[str, np.ndarray]:
    """R̂ croisé, R̂ urgences seules, R̂ SOS seul sur chaque fenêtre (effets d'unité systématiques)."""
    sortie = {"croise": [], "urgences": [], "sos": []}
    for f in fenetres(urg.shape[0], taille, pas):
        c = None if controles is None else controles[f]
        for cle, fonction in (
            ("croise", lambda: pente_croisee(urg[f], sos[f], effets_temporels=effets_temporels, effets_unite=True, controles=c)),
            ("urgences", lambda: pente_naive(urg[f], urg[f], effets_unite=True, effets_temporels=effets_temporels, controles=c)),
            ("sos", lambda: pente_naive(sos[f], sos[f], effets_unite=True, effets_temporels=effets_temporels, controles=c)),
        ):
            try:
                sortie[cle].append(fonction())
            except (ValueError, np.linalg.LinAlgError, ZeroDivisionError):
                sortie[cle].append(np.nan)
    return {k: np.array(v) for k, v in sortie.items()}


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 5 or np.ptp(a[ok]) == 0 or np.ptp(b[ok]) == 0:
        return float("nan")
    return float(spearmanr(a[ok], b[ok])[0])


def _indices_blocs(n: int, bloc: int, rng: np.random.Generator) -> np.ndarray:
    bloc = min(bloc, n)
    debuts = rng.integers(0, n - bloc + 1, int(np.ceil(n / bloc)))
    return np.concatenate([np.arange(d, d + bloc) for d in debuts])[:n]


def c1_prime(r: dict[str, np.ndarray], g: np.ndarray, rng: np.random.Generator, n_boot: int = N_BOOTSTRAP) -> dict:
    """C1′ : ρ de Spearman de chaque R̂ avec g ; Δ = ρ_croisé − max(ρ_urgences, ρ_SOS) ; IC à 90 % par blocs de 12 fenêtres.
    Réussi si les bornes basses des IC de Δ et de ρ_croisé sont > 0."""
    def rhos(idx):
        a = {k: _spearman(v[idx], g[idx]) for k, v in r.items()}
        return a, a["croise"] - max(a["urgences"], a["sos"])

    tout = np.arange(len(g))
    point, delta = rhos(tout)
    boot_d, boot_c = [], []
    for _ in range(n_boot):
        a, d = rhos(_indices_blocs(len(g), BLOC_BOOTSTRAP, rng))
        if np.isfinite(d) and np.isfinite(a["croise"]):
            boot_d.append(d)
            boot_c.append(a["croise"])
    ic_d = np.percentile(boot_d, [5, 95]) if boot_d else np.array([np.nan, np.nan])
    ic_c = np.percentile(boot_c, [5, 95]) if boot_c else np.array([np.nan, np.nan])
    return {
        "n_fenetres": int(np.isfinite(g).sum()),
        "rho_croise": point["croise"], "rho_urgences": point["urgences"], "rho_sos": point["sos"],
        "delta": delta, "ic90_delta": ic_d.tolist(), "ic90_rho_croise": ic_c.tolist(),
        "reussi": bool(len(boot_d) > 0 and ic_d[0] > 0 and ic_c[0] > 0),
    }


def c3_canaux_melanges(donnees: DonneesBanc, g: np.ndarray, r: dict[str, np.ndarray], rng: np.random.Generator, n_perm: int = N_PERMUTATIONS,
                       delta_observe: float | None = None) -> dict:
    """C3 (ii) : permute au hasard les départements du canal SOS par rapport aux urgences et recalcule Δ.
    Propre si la médiane des Δ placebo est ≤ 0 et si leur 95ᵉ centile est inférieur à Δ observé."""
    base = max(_spearman(r["urgences"], g), _spearman(r["sos"], g))
    deltas = []
    N = donnees.urgences.shape[1]
    for _ in range(n_perm):
        p = rng.permutation(N)
        rc = r_par_fenetre(donnees.urgences, donnees.sos[:, p], TAILLE_C1)["croise"]
        deltas.append(_spearman(rc, g) - base)
    deltas = np.array(deltas)
    if delta_observe is None:
        delta_observe = _spearman(r["croise"], g) - base
    p95 = float(np.nanpercentile(deltas, 95))
    return {"n_permutations": n_perm, "delta_placebo_mediane": float(np.nanmedian(deltas)), "delta_placebo_p95": p95,
            "delta_observe": float(delta_observe), "propre": bool(np.nanmedian(deltas) <= 0 and p95 < delta_observe)}


# ---------------------------------------------------------------------------------------------------------
# C2′ : signal avant une vague (descriptif)
# ---------------------------------------------------------------------------------------------------------
def indicateurs_pre_fenetre(urg, sos, debut: int, longueur: int = PRE_FENETRE, sous: int = SOUS_FENETRE) -> dict[str, float]:
    """Tendance de Kendall (τ) de chaque indicateur sur les sous-fenêtres de `sous` semaines (décalées d'une semaine) de la fenêtre
    [debut, debut + longueur[. Indicateurs : R̂ croisé, R̂ urgences, R̂ SOS (effets d'unité), AC1 moyenne et variance moyenne par département."""
    series = {k: [] for k in ("R_croise", "R_urgences", "R_sos", "AC1", "variance")}
    for j in range(longueur - sous + 1):
        f = slice(debut + j, debut + j + sous)
        u, s = urg[f], sos[f]
        for cle, fonction in (("R_croise", lambda: pente_croisee(u, s, effets_unite=True)), ("R_urgences", lambda: pente_naive(u, u, effets_unite=True)),
                              ("R_sos", lambda: pente_naive(s, s, effets_unite=True))):
            try:
                series[cle].append(fonction())
            except (ValueError, np.linalg.LinAlgError, ZeroDivisionError):
                series[cle].append(np.nan)
        ac = []
        for d in range(u.shape[1]):
            x = u[:, d]
            if np.isfinite(x).all() and np.ptp(x) > 0:
                ac.append(np.corrcoef(x[:-1], x[1:])[0, 1])
        series["AC1"].append(np.mean(ac) if ac else np.nan)
        series["variance"].append(np.nanmean(np.nanvar(u, axis=0)))
    return {k: (tendance_kendall(v) if np.isfinite(v).all() else float("nan")) for k, v in series.items()}


def fins_temoins(n: int, demarrages: list[int], longueur: int = PRE_FENETRE) -> list[int]:
    """Fins de fenêtres témoins : fenêtres de `longueur` semaines ne rencontrant aucun intervalle [t − 8 ; t + 12]."""
    return [e for e in range(longueur - 1, n) if all((e < t - 8 or e - (longueur - 1) > t + 12) for t in demarrages)]


def c2_prime(donnees: DonneesBanc, rng: np.random.Generator, n_tirages: int = N_TIRAGES_PLACEBO_DATES) -> dict:
    S = donnees.urgences.sum(axis=1)
    demarrages = detecter_demarrages(S)
    exploitables = [t for t in demarrages if t >= PRE_FENETRE]
    temoins = fins_temoins(len(S), demarrages)
    tau_temoins = [indicateurs_pre_fenetre(donnees.urgences, donnees.sos, e - PRE_FENETRE + 1) for e in temoins]
    vagues = []
    for t in exploitables:
        tau = indicateurs_pre_fenetre(donnees.urgences, donnees.sos, t - PRE_FENETRE)
        rang = {k: (float(np.mean([x[k] < tau[k] for x in tau_temoins])) if np.isfinite(tau[k]) and tau_temoins else float("nan")) for k in tau}
        vagues.append({"demarrage": str(donnees.semaines[t].date()), "tau": tau, "part_des_temoins_en_dessous": rang,
                       "bon_sens": {k: bool(v > 0) for k, v in tau.items() if np.isfinite(v)}})
    placebo = {}
    if len(temoins) >= 2 and exploitables:
        for k in ("R_croise", "R_urgences", "R_sos", "AC1", "variance"):
            valeurs = np.array([x[k] for x in tau_temoins], dtype=float)
            moyennes = [np.nanmean(rng.choice(valeurs, size=min(len(exploitables), len(valeurs)), replace=False)) for _ in range(n_tirages)]
            placebo[k] = {"q05": float(np.nanpercentile(moyennes, 5)), "mediane": float(np.nanmedian(moyennes)), "q95": float(np.nanpercentile(moyennes, 95))}
    return {"demarrages": [str(donnees.semaines[t].date()) for t in demarrages], "exploitables": [str(donnees.semaines[t].date()) for t in exploitables],
            "n_temoins": len(temoins), "fins_temoins": temoins, "vagues": vagues, "placebo_dates": placebo,
            "avertissement": "Descriptif : au plus 2 événements exploitables et 2 groupes de témoins ; aucune inférence."}


# ---------------------------------------------------------------------------------------------------------
# Analyses
# ---------------------------------------------------------------------------------------------------------
def analyse_c1(donnees: DonneesBanc, rng: np.random.Generator, *, taille: int = TAILLE_C1, effets_temporels: bool = False,
               avec_calendrier: bool = False, n_boot: int = N_BOOTSTRAP) -> tuple[dict, dict, np.ndarray]:
    r = r_par_fenetre(donnees.urgences, donnees.sos, taille, effets_temporels=effets_temporels,
                      controles=donnees.controles if avec_calendrier else None)
    g = croissance_eaux(donnees.eaux, taille)
    return c1_prime(r, g, rng, n_boot), r, g


def _variante_quotidienne(donnees: DonneesBanc, rng: np.random.Generator, n_boot: int) -> dict:
    """Pas quotidien (secondaire) : fenêtres de 84 jours décalées d'une semaine ; contrôles : jour de semaine, férié, vacances."""
    T = donnees.urgences.shape[0]
    taille_j = 7 * TAILLE_C1
    r = {"croise": [], "urgences": [], "sos": []}
    for i in range(T - TAILLE_C1 + 1):
        f = slice(7 * i, 7 * i + taille_j)
        u, s, c = donnees.urgences_j[f], donnees.sos_j[f], donnees.controles_j[f]
        for cle, fonction in (("croise", lambda: pente_croisee(u, s, effets_unite=True, controles=c)),
                              ("urgences", lambda: pente_naive(u, u, effets_unite=True, controles=c)),
                              ("sos", lambda: pente_naive(s, s, effets_unite=True, controles=c))):
            try:
                r[cle].append(fonction())
            except (ValueError, np.linalg.LinAlgError, ZeroDivisionError):
                r[cle].append(np.nan)
    return c1_prime({k: np.array(v) for k, v in r.items()}, croissance_eaux(donnees.eaux, TAILLE_C1), rng, n_boot)


def _variante_decalage(donnees: DonneesBanc, jours_decalage: int) -> DonneesBanc:
    """SOS décalé de `jours_decalage` jours vers l'avant avant l'agrégation hebdomadaire (SOS précède les urgences)."""
    sos_j = np.full_like(donnees.sos_j, np.nan)
    sos_j[jours_decalage:] = donnees.sos_j[:-jours_decalage]
    return replace(donnees, sos=semaines_depuis_jours(sos_j), sos_j=sos_j)


def _variante_stations(donnees: DonneesBanc, rng: np.random.Generator, n_boot: int) -> dict:
    """Indicateur de chaque station associée à son département, sur la période à au moins 20 stations (à partir du 19 février 2024)."""
    if donnees.eaux_stations is None or donnees.stations_departement is None:
        return {"non_disponible": True}
    i0 = int(np.searchsorted(donnees.semaines, SEMAINE_STATIONS))
    deps_avec_station = sorted({donnees.stations_departement[s] for s in donnees.eaux_stations.columns if donnees.stations_departement.get(s)} & set(donnees.departements))
    if len(deps_avec_station) < 5:
        return {"non_concluant": True, "n_departements_avec_station": len(deps_avec_station), "departements": deps_avec_station}
    cols = [donnees.departements.index(d) for d in deps_avec_station]
    urg, sos = donnees.urgences[i0:, cols], donnees.sos[i0:, cols]
    r = r_par_fenetre(urg, sos, TAILLE_C1)
    n_f = urg.shape[0] - TAILLE_C1 + 1
    g = np.full(n_f, np.nan)
    for i in range(n_f):
        par_dep = []
        for d in deps_avec_station:
            vals = []
            for st in donnees.eaux_stations.columns:
                if donnees.stations_departement.get(st) == d:
                    serie = donnees.eaux_stations[st].to_numpy(float)[i0 + i:i0 + i + TAILLE_C1]
                    if np.isfinite(serie).all() and (serie > 0).all():
                        vals.append(np.mean(np.diff(np.log(serie))))
            if vals:
                par_dep.append(np.mean(vals))
        g[i] = np.mean(par_dep) if par_dep else np.nan
    res = c1_prime(r, g, rng, n_boot)
    res["departements"] = deps_avec_station
    return res


def executer_tout(donnees: DonneesBanc, donnees_partielles: DonneesBanc | None = None, graine: int = 20261018,
                  n_boot: int = N_BOOTSTRAP, n_perm: int = N_PERMUTATIONS, n_placebo: int = N_TIRAGES_PLACEBO_DATES) -> dict:
    """Exécute le pré-enregistrement : analyse principale (C1′, C3, C2′) puis toutes les sensibilités du §6."""
    rng = np.random.default_rng(graine)
    principale, r, g = analyse_c1(donnees, rng, n_boot=n_boot)
    c3 = c3_canaux_melanges(donnees, g, r, rng, n_perm, principale["delta"])
    resultat = {
        "graine": graine, "n_departements": len(donnees.departements), "n_semaines": len(donnees.semaines),
        "C1_prime": principale, "C3_canaux_melanges": c3,
        "decision": ("succes" if principale["reussi"] and c3["propre"] else
                     "echec_partiel" if principale["reussi"] or c3["propre"] else "echec"),
        "C2_prime": c2_prime(donnees, rng, n_placebo),
        "sensibilites": {},
    }
    s = resultat["sensibilites"]
    s["effets_temporels_complets"] = analyse_c1(donnees, rng, effets_temporels=True, n_boot=n_boot)[0]
    if donnees.controles is not None:
        s["controles_calendrier"] = analyse_c1(donnees, rng, avec_calendrier=True, n_boot=n_boot)[0]
    if donnees.sos_j is not None:
        s[f"sos_decale_{DECALAGE_SOS_JOURS}_jours"] = analyse_c1(_variante_decalage(donnees, DECALAGE_SOS_JOURS), rng, n_boot=n_boot)[0]
        if donnees.urgences_j is not None and donnees.controles_j is not None:
            s["pas_quotidien"] = _variante_quotidienne(donnees, rng, n_boot)
    if donnees_partielles is not None:
        s["departements_45"] = analyse_c1(donnees_partielles, rng, n_boot=n_boot)[0]
    for taille in (8, 16):
        s[f"fenetre_{taille}_semaines"] = analyse_c1(donnees, rng, taille=taille, n_boot=n_boot)[0]
    s["stations_eaux_usees"] = _variante_stations(donnees, rng, n_boot)
    return resultat
