"""Modele reduit 0-D de bilan de puissance et seuil d'ignition (critere de
Lawson) -- cahier des charges Helios §7quater, troisieme domaine
d'application. Modele standard de la discipline (Freidberg, 2007 ; Wesson,
2004), utilise pour l'enseignement et la conception preliminaire des
reacteurs a fusion -- pas une simulation complete de magnetohydrodynamique,
pas une simulation de reacteur reel precis.

L'energie contenue dans le plasma W evolue selon :
    dW/dt = P_chauffage + P_fusion(T) - W/tau_E - P_rayonnement(T)
avec W = (3/2) n T (densite d'energie, n suppose constant -- approximation
standard du modele 0-D). Unites "pratiques" du domaine (identiques a celles
des formules sources, pour rester fidele aux references) : T en keV, n en
cm^-3, puissances en W/cm^3, temps en secondes.

P_fusion(T) est la puissance d'auto-chauffage par les particules alpha
(melange D-T 50/50, n_D=n_T=n/2), utilisant la reactivite <sigma*v>(T)
parametree par Bosch & Hale (1992, Table VII) -- la formule empirique de
reference du domaine, valide 0.2-100 keV pour D-T. Seule l'energie alpha
(3.5 MeV sur les 17.6 MeV totaux) chauffe le plasma ; le neutron (14.1 MeV)
s'echappe sans interagir.

P_rayonnement(T) est le rayonnement de freinage (bremsstrahlung),
formulaire standard (NRL Plasma Formulary) : P_brem = 1.69e-32 * n^2 *
sqrt(T) (W/cm^3, Z_eff=1).

Structure de bifurcation (le coeur du §7quater) : a chauffage externe fixe,
les courbes de gain (P_chauffage + P_fusion) et de perte (W/tau_E +
P_rayonnement), tracees en fonction de T, se croisent en un point stable a
basse temperature (une perturbation y est amortie). Si le chauffage externe
augmente lentement, ce point stable remonte en temperature jusqu'a
rencontrer un point d'equilibre instable associe -- les deux fusionnent et
disparaissent (bifurcation noeud-col, meme structure mathematique qu'au
§5.6quater/quinquies du Journal de recherche, mais ici c'est le vrai
critere d'ignition de Lawson (1957), pas une transposition sociale) :
au-dela, plus aucun equilibre stable n'existe et T s'emballe vers
l'ignition. Le chauffage externe joue exactement le role de mu(t) dans le
modele saddle-node deja construit pour la validation de H1
(`lyapunov_precedence.py`) : une rampe lente vers le seuil, testee par
Monte-Carlo avec bruit.
"""
from __future__ import annotations

import numpy as np

KEV_TO_JOULE = 1.602176634e-16  # 1 keV = 1.602...e-16 J
E_ALPHA_JOULE = 3.5e6 * 1.602176634e-19  # energie de la particule alpha (3.5 MeV)

# Bosch & Hale (1992), Table VII -- parametrage D-T, valide 0.2-100 keV.
_B_G = 34.3827  # keV^0.5, constante de Gamow D-T
_M_RC2 = 1124656.0  # keV, energie de masse reduite D-T
_C1, _C2, _C3, _C4, _C5, _C6, _C7 = (
    1.17302e-9,
    1.51361e-2,
    7.51886e-2,
    4.60643e-3,
    1.35000e-2,
    -1.06750e-4,
    1.36600e-5,
)

_BREM_CONST = 1.69e-32  # W cm^3 keV^-0.5 (formulaire NRL, Z_eff=1)

