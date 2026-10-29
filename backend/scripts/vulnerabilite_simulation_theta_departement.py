"""Usage (depuis backend/) :  python -m scripts.vulnerabilite_simulation_theta_departement

Étude de simulation (aucune donnée réelle) : que permet l'identité de la proposition 8 département par département, avec 105 semaines ?
Calibrage des comptes sur les ordres de grandeur de la fiche de données (comptes hebdomadaires médians ~17-19, D9 ~57-90).
"""
import numpy as np

from app.vulnerabilite.multicanal import taux_detection

T = 105


def simuler_dep(rng, taille, th_u, th_s, R=0.8, amplitude=4.0):
    t = np.arange(T)
    vague = sum(np.exp(-0.5 * ((t - c) / 5.0) ** 2) for c in (14, 45, 80))
    mu = taille * (1.0 + amplitude * vague) * (1 - R)
    y = np.full(1, taille)
    vrai = np.zeros(T)
    for i in range(T):
        y = rng.poisson(mu[i] + R * y).astype(float)
        vrai[i] = y[0]
    ou = rng.binomial(vrai.astype(int), th_u).astype(float)
    os_ = rng.binomial(vrai.astype(int), th_s).astype(float)
    return ou, os_


def theta_dep(ou, os_):
    return taux_detection(ou[:, None], os_[:, None]), taux_detection(os_[:, None], ou[:, None])


rng = np.random.default_rng(0)
print("niveau moyen vrai | θ vrai (urg, sos) | part θ̂ dans ]0,1[ | médiane θ̂ | IQR θ̂ (urg) | corr. entre moitiés")
for taille, (tu, ts) in [(60, (0.4, 0.6)), (150, (0.4, 0.6)), (400, (0.4, 0.6)), (150, (0.2, 0.3)), (150, (0.7, 0.5))]:
    est_u, est_s, dedans, ou_moy = [], [], [], []
    for _ in range(400):
        ou, os_ = simuler_dep(rng, taille, tu, ts)
        a, b = theta_dep(ou, os_)
        est_u.append(a)
        est_s.append(b)
        dedans.append(0 < a < 1 and 0 < b < 1)
        ou_moy.append(ou.mean())
    q = np.percentile(est_u, [25, 50, 75])
    print(f"{taille:4d} (comptes urgences moyens ~{np.mean(ou_moy):5.1f}) | ({tu},{ts}) | {np.mean(dedans):.2f} | {q[1]:.2f} | [{q[0]:.2f} ; {q[2]:.2f}] | -")

# fiabilité inter-moitiés : 37 départements, θ_i variables, tailles variées
print("\nFiabilité entre moitiés (37 départements, θ_i tirés entre 0,2 et 0,8, tailles log-uniformes 40-300) :")
cors, dedans_tot = [], []
for rep in range(100):
    th_u = rng.uniform(0.2, 0.8, 37)
    th_s = rng.uniform(0.2, 0.8, 37)
    tailles = np.exp(rng.uniform(np.log(40), np.log(300), 37))
    h1, h2, tous = [], [], []
    for i in range(37):
        ou, os_ = simuler_dep(rng, tailles[i], th_u[i], th_s[i])
        h1.append(theta_dep(ou[:52], os_[:52])[0])
        h2.append(theta_dep(ou[52:], os_[52:])[0])
        tous.append(theta_dep(ou, os_)[0])
    cors.append(np.corrcoef(h1, h2)[0, 1])
    dedans_tot.append(np.mean([0 < x < 1 for x in tous]))
print("corr. θ̂ moitié 1 / moitié 2 : médiane", np.round(np.median(cors), 2), "5e-95e centile", np.round(np.percentile(cors, [5, 95]), 2))
print("part des départements avec θ̂ (urgences) dans ]0,1[ sur 105 semaines : médiane", np.round(np.median(dedans_tot), 2), "5e centile", np.round(np.percentile(dedans_tot, 5), 2))
