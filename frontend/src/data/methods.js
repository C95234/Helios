/**
 * Explications des outils statistiques utilisés par Hélios -- cahier des charges §3, §5, §12.
 *
 * §3 (version révisée) : le mode expert doit afficher la DÉMONSTRATION complète,
 * pas seulement la formule finale, rendue en LaTeX (KaTeX) -- et chaque formule
 * doit citer sa référence exacte (§12), pas juste un nom d'auteur.
 *
 * `derivationSteps` (quand présent) reprend le contenu obligatoire fourni par
 * le cahier des charges lui-même (§5.1bis, §5.6) -- verbatim, pas reformulé.
 * Les méthodes qui n'ont pas de démonstration imposée par le cahier des
 * charges (Kendall, Moran, permutation) gardent une explication plus courte,
 * mais toujours avec la formule en LaTeX et une référence exacte.
 */
export const METHODS = {
  rolling_variance: {
    label: "Variance glissante",
    simple:
      "On regarde, sur une fenêtre de quelques points qui avance dans le temps, à quel point la série s'écarte de sa propre moyenne récente. Plus cet écart grandit, plus le système « tremble ».",
    formula: "\\text{Var}_w(x_t)",
    derivationSteps: [
      { text: "Soit un système dynamique au voisinage d'un équilibre stable $x^*$ :" },
      { tex: "dx = f(x,\\mu)\\,dt + \\sigma\\,dW", block: true },
      { text: "En linéarisant autour de $x^*$ :" },
      {
        tex: "dx \\approx \\lambda(\\mu)(x-x^*)\\,dt + \\sigma\\,dW, \\qquad \\lambda(\\mu) = \\frac{\\partial f}{\\partial x}\\Big|_{x^*} < 0",
        block: true,
      },
      { text: "C'est un processus d'Ornstein-Uhlenbeck. Sa variance stationnaire et son autocorrélation à lag-1 (temps discret, pas $\\Delta t$) ont une forme connue :" },
      {
        tex: "\\text{Var}(x) = \\frac{\\sigma^2}{2|\\lambda|}, \\qquad \\text{AC1} = e^{\\lambda \\Delta t} \\approx 1 + \\lambda \\Delta t",
        block: true,
      },
      {
        text: "Près d'une bifurcation (fold/transcritique), $\\lambda \\to 0^-$ : le dénominateur de la variance s'effondre (variance $\\to \\infty$) et AC1 $\\to 1$. C'est ce mécanisme — pas une corrélation empirique observée a posteriori — qui justifie que ces deux indicateurs montent avant une rupture.",
      },
    ],
    detail:
      "En pratique : fenêtre glissante de taille w, variance non biaisée (ddof=1, comme pandas.Series.rolling(w).var()) -- estimateur empirique de Var(x) ci-dessus sur une fenêtre finie.",
    references: ["Ives, A. R. (1995). « Measuring resilience in stochastic systems. » Ecological Monographs, 65(2), 217–233.", "Scheffer, M. et al. (2009). « Early-warning signals for critical transitions. » Nature, 461, 53–59."],
  },
  rolling_ac1: {
    label: "Autocorrélation à lag-1 (AC1)",
    simple:
      "On mesure, sur la même fenêtre glissante, à quel point chaque valeur ressemble à celle qui la précède immédiatement. Si le système « oublie » de plus en plus lentement ses propres à-coups, c'est le signe classique qu'il approche d'un point de bascule.",
    formula: "\\text{AC1}_w(x_t) = \\text{Corr}(x_t, x_{t-1})",
    derivationSteps: [
      { text: "Même dérivation que la variance glissante (processus d'Ornstein-Uhlenbeck linéarisé près de l'équilibre) :" },
      {
        tex: "dx \\approx \\lambda(\\mu)(x-x^*)\\,dt + \\sigma\\,dW, \\qquad \\lambda(\\mu) < 0",
        block: true,
      },
      {
        tex: "\\text{AC1} = e^{\\lambda \\Delta t} \\approx 1 + \\lambda \\Delta t",
        block: true,
      },
      {
        text: "Près d'une bifurcation, $\\lambda \\to 0^-$ donc AC1 $\\to 1$ : le système « oublie » de plus en plus lentement ses perturbations. Mécanisme dynamique, pas coïncidence statistique.",
      },
    ],
    detail:
      "Calculée avec statsmodels.tsa.stattools.acf (nlags=1) sur chaque fenêtre glissante -- la même fonction de référence utilisée pour valider l'implémentation à ±1e-6 près (§11).",
    references: ["Ives, A. R. (1995). « Measuring resilience in stochastic systems. » Ecological Monographs, 65(2), 217–233.", "Scheffer, M. et al. (2009). « Early-warning signals for critical transitions. » Nature, 461, 53–59."],
  },
  kendall_tau: {
    label: "Tendance (tau de Kendall)",
    simple:
      "Une fois la variance ou l'AC1 calculée point par point, on se demande si elle a une vraie tendance à la hausse dans le temps, ou si elle monte et descend sans direction claire.",
    formula: "\\tau = \\frac{n_c - n_d}{n(n-1)/2}",
    detail:
      "$n_c$ = paires concordantes, $n_d$ = paires discordantes, entre l'indicateur et le temps (scipy.stats.kendalltau). $\\tau$ proche de $+1$ = tendance à la hausse quasi parfaite ; proche de 0 = pas de tendance. Ce $\\tau$ seul ne suffit jamais à conclure : voir le test par données de substitution (§5.4).",
    references: ["Kendall, M. G. (1938). « A New Measure of Rank Correlation. » Biometrika, 30(1/2), 81–93."],
  },
  surrogate_test: {
    label: "Test par données de substitution (surrogates)",
    simple:
      "Une tendance à la hausse peut arriver par pur hasard sur une série bruitée. Pour vérifier que ce n'est pas le cas, on fabrique des milliers de fausses versions de la même série -- avec le même « bruit de fond », mais sans tendance -- et on regarde si la vraie tendance dépasse presque toutes les fausses.",
    formula: "p = \\frac{\\#\\{\\tau_{\\text{substitution}} \\geq \\tau_{\\text{observé}}\\}}{M}",
    detail:
      "Les séries de substitution sont générées par randomisation de phase (Theiler et al., 1992) : on garde le spectre de puissance de Fourier -- donc la « couleur » du bruit -- mais on détruit toute tendance ou structure non linéaire en tirant des phases aléatoires. C'est la méthode standard de la littérature EWS (§5.4), pas une invention propre à Hélios.",
    references: ["Theiler, J. et al. (1992). « Testing for nonlinearity in time series: the method of surrogate data. » Physica D, 58(1-4), 77–94.", "Dakos, V. et al. (2012). « Methods for Detecting Early Warnings of Critical Transitions in Time Series. » PLoS ONE, 7(7), e41010."],
  },
  morans_i: {
    label: "Indice de Moran",
    simple:
      "Version géographique de la même idée : est-ce que des territoires voisins se ressemblent plus entre eux que ce que le hasard produirait ? Un indice élevé veut dire que les voisins évoluent ensemble -- une synchronisation spatiale.",
    formula:
      "I_t = \\frac{N}{\\sum_{i,j} w_{ij}} \\cdot \\frac{\\sum_{i,j} w_{ij}(x_i-\\bar{x})(x_j-\\bar{x})}{\\sum_i (x_i-\\bar{x})^2}",
    detail:
      "$N$ = nombre de territoires, $w_{ij}=1$ si $i$ et $j$ sont voisins (0 sinon), $\\bar{x}$ = moyenne. Une hausse de $I_t$ dans le temps indique une synchronisation croissante entre territoires voisins (§5.2). Implémentation vérifiée par un exemple calculé à la main (chaîne de 4 nœuds, $I=1/3$ exact) et par des propriétés connues (damier → $I$ très négatif, gradient → $I$ très positif).",
    references: ["Moran, P. A. P. (1950). « Notes on Continuous Stochastic Phenomena. » Biometrika, 37(1/2), 17–23.", "Dakos, V. et al. (2010). « Spatial correlation as leading indicator of catastrophic shifts. » Theoretical Ecology, 3, 163–174.", "MacLaren, N. G., Aihara, K., & Masuda, N. (2025). « Applicability of spatial early warning signals to complex network dynamics. » Journal of the Royal Society Interface, 22(226), 20240696."],
  },
  permutation_test: {
    label: "Test par permutation (indice de Moran)",
    simple:
      "Équivalent géographique du test par substitution : on redistribue les valeurs au hasard entre les territoires, en gardant le réseau de voisinage fixe, et on regarde si l'indice de Moran observé dépasse presque toutes les versions mélangées.",
    formula: "p = \\frac{\\#\\{I_{\\text{permutation}} \\geq I_{\\text{observé}}\\}}{M}",
    detail:
      "Sous l'hypothèse nulle (aucune structure spatiale réelle), l'espérance théorique de l'indice de Moran vaut $-1/(N-1)$ -- propriété vérifiée dans les tests automatisés d'Hélios.",
    references: ["Cliff, A. D., & Ord, J. K. (1981). Spatial Processes: Models & Applications. Pion."],
  },
  moran_trend: {
    label: "Tendance de l'indice de Moran dans le temps",
    simple:
      "Une fois l'indice de Moran calculé à chaque trimestre, on applique exactement le même test de tendance que pour la variance et l'AC1 (tau de Kendall + substitutions) -- mais sur cette série d'indices spatiaux plutôt que sur la série brute.",
    formula: "p = \\frac{\\#\\{\\tau_{\\text{substitution}} \\geq \\tau_{\\text{observé}}\\}}{M} \\quad \\text{appliqué à } (I_t)",
    detail:
      "Une hausse significative de l'indice de Moran dans le temps indiquerait une synchronisation spatiale croissante -- le signal précurseur spatial décrit au §5.2.",
    references: ["Dakos, V. et al. (2012). « Methods for Detecting Early Warnings of Critical Transitions in Time Series. » PLoS ONE, 7(7), e41010."],
  },
  h3_joint: {
    label: "Statistique jointe H3",
    simple:
      "On combine le signal temporel national et le signal spatial départemental d'un même phénomène en une seule note, puis on compare cette note à celles obtenues sur chaque trimestre des 26 dernières années. Si la note du phénomène dépasse presque toutes les autres, c'est que les deux signaux sont inhabituels EN MÊME TEMPS -- pas juste l'un ou l'autre séparément.",
    formula: "T = -2\\sum_{i=1}^{k} \\ln(p_i)",
    derivationSteps: [
      {
        text: "Sous $H_0$, si les $p_i$ sont indépendantes et uniformes sur $[0,1]$, alors :",
      },
      { tex: "-2\\ln(p_i) \\sim \\chi^2(2)", block: true },
      { text: "(transformation standard d'une uniforme). La somme de $k$ variables $\\chi^2(2)$ indépendantes suit une $\\chi^2(2k)$ :" },
      { tex: "T = \\sum_{i=1}^{k} -2\\ln(p_i) \\sim \\chi^2(2k)", block: true },
      {
        text: "C'est la justification de la loi de Fisher (1925). Mais quand les $p_i$ sont corrélées (ce qui est le cas ici : les indicateurs sont calculés sur le même système économique sous-jacent), $\\text{Var}(T)$ diffère de la variance théorique de la $\\chi^2(2k)$ : la covariance entre les termes $-2\\ln(p_i)$ n'est plus nulle, donc utiliser le seuil théorique sous- ou sur-estime le vrai taux de faux positifs selon le signe de cette covariance.",
      },
      {
        text: "Adaptation Hélios : plutôt que de générer des surrogates synthétiques à phase aléatoire couplés (§5.6 étape 4, un problème de recherche ouvert vu les contraintes de données -- voir /hypotheses), $p_{joint}$ est calibré directement contre l'historique réel 2000-2026 :",
      },
      { tex: "p_{joint} = \\frac{\\#\\{T_{\\text{historique}} \\geq T_{\\text{observé}}\\}}{n_{\\text{trimestres}}}", block: true },
      {
        text: "Cette calibration empirique par l'historique réel préserve automatiquement toute corrélation réelle entre les deux composantes, sans supposer l'indépendance -- même objectif que l'étape 4 du §5.6, méthode différente, documentée comme telle.",
      },
      {
        text: "Cadrage honnête : la construction générale (combiner des p-values corrélées via une distribution nulle empirique) n'est pas une originalité d'Hélios -- c'est la méthode empirique de Brown (Empirical Brown's Method, Poole et al., 2016), déjà publiée et implémentée. Ce que documente cette page est comment l'appliquer à notre cas (indicateur temporel + indicateur spatial) et pourquoi, faute d'un générateur de surrogates couplés adapté à nos données, la calibration ci-dessus s'appuie sur l'historique réel plutôt que sur des données de substitution synthétiques.",
      },
    ],
    detail:
      "$p_i$ = p-value de rang empirique (proportion de trimestres historiques au moins aussi extrêmes), pas une p-value de surrogates synthétiques -- voir la page Tester H3 pour le détail complet.",
    references: [
      "Fisher, R. A. (1925). Statistical Methods for Research Workers. Oliver and Boyd.",
      "Brown, M. B. (1975). « A method for combining non-independent, one-sided tests of significance. » Biometrics, 31(4), 987–992.",
      "Poole, W., Gibbs, D. L., Shmulevich, I., Bernard, B., & Knijnenburg, T. A. (2016). « Combining dependent P-values with an empirical adaptation of Brown's method. » Bioinformatics, 32(17), i430–i436.",
    ],
  },
  kuramoto_h4: {
    label: "Modèle de Kuramoto et contrôle adaptatif (H4)",
    simple:
      "On modélise N oscillateurs -- imaginez N métronomes qui battent chacun à son propre rythme -- reliés entre eux par un couplage K : plus K est fort, plus ils tirent les uns sur les autres pour s'aligner. Au-delà d'un certain seuil de couplage, ils basculent brutalement dans un rythme commun (synchronisation). Une régulation qui affaiblit localement le lien entre les paires en train de se verrouiller peut empêcher cette bascule collective, sans réduire l'activité individuelle à zéro -- ne pas supprimer les turbulences, empêcher seulement leur synchronisation.",
    formula: "\\dot\\theta_i = \\omega_i + \\frac{K}{N}\\sum_{j=1}^N \\sin(\\theta_j - \\theta_i), \\qquad i=1,\\dots,N",
    derivationSteps: [
      { text: "Chaque oscillateur $i$ a une phase $\\theta_i(t)$ et une fréquence propre $\\omega_i$, tirée d'une loi symétrique unimodale $g(\\omega)$ (ici une loi normale centrée). Le degré de synchronisation collective se mesure par le paramètre d'ordre :" },
      { tex: "r\\,e^{i\\psi} = \\frac{1}{N}\\sum_{j=1}^N e^{i\\theta_j}, \\qquad r \\in [0,1]", block: true },
      { text: "$r=0$ : phases dispersées sur tout le cercle (incohérence). $r=1$ : toutes les phases confondues (synchronisation totale). En multipliant cette définition par $e^{-i\\theta_i}$ et en prenant la partie imaginaire, le terme de couplage se réécrit exactement en fonction du seul champ moyen $(r,\\psi)$ -- chaque oscillateur ne « voit » plus les $N-1$ autres individuellement, seulement la moyenne collective :" },
      { tex: "\\dot\\theta_i = \\omega_i + K r \\sin(\\psi - \\theta_i)", block: true },
      { text: "C'est la réduction en champ moyen (Kuramoto, 1975). Par symétrie de $g(\\omega)$, on peut fixer $\\psi=0$. Un oscillateur reste « verrouillé » (phase constante dans le référentiel tournant) tant que $|\\omega_i| \\le Kr$, avec $\\theta_i = \\arcsin(\\omega_i / Kr)$ ; au-delà, il continue de dériver librement. Seuls les oscillateurs verrouillés contribuent à $r$ à l'équilibre, ce qui donne l'équation d'auto-cohérence (changement de variable $\\omega = Kr\\sin\\theta$) :" },
      { tex: "r = Kr \\int_{-\\pi/2}^{\\pi/2} \\cos^2(\\theta)\\, g(Kr\\sin\\theta)\\, d\\theta", block: true },
      { text: "Près du seuil ($r \\to 0^+$), $g(Kr\\sin\\theta) \\approx g(0)$, donc l'intégrale se calcule directement ($\\int_{-\\pi/2}^{\\pi/2}\\cos^2\\theta\\,d\\theta = \\pi/2$) et $r$ se simplifie des deux côtés :" },
      { tex: "1 = K\\,g(0)\\,\\frac{\\pi}{2} \\quad\\Longrightarrow\\quad K_c = \\frac{2}{\\pi\\,g(0)}", block: true },
      { text: "En dessous de $K_c$, le système reste incohérent ($r \\approx 0$) ; au-delà, $r$ croît continûment depuis 0 (transition de phase du second ordre, Strogatz 2000) -- c'est la bascule collective que le module H4 illustre." },
      { text: "Contrôle adaptatif (inspiré du RCA, §5.8) : au lieu d'un $K$ global fixe, chaque paire $(i,j)$ a son propre couplage $K_{ij}(t)$, affaibli tant que la paire reste verrouillée en phase (mesuré par la vitesse angulaire relative $|\\dot\\theta_i - \\dot\\theta_j|$, proche de 0 pour une paire verrouillée), avec une lente relaxation vers $K_{base}$. Adaptation Hélios par rapport au texte du §5.8 (qui propose une règle sur $d|\\theta_i-\\theta_j|/dt$) : cette dérivée s'annule aussi une fois la paire verrouillée, donc une règle prise au pied de la lettre cesse d'agir dès que le verrouillage est atteint. La vitesse angulaire relative reste, elle, un indicateur direct et permanent du verrouillage, ce qui rend la suppression active en régime établi -- même principe, mécanisme rendu effectif." },
      { text: "Objectif du contrôle : ni $r=0$ (rigidité totale, coûteuse) ni $r=1$ (bascule), mais un maintien de $r$ sous un seuil $r_c$ choisi, malgré les mêmes perturbations que la simulation non contrôlée." },
    ],
    references: [
      "Kuramoto, Y. (1975). « Self-entrainment of a population of coupled non-linear oscillators. » Lecture Notes in Physics, 39, 420–422.",
      "Strogatz, S. H. (2000). « From Kuramoto to Crawford: exploring the onset of synchronization in populations of coupled oscillators. » Physica D, 143(1-4), 1–20.",
      "Popovych, O. V., & Tass, P. A. (2012). « Desynchronizing electrical and sensory coordinated reset neuromodulation. » Frontiers in Human Neuroscience, 6, 58.",
    ],
  },
  power_law_h5: {
    label: "Loi de puissance et criticité auto-organisée (H5)",
    simple:
      "Au lieu de chercher une seule bascule à venir, on regarde si les tailles des chocs déjà observés (petits, moyens, très grands) suivent une loi de puissance -- un motif où des événements bien plus grands que la moyenne restent, en proportion, beaucoup plus probables qu'avec une distribution habituelle. C'est la signature d'un système qui vit en permanence à la limite de la stabilité plutôt que d'approcher un seul point de rupture.",
    formula: "\\hat\\alpha = 1 + \\frac{n}{\\sum_{i=1}^n \\ln(x_i/x_{\\min})}",
    derivationSteps: [
      { text: "Une loi de puissance continue de support $x \\ge x_{\\min}$ a pour densité $p(x) = \\frac{\\alpha-1}{x_{\\min}}(x/x_{\\min})^{-\\alpha}$. La log-vraisemblance de $n$ observations indépendantes, pour $x_{\\min}$ fixé, vaut :" },
      { tex: "\\ln L(\\alpha) = n\\ln(\\alpha-1) - n\\ln(x_{\\min}) - \\alpha\\sum_{i=1}^n \\ln(x_i/x_{\\min})", block: true },
      { text: "En dérivant par rapport à $\\alpha$ et en annulant :" },
      { tex: "\\frac{n}{\\alpha-1} - \\sum_i \\ln(x_i/x_{\\min}) = 0 \\ \\Longrightarrow\\ \\hat\\alpha = 1 + \\frac{n}{\\sum_i \\ln(x_i/x_{\\min})}", block: true },
      { text: "$x_{\\min}$ lui-même est choisi comme la valeur qui minimise la distance de Kolmogorov-Smirnov entre le modèle et les données (Clauset, Shalizi & Newman, 2009), pas fixé arbitrairement." },
      { text: "Un ajustement plausible ne suffit pas (mise en garde de Touboul & Destexhe, 2010, contre le simple ajustement visuel log-log) : un test de plausibilité par bootstrap semi-paramétrique (générer des jeux de données à partir du modèle ajusté lui-même, comparer leur propre distance de Kolmogorov-Smirnov à celle observée) et une comparaison à des modèles alternatifs (log-normale, exponentielle, par un test du rapport de vraisemblance de Vuong) sont exigés avant tout verdict." },
    ],
    references: [
      "Bak, P., Tang, C., & Wiesenfeld, K. (1987). « Self-organized criticality: An explanation of the 1/f noise. » Physical Review Letters, 59(4), 381–384.",
      "Clauset, A., Shalizi, C. R., & Newman, M. E. J. (2009). « Power-Law Distributions in Empirical Data. » SIAM Review, 51(4), 661–703.",
      "Touboul, J., & Destexhe, A. (2010). « Can Power-Law Scaling and Neuronal Avalanches Arise from Stochastic Dynamics? » PLoS ONE, 5(2), e9448.",
    ],
  },
};