# Parametres illustratifs du modele -- PAS ceux d'une machine reelle precise
# (voir disclaimer §7quater). Choisis pour qu'un point d'equilibre stable
# existe a ILLUSTRATIVE_P_HEAT_BASE et qu'un chauffage croissant a
# ILLUSTRATIVE_IGNITED_HEATING_RATE traverse la bifurcation en quelques
# secondes de temps simule -- verifie numeriquement par
# `backend/tests/test_plasma_power_balance.py` (30/30 realisations
# "ignited" atteignent l'ignition, 0/30 "stable" ne l'atteignent jamais).
# Seule source de verite pour ces constantes : reutilisees telles quelles
# par `routers/plasma.py` et par les tests, jamais redupliquees.
ILLUSTRATIVE_N_CM3 = 3e14
ILLUSTRATIVE_TAU_E_S = 2.0
ILLUSTRATIVE_P_HEAT_BASE = 0.05
ILLUSTRATIVE_IGNITED_HEATING_RATE = 0.03
ILLUSTRATIVE_STABLE_HEATING_RATE = 0.0
ILLUSTRATIVE_T_MAX_S = 9.0


def reactivity_dt(t_kev: np.ndarray) -> np.ndarray:
    """<sigma*v> (cm^3/s) pour la reaction D-T, Bosch & Hale (1992)."""
    t = np.clip(np.asarray(t_kev, dtype=float), 0.2, 100.0)
    theta = t / (
        1
        - (t * (_C2 + t * (_C4 + t * _C6))) / (1 + t * (_C3 + t * (_C5 + t * _C7)))
    )
    xi = (_B_G**2 / (4 * theta)) ** (1 / 3)
    return _C1 * theta * np.sqrt(xi / (_M_RC2 * t**3)) * np.exp(-3 * xi)


def fusion_power_density(t_kev: np.ndarray, n_cm3: float) -> np.ndarray:
    """Puissance d'auto-chauffage alpha (W/cm^3) -- melange D-T 50/50."""
    return 0.25 * n_cm3**2 * reactivity_dt(t_kev) * E_ALPHA_JOULE


def bremsstrahlung_density(t_kev: np.ndarray, n_cm3: float) -> np.ndarray:
    """Rayonnement de freinage (W/cm^3), formulaire NRL, Z_eff=1."""
    t = np.clip(np.asarray(t_kev, dtype=float), 1e-6, None)
    return _BREM_CONST * n_cm3**2 * np.sqrt(t)


def confinement_loss_density(t_kev: np.ndarray, n_cm3: float, tau_e_s: float) -> np.ndarray:
    """Perte par confinement W/tau_E (W/cm^3), avec W = (3/2) n T."""
    energy_density = 1.5 * n_cm3 * np.asarray(t_kev, dtype=float) * KEV_TO_JOULE
    return energy_density / tau_e_s


def net_power_density(t_kev: np.ndarray, n_cm3: float, tau_e_s: float, p_heat: float = 0.0) -> np.ndarray:
    """Gain moins perte (W/cm^3) a chauffage externe p_heat fixe -- sert a
    localiser les points d'equilibre (racines) et la bifurcation noeud-col."""
    return (
        p_heat
        + fusion_power_density(t_kev, n_cm3)
        - confinement_loss_density(t_kev, n_cm3, tau_e_s)
        - bremsstrahlung_density(t_kev, n_cm3)
    )


def find_critical_heating(
    n_cm3: float,
    tau_e_s: float,
    t_grid: np.ndarray | None = None,
) -> float:
    """Chauffage externe critique (W/cm^3) au-dela duquel `net_power_density`
    n'a plus aucune racine stable sur `t_grid` -- le point de bifurcation
    noeud-col. Trouve par balayage : pour chaque p_heat croissant, cherche si
    net_power_density(T) change de signe de + a - (equilibre stable) quelque
    part sur la grille ; retourne le plus petit p_heat pour lequel ce n'est
    plus le cas."""
    if t_grid is None:
        t_grid = np.linspace(0.5, 60.0, 4000)
    net_at_zero = net_power_density(t_grid, n_cm3, tau_e_s, p_heat=0.0)
    # p_heat_hi : borne superieure grossiere garantissant l'absence d'equilibre stable.
    p_heat_lo, p_heat_hi = 0.0, float(np.max(-net_at_zero)) + 1.0
    while not _has_stable_equilibrium(t_grid, n_cm3, tau_e_s, p_heat_hi):
        p_heat_hi /= 2
        if p_heat_hi < 1e-12:
            return 0.0
    # p_heat_hi est maintenant le plus petit multiple de 2 testé sans equilibre ;
    # ajuste par dichotomie entre le dernier "stable" (p_heat_hi*2) et p_heat_hi.
    lo, hi = p_heat_hi, p_heat_hi * 2
    for _ in range(60):
        mid = (lo + hi) / 2
        if _has_stable_equilibrium(t_grid, n_cm3, tau_e_s, mid):
            lo = mid
        else:
            hi = mid
    return lo


