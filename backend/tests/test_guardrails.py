import pandas as pd
import pytest

from app.guardrails import NominalDataRejected, validate_no_nominal_columns


def test_rejects_email_column():
    df = pd.DataFrame({"date": ["2024-01-01"], "email": ["a@example.com"], "valeur": [1.0]})
    with pytest.raises(NominalDataRejected):
        validate_no_nominal_columns(df)


def test_rejects_column_named_nom_prenom():
    df = pd.DataFrame({"nom": ["Dupont"], "prenom": ["Jean"], "valeur": [1.0]})
    with pytest.raises(NominalDataRejected):
        validate_no_nominal_columns(df)


def test_rejects_free_text_full_names_even_without_matching_header():
    first_names = ["Jean", "Marie", "Paul", "Claire", "Ahmed", "Julie", "Marc", "Sophie", "Louis", "Nadia"]
    last_names = ["Dupont", "Martin", "Bernard", "Petit", "Moreau", "Girard"]
    full_names = [f"{f} {l}" for f in first_names for l in last_names]  # 60 combinaisons uniques
    df = pd.DataFrame({"identifiant": full_names, "valeur": range(len(full_names))})
    with pytest.raises(NominalDataRejected):
        validate_no_nominal_columns(df)


def test_accepts_aggregated_numeric_data():
    df = pd.DataFrame(
        {
            "territoire": ["75", "75", "13"],
            "date": ["2024-01-01", "2024-02-01", "2024-01-01"],
            "indicateur": ["chomage", "chomage", "chomage"],
            "valeur": [7.1, 7.3, 8.0],
        }
    )
    validate_no_nominal_columns(df)  # ne doit pas lever
