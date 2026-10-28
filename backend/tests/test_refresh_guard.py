import json

import pytest

from scripts import refresh_results as rr


def h2(n_variables=5, n_units=96, errors=()):
    return {"result": {"nUnits": n_units}, "aggregate": {"nVariablesTested": n_variables, "errors": list(errors)}}


def h3(n_calculables=4, unavailable=()):
    return {"summary": {"nCalculable": n_calculables}, "unavailable": list(unavailable)}


def h5(n_departments=96, n_quarters=105):
    return {"nDepartments": n_departments, "nQuarters": n_quarters, "alpha": 5.9}


def test_premier_ecriture_et_resultat_identique_acceptes():
    assert rr._degradation("h2", None, h2()) is None
    assert rr._degradation("h2", h2(), h2()) is None


def test_couverture_plus_large_acceptee():
    assert rr._degradation("h5", h5(94, 105), h5(96, 106)) is None
    assert rr._degradation("h2", h2(3), h2(5)) is None


def test_cas_reel_du_28_octobre_2026_est_refuse():
    """H2 passe de 5 a 3 variables (connecteur Insee indisponible), H3 de 4 a 2 phenomenes, H5 de 96 a 94 departements."""
    erreurs = ["chomage : Connecteur INSEE (insee_taux_chomage_departements) indisponible : "]
    assert "indisponible" in rr._degradation("h2", h2(), h2(3, errors=erreurs))
    assert "variables testees" in rr._degradation("h2", h2(), h2(3))
    assert "phenomenes calculables" in rr._degradation("h3", h3(4), h3(2))
    assert "departements" in rr._degradation("h5", h5(96), h5(94))
    assert "trimestres" in rr._degradation("h5", h5(96, 105), h5(96, 100))


def test_nouvelle_mention_indisponible_refusee_mais_pas_une_mention_deja_presente():
    deja = h3(2, [{"label": "x", "reason": "Pas assez de points"}, {"label": "y", "reason": "Connecteur INSEE indisponible : "}])
    assert rr._degradation("h3", deja, deja) is None
    plus = h3(2, [{"label": "y", "reason": "Connecteur INSEE indisponible : "}, {"label": "z", "reason": "Connecteur INSEE indisponible : "}])
    assert "indisponible" in rr._degradation("h3", deja, plus)


def test_hypotheses_sans_controle_specifique_ne_sont_pas_bloquees_a_tort():
    assert rr._degradation("fusion", {"nShots": 20}, {"nShots": 18}) is None


def test_ecriture_refusee_ne_touche_pas_le_fichier(tmp_path, monkeypatch):
    monkeypatch.setattr(rr, "RESULTS_DIR", tmp_path)
    monkeypatch.delenv("REFRESH_FORCE", raising=False)
    (tmp_path / "h5.json").write_text(json.dumps(h5(96)), encoding="utf-8")
    avant = (tmp_path / "h5.json").read_text(encoding="utf-8")
    with pytest.raises(rr.ResultatDegrade, match="departements"):
        rr._write_if_ok("h5", h5(94))
    assert (tmp_path / "h5.json").read_text(encoding="utf-8") == avant


def test_ecriture_acceptee_et_premiere_ecriture(tmp_path, monkeypatch):
    monkeypatch.setattr(rr, "RESULTS_DIR", tmp_path)
    monkeypatch.delenv("REFRESH_FORCE", raising=False)
    rr._write_if_ok("h5", h5(96))  # fichier absent
    rr._write_if_ok("h5", h5(96, 106))  # plus de trimestres
    assert json.loads((tmp_path / "h5.json").read_text(encoding="utf-8"))["nQuarters"] == 106


def test_force_permet_d_accepter_une_baisse_legitime(tmp_path, monkeypatch):
    monkeypatch.setattr(rr, "RESULTS_DIR", tmp_path)
    (tmp_path / "h5.json").write_text(json.dumps(h5(96)), encoding="utf-8")
    monkeypatch.setenv("REFRESH_FORCE", "1")
    rr._write_if_ok("h5", h5(94))
    assert json.loads((tmp_path / "h5.json").read_text(encoding="utf-8"))["nDepartments"] == 94


def test_fichier_existant_illisible_n_empeche_pas_l_ecriture(tmp_path, monkeypatch):
    monkeypatch.setattr(rr, "RESULTS_DIR", tmp_path)
    monkeypatch.delenv("REFRESH_FORCE", raising=False)
    (tmp_path / "h5.json").write_text("{pas du json", encoding="utf-8")
    rr._write_if_ok("h5", h5(96))
    assert json.loads((tmp_path / "h5.json").read_text(encoding="utf-8"))["nDepartments"] == 96
