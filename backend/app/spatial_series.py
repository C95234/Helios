"""Serie spatiale partagee entre H2 et H3 -- indice de Moran par periode sur
le reseau reel des departements, calcule une seule fois et reutilise, plutot
que duplique dans chaque routeur qui en a besoin.

Generalise (H2, "pousser au maximum de series reelles") : `get_department_wide`
et `compute_network_moran_series` acceptent n'importe quel connecteur au
format departemental commun (`connectors/insee_departments.py`), pas
seulement le chomage -- `get_department_unemployment_wide` et
`get_real_network_moran_series` restent des raccourcis vers le chomage,
inchanges en sortie, pour ne rien casser pour H2/H3/H4/H5 existants.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .connectors.insee_departments import InseeDepartmentSeriesConnector, UNEMPLOYMENT_CONNECTOR
from .geo import department_weight_matrix, load_department_network, regular_grid_weight_matrix
from .stats.moran import morans_i


class SpatialDataUnavailable(Exception):
    pass


async def get_department_wide(
    connector: InseeDepartmentSeriesConnector,
    start_period: str | None = None,
    rolling_12: bool = False,
    min_departments: int = 90,
    min_periods: int = 8,
) -> pd.DataFrame:
    """DataFrame periode x departement (colonnes = codes departement), sans trous,
    pour n'importe quel connecteur departemental commun."""
    try:
        raw = await connector.fetch(start_period=start_period)
        df = connector.normalize(raw)
    except Exception as exc:
        raise SpatialDataUnavailable(f"Connecteur INSEE ({connector.name}) indisponible : {exc}") from exc

    if df.empty:
        raise SpatialDataUnavailable(f"Aucune donnée départementale reçue de l'Insee ({connector.name}).")

    network = load_department_network()
    metro_codes = set(network["adjacency"].keys())
    df = df[df["territoire"].isin(metro_codes)]

    wide = df.pivot_table(index="date", columns="territoire", values="valeur")
    if rolling_12:
        wide = wide.rolling(12).sum()
    wide = wide.dropna(axis=0, how="any")
    if wide.shape[1] < min_departments or wide.shape[0] < min_periods:
        raise SpatialDataUnavailable(
            f"Couverture insuffisante pour {connector.name} "
            f"({wide.shape[0]} périodes, {wide.shape[1]} départements)."
        )
    return wide


async def get_department_unemployment_wide() -> pd.DataFrame:
    return await get_department_wide(UNEMPLOYMENT_CONNECTOR, start_period="2000-Q1")


def compute_network_moran_series(wide: pd.DataFrame) -> dict:
    """I_t (indice de Moran sur le reseau reel) pour chaque periode disponible
    d'un DataFrame deja construit, plus tout ce qu'il faut pour recalculer une
    grille de controle ou une coupe."""
    network = load_department_network()
    codes = list(wide.columns)
    w_real = department_weight_matrix(codes, network["adjacency"])
    w_grid, grid_shape = regular_grid_weight_matrix(len(codes))

    dates = wide.index  # DatetimeIndex, un par periode
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


async def get_real_network_moran_series() -> dict:
    wide = await get_department_unemployment_wide()
    return compute_network_moran_series(wide)


async def get_unemployment_shock_sizes() -> dict:
    """Amplitude des chocs trimestriels de chomage departemental -- |delta|
    d'un trimestre au suivant, pour chaque departement -- source reelle pour
    H5 (§5.9.3, "tailles d'evenements") : GDELT (rate limite de facon
    persistante, cf. connecteur Google Trends/tests) et Reddit/SNAP (aucun
    connecteur construit) restent indisponibles ; cette serie, deja connectee
    pour H2/H4, est l'alternative explicitement citee par le cahier des
    charges."""
    wide = await get_department_unemployment_wide()
    shocks = wide.diff().abs().to_numpy().flatten()
    shocks = shocks[~np.isnan(shocks)]
    shocks = shocks[shocks > 0]
    return {
        "shocks": shocks,
        "n_departments": wide.shape[1],
        "n_quarters": wide.shape[0],
        "period_start": wide.index[0].strftime("%Y-%m-%d"),
        "period_end": wide.index[-1].strftime("%Y-%m-%d"),
    }
