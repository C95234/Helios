"""Drapeaux de garde-fou : situations où l'estimation ne doit pas être lue au pied de la lettre
(cahier des charges §3.1 et §8 ; pièges de la note).

Chaque drapeau est un fait vérifiable sur l'entrée ; aucun n'invalide silencieusement un résultat, ils sont
rapportés avec lui. Les seuils marqués PROVISOIRE ne sont pas fixés par la note et doivent l'être dans le
pré-enregistrement avant toute évaluation sur données réelles.
"""
from __future__ import annotations

from dataclasses import dataclass, fields

import numpy as np

from .incertitude import SEUIL_PEU_D_UNITES

#: Φ̂ en dessous duquel l'estimation plafonne (note, section 5 : « plancher » pour Φ ≲ 2).
SEUIL_PLANCHER_PHI = 2.0
#: PROVISOIRE : écart absolu entre estimateurs croisés au-delà duquel on déclare une asymétrie.
SEUIL_ASYMETRIE = 0.10


@dataclass(frozen=True)
class Drapeaux:
    plancher: bool = False  # Φ̂ < 2 : « très vulnérable », sans valeur précise (piège 4)
    peu_d_unites: bool = False  # < 30 unités : intervalles trop optimistes (piège 6)
    coupure_trop_basse: bool = False  # coupure sous le seuil estimé m̂₊ : fait paraître la société plus sûre (piège 1)
    theta_hors_intervalle: bool = False  # θ̂ hors ]0, 1[ : hypothèse 2 violée ou modèle mal spécifié
    asymetrie_croisee: bool = False  # estimateurs croisés incohérents : boucle de surveillance ou dépendance entre canaux
    pas_de_seuil: bool = False  # ĉ ≤ 0 : aucun seuil détecté, c'est R qui compte
    pas_d_etat_calme: bool = False  # R̂ ≥ 1 : plus d'état calme

    def liste(self) -> list[str]:
        """Noms des drapeaux levés."""
        return [f.name for f in fields(self) if getattr(self, f.name)]

    @property
    def aucun(self) -> bool:
        return not self.liste()


def evaluer_garde_fous(
    *,
    phi: float | None = None,
    c: float | None = None,
    R: float | None = None,
    n_unites: int | None = None,
    seuil_coupure: float | None = None,
    m_haut_estime: float | None = None,
    theta: float | None = None,
    ecart_croise: float | None = None,
    seuil_asymetrie: float = SEUIL_ASYMETRIE,
) -> Drapeaux:
    """Lève les drapeaux applicables aux informations fournies (les arguments absents ne lèvent rien)."""
    def present(v):
        return v is not None and not (isinstance(v, float) and np.isnan(v))

    return Drapeaux(
        plancher=present(phi) and np.isfinite(phi) and 0.0 < phi < SEUIL_PLANCHER_PHI,
        peu_d_unites=n_unites is not None and n_unites < SEUIL_PEU_D_UNITES,
        coupure_trop_basse=present(seuil_coupure) and present(m_haut_estime) and seuil_coupure < m_haut_estime,
        theta_hors_intervalle=present(theta) and not (0.0 < theta < 1.0),
        asymetrie_croisee=present(ecart_croise) and abs(ecart_croise) > seuil_asymetrie,
        pas_de_seuil=present(c) and c <= 0,
        pas_d_etat_calme=present(R) and R >= 1.0,
    )
