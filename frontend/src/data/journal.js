/**
 * Journal de recherche -- cahier des charges §7bis (module obligatoire).
 *
 * Tout ce qui a été établi mathématiquement pendant la conception du
 * projet (§5.6bis à §5.6quinquies) doit être visible et lisible dans le
 * logiciel lui-même, y compris l'erreur de raisonnement corrigée -- pas
 * effacée, montrée comme contenu pédagogique en soi. Contenu repris
 * verbatim depuis le cahier des charges, dans l'ordre imposé.
 */
export const JOURNAL_SECTIONS = [
  {
    id: "postulat",
    title: "1. Le postulat de départ",
    simple:
      "Est-ce que le signal de tension « temporel » (une série qui devient plus instable dans le temps) apparaît toujours avant le signal de tension « spatial » (des territoires voisins qui se mettent à évoluer ensemble) — ou est-ce que ça dépend du type de bascule ?",
    expertBlocks: [
      {
        text: "Question posée : pour un réseau d'oscillateurs stochastiques couplés approchant une bifurcation, l'indicateur temporel (AC1 agrégée) précède-t-il systématiquement l'indicateur spatial (indice de Moran) — et pourquoi ? Ce point conditionne directement la valeur ajoutée de l'indicateur joint H3 (§5.6) : s'il ne s'agit que d'un simple décalage temporel entre deux mesures du même phénomène, combiner les deux n'apporte rien de plus que le plus précoce des deux pris seul.",
      },
    ],
  },
  {
    id: "modele",
    title: "2. Le modèle",
    simple:
      "On simule un réseau de « ressorts couplés » bruités (comme des points reliés par des ressorts, secoués aléatoirement), dont un sous-groupe de tailles variables devient de plus en plus instable, et on regarde lequel des deux signaux (temporel ou spatial) bouge en premier.",
    expertBlocks: [
      { text: "Réseau d'oscillateurs stochastiques couplés par le Laplacien du graphe (processus d'Ornstein-Uhlenbeck multivarié), approchant une bifurcation :" },
      { tex: "dy = (\\Lambda - \\beta L)\\,y\\,dt + \\sigma\\,dW", block: true },
      { text: "La relation entre l'indicateur temporel (AC1 agrégée) et l'indicateur spatial (indice de Moran) est établie analytiquement/numériquement via l'équation de Lyapunov stationnaire, avec $A = \\Lambda - \\beta L$ :" },
      { tex: "A\\Sigma + \\Sigma A^T + \\sigma^2 I = 0", block: true },
      { text: "Résolution numérique exacte (pas d'approximation à la main) sur un réseau en anneau ($N=40$), en faisant varier la taille $|S|$ d'un sous-ensemble de nœuds dont la stabilité locale $\\lambda_S$ se rapproche de 0 -- d'un seul nœud (bifurcation très localisée) à $N$ (bifurcation homogène)." },
    ],
  },
  {
    id: "erreur",
    title: "3. L'erreur initiale et sa correction",
    simple:
      "Un premier raisonnement, fait « à la main » sans calcul exact, s'était trompé sur deux points. Le calcul exact a montré l'inverse. On garde cette erreur visible plutôt que de l'effacer : voir où et comment un raisonnement intuitif peut se tromper fait partie de la démonstration scientifique.",
    expertBlocks: [
      {
        text: "Un premier raisonnement qualitatif avait conclu à tort que (a) le cas homogène ne produirait aucune tendance sur l'indice de Moran, et (b) qu'une bifurcation localisée ferait apparaître le signal spatial avant le signal temporel.",
      },
      {
        text: "Le calcul exact contredit les deux points : c'était une confusion entre « le terme correctif tend vers zéro » et « pas de tendance », alors que ce terme qui s'annule est justement ce qui pousse l'indice de Moran vers son maximum. Ceci illustre pourquoi ce protocole exige une validation numérique et non une simple dérivation verbale.",
      },
    ],
  },
  {
    id: "lineaire",
    title: "4. Résultat sur système linéaire stationnaire",
    simple:
      "Sur ce modèle simplifié (réseau en anneau, système qui reste stable), le signal temporel franchit toujours son seuil avant le signal spatial -- même quand la bifurcation touche tout le réseau d'un coup. Testé aussi en faisant varier la force du couplage et la forme du réseau : le résultat tient dans 16 cas sur 17.",
    expertBlocks: [
      {
        text: "Résultat numérique (réseau en anneau, $\\beta=0{,}6$, $\\Delta t=0{,}5$, $\\sigma=1$) : dans toutes les configurations testées (bifurcation localisée sur 1 nœud jusqu'à homogène sur les 40), l'indicateur temporel franchit son seuil de déclenchement avant l'indicateur spatial. Même dans le cas homogène, l'indice de Moran montre une tendance forte (+170% sur la plage testée, contre +62% pour l'indicateur temporel) mais plus tardive.",
      },
      {
        text: "Balayage de sensibilité : couplage $\\beta \\in \\{0{,}1;\\,0{,}3;\\,0{,}6;\\,1;\\,2;\\,4\\}$, topologie (anneau régulier vs 5 réseaux irréguliers aléatoires distincts, connexité garantie), taille du patch instable (2,5% à 100% du réseau). La précédence temporel → spatial est robuste sur l'ensemble du balayage — 16 configurations sur 17 confirment « AC1 précède », la seule exception (patch de 2,5%, un seul nœud) donnant un résultat simultané, probablement une limite de résolution numérique plutôt qu'un vrai contre-exemple.",
      },
      {
        text: "Portée réelle -- à ne pas dépasser : établi uniquement pour un réseau d'Ornstein-Uhlenbeck linéaire, à couplage diffusif (Laplacien), avec un seul pas d'échantillonnage testé ($\\Delta t=0{,}5$). Ne dit rien sur les dynamiques non linéaires proches d'un vrai point de bifurcation (saddle-node), les couplages non diffusifs, ou une variation de $\\Delta t$. Observation robuste dans un modèle simplifié, pas une loi générale.",
      },
    ],
  },
  {
    id: "montecarlo",
    title: "5. Validation Monte-Carlo sur un vrai basculement",
    simple:
      "Le test précédent approchait l'instabilité sans jamais vraiment basculer. Ici, le système bascule pour de vrai (40 simulations indépendantes). Résultat : la variance annonce la bascule avant l'indice de Moran dans 8 cas sur 10, et nettement plus tôt. Découverte imprévue : l'autocorrélation, pourtant l'indicateur de référence utilisé ailleurs dans Hélios (H1), se révèle être un détecteur nettement plus faible que la variance.",
    expertBlocks: [
      {
        text: "Limite du résultat précédent : les points 4 (§5.6bis/ter) reposaient sur un système linéaire qui s'approche de l'instabilité sans jamais réellement basculer (l'équation de Lyapunov n'est définie que pour un système stable). Il fallait vérifier si la précédence tenait sur un vrai basculement.",
      },
      { text: "Modèle : bifurcation nœud-col (saddle-node) par nœud, couplée diffusivement sur le réseau, avec bruit :" },
      { tex: "dx_i = \\big(\\mu(t) + x_i^2 - \\beta(Lx)_i\\big)\\,dt + \\sigma\\,dW_i", block: true },
      {
        text: "$\\mu(t)$ croît lentement de $-2$ vers $0$ puis au-delà : les deux points d'équilibre (stable/instable) fusionnent en $\\mu=0$ et disparaissent, provoquant l'échappement (le vrai basculement). Réseau en anneau, $N=40$, $\\beta=0{,}6$, 40 réalisations Monte-Carlo indépendantes.",
      },
      {
        text: "Résultat : les 40 réalisations basculent réellement, au voisinage du point critique attendu ($t\\approx406$ contre $t_{\\text{théorique}}=400$). Détection par franchissement de seuil (3 écarts-types au-dessus de la ligne de base) : la variance précède l'indice de Moran dans 32/40 cas (80%), avec une avance moyenne nettement supérieure (≈284 unités de temps contre ≈152). Ce résultat confirme, dans un régime de basculement réel, la conclusion préliminaire des points 4.",
      },
      {
        text: "Découverte secondaire, non planifiée : l'autocorrélation (AC1), utilisée comme indicateur temporel de référence pour H1 (§5.1), se révèle ici un détecteur nettement plus faible que la variance — seules 11/40 réalisations franchissent son seuil de détection avant la bascule, avec une avance moyenne bien plus courte. Cette faiblesse relative de l'AC1 par rapport à la variance sur données bruitées est cohérente avec un résultat déjà documenté dans la littérature clinique (Legault et al., 2024, indicateurs EWS multivariés en hémodialyse).",
      },
      {
        text: "Limites encore ouvertes : ce test ne couvre que le couplage diffusif et la topologie en anneau ; le couplage non diffusif (point 6) et le réseau réel irrégulier restent à mener avant toute conclusion définitive.",
      },
    ],
  },
  {
    id: "robustesse",
    title: "6. Robustesse au type de couplage (non diffusif)",
    simple:
      "Même test, mais avec un couplage qui ne se propage plus linéairement entre voisins (plutôt une logique de contagion à seuil, où l'influence d'un voisin plafonne). Le résultat tient toujours -- variance avant Moran dans 9 cas sur 10. Ce n'est donc pas un artefact du type de couplage choisi au départ.",
    expertBlocks: [
      {
        text: "Test : même modèle (bifurcation nœud-col, réseau en anneau, $N=40$, 40 réalisations), mais couplage remplacé par une forme saturante de type contagion plutôt que diffusive linéaire :",
      },
      { tex: "dx_i = \\Big(\\mu(t) + x_i^2 + \\beta\\sum_j W_{ij}\\tanh(x_j-x_i)\\Big)\\,dt + \\sigma\\,dW_i", block: true },
      {
        text: "Contrairement au couplage diffusif (point 5), l'influence d'un voisin sature ici pour les grands écarts plutôt que de croître linéairement — un régime qualitativement différent, plus proche d'une dynamique de contagion/seuil.",
      },
      {
        text: "Résultat : la précédence tient toujours — la variance précède l'indice de Moran dans 36/40 cas (90%), avec un délai d'anticipation du même ordre de grandeur qu'avec le couplage diffusif (≈288 contre ≈155 unités de temps). L'autocorrélation reste un détecteur faible (13/40 détections). Ce résultat n'est donc pas un artefact du couplage diffusif linéaire : il tient sous un type de couplage qualitativement différent.",
      },
      {
        text: "Ce qui reste à faire avant généralisation complète : réseau réel irrégulier (communes françaises) en régime de basculement effectif (pas seulement en régime linéaire stationnaire comme au point 4), et in fine la confrontation aux données réelles.",
      },
    ],
  },
];

/** §7bis, point 7 -- état d'avancement du protocole de généralisation. */
export const PROGRESS_CHECKLIST = [
  { done: true, label: "Bifurcation réellement franchie (pas seulement approchée)" },
  { done: true, label: "Robustesse testée sur un couplage non diffusif" },
  { done: false, label: "Testé sur un réseau réel irrégulier (communes françaises)" },
  { done: true, label: "Fenêtres finies et bruit d'estimation (déjà inhérent au Monte-Carlo)" },
  { done: false, label: "Confronté aux épisodes historiques réels" },
];

export const JOURNAL_REFERENCES = [
  "Ives, A. R. (1995). « Measuring resilience in stochastic systems. » Ecological Monographs, 65(2), 217–233.",
  "Dakos, V., van Nes, E. H., Donangelo, R., Fort, H., & Scheffer, M. (2010). « Spatial correlation as leading indicator of catastrophic shifts. » Theoretical Ecology, 3, 163–174.",
  "Legault, V., Pu, Y., Weinans, E., & Cohen, A. A. (2024). « Application of early warning signs to physiological contexts: a comparison of multivariate indices in patients on long-term hemodialysis. » Frontiers in Network Physiology, 4, 1299162.",
];
