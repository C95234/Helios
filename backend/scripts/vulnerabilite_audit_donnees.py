"""Audit DESCRIPTIF des données brutes du banc « épidémies » (module vulnérabilité, phase 2).

Usage (depuis backend/) :  python -m scripts.vulnerabilite_audit_donnees > ../docs/vulnerabilite/fiche_donnees_auto.md

Règle d'intégrité du pré-enregistrement : ce script ne calcule NI R, NI c, NI Φ, NI AUC, NI date de démarrage de vague.
Il décrit : couverture, valeurs manquantes, incohérences, ruptures, codage, décalage temporel entre les deux canaux
(corrélation croisée des comptes nationaux lissés) et chevauchement avec la référence de R.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RACINE = Path(__file__).resolve().parents[2] / "data" / "vulnerabilite"
BRUT = RACINE / "raw"
ADJ = Path(__file__).resolve().parents[1] / "app" / "data" / "departements_adjacency.json"
SURSAUD = "sursaud-covid-quot-dep-2025-01-01-18h00.csv"
REFERENCE = "table-indicateurs-open-data-dep-serie.csv"


def p(txt: str = "") -> None:
    print(txt)


def tableau(df: pd.DataFrame, index: bool = True) -> None:
    d = df.reset_index() if index else df
    p("| " + " | ".join(map(str, d.columns)) + " |")
    p("|" + "---|" * len(d.columns))
    for ligne in d.itertuples(index=False):
        p("| " + " | ".join(str(v) for v in ligne) + " |")
    p()


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    manifeste = {f["nom"]: f for f in json.loads((RACINE / "manifeste.json").read_text(encoding="utf-8"))["fichiers"]}
    s = pd.read_csv(BRUT / SURSAUD, sep=";", dtype={"dep": str, "sursaud_cl_age_corona": str}, parse_dates=["date_de_passage"])
    t = s[s.sursaud_cl_age_corona == "0"].copy()
    deps = sorted(t.dep.unique())
    metro = [d for d in deps if not d.startswith("97")]
    dom = [d for d in deps if d.startswith("97")]
    jours = pd.date_range(t.date_de_passage.min(), t.date_de_passage.max(), freq="D")

    p("# Fiche de données : urgences, SOS Médecins et référence de R (généré par `vulnerabilite_audit_donnees.py`)\n")
    p("## 1. Identification\n")
    lignes = []
    for nom in (SURSAUD, REFERENCE):
        m = manifeste[nom]
        lignes.append((nom, m["titre_du_jeu"], m["licence"], m["telecharge_le"], f"{m['taille_octets']:,}".replace(",", " "), m["sha256"][:16] + "…"))
    tableau(pd.DataFrame(lignes, columns=["fichier", "jeu", "licence", "téléchargé le (UTC)", "octets", "sha256 (début)"]), index=False)

    p("## 2. Urgences et SOS Médecins : structure\n")
    p(f"- Lignes : {len(s):,}".replace(",", " ") + f" ; départements : {len(deps)} ({len(metro)} de métropole, {len(dom)} d'outre-mer : {', '.join(dom)}).")
    p(f"- Période (fichier entier) : **{s.date_de_passage.min().date()} → {s.date_de_passage.max().date()}** ({s.date_de_passage.nunique()} jours distincts, "
      f"{len(jours)} attendus : {'aucun jour manquant' if s.date_de_passage.nunique() == len(jours) else 'JOURS MANQUANTS'}).")
    p(f"- Classes d'âge présentes : {', '.join(sorted(s.sursaud_cl_age_corona.unique()))} (nouveau codage 0 à 6 ; le changement du 4 novembre 2021 est antérieur à la période du fichier : "
      "aucun mélange d'anciens et de nouveaux codes). Analyse sur la classe 0 (tous âges).")
    p(f"- Lignes « tous âges » : {len(t):,}".replace(",", " ") + f" = {len(deps)} départements × {len(jours)} jours ; doublons (département, date) : {int(t.duplicated(['dep', 'date_de_passage']).sum())}.")
    p("- Pas de temps : quotidien. Unités : comptes de personnes (passages ou actes). Aucune variable « nombre d'établissements participants » dans le fichier.\n")

    p("## 3. Valeurs manquantes\n")
    nan = t[["nbre_pass_corona", "nbre_pass_tot", "nbre_hospit_corona", "nbre_acte_corona", "nbre_acte_tot"]].isna().mean().mul(100).round(1)
    tableau(pd.DataFrame({"champ": nan.index, "% de valeurs absentes (tous âges)": nan.values}), index=False)

    sos_ok = t.dropna(subset=["nbre_acte_tot"])
    couv = sos_ok.groupby("dep").date_de_passage.agg(["min", "max", "count"])
    pleine = couv[couv["count"] == len(jours)].index.tolist()
    partielle = couv[couv["count"] < len(jours)]
    p("## 4. Couverture du canal SOS Médecins\n")
    p(f"- Départements ayant des données SOS Médecins (au moins un jour) : **{len(couv)} sur {len(deps)}** ({len([d for d in couv.index if not d.startswith('97')])} de métropole).")
    p(f"- Dont couverture complète sur les {len(jours)} jours : **{len(pleine)}** ; couverture partielle : {len(partielle)}.")
    p(f"- Les deux canaux (urgences et SOS) sont donc disponibles dans **{len(couv)} départements au plus** ({len(pleine)} à couverture complète), "
      f"contre ~96 visés par le cahier ; le seuil de 30 unités du bootstrap est {'respecté' if len(pleine) >= 30 else 'NON respecté'} avec la couverture complète.")
    p(f"- Départements avec les deux canaux, couverture complète : {', '.join(sorted(pleine))}.\n")
    if len(partielle):
        p("Couverture partielle :\n")
        pp = partielle.copy()
        pp["min"] = pp["min"].dt.date
        pp["max"] = pp["max"].dt.date
        tableau(pp.rename(columns={"min": "premier jour", "max": "dernier jour", "count": "jours renseignés"}))
    sans = sorted(set(deps) - set(couv.index))
    p(f"- Sans aucun SOS Médecins ({len(sans)}) : {', '.join(sans)}.\n")

    # Comptes faibles : risque n°3 du plan
    deux = t[t.dep.isin(pleine)].copy()
    deux["semaine"] = deux.date_de_passage.dt.to_period("W").dt.start_time
    sem = deux.groupby(["dep", "semaine"])[["nbre_pass_corona", "nbre_acte_corona", "nbre_pass_tot", "nbre_acte_tot"]].sum(min_count=7)
    p("## 5. Petits effectifs (départements avec les deux canaux, couverture complète)\n")
    q = [0.1, 0.25, 0.5, 0.75, 0.9]
    rows = []
    for c in ("nbre_pass_corona", "nbre_acte_corona", "nbre_pass_tot", "nbre_acte_tot"):
        v = sem[c].dropna()
        rows.append((c, len(v), f"{(v == 0).mean():.1%}", *[f"{v.quantile(x):.0f}" for x in q], int(v.max())))
    tableau(pd.DataFrame(rows, columns=["compte hebdomadaire", "n (dép.-semaines)", "% de zéros", "D1", "Q1", "médiane", "Q3", "D9", "max"]), index=False)
    jr = deux[["nbre_pass_corona", "nbre_acte_corona"]]
    vc = {c: jr[c].value_counts().reindex(range(0, 7), fill_value=0) for c in jr}
    p("Répartition des valeurs quotidiennes basses (un déficit anormal des valeurs 1 à 4 trahirait un masquage des petits effectifs) :\n")
    tableau(pd.DataFrame(vc).rename_axis("valeur quotidienne"))

    p("## 6. Incohérences et anomalies\n")
    p(f"- Lignes « tous âges » où les comptes COVID dépassent le total : urgences {int((t.nbre_pass_corona > t.nbre_pass_tot).sum())}, SOS {int((t.nbre_acte_corona > t.nbre_acte_tot).sum())}.")
    ok = t.dropna(subset=["nbre_pass_corona_h", "nbre_pass_corona_f"])
    p(f"- Somme hommes + femmes ≠ total (urgences COVID) : {int(((ok.nbre_pass_corona_h + ok.nbre_pass_corona_f) != ok.nbre_pass_corona).sum())} lignes sur {len(ok)} renseignées.")
    ok2 = t.dropna(subset=["nbre_pass_tot_h", "nbre_pass_tot_f"])
    p(f"- Somme hommes + femmes ≠ total (urgences totales) : {int(((ok2.nbre_pass_tot_h + ok2.nbre_pass_tot_f) != ok2.nbre_pass_tot).sum())} lignes sur {len(ok2)}.")
    parages = s[s.sursaud_cl_age_corona != "0"].groupby(["dep", "date_de_passage"]).nbre_pass_corona.sum(min_count=1).rename("somme_classes")
    cmp_ = t.set_index(["dep", "date_de_passage"]).nbre_pass_corona.to_frame().join(parages).dropna()
    p(f"- Somme des classes d'âge 1 à 6 ≠ classe 0 (urgences COVID) : {int((cmp_.nbre_pass_corona != cmp_.somme_classes).sum())} lignes sur {len(cmp_)} "
      "(le fichier signale des âges non identifiés).")
    neg = int((t.select_dtypes('number') < 0).sum().sum())
    p(f"- Valeurs négatives : {neg}.\n")

    p("## 7. Ruptures de série\n")
    p("Règle descriptive : pour chaque département, médiane mensuelle du total (urgences : `nbre_pass_tot` ; SOS : `nbre_acte_tot`) ; "
      "rupture si la médiane du mois est > 2 fois ou < 0,5 fois celle du mois précédent (mois précédent ≥ 10).\n")
    for nom, col, dep_liste in (("urgences", "nbre_pass_tot", deps), ("SOS Médecins", "nbre_acte_tot", list(couv.index))):
        x = t[t.dep.isin(dep_liste)].copy()
        x["mois"] = x.date_de_passage.dt.to_period("M")
        med = x.groupby(["dep", "mois"])[col].median().unstack("dep")
        rap = med / med.shift(1)
        mask = ((rap > 2) | (rap < 0.5)) & (med.shift(1) >= 10)
        evts = [(d, str(m), int(med.shift(1).loc[m, d]), int(med.loc[m, d])) for m in mask.index for d in mask.columns if bool(mask.loc[m, d])]
        p(f"- {nom} : {len(evts)} rupture(s) mensuelle(s) sur {med.shape[1]} départements × {med.shape[0] - 1} transitions.\n")
        if evts:
            tableau(pd.DataFrame(evts[:20], columns=["département", "mois", "médiane mois précédent", "médiane du mois"]), index=False)
        longs = []
        for d, g in x.groupby("dep"):
            v = g.sort_values("date_de_passage")[col]
            bad = (v.isna() | (v == 0)).to_numpy()
            run = 0
            for flag in bad:
                run = run + 1 if flag else 0
                if run == 7:
                    longs.append(d)
                    break
        p(f"- {nom} : départements avec au moins 7 jours consécutifs sans donnée ou à zéro (total) : {len(set(longs))}" + (f" ({', '.join(sorted(set(longs))[:15])})" if longs else "") + ".\n")

    p("## 8. Décalage temporel entre les deux canaux (corrélation croisée)\n")
    nat = deux.groupby("date_de_passage")[["nbre_pass_corona", "nbre_acte_corona"]].sum()
    lis = nat.rolling(7, center=True).mean().dropna()
    res = []
    for k in range(-21, 22):
        a = lis["nbre_acte_corona"]
        b = lis["nbre_pass_corona"].shift(-k)
        res.append((k, a.corr(b)))
    best = max(res, key=lambda z: z[1])
    zero = dict(res)[0]
    p(f"Comptes COVID nationaux sur les {len(pleine)} départements à couverture complète, moyenne mobile centrée sur 7 jours. "
      f"Corrélation à décalage 0 : {zero:.3f}. Meilleur décalage : **{best[0]:+d} jour(s)** (corrélation {best[1]:.3f}) ; "
      "un décalage positif signifie que SOS Médecins précède les urgences.\n")
    p("Évolution mensuelle des comptes COVID (somme sur ces départements), à titre descriptif :\n")
    mens = deux.assign(mois=deux.date_de_passage.dt.to_period("M").astype(str)).groupby("mois")[["nbre_pass_corona", "nbre_acte_corona"]].sum().astype(int)
    tableau(mens.rename(columns={"nbre_pass_corona": "urgences COVID", "nbre_acte_corona": "actes SOS COVID"}))

    p("## 9. Référence de R (indicateurs de suivi, ministère de la Santé)\n")
    r = pd.read_csv(BRUT / REFERENCE, dtype={"departement": str}, parse_dates=["extract_date"])
    rr = r.dropna(subset=["R"])
    p(f"- Période du fichier : {r.extract_date.min().date()} → {r.extract_date.max().date()} ; {r.departement.nunique()} départements ; "
      f"R renseigné pour {r.R.notna().mean():.1%} des lignes, du **{rr.extract_date.min().date()} au {rr.extract_date.max().date()}**.")
    p()
    par_an = r.assign(annee=r.extract_date.dt.year).groupby("annee").apply(lambda g: pd.Series({"lignes": len(g), "% R renseigné": round(100 * g.R.notna().mean(), 1)}), include_groups=False)
    par_an["lignes"] = par_an["lignes"].astype(int)
    tableau(par_an)
    chev = (rr.extract_date.max() >= s.date_de_passage.min())
    p(f"- **Chevauchement avec la période urgences/SOS ({s.date_de_passage.min().date()} → {s.date_de_passage.max().date()}) : {'OUI' if chev else 'AUCUN'}.** "
      f"Dernier R publié : {rr.extract_date.max().date()} ; premier jour des urgences/SOS : {s.date_de_passage.min().date()} "
      f"(écart de {(s.date_de_passage.min() - rr.extract_date.max()).days} jours).")
    p("- Le R du fichier est celui des indicateurs de suivi, calculé à partir des tests (SI-DEP) : indépendant des deux canaux, mais sans recouvrement ici.\n")

    p("## 10. Codes de départements et matrice de voisinage\n")
    adj = json.loads(ADJ.read_text(encoding="utf-8"))
    codes_adj = set(adj["adjacency"].keys())
    p(f"- Matrice de voisinage du dépôt : {adj['n_departments']} départements ({adj.get('source', '?')}).")
    p(f"- Départements du fichier de métropole absents de la matrice : {sorted(set(metro) - codes_adj) or 'aucun'} ; "
      f"départements de la matrice absents du fichier : {sorted(codes_adj - set(deps)) or 'aucun'}.")
    p(f"- Parmi les {len(couv)} départements avec SOS Médecins, ceux de la matrice : {len([d for d in couv.index if d in codes_adj])}.")


if __name__ == "__main__":
    main()
