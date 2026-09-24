"""Banc d'essai comparatif : indicateurs statistiques classiques vs un
classifieur de deep learning -- cahier des charges, suite ewstools §3bis.

Module de recherche hors-ligne, comme `lyapunov_precedence.py` : jamais
expose par l'API produit, utilise seulement par
`scripts/train_and_compare_classifier.py`.

Motivation (§3bis) : l'approche signature de Thomas Bury (PNAS 2021, avec
Marten Scheffer) combine les indicateurs statistiques classiques a un
classifieur de deep learning entraine sur des series simulees pres de
bifurcations connues. Ce module compare cette approche aux indicateurs
deja utilises par Helios (variance, AC1), sur les deux modeles de
bifurcation deja construits cette session -- pas une nouvelle methode,
un test de replication comparative.

Adaptation Helios -- echelle reduite pour l'entrainement : les deux
modeles sources (`simulate_saddle_node`, reseau en anneau N=40 ;
`simulate_uncontrolled` de Kuramoto) sont trop lents a leur echelle
habituelle pour generer les milliers de fenetres necessaires a
l'entrainement d'un classifieur (~5,5s par realisation a N=40). Les
memes equations, les memes fonctions, sont reutilisees a une echelle
reduite (reseaux plus petits, duree plus courte) uniquement pour la
generation de donnees d'entrainement/test -- pas une nouvelle
modelisation.
"""
from __future__ import annotations

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

from .kuramoto import order_parameter
from .lyapunov_precedence import ring_weights, simulate_saddle_node
from .stats.surrogates import phase_randomized_surrogate

# -- Generateurs de series (echelle reduite pour la vitesse) ------------------

SADDLE_NODE_N = 5
SADDLE_NODE_DT = 0.02
SADDLE_NODE_T_MAX = 150.0

KURAMOTO_N = 10
KURAMOTO_DT = 0.02
KURAMOTO_T_MAX = 150.0


def generate_saddle_node_series(seed: int, tips: bool, beta: float = 0.6, sigma: float = 0.2) -> dict:
    """Reutilise `simulate_saddle_node` a echelle reduite (N=5). `tips=True` :
    mu rampe jusqu'a franchir 0 (bascule reelle) dans l'horizon simule.
    `tips=False` : mu FIXE (mu_rate=0), loin de 0, tout l'horizon --
    controle negatif genuinement stable, pas juste une rampe plus lente.

    Correction (trouvee en verifiant un premier resultat suspect : le
    detecteur classique flaguait 100% des "controles negatifs" comme
    fausses alertes) : un mu_rate positif meme faible reste un VRAI
    ralentissement critique progressif (le systeme se rapproche
    reellement, juste plus lentement, de la bifurcation) -- un detecteur
    qui le repere ne se trompe pas, ce n'est simplement pas un controle
    negatif valide. Un controle negatif honnete exige un parametre
    FIXE, jamais en derive vers le seuil."""
    W = ring_weights(SADDLE_NODE_N)
    mu_rate = 0.015 if tips else 0.0
    sim = simulate_saddle_node(
        W,
        beta=beta,
        sigma=sigma,
        dt=SADDLE_NODE_DT,
        t_max=SADDLE_NODE_T_MAX,
        mu_rate=mu_rate,
        coupling="diffusive",
        seed=seed,
    )
    return {"series": sim["xbar"], "dt": SADDLE_NODE_DT, "t_event": sim["t_escape"], "kind": "saddle_node"}


KURAMOTO_BURN_IN = 50.0