def _has_stable_equilibrium(t_grid: np.ndarray, n_cm3: float, tau_e_s: float, p_heat: float) -> bool:
    net = net_power_density(t_grid, n_cm3, tau_e_s, p_heat=p_heat)
    # Equilibre stable : net passe de + (basse T) a - (haute T) en croisant zero
    # (une perturbation vers le haut voit alors la perte l'emporter -- retour a l'equilibre).
    sign = np.sign(net)
    crossings = np.where(np.diff(sign) < 0)[0]
    return len(crossings) > 0


def simulate_power_balance(
    n_cm3: float,
    tau_e_s: float,
    heating_rate: float,
    p_heat_base: float = 0.0,
    dt: float = 0.002,
    t_max: float = ILLUSTRATIVE_T_MAX_S,
    sigma_noise: float = 0.03,
    seed: int = 0,
    t0_kev: float = 1.5,
    ignition_t_kev: float = 30.0,
) -> dict:
    """Integre dT/dt (Euler-Maruyama, sur le modele de `simulate_saddle_node`
    dans `lyapunov_precedence.py`) avec un chauffage externe P_chauffage(t) =
    p_heat_base + heating_rate * t -- `heating_rate` joue le meme role que
    mu_rate dans le modele saddle-node deja construit pour H1 : une rampe
    lente vers le seuil de bifurcation, avec bruit. `heating_rate=0` donne
    un scenario de controle qui reste pres de l'equilibre stable associe a
    `p_heat_base` ; un `heating_rate` qui traverse
    `find_critical_heating(n_cm3, tau_e_s)` dans `t_max` donne un scenario
    qui s'emballe vers l'ignition.

    Retourne {"times", "temperatures", "t_ignition"} -- `t_ignition=None`
    si `ignition_t_kev` n'est jamais atteint dans `t_max` (le point instable
    associe a `p_heat_base` sert de reference : `ignition_t_kev` doit lui
    etre nettement superieur pour signaler un vrai emballement, pas juste
    une fluctuation autour de l'equilibre stable)."""
    rng = np.random.default_rng(seed)
    n_steps = int(t_max / dt)
    heat_capacity = 1.5 * n_cm3 * KEV_TO_JOULE  # J/(cm^3.keV) -- dW = heat_capacity * dT

    temperatures = np.empty(n_steps)
    temperatures[0] = t0_kev
    t_ignition = None
    steps_run = n_steps

    for k in range(1, n_steps):
        t = k * dt
        p_heat = p_heat_base + heating_rate * t
        dT = net_power_density(temperatures[k - 1], n_cm3, tau_e_s, p_heat=p_heat) / heat_capacity
        noise = sigma_noise * np.sqrt(dt) * rng.normal()
        temperatures[k] = max(temperatures[k - 1] + dT * dt + noise, 0.05)
        if t_ignition is None and temperatures[k] >= ignition_t_kev:
            t_ignition = t
            steps_run = k + 1
            break

    temperatures = temperatures[:steps_run]
    times = np.arange(steps_run) * dt
    return {"times": times, "temperatures": temperatures, "t_ignition": t_ignition}
