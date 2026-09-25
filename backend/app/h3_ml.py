"""§2.3 du cahier des charges "banc d'essai IA vs statistiques" : un
classifieur a DOUBLE ENTREE (une fenetre temporelle + un instantane spatial,
sur le MEME systeme) pour la question propre a H3 -- "les deux signaux
sont-ils anormaux EN MEME TEMPS ?" -- compare a la methode empirique de
Brown/Kost & McDermott deja utilisee par H3 (`stats/h3_joint.py`).

Architecture (§2.3, "deux branches ... fusionnees avant la decision
finale") : une branche temporelle (Conv1D + LSTM, meme famille que le
CNN-LSTM de §1.1 mais reduite -- ce module ne reproduit PAS Bury et al.,
qui ne traite qu'un seul flux temporel) et une branche spatiale (la meme
convolution de graphe que §2.2, `spatial_ml.SpatialGraphClassifier`, mais
UNE SEULE branche ici -- sur le reseau reel uniquement, puisque la question
n'est plus "reseau reel ou grille ?" mais "anomalie jointe sur le reseau
reel"). Les deux embeddings sont concatenes puis passes a une seule couche
de decision -- une fusion tardive, la plus simple qui reponde a la
consigne du cahier des charges, pas une architecture de fusion plus
sophistiquee (fusion precoce, attention croisee) qui n'a pas ete demandee.

Donnees d'entrainement : la MEME trajectoire simulee
(`lyapunov_precedence.simulate_saddle_node`, couplee sur le RESEAU REEL des
departements, §2.2) fournit a la fois la moyenne du reseau xbar(t) (branche
temporelle) et les instantanes par noeud x(t) (branche spatiale) -- les
deux canaux sont donc TOUJOURS synchrones par construction, pas deux jeux
de donnees appairs artificiellement.
"""
from __future__ import annotations

import numpy as np
import torch
from torch import nn

from .lyapunov_precedence import simulate_saddle_node
from .spatial_ml import normalized_propagation