def generate_kuramoto_ramp_series(seed: int, tips: bool, sigma: float = 1.0, sync_threshold: float = 0.9) -> dict:
    """Kuramoto avec un couplage K(t) qui rampe lentement (generalise
    `simulate_uncontrolled`, dont le couplage est fixe, exactement comme
    `simulate_saddle_node` generalise un mu(t) qui rampe plutot qu'un mu
    fixe). `tips=True` : K depasse nettement le couplage critique dans
    l'horizon simule, le systeme se synchronise (r depasse
    `sync_threshold`). `tips=False` : K reste FIXE (jamais en derive) a
    une valeur sous-critique tout l'horizon -- meme correction que pour
    le nœud-col (voir sa docstring) : un couplage qui rampe, meme
    lentement, vers le seuil critique reste un vrai signal d'approche, pas
    un controle negatif valide.

    Rodage (`KURAMOTO_BURN_IN`) avant l'enregistrement : les phases
    partent d'une configuration uniforme aleatoire, tres loin de
    l'equilibre stationnaire du couplage de depart -- sans rodage, le
    parametre d'ordre r(t) grimpe reellement tout au long de la fenetre
    enregistree, meme a couplage fixe, simplement parce que le systeme
    n'a pas fini de relaxer vers son etat stationnaire. Verifie
    directement sur une trajectoire "stable" : r montait de 0,20 a 0,93
    sur toute la duree, un vrai transitoire de relaxation, pas du bruit
    -- ce n'etait donc pas un faux positif du detecteur mais un vrai
    signal, juste un controle negatif invalide (le nœud-col n'a pas ce
    probleme : `simulate_saddle_node` part deja du point fixe stable de
    mu0, equivalent a un rodage analytique). Le rodage tourne a
    coupling=k0 (le point de depart de la rampe, fixe ou non), pour que
    l'enregistrement commence pres de l'equilibre reel de ce couplage."""
    n = KURAMOTO_N
    rng = np.random.default_rng(seed)
    omega = rng.normal(0, sigma, size=n)
    theta = rng.uniform(0, 2 * np.pi, size=n)

    from .kuramoto import critical_coupling

    k_c = critical_coupling(sigma)
    if tips:
        k0, k_rate = 0.0, (k_c * 2.5) / KURAMOTO_T_MAX
    else:
        k0, k_rate = 0.3 * k_c, 0.0

    def _step(theta, k):
        diffs = theta[None, :] - theta[:, None]
        coupling = (k / n) * np.sum(np.sin(diffs), axis=1)
        return theta + KURAMOTO_DT * (omega + coupling)

    for _ in range(int(KURAMOTO_BURN_IN / KURAMOTO_DT)):
        theta = _step(theta, k0)

    n_steps = int(KURAMOTO_T_MAX / KURAMOTO_DT)
    r_series = np.empty(n_steps)
    t_sync = None
    for step in range(n_steps):
        t = step * KURAMOTO_DT
        k = k0 + k_rate * t
        theta = _step(theta, k)
        r = order_parameter(theta)
        r_series[step] = r
        if t_sync is None and r > sync_threshold:
            t_sync = t

    return {"series": r_series, "dt": KURAMOTO_DT, "t_event": t_sync, "kind": "kuramoto"}


# -- Fenetrage et etiquetage ---------------------------------------------------


def make_windows(
    series: np.ndarray, dt: float, t_event: float | None, window_len: int, stride: int, horizon_fraction: float = 0.35
) -> list[dict]:
    """Decoupe `series` en fenetres glissantes de longueur `window_len`
    (en pas de temps), etiquette positive (label=1) si la fin de la
    fenetre tombe dans les derniers `horizon_fraction` de la periode
    d'approche (entre 0 et `t_event`), negative sinon -- meme logique que
    Bury et al. (2021) (une fenetre "approche une bascule" plutot qu'un
    seul instant juste avant), appliquee aux deux generateurs ci-dessus.

    Une fraction de la duree d'approche plutot qu'une duree absolue : le
    temps de bascule varie beaucoup d'une realisation Kuramoto a l'autre
    (bruit sur le franchissement du seuil de synchronisation), une
    fenetre "positive" absolue donnerait une part du signal d'approche
    tres differente selon la realisation."""
    windows = []
    for end in range(window_len, len(series), stride):
        window = series[end - window_len : end]
        t_end = end * dt
        if t_event is not None and (1 - horizon_fraction) * t_event <= t_end <= t_event:
            label = 1
        elif t_event is not None and t_end > t_event:
            continue  # apres la bascule reelle -- ni positif ni negatif propre, on ignore
        else:
            label = 0
        windows.append({"window": window, "t_end": t_end, "label": label})
    return windows


