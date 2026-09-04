"""Detection de disruption par chute brutale du courant plasma (quench) --
cahier des charges Helios §7ter.

Verite terrain necessaire au module fusion : DisruptionBench (§6/§7ter) n'est
en realite PAS "public" -- DIII-D, EAST et Alcator C-Mod, les machines qui y
sont referencees, exigent des identifiants institutionnels (verifie via la
documentation de DisruptionPy). Decision utilisateur (AskUserQuestion) :
deriver la verite terrain directement des donnees MAST elles-memes plutot
que de faire confiance a une etiquette externe -- une disruption se
caracterise physiquement par une chute brutale (quelques ms) du courant
plasma, contrairement a la descente lente (dizaines de ms) d'une fin de tir
normale.

Adaptation Helios (critere simplifie, documente comme limite dans
l'interface plutot que masque) : on ne compare pas une vitesse de descente
a un seuil physique absolu (qui varierait selon la machine et le regime),
mais on verifie si le courant, apres son pic, passe sous une fraction de ce
pic en moins de `quench_window_s` secondes -- un critere simple, pas un
detecteur de disruption valide cliniquement (les detecteurs de reference de
la litterature utilisent des criteres plus riches : dI/dt, mode locking,
verrouillage de mode, etc.).
"""
from __future__ import annotations

import numpy as np

MIN_PEAK_KA = 10.0  # en dessous, le tir n'a jamais vraiment forme de plasma courant


def detect_quench(
    time: np.ndarray,
    current: np.ndarray,
    drop_fraction: float = 0.5,
    high_fraction: float = 0.9,
    quench_window_s: float = 0.005,
    min_peak_ka: float = MIN_PEAK_KA,
) -> dict:
    """time (s) et current (kA, peut contenir des NaN de padding) doivent
    avoir la meme longueur. Mesure le temps ECOULE ENTRE deux franchissements
    apres le pic -- `high_fraction*peak` puis `drop_fraction*peak` -- plutot
    qu'un simple pas d'echantillonnage : une chute lente (fin de tir normale)
    traverse ces deux seuils en un temps long meme si chaque pas
    d'echantillonnage est petit, alors qu'un vrai quench les traverse
    quasi instantanement. Retourne :
    {disrupted, t_quench, t_peak, peak_current, i_peak} -- `i_peak` (index
    dans les tableaux nettoyes/tries) permet a l'appelant d'isoler la
    fenetre PRE-quench sans redupliquer la logique de nettoyage.
    """
    time = np.asarray(time, dtype=float)
    current = np.asarray(current, dtype=float)
    valid = np.isfinite(time) & np.isfinite(current)
    time, current = time[valid], current[valid]
    order = np.argsort(time)
    time, current = time[order], current[order]

    abs_current = np.abs(current)
    if len(abs_current) == 0 or np.max(abs_current) < min_peak_ka:
        peak = float(np.max(abs_current)) if len(abs_current) else 0.0
        return {
            "disrupted": False,
            "t_quench": None,
            "t_peak": None,
            "peak_current": peak,
            "i_peak": None,
            "time": time,
            "current": current,
        }

    i_peak = int(np.argmax(abs_current))
    peak = float(abs_current[i_peak])
    t_peak = float(time[i_peak])
    high_threshold = high_fraction * peak
    low_threshold = drop_fraction * peak

    post_current = abs_current[i_peak:]
    post_time = time[i_peak:]

    below_high = post_current < high_threshold
    disrupted = False
    t_quench = None
    if below_high.any():
        j_high = int(np.argmax(below_high))
        t_high = float(post_time[j_high])

        below_low = post_current[j_high:] < low_threshold
        if below_low.any():
            j_low = j_high + int(np.argmax(below_low))
            t_low = float(post_time[j_low])
            if (t_low - t_high) <= quench_window_s:
                disrupted = True
                t_quench = t_low

    return {
        "disrupted": disrupted,
        "t_quench": t_quench,
        "t_peak": t_peak,
        "peak_current": peak,
        "i_peak": i_peak,
        "time": time,
        "current": current,
    }
