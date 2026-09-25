"""§2.2 du cahier des charges "banc d'essai IA vs statistiques" : un
classifieur spatial entraine a distinguer un instantane genere par diffusion
sur le RESEAU REEL des departements d'un instantane genere sur une GRILLE DE
CONTROLE de meme taille -- l'analogue spatial du CNN-LSTM temporel de
`ml_benchmark.py` (§1.1), compare a l'indice de Moran (§5.2) sur la meme
tache plutot qu'a une nouvelle methode statistique inventee pour l'occasion.

Architecture (§2.2, "CNN 2D leger sur la grille/le graphe") : les
departements n'ont pas de coordonnees geographiques disponibles dans le
projet (`app/geo.py` ne contient que l'adjacence, verifie avant de choisir
cette voie plutot qu'une rasterisation 2D sur une carte) -- la
generalisation directe d'une convolution a un graphe irregulier est un
reseau de convolution de graphe (GCN, Kipf & Welling 2017). Deux branches de
propagation, une utilisant l'adjacence REELLE, une utilisant la grille de
CONTROLE, TOUTES DEUX appliquees au MEME instantane brut (centre par sa
propre moyenne, jamais la topologie d'origine donnee explicitement en
entree) -- l'analogue neuronal, a poids appris, de calculer l'indice de
Moran une fois avec chaque topologie sur le meme instantane (ce que fait
deja `spatial_series.compute_network_moran_series`), plutot qu'une nouvelle
methode statistique.

Adaptation Helios : contrairement au CNN-LSTM temporel (§1.1, adaptation
fidele de Bury et al. 2021), il n'existe pas d'architecture publiee pour un
classifieur spatial reseau-reel-vs-grille sur ce probleme precis -- celle-ci
est concue pour ce banc d'essai, deliberement legere (une seule couche de
convolution de graphe par branche), pas une reproduction d'un papier.
"""
from __future__ import annotations

import numpy as np
import torch
from torch import nn

from .lyapunov_precedence import morans_i_instant, simulate_saddle_node


def normalized_propagation(W: np.ndarray) -> np.ndarray:
    """D^-1/2 (W + I) D^-1/2 -- propagation spectrale standard d'un GCN
    (Kipf & Welling, 2017), avec boucles propres (chaque noeud voit sa
    propre valeur en plus de celle de ses voisins)."""
    n = W.shape[0]
    a = W + np.eye(n)
    deg = a.sum(axis=1)
    d_inv_sqrt = np.diag(1.0 / np.sqrt(deg))
    return d_inv_sqrt @ a @ d_inv_sqrt