def build_dataset(
    n_saddle: int, n_kuramoto: int, seed0: int, window_len: int = 60, stride: int = 5, negative_ratio: float = 4.0
) -> tuple[np.ndarray, np.ndarray]:
    """Assemble un jeu de fenetres + labels a partir des deux generateurs,
    moitie bascule reelle / moitie controle negatif pour chacun.

    Sous-echantillonne les fenetres negatives a `negative_ratio` fois le
    nombre de positives (graine fixe) : sans ca, la tres large majorite
    des fenetres d'une trajectoire est loin de toute bascule (y compris
    dans les trajectoires qui basculent), et le desequilibre de classes
    qui en resulte (>99% de negatives observe sans ce garde-fou) empeche
    le classifieur d'apprendre quoi que ce soit d'utile -- verifie
    empiriquement avant d'ajouter ce sous-echantillonnage."""
    all_windows: list[np.ndarray] = []
    all_labels: list[int] = []
    seed = seed0

    for i in range(n_saddle):
        tips = i % 2 == 0
        sim = generate_saddle_node_series(seed=seed, tips=tips)
        seed += 1
        for w in make_windows(sim["series"], sim["dt"], sim["t_event"], window_len, stride):
            all_windows.append(w["window"])
            all_labels.append(w["label"])

    for i in range(n_kuramoto):
        tips = i % 2 == 0
        sim = generate_kuramoto_ramp_series(seed=seed, tips=tips)
        seed += 1
        for w in make_windows(sim["series"], sim["dt"], sim["t_event"], window_len, stride):
            all_windows.append(w["window"])
            all_labels.append(w["label"])

    X_all = np.stack(all_windows).astype(np.float32)
    y_all = np.array(all_labels, dtype=np.float32)

    pos_idx = np.where(y_all == 1)[0]
    neg_idx = np.where(y_all == 0)[0]
    rng = np.random.default_rng(seed0)
    n_neg_keep = min(len(neg_idx), int(len(pos_idx) * negative_ratio))
    neg_idx_kept = rng.choice(neg_idx, size=n_neg_keep, replace=False)

    keep_idx = np.concatenate([pos_idx, neg_idx_kept])
    rng.shuffle(keep_idx)
    return X_all[keep_idx], y_all[keep_idx]


# -- Classifieur (PyTorch, CPU) -- architecture adaptee de Bury et al. (2021) --
#
# Correction (cahier des charges "banc d'essai IA vs statistiques" §1.1) : la
# premiere version etait "un petit CNN 1D, pas une reproduction de
# l'architecture de Bury et al." -- un choix documente comme provisoire. Le
# code d'entrainement complet de Bury et al. est publie
# (github.com/ThomasMBury/deep-early-warnings-pnas, dl_train/DL_training.py,
# recupere et lu directement, pas reimplemente de memoire) : l'architecture
# reelle est Conv1D(50 filtres, noyau 12) -> Dropout(0,10) -> MaxPool(2) ->
# LSTM(50) -> Dropout(0,10) -> LSTM(10) -> Dropout(0,10) -> Dense, entrainee
# avec Adam(lr=0,0005). Reprise ici telle quelle pour la partie traitement du
# signal (les memes hyperparametres exacts : filtres, taille de noyau,
# tailles de memoire LSTM, taux de dropout, taux d'apprentissage).
#
# Ce qui CHANGE necessairement, documente honnetement (§1.1 : "reproduire
# fidelement... jamais pretendre faire mieux") :
# - Sortie Dense(4, softmax) -> Dense(1, sigmoid) : Bury et al. classent le
#   TYPE de bifurcation (fold/Hopf/transcritical/nul, 4 classes) sur un tres
#   grand nombre de modeles generiques ; Helios teste seulement "bascule
#   proche ou non" sur les 2 modeles deja construits (noeud-col, Kuramoto) --
#   une tache differente, plus simple, qui ne justifie pas 4 sorties.
# - Echelle d'entrainement drastiquement reduite : Bury et al. entrainent sur
#   200 000 sequences de longueur 500-1500 pendant 1500 epoques en
#   entrainement pleine-batch -- verifie directement sur ce materiel (une
#   seule epoque pleine-batch a 8 000 fenetres de longueur 60 a deja pris
#   ~21s, l'echelle de Bury et al. y prendrait des heures par modele). Le jeu
#   d'entrainement et le nombre d'epoques sont donc reduits (voir
#   train_and_compare_classifier.py), et l'entrainement se fait par
#   mini-lots plutot qu'en pleine-batch -- Bury et al. utilisent egalement un
#   entrainement par lots (batch_size=1000), la mecanique n'est donc pas
#   nouvelle, seule sa taille est adaptee a notre echelle de donnees.


