"""Interface haut niveau du module : format long `unite, date, source, valeur` → table de résultats (cahier §3.2).

    res = estimer_vulnerabilite(donnees, sources=("urgences", "sos"), bruit="binomiale_negative",
                                observation="canaux_amincis", pas="semaine", bootstrap=200)

Une ligne par fenêtre. Estimation REGROUPÉE sur les unités : aucune estimation par unité n'est produite (la note
montre qu'un classement des unités les plus vulnérables n'est pas fiable avec quelques centaines de points par unité).
Aucun lien avec l'API, le site ou le rafraîchissement automatique.

Choix de la configuration des canaux (comptages) : 1 source → ajustement direct ; 2 sources → estimation croisée
avec dispersion (props. 8 et 10) ; 3 sources ou plus → `sortie` = source 0, instrument et calibrage = dernière source
(configuration robuste de la note, y compris si une source est sous boucle de surveillance).
"""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

from app.guardrails import validate_no_nominal_columns

from . import estimation as est
from . import multicanal as mc
from .bruits import BinomialeNegative, Poisson
from .garde_fous import evaluer_garde_fous
from .incertitude import SEUIL_PEU_D_UNITES
from .modele import params_depuis_inflammabilite
from .vstar import vstar_1d

COLONNES = ("unite", "date", "source", "valeur")
PLAFOND_PHI = 99.0


# ---------------------------------------------------------------------------------------------------------
# Préparation des données
# ---------------------------------------------------------------------------------------------------------
def preparer_donnees(donnees: pd.DataFrame, sources, pas: str, comptages: bool = True):
    """Format long → tableau (n_sources, n_pas, n_unites) avec NaN pour les valeurs absentes.

    `pas="semaine"` : somme par semaine ISO (lundi → dimanche) ; les semaines pour lesquelles une unité n'a pas les
    7 jours sont traitées comme manquantes (jamais comme zéro). `pas="jour"` : pas d'agrégation.
    """
    manquantes = [c for c in COLONNES if c not in donnees.columns]
    if manquantes:
        raise ValueError(f"Colonnes manquantes : {', '.join(manquantes)} (attendu : {', '.join(COLONNES)}).")
    validate_no_nominal_columns(donnees)
    if pas not in ("jour", "semaine"):
        raise ValueError("pas doit valoir « jour » ou « semaine ».")
    df = donnees[list(COLONNES)].copy()
    df["date"] = pd.to_datetime(df["date"])
    absentes = [s for s in sources if s not in set(df["source"])]
    if absentes:
        raise ValueError(f"Source(s) absente(s) des données : {', '.join(map(str, absentes))}.")
    df = df[df["source"].isin(sources)]
    if df["valeur"].isna().any():
        raise ValueError("Valeurs manquantes (NaN) dans les données : les retirer explicitement (une valeur absente n'est pas un zéro).")
    if comptages and (df["valeur"] < 0).any():
        raise ValueError("Valeurs négatives : un comptage ne peut pas être négatif.")
    if comptages and not np.allclose(df["valeur"], np.round(df["valeur"])):
        raise ValueError("Valeurs non entières : le modèle de comptage ne s'applique pas à des taux ou des moyennes "
                         "(cahier §8, piège 8). Fournir les comptes bruts.")
    if df.duplicated(["unite", "date", "source"]).any():
        raise ValueError("Doublons (unite, date, source) dans les données.")
    if pas == "semaine":
        df["periode"] = df["date"].dt.to_period("W").dt.start_time
        agg = df.groupby(["source", "unite", "periode"])["valeur"].agg(["sum", "count"]).reset_index()
        agg = agg[agg["count"] == 7].rename(columns={"sum": "valeur"})
    else:
        agg = df.rename(columns={"date": "periode"})[["source", "unite", "periode", "valeur"]]
    if agg.empty:
        raise ValueError("Aucune période complète dans les données.")
    periodes = pd.DatetimeIndex(sorted(agg["periode"].unique()))
    pas_attendu = pd.Timedelta(days=7 if pas == "semaine" else 1)
    plage = pd.date_range(periodes.min(), periodes.max(), freq=pas_attendu)
    unites = sorted(agg["unite"].unique(), key=str)
    O = np.full((len(sources), len(plage), len(unites)), np.nan)
    ip = {p: i for i, p in enumerate(plage)}
    iu = {u: i for i, u in enumerate(unites)}
    for ligne in agg.itertuples(index=False):
        O[sources.index(ligne.source), ip[ligne.periode], iu[ligne.unite]] = ligne.valeur
    return O, plage, unites