class DualBranchFusionClassifier(nn.Module):
    """Fenetre temporelle (longueur `window_len`) + instantane spatial
    (longueur `n_nodes`, MEME systeme, MEME instant) -> probabilite que les
    deux soient anormaux en meme temps (proche d'une bascule reelle)."""

    FILTERS = 16
    KERNEL_SIZE = 8
    LSTM_UNITS = 10
    SPATIAL_HIDDEN = 8

    def __init__(self, window_len: int, w_real: np.ndarray, seed: int = 0):
        super().__init__()
        torch.manual_seed(seed)
        self.window_len = window_len
        self.register_buffer("a_real", torch.tensor(normalized_propagation(w_real), dtype=torch.float32))

        self.conv = nn.Conv1d(1, self.FILTERS, kernel_size=self.KERNEL_SIZE, padding=self.KERNEL_SIZE // 2)
        self.pool = nn.MaxPool1d(2)
        self.lstm = nn.LSTM(self.FILTERS, self.LSTM_UNITS, batch_first=True)

        self.theta_spatial = nn.Linear(1, self.SPATIAL_HIDDEN)

        self.head = nn.Linear(self.LSTM_UNITS + 2 * self.SPATIAL_HIDDEN, 1)

    def _temporal_embedding(self, x_temporal: torch.Tensor) -> torch.Tensor:
        # x_temporal : (batch, window_len)
        h = torch.relu(self.conv(x_temporal.unsqueeze(1)))  # (batch, filters, window_len)
        h = self.pool(h).transpose(1, 2)  # (batch, seq, filters)
        _, (hn, _) = self.lstm(h)
        return hn[-1]  # (batch, lstm_units)

    def _spatial_embedding(self, x_spatial: torch.Tensor) -> torch.Tensor:
        centered = x_spatial - x_spatial.mean(dim=1, keepdim=True)
        h = self.theta_spatial(centered.unsqueeze(-1))  # (batch, n_nodes, hidden)
        h = torch.einsum("ij,bjh->bih", self.a_real, h)
        h = torch.relu(h)
        return torch.cat([h.mean(dim=1), h.amax(dim=1)], dim=-1)

    def forward(self, x_temporal: torch.Tensor, x_spatial: torch.Tensor) -> torch.Tensor:
        temporal_emb = self._temporal_embedding(x_temporal)
        spatial_emb = self._spatial_embedding(x_spatial)
        return self.head(torch.cat([temporal_emb, spatial_emb], dim=-1)).squeeze(-1)

    def fit(
        self,
        x_temporal: np.ndarray,
        x_spatial: np.ndarray,
        y: np.ndarray,
        epochs: int = 30,
        lr: float = 0.001,
        batch_size: int = 64,
        seed: int = 0,
    ) -> list[float]:
        self._mean = float(x_temporal.mean())
        self._std = float(x_temporal.std() + 1e-8)
        rng = np.random.default_rng(seed)
        xt = torch.tensor((x_temporal - self._mean) / self._std, dtype=torch.float32)
        xs = torch.tensor(x_spatial, dtype=torch.float32)
        y_t = torch.tensor(y, dtype=torch.float32)
        opt = torch.optim.Adam(self.parameters(), lr=lr)
        loss_fn = nn.BCEWithLogitsLoss()
        n = len(y)
        losses = []
        for _ in range(epochs):
            perm = rng.permutation(n)
            epoch_losses = []
            for start in range(0, n, batch_size):
                idx = perm[start:start + batch_size]
                opt.zero_grad()
                loss = loss_fn(self(xt[idx], xs[idx]), y_t[idx])
                loss.backward()
                opt.step()
                epoch_losses.append(loss.item())
            losses.append(float(np.mean(epoch_losses)))
        return losses

    def predict_proba(self, x_temporal: np.ndarray, x_spatial: np.ndarray) -> np.ndarray:
        self.eval()
        xt = torch.tensor((x_temporal - self._mean) / self._std, dtype=torch.float32)
        xs = torch.tensor(x_spatial, dtype=torch.float32)
        with torch.no_grad():
            return torch.sigmoid(self(xt, xs)).numpy()

    def save(self, path: str) -> None:
        torch.save({"state_dict": self.state_dict(), "mean": self._mean, "std": self._std}, path)

    def load(self, path: str) -> None:
        checkpoint = torch.load(path, map_location="cpu", weights_only=False)
        self.load_state_dict(checkpoint["state_dict"])
        self._mean = checkpoint["mean"]
        self._std = checkpoint["std"]
        self.eval()


def generate_joint_dataset(
    w_real: np.ndarray,
    n_runs_per_class: int,
    seed0: int,
    window_len: int = 60,
    dt: float = 0.02,
    t_max: float = 150.0,
    mu_rate_tip: float = 0.02,
    snapshot_stride: int = 5,
    horizon_steps: int = 150,
    negative_ratio: float = 4.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Paires (fenetre temporelle, instantane spatial) SYNCHRONES issues de la
    MEME trajectoire simulee sur le reseau reel -- label=1 si la fenetre se
    termine dans les `horizon_steps` derniers pas avant une VRAIE bascule
    (§5.6quater : la meme logique de fenetre que le CNN-LSTM temporel,
    §1.1), label=0 sinon (loin de toute bascule, ou trajectoire de controle
    qui ne bascule jamais -- mu_rate=0, jamais juste une rampe plus lente).
    Sous-echantillonne les negatives comme `ml_benchmark.build_dataset`
    (deja verifie necessaire empiriquement pour ce type de tache)."""
    x_temporal, x_spatial, labels = [], [], []
    for class_label, mu_rate in [(1, mu_rate_tip), (0, 0.0)]:
        for i in range(n_runs_per_class):
            sim = simulate_saddle_node(
                w_real, dt=dt, t_max=t_max, mu_rate=mu_rate, seed=seed0 + class_label * 100_000 + i,
                return_snapshots=True, snapshot_stride=snapshot_stride,
            )
            xbar, snaps = sim["xbar"], sim["x_snapshots"]
            t_escape_step = int(sim["t_escape"] / dt) if sim["t_escape"] is not None else None
            n_steps = len(xbar)
            for end in range(window_len, n_steps, snapshot_stride):
                snap_idx = end // snapshot_stride
                if snap_idx >= len(snaps):
                    continue
                is_positive = t_escape_step is not None and (t_escape_step - horizon_steps) <= end < t_escape_step
                x_temporal.append(xbar[end - window_len:end])
                x_spatial.append(snaps[snap_idx])
                labels.append(1 if is_positive else 0)

    x_temporal = np.array(x_temporal, dtype=np.float32)
    x_spatial = np.array(x_spatial, dtype=np.float32)
    labels = np.array(labels, dtype=np.float32)

    pos_idx = np.where(labels == 1)[0]
    neg_idx = np.where(labels == 0)[0]
    rng = np.random.default_rng(seed0)
    n_neg_keep = min(len(neg_idx), int(len(pos_idx) * negative_ratio)) if len(pos_idx) else len(neg_idx)
    neg_keep = rng.choice(neg_idx, size=n_neg_keep, replace=False) if n_neg_keep < len(neg_idx) else neg_idx
    keep = np.concatenate([pos_idx, neg_keep])
    rng.shuffle(keep)
    return x_temporal[keep], x_spatial[keep], labels[keep]


def classical_joint_predictions(x_temporal: np.ndarray, x_spatial: np.ndarray, w_real: np.ndarray) -> np.ndarray:
    """Baseline sans reseau de neurones, a armes egales (meme fenetre/
    instantane) : predit "anomalie jointe" si la fenetre temporelle montre
    une tendance croissante de variance ET si l'instantane spatial montre un
    indice de Moran superieur a sa mediane empirique sur le lot -- une
    combinaison simple des deux signaux, dans l'esprit de la methode de
    Brown/H3 (combiner temporel et spatial) mais sans la calibration
    historique complete de `stats/h3_joint.py` (qui a besoin d'un historique
    reel, absent ici puisque les donnees sont simulees)."""
    from .lyapunov_precedence import morans_i_instant
    from .stats.indicators import kendall_trend, rolling_variance
    import pandas as pd

    n = len(x_temporal)
    tau = np.empty(n)
    moran = np.empty(n)
    for i in range(n):
        var_series = rolling_variance(pd.Series(x_temporal[i]), max(4, len(x_temporal[i]) // 6))
        t, _ = kendall_trend(var_series)
        tau[i] = 0.0 if np.isnan(t) else t
        moran[i] = morans_i_instant(x_spatial[i], w_real)
    return ((tau > np.median(tau)) & (moran > np.median(moran))).astype(np.float32)