class CnnLstmClassifier:
    """Classifieur CNN-LSTM binaire "bascule proche / non" -- architecture
    adaptee de Bury et al. (2021), voir le commentaire de module ci-dessus."""

    FILTERS = 50
    KERNEL_SIZE = 12
    LSTM1_UNITS = 50
    LSTM2_UNITS = 10
    DROPOUT = 0.10

    def __init__(self, window_len: int, seed: int = 0):
        import torch
        import torch.nn as nn

        torch.manual_seed(seed)
        filters, kernel, lstm1, lstm2, dropout = (
            self.FILTERS,
            self.KERNEL_SIZE,
            self.LSTM1_UNITS,
            self.LSTM2_UNITS,
            self.DROPOUT,
        )

        class _Net(nn.Module):
            def __init__(self):
                super().__init__()
                self.conv = nn.Conv1d(1, filters, kernel_size=kernel, padding=kernel // 2)
                self.dropout1 = nn.Dropout(dropout)
                self.pool = nn.MaxPool1d(2)
                self.lstm1 = nn.LSTM(filters, lstm1, batch_first=True)
                self.dropout2 = nn.Dropout(dropout)
                self.lstm2 = nn.LSTM(lstm1, lstm2, batch_first=True)
                self.dropout3 = nn.Dropout(dropout)
                self.fc = nn.Linear(lstm2, 1)

            def forward(self, x):
                # x : (batch, 1, window_len)
                x = torch.relu(self.conv(x))
                x = self.dropout1(x)
                x = self.pool(x)  # (batch, filters, window_len//~2)
                x = x.transpose(1, 2)  # (batch, seq, filters) -- LSTM batch_first
                x, _ = self.lstm1(x)  # equivalent de return_sequences=True (Keras)
                x = self.dropout2(x)
                _, (h, _) = self.lstm2(x)  # equivalent de return_sequences=False : dernier etat cache
                x = self.dropout3(h[-1])
                return self.fc(x).squeeze(-1)

        self.torch = torch
        self.net = _Net()

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 30,
        lr: float = 0.0005,
        batch_size: int = 256,
        seed: int = 0,
    ) -> list[float]:
        """Entrainement par mini-lots (Bury et al. utilisent aussi des lots,
        batch_size=1000 -- adapte ici a la taille reduite de notre jeu de
        donnees, voir le commentaire de module). Une "perte" par epoque =
        moyenne des pertes de mini-lots de cette epoque."""
        torch = self.torch
        torch.manual_seed(seed)
        rng = np.random.default_rng(seed)

        mean, std = X.mean(), X.std() + 1e-8
        X_norm = (X - mean) / std
        self._mean, self._std = mean, std

        X_t = torch.tensor(X_norm, dtype=torch.float32).unsqueeze(1)
        y_t = torch.tensor(y, dtype=torch.float32)
        n = len(y_t)

        # pos_weight contrebalance le desequilibre residuel (~4:1 negatif
        # apres le sous-echantillonnage de build_dataset) -- sans lui, le
        # classifieur apprend un signal reel mais jamais assez fort pour
        # franchir le seuil de decision a 0,5 (verifie empiriquement).
        n_pos = float(y_t.sum())
        n_neg = float(n - n_pos)
        pos_weight = torch.tensor(n_neg / max(n_pos, 1.0))

        optimizer = torch.optim.Adam(self.net.parameters(), lr=lr)
        loss_fn = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight)

        epoch_losses = []
        self.net.train()
        for _ in range(epochs):
            order = rng.permutation(n)
            batch_losses = []
            for start in range(0, n, batch_size):
                idx = order[start : start + batch_size]
                optimizer.zero_grad()
                logits = self.net(X_t[idx])
                loss = loss_fn(logits, y_t[idx])
                loss.backward()
                optimizer.step()
                batch_losses.append(float(loss.item()))
            epoch_losses.append(float(np.mean(batch_losses)))
        return epoch_losses

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        torch = self.torch
        X_norm = (X - self._mean) / self._std
        X_t = torch.tensor(X_norm, dtype=torch.float32).unsqueeze(1)
        self.net.eval()
        with torch.no_grad():
            logits = self.net(X_t)
            return torch.sigmoid(logits).numpy()

    def save(self, path: str) -> None:
        """Sauvegarde les poids + la normalisation -- evite de reentrainer
        (plusieurs dizaines de minutes) a chaque ajustement de la logique
        d'evaluation, qui ne concerne que l'inference."""
        self.torch.save({"state_dict": self.net.state_dict(), "mean": self._mean, "std": self._std}, path)

    def load(self, path: str) -> "CnnLstmClassifier":
        checkpoint = self.torch.load(path, weights_only=False)
        self.net.load_state_dict(checkpoint["state_dict"])
        self._mean = checkpoint["mean"]
        self._std = checkpoint["std"]
        return self