# ---------------------------------------------------------------------------------------------------------
# Estimation sur un tableau
# ---------------------------------------------------------------------------------------------------------
def _v_etoile_1d(R: float, c: float, m_bas: float, dispersion: float) -> float:
    """V* du modèle quadratique reconstruit à partir de (R̂, ĉ, m̂₋) ; NaN si les paramètres sont inadmissibles."""
    if not (c > 0 and R < 1 and m_bas > 0):
        return float("nan")
    try:
        a, mu, _, m_haut = params_depuis_inflammabilite(R, c, m_bas)
    except ValueError:
        return float("nan")
    bruit = BinomialeNegative(dispersion) if np.isfinite(dispersion) and dispersion > 1.0 else Poisson()
    return vstar_1d(lambda x: mu + a * x + c * x * x, bruit, m_bas, m_haut, 1e-3, 1.6 * m_haut + 5.0, 600)


def _estimer_comptages(O: np.ndarray, bruit_nom: str, effets: str) -> dict:
    """Une estimation sur un tableau (K, T, N). Renvoie un dictionnaire de grandeurs (NaN si indisponible)."""
    K = O.shape[0]
    temps = effets == "temps"
    sortie = {"R": np.nan, "c": np.nan, "m_bas": np.nan, "phi": np.nan, "dispersion": np.nan, "theta": [np.nan] * K,
              "r_croise": np.nan, "r_croise_inverse": np.nan, "configuration": ""}
    if K == 1:
        aj = est.ajuster_effets_temporels(O[0]) if temps else est.ajuster(O[0])
        sortie.update(R=aj.R, c=aj.c, m_bas=aj.m_bas, phi=aj.phi, theta=[np.nan], configuration="un canal (non corrigé de la sous-déclaration)")
        return sortie
    if K == 2:
        r_lk = mc.pente_croisee(O[1], O[0], temps)
        r_kl = mc.pente_croisee(O[0], O[1], temps)
        sortie.update(r_croise=r_lk, r_croise_inverse=r_kl)
        if temps or bruit_nom == "poisson":
            e = mc.estimer_multicanal(O, sortie=1, instrument=0, calibrage=0, effets_temporels=temps)
            sortie.update(R=e.R, c=e.c, m_bas=e.m_bas, phi=e.phi, dispersion=1.0 if not temps else np.nan,
                          configuration="deux canaux, bruit de Poisson" + (", effets temporels" if temps else ""))
        else:
            e = mc.estimer_deux_canaux_avec_dispersion(O, sortie=1, autre=0)
            sortie.update(R=e.R, c=e.c, m_bas=e.m_bas, phi=e.phi, dispersion=e.dispersion, configuration="deux canaux, dispersion estimée")
        sortie["theta"] = [mc.taux_detection(O[0], O[1]), mc.taux_detection(O[1], O[0])]
        return sortie
    e = mc.estimer_multicanal(O, sortie=0, instrument=K - 1, calibrage=K - 1, effets_temporels=temps)
    sortie.update(R=e.R, c=e.c, m_bas=e.m_bas, phi=e.phi, dispersion=np.nan, configuration=f"{K} canaux : sortie 0, instrument et calibrage {K - 1}")
    sortie["theta"] = [mc.taux_detection(O[k], O[K - 1] if k != K - 1 else O[0]) for k in range(K)]
    sortie["r_croise"] = mc.pente_croisee(O[0], O[K - 1], temps)
    sortie["r_croise_inverse"] = mc.pente_croisee(O[K - 1], O[0], temps)
    return sortie


def _bootstrap(O: np.ndarray, bruit_nom: str, effets: str, n_tirages: int, rng: np.random.Generator) -> dict:
    n = O.shape[2]
    valeurs = {"R": [], "c": [], "phi": []}
    for _ in range(n_tirages):
        try:
            e = _estimer_comptages(O[:, :, rng.integers(0, n, n)], bruit_nom, effets)
        except ValueError:
            continue
        valeurs["R"].append(e["R"])
        valeurs["c"].append(e["c"])
        valeurs["phi"].append(min(e["phi"], PLAFOND_PHI))
    return {k: (np.percentile(v, [5, 95]) if v else np.array([np.nan, np.nan])) for k, v in valeurs.items()}


