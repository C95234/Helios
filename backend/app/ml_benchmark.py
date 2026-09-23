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

from .kuramoto import order_parameter
from .lyapunov_precedence import ring_weights, simulate_saddle_node

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


# -- Classifieur (PyTorch, CPU, volontairement modeste) ------------------------


class SimpleCNN1D:
    """Petit CNN 1D pour classification binaire "bascule proche / non" sur
    une fenetre brute. Volontairement modeste : pas une reproduction de
    l'architecture de Bury et al. (2021), juste assez pour la comparaison
    (§3bis : "pas besoin de reproduire l'architecture exacte")."""

    def __init__(self, window_len: int, seed: int = 0):
        import torch
        import torch.nn as nn

        torch.manual_seed(seed)

        # Note : une premiere version utilisait un AdaptiveAvgPool1d(1) final,
        # qui moyenne tout le canal en un seul nombre et efface donc OU dans
        # la fenetre se trouve un signal montant -- exactement l'information
        # utile pour detecter une approche de bascule. Remplace par un
        # flatten apres pooling local (MaxPool1d), qui garde une notion de
        # position le long de la fenetre.
        n_flat = 16 * (window_len // 4)

        class _Net(nn.Module):
            def __init__(self):
                super().__init__()
                self.conv1 = nn.Conv1d(1, 8, kernel_size=5, padding=2)
                self.pool1 = nn.MaxPool1d(2)
                self.conv2 = nn.Conv1d(8, 16, kernel_size=5, padding=2)
                self.pool2 = nn.MaxPool1d(2)
                self.fc1 = nn.Linear(n_flat, 32)
                self.fc2 = nn.Linear(32, 1)

            def forward(self, x):
                x = self.pool1(torch.relu(self.conv1(x)))
                x = self.pool2(torch.relu(self.conv2(x)))
                x = x.flatten(start_dim=1)
                x = torch.relu(self.fc1(x))
                return self.fc2(x).squeeze(-1)

        self.torch = torch
        self.net = _Net()

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 30, lr: float = 1e-3, seed: int = 0) -> list[float]:
        torch = self.torch
        torch.manual_seed(seed)
        mean, std = X.mean(), X.std() + 1e-8
        X_norm = (X - mean) / std
        self._mean, self._std = mean, std

        X_t = torch.tensor(X_norm, dtype=torch.float32).unsqueeze(1)
        y_t = torch.tensor(y, dtype=torch.float32)

        # pos_weight contrebalance le desequilibre residuel (~4:1 negatif
        # apres le sous-echantillonnage de build_dataset) -- sans lui, le
        # classifieur apprend un signal reel (verifie : proba moyenne plus
        # haute sur les positifs) mais jamais assez pour franchir le seuil
        # de decision a 0,5.
        n_pos = float(y_t.sum())
        n_neg = float(len(y_t) - n_pos)
        pos_weight = torch.tensor(n_neg / max(n_pos, 1.0))

        optimizer = torch.optim.Adam(self.net.parameters(), lr=lr)
        loss_fn = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight)

        losses = []
        self.net.train()
        for _ in range(epochs):
            optimizer.zero_grad()
            logits = self.net(X_t)
            loss = loss_fn(logits, y_t)
            loss.backward()
            optimizer.step()
            losses.append(float(loss.item()))
        return losses

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

    def load(self, path: str) -> "SimpleCNN1D":
        checkpoint = self.torch.load(path, weights_only=False)
        self.net.load_state_dict(checkpoint["state_dict"])
        self._mean = checkpoint["mean"]
        self._std = checkpoint["std"]
        return self


# -- Detecteur classique de reference (meme fenetre, methode differente) ------


def window_tail_variance(window: np.ndarray, sub_window: int = 15) -> float:
    """Variance des derniers `sub_window` points de la fenetre -- la
    statistique que `classical_verdict` seuille.

    Deuxieme essai, plus robuste que le premier (rapport de variance
    premier/dernier bloc) : un RAPPORT de deux variances estimees sur
    seulement 15 points chacune est une statistique a queue tres lourde
    (proche d'un rapport de Fisher a faible degre de liberte) -- son 95e
    percentile calibre sur un lot de series bougeait d'un facteur 4 selon
    les graines de calibration utilisees (23,8 puis 5,49 sur deux lots
    differents de meme taille), un signe classique d'instabilite
    d'echantillonnage sur une statistique a queue lourde. Une variance
    ABSOLUE (pas un rapport) comparee a un seuil calibre sur une grande
    population de reference -- exactement le principe de
    `detect_precedence` (ligne de base + k*ecart-type) -- est beaucoup
    mieux comportee."""
    return float(np.var(window[-sub_window:], ddof=1))


def calibrate_variance_threshold(n_series: int = 150, sub_window: int = 15, percentile: float = 95.0, seed: int = 20_000, kind: str = "saddle_node") -> float:
    """Calibre le seuil de `classical_verdict` empiriquement sur de vrais
    controles negatifs d'UN SEUL modele, plutot qu'un seuil invente a la
    main -- meme principe que `detect_precedence` (ligne de base + k*
    ecart-type sur une vraie periode de reference).

    `kind` doit toujours etre "saddle_node" ou "kuramoto" (jamais "both") :
    un seuil unique calibre sur les deux modeles pooles a l'origine
    donnait 0% de fausses alertes sur le nœud-col mais 100% sur Kuramoto
    -- les deux systemes n'ont pas la meme distribution de bruit de base
    (N=10 oscillateurs a couplage sous-critique fixe a des fluctuations
    de taille finie bien plus grandes que le bruit gaussien du nœud-col).
    `n_series` volontairement plus grand que le premier essai (150 contre
    60) pour stabiliser l'estimation du percentile."""
    if kind not in ("saddle_node", "kuramoto"):
        raise ValueError('kind doit valoir "saddle_node" ou "kuramoto"')
    generator = generate_saddle_node_series if kind == "saddle_node" else generate_kuramoto_ramp_series

    variances = []
    for i in range(n_series):
        sim = generator(seed=seed + i, tips=False)
        if sim["t_event"] is not None:
            continue  # bascule reelle par hasard -- exclu de la calibration du controle negatif
        for w in make_windows(sim["series"], sim["dt"], None, window_len=60, stride=5):
            variances.append(window_tail_variance(w["window"], sub_window))
    return float(np.percentile(variances, percentile))


def classical_verdict(window: np.ndarray, dt: float, sub_window: int = 15, variance_threshold: float = 1.0) -> bool:
    """Verdict "bascule proche" du detecteur classique sur la MEME fenetre
    brute que celle vue par le CNN : variance absolue de la fin de la
    fenetre comparee a un seuil -- meme mecanique de decision que
    `detect_precedence` (lyapunov_precedence.py), appliquee ici a une
    fenetre courte plutot qu'a une trajectoire complete.
    `variance_threshold` doit venir de `calibrate_variance_threshold`, pas
    d'une valeur devinee."""
    return window_tail_variance(window, sub_window) > variance_threshold
