from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from app.vulnerabilite import calendrier as cal

RAW = Path(__file__).resolve().parents[3] / "data" / "vulnerabilite" / "raw"
FERIES = RAW / "jours_feries_metropole.csv"
SCOLAIRE = RAW / "fr-en-calendrier-scolaire.csv"
donnees_presentes = pytest.mark.skipif(not (FERIES.exists() and SCOLAIRE.exists()), reason="données brutes absentes (hors git)")


def test_la_table_departement_zone_couvre_la_metropole_exactement_une_fois():
    tous = [d for deps in cal.ACADEMIES.values() for d in deps]
    assert sorted(tous) == sorted(cal.departements_metropole()) and len(tous) == len(set(tous)) == 96
    assert set(cal.ZONE_DU_DEPARTEMENT.values()) == {"Zone A", "Zone B", "Zone C", "Corse"}
    assert cal.ZONE_DU_DEPARTEMENT["75"] == "Zone C" and cal.ZONE_DU_DEPARTEMENT["33"] == "Zone A" and cal.ZONE_DU_DEPARTEMENT["59"] == "Zone B"


@donnees_presentes
def test_academies_et_zones_conformes_au_fichier_officiel():
    d = pd.read_csv(SCOLAIRE, sep=";", encoding="utf-8-sig")
    officiel = d[d.Zones.isin(["Zone A", "Zone B", "Zone C", "Corse"])].groupby("Académies").Zones.agg(lambda s: set(s))
    for academie, zones in officiel.items():
        if academie in ("Caen", "Rouen"):  # anciennes académies, fusionnées dans « Normandie »
            academie = "Normandie"
        assert academie in cal.ZONE_DE_L_ACADEMIE, academie
        assert zones == {cal.ZONE_DE_L_ACADEMIE[academie]}, (academie, zones)
    assert {a for a in cal.ZONE_DE_L_ACADEMIE} <= set(officiel.index) | {"Normandie"}


@donnees_presentes
def test_controles_connus_noel_toussaint_ete_et_feries():
    semaines = pd.DatetimeIndex(pd.to_datetime(["2023-10-23", "2023-11-06", "2023-12-25", "2024-01-01", "2024-01-08", "2024-07-08", "2024-09-02", "2024-05-06", "2024-05-13"]))
    C = cal.controles_hebdomadaires(semaines, ["75", "33", "59", "2A", "971"], cal.charger_jours_feries(FERIES), cal.charger_vacances(SCOLAIRE))
    vac, fer = C[:, :, 1], C[:, 0, 0]
    assert np.allclose(vac[:2, :4], [[1, 1, 1, 1], [0, 0, 0, 0]])  # Toussaint 2023 : du 21/10 au 6/11 (reprise)
    assert np.allclose(vac[2:5, :4], [[1] * 4, [1] * 4, [0] * 4])  # Noël 2023 : du 23/12 au 8/01
    assert np.allclose(vac[5, :4], 1)  # été 2024 : du 6 juillet à la rentrée
    assert np.allclose(vac[6, :3], 0) and vac[6, 3] == pytest.approx(3 / 7)  # rentrée du 2 septembre ; en Corse le 5 (fichier officiel)
    assert np.all(np.isnan(vac[:, 4]))  # outre-mer non géré
    # fériés : 1er janvier 2024 (lundi), 8 mai 2024 (mercredi, semaine du 6 mai), semaine du 13 mai : Ascension le jeudi 9 mai, Pentecôte le lundi 20
    assert fer.tolist() == [0, 1, 1, 1, 0, 1, 0, 1, 0]


@donnees_presentes
def test_le_nombre_de_jours_feries_metropole_est_celui_de_la_loi():
    f = cal.charger_jours_feries(FERIES)
    for annee in (2023, 2024):
        assert len([d for d in f if d.year == annee]) == 11  # 1er janv., lundi de Pâques, 1er mai, 8 mai, Ascension, lundi de Pentecôte, 14 juil., 15 août, Toussaint, 11 nov., Noël
