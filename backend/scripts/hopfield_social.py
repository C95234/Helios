"""
hopfield_social.py
====================
Démonstration numérique : un réseau de Hopfield appliqué à des groupes
sociaux, dans l'esprit du logiciel de Moussa et Louise (Hélios).

Chaque "neurone" représente un territoire ou un groupe (état +1 = adhère
à la norme / calme, -1 = résiste / mobilisé). Le réseau mémorise des
CONFIGURATIONS SOCIALES passées par la règle de Hebb, puis est capable
de "reconnaître" une configuration à partir d'un signal partiel ou
bruité -- exactement l'idée du roman : des liens qui se renforcent
quand une séquence se répète, formant une mémoire du système.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)


class HopfieldSocial:
    def __init__(self, n_units):
        self.n = n_units
        self.W = np.zeros((n_units, n_units))

    def train(self, patterns):
        """Apprentissage hebbien : mémorise une liste de configurations
        sociales (vecteurs +/-1)."""
        self.W = np.zeros((self.n, self.n))
        for xi in patterns:
            self.W += np.outer(xi, xi)
        self.W /= self.n
        np.fill_diagonal(self.W, 0)

    def energy(self, s):
        return -0.5 * s @ self.W @ s

    def recall(self, s, max_steps=200, record=False, order_mode="random"):
        """Mise à jour asynchrone jusqu'à convergence (plus de changement).
        order_mode='sequential' : ordre fixe 0,1,2,...,n-1 à chaque passage
        order_mode='random'     : ordre re-mélangé à chaque passage (classique)
        """
        s = s.copy()
        history = [self.energy(s)] if record else None
        order = np.arange(self.n)
        for step in range(max_steps):
            if order_mode == "random":
                rng.shuffle(order)
            changed = False
            for i in order:
                h_i = self.W[i] @ s
                new_si = 1 if h_i >= 0 else -1
                if new_si != s[i]:
                    s[i] = new_si
                    changed = True
                if record:
                    history.append(self.energy(s))
            if not changed:
                break
        return (s, history) if record else s


def corrupt(pattern, n_flip, rng):
    s = pattern.copy()
    idx = rng.choice(len(s), size=n_flip, replace=False)
    s[idx] *= -1
    return s


# ---------------------------------------------------------------------
# 1. DEMO PEDAGOGIQUE : 4 territoires, 2 configurations sociales connues
# ---------------------------------------------------------------------
print("=" * 70)
print("1. Petite démo (4 territoires, 2 configurations mémorisées)")
print("=" * 70)

societe_apaisee   = np.array([ 1,  1,  1,  1])   # tout le monde calme
fracture_nordsud  = np.array([ 1,  1, -1, -1])   # régions 3-4 mobilisées

net = HopfieldSocial(n_units=4)
net.train([societe_apaisee, fracture_nordsud])
print("Matrice de poids (liens renforcés par Hebb) :\n", net.W)

corrupted = np.array([-1, 1, -1, -1])  # région 1 mal rapportée
print(f"\nÉtat de départ (corrompu) : {corrupted}, énergie = {net.energy(corrupted):.2f}")

recovered_seq, hist = net.recall(corrupted, record=True, order_mode="sequential")
print(f"[Ordre séquentiel 1→2→3→4] État reconnu : {recovered_seq}, "
      f"énergie = {net.energy(recovered_seq):.2f}")
print(f"  Correspond à 'fracture nord-sud' : {np.array_equal(recovered_seq, fracture_nordsud)}")

recovered_rand = net.recall(corrupted, order_mode="random")
print(f"[Ordre aléatoire]              État reconnu : {recovered_rand}, "
      f"énergie = {net.energy(recovered_rand):.2f}")
is_antipattern = np.array_equal(recovered_rand, -societe_apaisee)
print(f"  Correspond au NÉGATIF de 'société apaisée' (attracteur parasite) : {is_antipattern}")
print("  -> L'ordre de mise à jour peut faire converger vers un état stable")
print("     différent : le négatif exact d'un motif mémorisé est TOUJOURS,")
print("     lui aussi, un attracteur — un phénomène connu et documenté des")
print("     réseaux de Hopfield, pas un défaut de cette implémentation.")

# ---------------------------------------------------------------------
# 2. CAPACITE : combien de configurations un groupe de taille N peut-il
#    retenir de façon fiable avant que le rappel échoue ?
# ---------------------------------------------------------------------
print()
print("=" * 70)
print("2. Test empirique de la capacité de mémoire (N=100)")
print("=" * 70)

N = 100
n_trials = 30
flip_fraction = 0.15  # 15% des bits corrompus au départ

p_values = list(range(1, 26))
success_rates = []

for p in p_values:
    successes = 0
    for trial in range(n_trials):
        patterns = [rng.choice([-1, 1], size=N) for _ in range(p)]
        net = HopfieldSocial(n_units=N)
        net.train(patterns)
        target = patterns[0]
        n_flip = max(1, int(flip_fraction * N))
        s0 = corrupt(target, n_flip, rng)
        s_final = net.recall(s0)
        # succès si le rappel retombe exactement sur le motif d'origine
        if np.array_equal(s_final, target):
            successes += 1
    rate = successes / n_trials
    success_rates.append(rate)
    print(f"  p={p:3d} motifs stockés -> taux de rappel correct = {rate:.2f}")

theoretical_ags = 0.138 * N
theoretical_hopfield82 = N / (4 * np.log(N))
print(f"\nSeuil théorique (Amit-Gutfreund-Sompolinsky, 1985) : {theoretical_ags:.1f} motifs")
print(f"Estimation historique (Hopfield, 1982)             : {theoretical_hopfield82:.1f} motifs")

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

axes[0].plot(range(len(hist)), hist, color="#e85a2a", marker="o", markersize=3)
axes[0].set_title("Énergie pendant le rappel (exemple à 4 territoires)")
axes[0].set_xlabel("Étapes de mise à jour")
axes[0].set_ylabel("Énergie E(s)")
axes[0].grid(alpha=0.3)

axes[1].plot(p_values, success_rates, color="#3fa9dc", marker="o")
axes[1].axvline(theoretical_ags, color="#e85a2a", linestyle="--",
                 label=f"Seuil AGS 1985 ≈ {theoretical_ags:.0f}")
axes[1].axvline(theoretical_hopfield82, color="grey", linestyle=":",
                 label=f"Estimation Hopfield 1982 ≈ {theoretical_hopfield82:.0f}")
axes[1].set_title(f"Capacité de mémoire empirique (N={N})")
axes[1].set_xlabel("Nombre de configurations mémorisées (p)")
axes[1].set_ylabel("Taux de rappel correct")
axes[1].legend()
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig("hopfield_social_results.png", dpi=150)
print("\nFigure enregistrée dans hopfield_social_results.png")