# -- Detecteur classique de reference (meme fenetre, methode differente) ------
#
# Correction (cahier des charges "banc d'essai IA vs statistiques" §1.2) :
# la premiere version comparait une variance de fin de fenetre a un seuil
# calibre empiriquement -- un adversaire appauvri par rapport a ce que H1
# utilise reellement ailleurs dans le projet (variance ET autocorrelation,
# tau de Kendall, test de significativite par donnees de substitution,
# §5.1/§5.4). Remplace ici par l'indicateur complet : `surrogate_test`
# (stats/surrogates.py) applique DIRECTEMENT sur chaque fenetre de 60 points
# (comme le CNN, le detecteur classique ne voit que cette fenetre, jamais
# l'historique de la trajectoire) -- positif si la tendance de la variance
# OU celle de l'AC1 glissante est significative (meme combinaison "OU" que
# le module Fusion, routers/fusion.py).
#
# Adaptation Helios -- implementation vectorisee : `rolling_ac1`
# (stats/indicators.py) appelle `statsmodels.tsa.stattools.acf` a l'interieur
# d'un `pandas.rolling().apply()`, beaucoup trop lent pour etre repete sur les
# ~1500 fenetres d'une trajectoire x des dizaines de trajectoires x une
# centaine de surrogates par fenetre. `_rolling_ac1_batch` ci-dessous calcule
# la MEME formule fermee que `acf(x, nlags=1, fft=False)` --
# r_1 = sum((x_t-xbar)(x_{t+1}-xbar)) / sum((x_t-xbar)^2) -- verifiee
# numeriquement identique a la reference statsmodels (ecart ~1e-16, precision
# machine) mais vectorisee sur toutes les fenetres glissantes et tous les
# surrogates d'un coup plutot qu'un appel Python par sous-fenetre.