def estimer_vulnerabilite(
    donnees: pd.DataFrame,
    sources=("urgences", "sos"),
    bruit: str = "binomiale_negative",
    observation: str = "canaux_amincis",
    pas: str = "semaine",
    voisinage: pd.DataFrame | None = None,
    effets_fixes: str = "jour_semaine",
    fenetre: int | None = None,
    pas_fenetre: int | None = None,
    bootstrap: int = 200,
    coupure_k: float | None = None,
    graine: int = 0,
) -> pd.DataFrame:
    """Estime R, c, s*, Φ, V* et les diagnostics pour chaque fenêtre. Voir le docstring du module.

    `effets_fixes` : « aucun » ; « jour_semaine » (retiré par l'agrégation hebdomadaire ; non implémenté au pas
    journalier) ; « temps » (retire la moyenne transversale à chaque instant : retire aussi une vague nationale).
    `coupure_k` : si donné, chaque unité est coupée au premier dépassement de k fois sa moyenne récente (règle de la
    note, calculée sur la première source puis appliquée à toutes) ; par défaut, aucune coupure (à fixer au
    pré-enregistrement). `voisinage` : réservé (le terme de voisinage est dans `reseau.py`, non branché ici).
    """
    sources = tuple(sources)
    if observation not in ("canaux_amincis", "capteurs_affines"):
        raise ValueError("observation doit valoir « canaux_amincis » ou « capteurs_affines ».")
    if effets_fixes not in ("aucun", "jour_semaine", "temps"):
        raise ValueError("effets_fixes doit valoir « aucun », « jour_semaine » ou « temps ».")
    if effets_fixes == "jour_semaine" and pas == "jour":
        raise NotImplementedError("Les effets « jour de semaine » au pas journalier ne sont pas implémentés ; "
                                  "utiliser pas='semaine' (l'agrégation hebdomadaire les retire) ou effets_fixes='temps'.")
    if voisinage is not None:
        raise NotImplementedError("Le terme de voisinage n'est pas branché sur cette interface (voir reseau.py).")
    if bruit not in ("poisson", "binomiale_negative", "gaussien"):
        raise ValueError("bruit doit valoir « poisson », « binomiale_negative » ou « gaussien ».")
    comptages = observation == "canaux_amincis"
    if comptages and bruit == "gaussien":
        raise ValueError("Le bruit gaussien s'applique à des signaux continus : utiliser observation='capteurs_affines'.")
    if not comptages and bruit != "gaussien":
        raise ValueError("Les capteurs affines (signaux continus) exigent bruit='gaussien'.")
    O, dates, unites = preparer_donnees(donnees, list(sources), pas, comptages)
    if comptages and coupure_k is not None:
        masque = np.isnan(est.couper_niveau_glissant(np.nan_to_num(O[0], nan=0.0), k=coupure_k, niveau_initial=float(np.nanmedian(O[0][:5]))))
        O = np.where(masque[None, :, :], np.nan, O)
    n_pas = O.shape[1]
    taille = fenetre or n_pas
    avance = pas_fenetre or (max(1, taille // 3) if fenetre else n_pas)
    rng = np.random.default_rng(graine)
    lignes = []
    for debut in range(0, n_pas - taille + 1, avance):
        W = O[:, debut:debut + taille, :]
        ligne = {"debut": dates[debut], "fin": dates[debut + taille - 1], "n_unites": len(unites), "n_pas": taille,
                 "n_unites_observees": int((~np.isnan(W[0])).any(axis=0).sum())}
        try:
            if comptages:
                e = _estimer_comptages(W, bruit, effets_fixes)
                R, c, m_bas, phi = e["R"], e["c"], e["m_bas"], e["phi"]
                ligne.update(R=R, c=c, s_etoile=(1 - R) / c if c > 0 else np.nan, phi=phi, m_bas=m_bas,
                             V_etoile=_v_etoile_1d(R, c, m_bas, e["dispersion"]), dispersion=e["dispersion"],
                             r_croise=e["r_croise"], r_croise_inverse=e["r_croise_inverse"], configuration=e["configuration"])
                for s, th in zip(sources, e["theta"]):
                    ligne[f"theta_{s}"] = th
                if bootstrap > 0:
                    iv = _bootstrap(W, bruit, effets_fixes, bootstrap, rng)
                    for g in ("R", "c", "phi"):
                        ligne[f"{g}_bas"], ligne[f"{g}_haut"] = iv[g]
                ecart = (e["r_croise_inverse"] - e["r_croise"]) if np.isfinite(e["r_croise"]) else None
                m_haut = m_bas + (1 - R) / c if c > 0 and R < 1 else None
                drapeaux = evaluer_garde_fous(
                    phi=phi, c=c, R=R, n_unites=len(unites),
                    theta=min(e["theta"]) if np.all(np.isfinite(e["theta"])) else None,
                    ecart_croise=ecart,
                    seuil_coupure=coupure_k * m_bas if coupure_k is not None else None, m_haut_estime=m_haut,
                )
            else:
                v = mc.estimer_vstar_deux_capteurs(W, 0, 1)
                ligne.update(V_etoile=v, configuration="deux capteurs affines")
                drapeaux = evaluer_garde_fous(n_unites=len(unites))
            ligne["drapeaux"] = ",".join(drapeaux.liste())
        except ValueError as erreur:
            ligne["drapeaux"] = "estimation_impossible"
            ligne["erreur"] = str(erreur)
        lignes.append(ligne)
    res = pd.DataFrame(lignes)
    res.attrs["avertissements"] = []
    if len(unites) < SEUIL_PEU_D_UNITES:
        message = f"Seulement {len(unites)} unités (< {SEUIL_PEU_D_UNITES}) : intervalles bootstrap trop optimistes."
        res.attrs["avertissements"].append(message)
        warnings.warn(message, stacklevel=2)
    return res
