/**
 * Explications des outils statistiques utilisés par Hélios -- cahier des charges §3 :
 * "Mode expert : la formule, la méthode statistique, les valeurs numériques, les
 * références bibliographiques." Contenu centralisé pour rester cohérent partout où
 * un résultat s'appuie sur l'une de ces méthodes (démo, analyse, H1, H2).
 */
export const METHODS = {
  rolling_variance: {
    label: "Variance glissante",
    simple:
      "On regarde, sur une fenêtre de quelques points qui avance dans le temps, à quel point la série s'écarte de sa propre moyenne récente. Plus cet écart grandit, plus le système « tremble ».",
    formula: "Var_w(x_t) = variance des points [x_{t-w+1}, ..., x_t]",
    detail:
      "Fenêtre glissante de taille w, variance non biaisée (ddof=1, comme pandas.Series.rolling(w).var()). Une hausse de la variance glissante avant une bascule est le signal précurseur le plus documenté de la littérature sur le ralentissement critique.",
    reference: "Scheffer et al., Nature 2009 ; Dakos et al., PLOS ONE 2012.",
  },
  rolling_ac1: {
    label: "Autocorrélation à lag-1 (AC1)",
    simple:
      "On mesure, sur la même fenêtre glissante, à quel point chaque valeur ressemble à celle qui la précède immédiatement. Si le système « oublie » de plus en plus lentement ses propres à-coups, c'est le signe classique qu'il approche d'un point de bascule.",
    formula: "AC1_w(x_t) = Corr(x_{t-w+1..t-1}, x_{t-w+2..t})",
    detail:
      "Calculée avec statsmodels.tsa.stattools.acf (nlags=1) sur chaque fenêtre glissante -- la même fonction de référence utilisée pour valider l'implémentation à ±1e-6 près. Un ralentissement de la dynamique interne du système se traduit mécaniquement par une AC1 plus proche de 1.",
    reference: "Scheffer et al., Nature 2009 ; Dakos et al., PLOS ONE 2012.",
  },
  kendall_tau: {
    label: "Tendance (tau de Kendall)",
    simple:
      "Une fois la variance ou l'AC1 calculée point par point, on se demande si elle a une vraie tendance à la hausse dans le temps, ou si elle monte et descend sans direction claire.",
    formula: "τ = (paires concordantes − paires discordantes) / [n(n−1)/2]",
    detail:
      "Corrélation de rang entre l'indicateur et le temps (scipy.stats.kendalltau). τ proche de +1 = tendance à la hausse quasi parfaite ; proche de 0 = pas de tendance. Ce tau seul ne suffit jamais à conclure : voir le test par données de substitution ci-dessous.",
    reference: "Kendall, Biometrika 1938.",
  },
  surrogate_test: {
    label: "Test par données de substitution (surrogates)",
    simple:
      "Une tendance à la hausse peut arriver par pur hasard sur une série bruitée. Pour vérifier que ce n'est pas le cas, on fabrique des milliers de fausses versions de la même série -- avec le même « bruit de fond », mais sans tendance -- et on regarde si la vraie tendance dépasse presque toutes les fausses.",
    formula: "p = #{τ_substitution ≥ τ_observé} / nombre de substitutions",
    detail:
      "Les séries de substitution sont générées par randomisation de phase (on garde le spectre de puissance de Fourier -- donc la « couleur » du bruit -- mais on détruit toute tendance ou structure non linéaire en tirant des phases aléatoires). C'est la méthode standard de la littérature EWS, pas une invention propre à Hélios.",
    reference: "Theiler et al., Physica D 1992 ; méthode de substitution appliquée aux EWS : Dakos et al., PLOS ONE 2012.",
  },
  morans_i: {
    label: "Indice de Moran",
    simple:
      "Version géographique de la même idée : est-ce que des territoires voisins se ressemblent plus entre eux que ce que le hasard produirait ? Un indice élevé veut dire que les voisins évoluent ensemble -- une synchronisation spatiale.",
    formula: "I = (N / S₀) × [Σᵢⱼ wᵢⱼ(xᵢ−x̄)(xⱼ−x̄)] / Σᵢ(xᵢ−x̄)²",
    detail:
      "N = nombre de territoires, wᵢⱼ = 1 si i et j sont voisins (0 sinon), S₀ = somme de tous les wᵢⱼ, x̄ = moyenne. Implémentation vérifiée par un exemple calculé à la main (chaîne de 4 nœuds, I = 1/3 exact) et par des propriétés connues (damier → I très négatif, gradient → I très positif).",
    reference: "Moran, Biometrika 1950.",
  },
  permutation_test: {
    label: "Test par permutation (indice de Moran)",
    simple:
      "Équivalent géographique du test par substitution : on redistribue les valeurs au hasard entre les territoires, en gardant le réseau de voisinage fixe, et on regarde si l'indice de Moran observé dépasse presque toutes les versions mélangées.",
    formula: "p = #{I_permutation ≥ I_observé} / nombre de permutations",
    detail:
      "Sous l'hypothèse nulle (aucune structure spatiale réelle), l'espérance théorique de l'indice de Moran vaut −1/(N−1) -- propriété vérifiée dans les tests automatisés d'Hélios.",
    reference: "Méthode standard d'inférence pour l'indice de Moran (voir Cliff & Ord, 1981).",
  },
  h3_joint: {
    label: "Statistique jointe H3 (bootstrap couplé par période)",
    simple:
      "On combine le signal temporel national et le signal spatial départemental d'un même phénomène en une seule note, puis on compare cette note à celles obtenues sur chaque trimestre des 26 dernières années. Si la note du phénomène dépasse presque toutes les autres, c'est que les deux signaux sont inhabituels EN MÊME TEMPS -- pas juste l'un ou l'autre séparément.",
    formula: "T = -2·[ln(p_temporel) + ln(p_spatial)] ; p_joint = #{T_historique ≥ T_observé} / nb trimestres",
    detail:
      "p_temporel et p_spatial sont des p-values de RANG : la proportion de trimestres historiques (2000-2026) où le signal correspondant était au moins aussi extrême. La loi nulle de T n'est PAS générée par des surrogates synthétiques : elle est calculée sur les VRAIES paires historiques (tendance nationale, indice de Moran) du même trimestre -- ce qui préserve automatiquement toute corrélation réelle entre les deux, sans supposer l'indépendance qu'interdit le §5.6 pour la loi du χ² théorique.",
    reference: "Fisher, Statistical Methods for Research Workers, 1925 (combinaison) ; calibration empirique par historique réel plutôt que par surrogates -- choix méthodologique propre à Hélios pour H3, documenté comme tel.",
  },
  moran_trend: {
    label: "Tendance de l'indice de Moran dans le temps",
    simple:
      "Une fois l'indice de Moran calculé à chaque trimestre, on applique exactement le même test de tendance que pour la variance et l'AC1 (tau de Kendall + substitutions) -- mais sur cette série d'indices spatiaux plutôt que sur la série brute.",
    formula: "Même méthode que le test par substitution ci-dessus, appliquée à la série (I_t) déjà calculée.",
    detail:
      "Une hausse significative de l'indice de Moran dans le temps indiquerait une synchronisation spatiale croissante -- le signal précurseur spatial décrit au §5.2 du cahier des charges.",
    reference: "Dakos et al., PLOS ONE 2012 (principe de substitution appliqué à un indicateur dérivé).",
  },
};