def _rolling_var_batch(batch: np.ndarray, sub_window: int) -> np.ndarray:
    """Variance glissante (ddof=1), vectorisee sur un lot de series de meme
    longueur -- (n_series, window_len) -> (n_series, window_len-sub_window+1)."""
    windows = sliding_window_view(batch, sub_window, axis=1)
    return windows.var(axis=-1, ddof=1)


def _rolling_ac1_batch(batch: np.ndarray, sub_window: int) -> np.ndarray:
    """AC1 glissante, formule fermee equivalente a `acf(x, nlags=1, fft=False)[1]`
    (verifie numeriquement, voir commentaire ci-dessus), vectorisee comme
    `_rolling_var_batch`."""
    windows = sliding_window_view(batch, sub_window, axis=1)
    xbar = windows.mean(axis=-1, keepdims=True)
    dev = windows - xbar
    num = np.sum(dev[..., :-1] * dev[..., 1:], axis=-1)
    den = np.sum(dev**2, axis=-1)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(den > 0, num / den, np.nan)


def _kendall_tau_rows(batch: np.ndarray) -> np.ndarray:
    """Tau de Kendall (tau-a) de chaque ligne contre le temps (0..n-1),
    vectorise sur toutes les lignes a la fois plutot qu'un appel
    `scipy.stats.kendalltau` par ligne (mesure : ~350 microsecondes par appel
    scipy, prohibitif repete sur ~1500 fenetres x une centaine de surrogates
    x deux indicateurs par trajectoire). Le temps (x) est toujours 0..n-1,
    strictement croissant et sans ex-aequo : tau-a et tau-b (la correction
    d'ex-aequo de scipy, negligeable ici puisque les indicateurs sont des
    flottants continus) coincident alors a la precision machine (verifie
    numeriquement, ecart max ~5e-17 sur des donnees synthetiques). Concordance
    calculee par comparaison de paires vectorisee (n*(n-1)/2 paires, n<=46
    ici -- trivial en memoire)."""
    n = batch.shape[1]
    iu = np.triu_indices(n, k=1)
    diff = batch[:, :, None] - batch[:, None, :]
    pairwise_sign = diff[:, iu[0], iu[1]]  # sign(y_i - y_j) pour i<j
    n_concordant_minus_discordant = -np.sum(np.sign(pairwise_sign), axis=1)
    n_pairs = n * (n - 1) / 2
    return n_concordant_minus_discordant / n_pairs


def classical_verdict(window: np.ndarray, sub_window: int = 15, n_surrogates: int = 100, seed: int | None = None) -> bool:
    """Verdict "bascule proche" du detecteur classique sur la fenetre brute :
    tendance (tau de Kendall) de la variance glissante ET de l'AC1 glissante
    A L'INTERIEUR de cette fenetre (46 positions pour une fenetre de 60 points
    et sub_window=15), chacune testee contre des donnees de substitution a
    phase aleatoire de la fenetre elle-meme -- exactement `surrogate_test`
    (stats/surrogates.py), pas une nouvelle methode. Positif si la variance OU
    l'AC1 est significative a 0,05 (meme combinaison que Fusion, routers/fusion.py)."""
    rng = np.random.default_rng(seed)
    surrogates = np.stack([phase_randomized_surrogate(window, rng) for _ in range(n_surrogates)])
    batch = np.vstack([window[None, :], surrogates])  # ligne 0 = observe, le reste = surrogates

    var_series = _rolling_var_batch(batch, sub_window)
    ac1_series = _rolling_ac1_batch(batch, sub_window)
    var_taus = _kendall_tau_rows(var_series)
    ac1_taus = _kendall_tau_rows(ac1_series)

    if np.isnan(var_taus[0]) and np.isnan(ac1_taus[0]):
        return False

    var_p = float(np.mean(var_taus[1:] >= var_taus[0])) if not np.isnan(var_taus[0]) else 1.0
    ac1_p = float(np.mean(ac1_taus[1:] >= ac1_taus[0])) if not np.isnan(ac1_taus[0]) else 1.0
    return var_p < 0.05 or ac1_p < 0.05
