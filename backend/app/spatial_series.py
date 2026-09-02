"""Serie spatiale partagee entre H2 et H3 -- indice de Moran par trimestre sur
le reseau reel des departements, calcule une seule fois et reutilise, plutot
que duplique dans chaque routeur qui en a besoin.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .connectors.insee_departments import InseeDepartmentUnemploymentConnector
from .geo import department_weight_matrix, load_department_network, regular_grid_weight_matrix
from .stats.moran import morans_i

_connector = InseeDepartmentUnemploymentConnector()


class SpatialDataUnavailable(Exception):
    pass


async def get_department_unemployment_wide() -> pd.DataFrame:
    """DataFrame trimestre x departement (colonnes = codes departement), sans trous."""
    try:
        raw = await _connector.fetch(start_period="2000-Q1")
        df = _connector.normalize(raw)
    except Exception as exc:
        raise SpatialDataUnavailable(f"Connecteur INSEE (départements) indisponible : {exc}") from exc

    if df.empty:
        raise SpatialDataUnavailable("Aucune donnée départementale reçue de l'Insee.")

    network = load_department_network()
    metro_codes = set(network["adjacency"].keys())
    df = df[df["territoire"].isin(metro_codes)]

    wide = df.pivot_table(index="date", columns="territoire", values="valeur")
    wide = wide.dropna(axis=0, how="any")
    if wide.shape[1] < 90 or wide.shape[0] < 8:
        raise SpatialDataUnavailable(
            f"Couverture insuffisante ({wide.shape[0]} trimestres, {wide.shape[1]} départements)."
        )
    return wide


async def get_real_network_moran_series() -> dict:
    """I_t (indice de Moran sur le reseau reel) pour chaque trimestre disponible,
    plus tout ce qu'il faut pour recalculer une grille de controle ou une coupe."""
    wide = await get_department_unemployment_wide()
    network = load_department_network()
    codes = list(wide.columns)
    w_real = department_weight_matrix(codes, network["adjacency"])
    w_grid, grid_shape = regular_grid_weight_matrix(len(codes))

    dates = wide.index  # DatetimeIndex, un par trimestre
    i_real = np.array([morans_i(wide.iloc[t].to_numpy(), w_real) for t in range(len(wide))])
    i_grid = np.array([morans_i(wide.iloc[t].to_numpy(), w_grid) for t in range(len(wide))])

    return {
        "wide": wide,
        "dates": dates,
        "codes": codes,
        "w_real": w_real,
        "w_grid": w_grid,
        "grid_shape": grid_shape,
        "i_real": i_real,
        "i_grid": i_grid,
        "network_names": network["names"],
    }
