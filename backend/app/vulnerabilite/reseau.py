"""Unités couplées en réseau (note, section 5, « Réseau : le couplage freine l'embrasement »).

L'exposition d'une unité mélange son activité et celle de ses voisins : x_i = (1 − w)·y_i + w·(W̃y)_i, avec une
contagion μ + A·x_i + c·x_i². Le mode uniforme a les mêmes R, s* et Φ pour tout w ; seul le couplage change la
barrière collective : un foyer doit entraîner ses voisins (nucléation).

Conséquences établies dans la note [vérifié numériquement ; borne non démontrée] :
- le Φ par unité est une BORNE PRUDENTE du temps d'attente (la barrière réelle est plus haute) : l'indicateur pèche
  par excès d'alerte, jamais par excès de confiance ;
- on ne convertit pas Φ en temps d'attente sans étalonnage par simulation sur le réseau réel (`etalonner_temps`) ;
- le classement des sociétés reste correct avec un terme de voisinage (AUC 0,85 à w = 0,3).
La barrière collective V* du réseau (points-selles, chemins de moindre action) est en phase 1b.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .estimation import _phi_ou_cas_limite
from .modele import params_depuis_inflammabilite


def matrice_grille(cote: int) -> np.ndarray:
    """Matrice de voisinage W̃ d'une grille torique cote × cote (4 voisins), normalisée par ligne."""
    N = cote * cote
    W = np.zeros((N, N))
    for i in range(cote):
        for j in range(cote):
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                W[i * cote + j, ((i + di) % cote) * cote + (j + dj) % cote] = 1.0
    return W / W.sum(axis=1, keepdims=True)


def normaliser_par_ligne(W: np.ndarray) -> np.ndarray:
    """Normalise par ligne une matrice d'adjacence ; une ligne nulle (unité isolée) lève une erreur."""
    W = np.asarray(W, dtype=float)
    sommes = W.sum(axis=1, keepdims=True)
    if np.any(sommes == 0):
        raise ValueError("Une unité n'a aucun voisin : la matrice ne peut pas être normalisée par ligne.")
    return W / sommes