/** Bibliographie complète (§12) -- affichée en un seul endroit pour référence croisée. */
export const BIBLIOGRAPHY = [
  "Ives, A. R. (1995). « Measuring resilience in stochastic systems. » Ecological Monographs, 65(2), 217–233.",
  "Scheffer, M., Bascompte, J., Brock, W. A., Brovkin, V., Carpenter, S. R., Dakos, V., Held, H., van Nes, E. H., Rietkerk, M., & Sugihara, G. (2009). « Early-warning signals for critical transitions. » Nature, 461, 53–59.",
  "Dakos, V., Carpenter, S. R., Brock, W. A., Ellison, A. M., Guttal, V., Ives, A. R., Kéfi, S., Livina, V., Seekell, D. A., van Nes, E. H., & Scheffer, M. (2012). « Methods for Detecting Early Warnings of Critical Transitions in Time Series Illustrated Using Simulated Ecological Data. » PLoS ONE, 7(7), e41010.",
  "Fisher, R. A. (1925). Statistical Methods for Research Workers. Oliver and Boyd.",
  "Brown, M. B. (1975). « A method for combining non-independent, one-sided tests of significance. » Biometrics, 31(4), 987–992.",
  "Dakos, V., van Nes, E. H., Donangelo, R., Fort, H., & Scheffer, M. (2010). « Spatial correlation as leading indicator of catastrophic shifts. » Theoretical Ecology, 3, 163–174.",
  "MacLaren, N. G., Aihara, K., & Masuda, N. (2025). « Applicability of spatial early warning signals to complex network dynamics. » Journal of the Royal Society Interface, 22(226), 20240696.",
  "Kuramoto, Y. (1975). « Self-entrainment of a population of coupled non-linear oscillators. » Lecture Notes in Physics, 39, 420–422.",
  "Strogatz, S. H. (2000). « From Kuramoto to Crawford: exploring the onset of synchronization in populations of coupled oscillators. » Physica D, 143(1-4), 1–20.",
  "Popovych, O. V., & Tass, P. A. (2012). « Desynchronizing electrical and sensory coordinated reset neuromodulation. » Frontiers in Human Neuroscience, 6, 58.",
  "Kendall, M. G. (1938). « A New Measure of Rank Correlation. » Biometrika, 30(1/2), 81–93.",
  "Theiler, J., Eubank, S., Longtin, A., Galdrikian, B., & Farmer, J. D. (1992). « Testing for nonlinearity in time series: the method of surrogate data. » Physica D, 58(1-4), 77–94.",
  "Moran, P. A. P. (1950). « Notes on Continuous Stochastic Phenomena. » Biometrika, 37(1/2), 17–23.",
  "Cliff, A. D., & Ord, J. K. (1981). Spatial Processes: Models & Applications. Pion.",
  "Poole, W., Gibbs, D. L., Shmulevich, I., Bernard, B., & Knijnenburg, T. A. (2016). « Combining dependent P-values with an empirical adaptation of Brown's method. » Bioinformatics, 32(17), i430–i436.",
  "Legault, V., Pu, Y., Weinans, E., & Cohen, A. A. (2024). « Application of early warning signs to physiological contexts: a comparison of multivariate indices in patients on long-term hemodialysis. » Frontiers in Network Physiology, 4, 1299162.",
  "Bak, P., Tang, C., & Wiesenfeld, K. (1987). « Self-organized criticality: An explanation of the 1/f noise. » Physical Review Letters, 59(4), 381–384.",
  "Clauset, A., Shalizi, C. R., & Newman, M. E. J. (2009). « Power-Law Distributions in Empirical Data. » SIAM Review, 51(4), 661–703.",
  "Touboul, J., & Destexhe, A. (2010). « Can Power-Law Scaling and Neuronal Avalanches Arise from Stochastic Dynamics? » PLoS ONE, 5(2), e9448.",
];