class SpatialGraphClassifier(nn.Module):
    """Deux branches de convolution de graphe (poids `theta_*` appris), une
    par topologie candidate (reelle / grille), appliquees au MEME instantane
    brut -- exactement comme le CNN-LSTM temporel ne voit que la fenetre
    brute, jamais une information supplementaire (§1.2, "comparaison a armes
    egales")."""

    HIDDEN = 8

    def __init__(self, w_real: np.ndarray, w_grid: np.ndarray, seed: int = 0):
        super().__init__()
        torch.manual_seed(seed)
        n = w_real.shape[0]
        if w_grid.shape[0] != n:
            raise ValueError("w_real et w_grid doivent avoir le meme nombre de noeuds")
        self.n_nodes = n
        self.register_buffer("a_real", torch.tensor(normalized_propagation(w_real), dtype=torch.float32))
        self.register_buffer("a_grid", torch.tensor(normalized_propagation(w_grid), dtype=torch.float32))
        self.theta_real = nn.Linear(1, self.HIDDEN)
        self.theta_grid = nn.Linear(1, self.HIDDEN)
        self.head = nn.Linear(4 * self.HIDDEN, 1)

    def _branch(self, x: torch.Tensor, a_hat: torch.Tensor, theta: nn.Linear) -> torch.Tensor:
        h = theta(x.unsqueeze(-1))  # (batch, n, hidden) -- projection par noeud
        h = torch.einsum("ij,bjh->bih", a_hat, h)  # propagation sur le graphe
        h = torch.relu(h)
        return torch.cat([h.mean(dim=1), h.amax(dim=1)], dim=-1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        centered = x - x.mean(dim=1, keepdim=True)
        real_feat = self._branch(centered, self.a_real, self.theta_real)
        grid_feat = self._branch(centered, self.a_grid, self.theta_grid)
        return self.head(torch.cat([real_feat, grid_feat], dim=-1)).squeeze(-1)

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 40, lr: float = 0.01, batch_size: int = 64, seed: int = 0) -> list[float]:
        rng = np.random.default_rng(seed)
        x_t = torch.tensor(X, dtype=torch.float32)
        y_t = torch.tensor(y, dtype=torch.float32)
        opt = torch.optim.Adam(self.parameters(), lr=lr)
        loss_fn = nn.BCEWithLogitsLoss()
        n = len(X)
        losses = []
        for _ in range(epochs):
            perm = rng.permutation(n)
            epoch_losses = []
            for start in range(0, n, batch_size):
                idx = perm[start:start + batch_size]
                opt.zero_grad()
                loss = loss_fn(self(x_t[idx]), y_t[idx])
                loss.backward()
                opt.step()
                epoch_losses.append(loss.item())
            losses.append(float(np.mean(epoch_losses)))
        return losses

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        self.eval()
        with torch.no_grad():
            return torch.sigmoid(self(torch.tensor(X, dtype=torch.float32))).numpy()

    def save(self, path: str) -> None:
        torch.save({"state_dict": self.state_dict()}, path)

    def load(self, path: str) -> None:
        checkpoint = torch.load(path, map_location="cpu", weights_only=False)
        self.load_state_dict(checkpoint["state_dict"])
        self.eval()


def classical_moran_predictions(X: np.ndarray, w_real: np.ndarray, w_grid: np.ndarray) -> np.ndarray:
    """Baseline classique, sans aucun parametre appris : predit "reseau reel"
    (1) si l'indice de Moran instantane calcule avec l'adjacence REELLE est
    strictement plus eleve que celui calcule avec la grille de CONTROLE, sur
    le MEME instantane -- exactement la comparaison que §5.2/H2 fait deja
    pour une serie temporelle complete, appliquee ici instantane par
    instantane, a armes egales avec le classifieur (meme donnee d'entree)."""
    preds = np.empty(len(X))
    for i, x in enumerate(X):
        preds[i] = 1.0 if morans_i_instant(x, w_real) > morans_i_instant(x, w_grid) else 0.0
    return preds


def generate_topology_dataset(
    w_real: np.ndarray,
    w_grid: np.ndarray,
    n_runs_per_class: int,
    seed0: int,
    dt: float = 0.02,
    t_max: float = 150.0,
    mu_rate: float = 0.02,
    snapshot_stride: int = 50,
    burn_in_snapshots: int = 2,
) -> tuple[np.ndarray, np.ndarray]:
    """Genere des instantanes de la MEME dynamique de bifurcation noeud-col
    (`simulate_saddle_node`, deja generalisee a n'importe quelle matrice de
    poids -- §5.6quater/quinquies), une fois couplee sur le reseau reel
    (label=1), une fois sur la grille de controle (label=0) -- seule la
    topologie change, jamais l'equation ni les autres parametres.
    `burn_in_snapshots` ecarte les tout premiers instantanes (encore trop
    proches du depart au repos, quasi identiques quelle que soit la
    topologie, donc non informatifs pour cette tache)."""
    x_parts, y_parts = [], []
    for label, w in [(1, w_real), (0, w_grid)]:
        for i in range(n_runs_per_class):
            sim = simulate_saddle_node(
                w, dt=dt, t_max=t_max, mu_rate=mu_rate, seed=seed0 + label * 100_000 + i,
                return_snapshots=True, snapshot_stride=snapshot_stride,
            )
            snaps = sim["x_snapshots"][burn_in_snapshots:]
            x_parts.append(snaps)
            y_parts.extend([label] * len(snaps))
    return np.concatenate(x_parts, axis=0).astype(np.float32), np.array(y_parts, dtype=np.float32)