def simuler_reseau(
    R: float,
    c: float,
    m_bas: float,
    w: float,
    W: np.ndarray,
    n_pas_max: int,
    rng: np.random.Generator,
    n_repetitions: int = 1,
    conserver_historique: bool = False,
    n_pas_observes: int | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    """Simule `n_repetitions` sociétés en réseau (script `t10`).

    Une société s'embrase quand une unité atteint 2·m₊ + 5. Renvoie (T, taille_du_foyer, historique) :
    T = temps du premier embrasement (NaN si censuré à `n_pas_max`) ; taille_du_foyer = nombre d'unités au-dessus
    de m₊ à ce moment ; historique de forme (n_pas_observes, n_repetitions, N), NaN après l'embrasement
    (None si `conserver_historique` est faux). Si l'historique est demandé, la simulation s'arrête après
    `n_pas_observes` pas.
    """
    A, mu, _, m_haut = params_depuis_inflammabilite(R, c, m_bas)
    N = W.shape[0]
    y = np.full((n_repetitions, N), float(round(m_bas)))
    T = np.full(n_repetitions, np.nan)
    taille = np.full(n_repetitions, np.nan)
    vivant = np.ones(n_repetitions, bool)
    historique = [] if conserver_historique else None
    for t in range(1, n_pas_max + 1):
        wy = y @ W.T
        x = (1 - w) * y + w * wy
        lam = np.clip(mu + (1 - w) * A * y + w * A * wy + c * x * x, 0, 1e6)
        y = np.where(vivant[:, None], rng.poisson(lam).astype(float), y)
        if conserver_historique and t <= (n_pas_observes or n_pas_max):
            historique.append(np.where(vivant[:, None], y, np.nan))
        chaud = y >= m_haut
        touche = vivant & (y >= 2 * m_haut + 5).any(axis=1)
        T[touche] = t
        taille[touche] = chaud[touche].sum(axis=1)
        vivant &= ~touche
        if not vivant.any() or (conserver_historique and t >= (n_pas_observes or n_pas_max)):
            break
    return T, taille, (np.array(historique) if conserver_historique else None)


@dataclass(frozen=True)
class AjustementReseau:
    mu: float
    a_propre: float  # coefficient de y_i
    a_voisins: float  # coefficient de (W̃y)_i
    c_yy: float
    c_yw: float
    c_ww: float
    R: float
    m_bas: float
    phi: float  # Φ du mode uniforme

    @property
    def c(self) -> float:
        """Courbure du mode uniforme : c_yy + c_yw + c_ww."""
        return self.c_yy + self.c_yw + self.c_ww

    @property
    def w_estime(self) -> float:
        """EXPÉRIMENTAL, NON FIABLE EN L'ÉTAT. Couplage ŵ = √c_ww / (√c_yy + √c_ww), car c_yy = c(1−w)² et c_ww = c·w² ;
        NaN si l'un des deux est ≤ 0. La note propose cette estimation sans la tester. Testée ici (grille 10×10,
        20 sociétés × 200 pas, R = 0,6) : ŵ médian = 0,38 pour w = 0, 0,41–0,59 pour w = 0,3, 0,55–0,59 pour w = 0,6 :
        il ne suit pas le couplage vrai. Ne pas l'utiliser pour étalonner un temps d'attente avant de l'avoir amélioré."""
        if self.c_yy > 0 and self.c_ww > 0:
            return float(np.sqrt(self.c_ww) / (np.sqrt(self.c_yy) + np.sqrt(self.c_ww)))
        return float("nan")


def ajuster_reseau(H: np.ndarray, W: np.ndarray) -> AjustementReseau:
    """Régression quadratique complète en (y_i, (W̃y)_i) regroupée sur toutes les sociétés et tous les pas (script `t10`).

    `H` de forme (n_pas, n_repetitions, N) comme renvoyé par `simuler_reseau` ; chaque société est utilisée jusqu'à
    son premier NaN. Moindres carrés ordinaires (le script de la note calcule un poids mais ne l'utilise pas).
    Φ est celui du mode uniforme : c = c_yy + c_yw + c_ww, R = a + a' + 2·c·m̂₋.
    """
    lignes, cibles = [], []
    for r in range(H.shape[1]):
        X = H[:, r, :]
        for t in range(X.shape[0] - 1):
            yt, yn = X[t], X[t + 1]
            if np.isnan(yt).any() or np.isnan(yn).any():
                break
            wy = W @ yt
            lignes.append(np.stack([np.ones(len(yt)), yt, wy, yt * yt, yt * wy, wy * wy], axis=1))
            cibles.append(yn)
    if not lignes:
        raise ValueError("Aucune paire (y_t, y_{t+1}) complète : ajustement impossible.")
    b = np.linalg.lstsq(np.vstack(lignes), np.concatenate(cibles), rcond=None)[0]
    mu, a1, a2, c1, c2, c3 = (float(v) for v in b)
    m_bas = float(np.nanmean(H))
    c_total = c1 + c2 + c3
    R = a1 + a2 + 2.0 * c_total * m_bas
    return AjustementReseau(mu, a1, a2, c1, c2, c3, R, m_bas, _phi_ou_cas_limite(R, c_total, m_bas))


def etalonner_temps(R: float, c: float, m_bas: float, w: float, W: np.ndarray, n_repetitions: int = 100, n_pas_max: int = 60_000, seed: int = 0) -> dict:
    """Étalonnage Φ → temps d'attente par simulation sur le réseau donné (à utiliser sur la matrice W du réseau réel).

    Renvoie le temps moyen du premier embrasement (parmi les sociétés non censurées), la part censurée et la taille
    médiane du foyer. Si la censure est forte, T_moyen est un minorant.
    """
    T, taille, _ = simuler_reseau(R, c, m_bas, w, W, n_pas_max, np.random.default_rng(seed), n_repetitions)
    return {
        "T_moyen": float(np.nanmean(T)) if np.isfinite(T).any() else float("nan"),
        "part_censuree": float(np.isnan(T).mean()),
        "taille_foyer_mediane": float(np.nanmedian(taille)) if np.isfinite(taille).any() else float("nan"),
    }
