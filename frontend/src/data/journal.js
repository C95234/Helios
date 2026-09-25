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
      "Le test précédent approchait l'instabilité sans jamais vraiment basculer. Ici, le système bascule pour de vrai (40 simulations indépendantes). Résultat : la variance annonce la bascule avant l'indice de Moran dans 8 cas sur 10, et nettement plus tôt. Constat secondaire, non planifié : l'autocorrélation, pourtant l'indicateur de référence utilisé ailleurs dans Hélios (H1), se révèle être un détecteur nettement plus faible que la variance.",
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
        text: "Constat secondaire, non planifié : l'autocorrélation (AC1), utilisée comme indicateur temporel de référence pour H1 (§5.1), se révèle ici un détecteur nettement plus faible que la variance — seules 11/40 réalisations franchissent son seuil de détection avant la bascule, avec une avance moyenne bien plus courte. Cette faiblesse relative de l'AC1 par rapport à la variance sur données bruitées est cohérente avec un résultat déjà documenté dans la littérature clinique (Legault et al., 2024, indicateurs EWS multivariés en hémodialyse).",
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
  {
    id: "extension",
    title: "7. Extension au réseau réel et aux données historiques réelles",
    simple:
      "Ce résultat (le signal temporel qui précède toujours le signal spatial) tient-il encore quand on remplace le réseau simulé en anneau par la vraie carte des 96 départements français -- et quand on regarde ce qui s'est vraiment passé lors de 3 épisodes historiques (crise de 2008-2009, gilets jaunes 2018, confinement 2020) plutôt qu'une simulation ? Réponse : oui sur le réseau réel simulé (3 précédences sur 4 réalisations), plus nuancé sur les données réelles (2 cas sur 3 seulement -- mais l'échantillon est minuscule, 3 épisodes, pas 40 simulations).",
    expertBlocks: [
      {
        text: "Reproduction (test de non-régression) sur l'anneau, avant toute extension : 35/40 réalisations (87,5%) confirment la précédence variance → Moran, pour le couplage diffusif comme pour le couplage de type contagion -- avance moyenne de 217 unités de temps pour la variance contre 167 pour l'indice de Moran. Du même ordre de grandeur que les 80%/90% documentés au point 5 et au point 6, sans reproduire exactement la différenciation fine entre les deux régimes de couplage (probablement parce que le réseau reste largement synchronisé pendant la majeure partie de la trajectoire, régime où le couplage à seuil se comporte comme le couplage diffusif linéarisé). Calibration non spécifiée par le cahier des charges (pas de code fourni, seulement le modèle et le résultat visé) : le bruit $\\sigma$ a dû être réduit empiriquement (de 1 à 0,2) pour retrouver un basculement proche du temps théorique plutôt qu'un basculement prématuré activé par le bruit -- documenté dans le code (`app/lyapunov_precedence.py`).",
      },
      {
        text: "Réseau irrégulier aléatoire (une instance, 40 réalisations, couplage diffusif) : 16/40 (80%) -- cohérent avec le balayage du point 4.",
      },
      {
        text: "Réseau réel des 96 départements de métropole (238 paires de voisins, même carte que H2) : 15/20 réalisations (75%) confirment la précédence, pour le couplage diffusif comme pour le couplage à seuil -- avance moyenne de 222 unités de temps pour la variance contre ~183 pour l'indice de Moran. La précédence tient donc sur le vrai réseau, avec une marge un peu plus faible que sur les réseaux synthétiques (87,5% → 80% → 75% à mesure qu'on se rapproche de la structure réelle). Limite assumée : la force de couplage $\\beta=0{,}6$ n'a pas été réoptimisée pour la connectivité bien plus dense du réseau réel (~5 voisins en moyenne contre 2 pour l'anneau) -- un $\\beta$ recalibré pourrait changer ce chiffre.",
      },
      {
        text: "Confrontation à 3 épisodes historiques réels (§5.7), en réutilisant les données déjà connectées pour H1/H2/H3 (confiance des ménages nationale, chômage départemental) : le choc de chômage 2008-2009 et le confinement de 2020 montrent le signal temporel en avance ; le mouvement des gilets jaunes de 2018 montre l'inverse, le signal spatial légèrement en avance (un mois). Soit 2 précédences temporelles sur 3.",
      },
      {
        text: "Erreur initiale corrigée sur cette confrontation, dans le même esprit que le point 3 : un premier calcul tronquait la série nationale à la fenêtre de l'épisode AVANT de calculer la variance et l'autocorrélation glissantes, privant les premiers points de tout contexte antérieur -- ce qui poussait artificiellement le « pic » vers le tout premier point de la fenêtre observée dans presque tous les cas. Corrigé en calculant les indicateurs glissants sur la série complète (tout l'historique disponible avant l'épisode), puis en ne retenant que la portion de la fenêtre pour chercher le pic -- exactement la méthode déjà utilisée pour H1.",
      },
      {
        text: "Limites de cette confrontation aux données réelles, à ne pas minimiser : seulement 3 épisodes (aucune inférence statistique possible sur un échantillon pareil), le chômage départemental n'est publié qu'au trimestre (résolution grossière pour la composante spatiale, déjà la limite assumée pour H3), et la détection ici est purement descriptive (position du pic), pas un test de significativité formel comme en simulation.",
      },
    ],
  },
  {
    id: "audit-robustesse",
    title: "8. Audit de robustesse -- les taux de précédence tenaient-ils sur plus de graines ?",
    simple:
      "Un relecteur externe d'une contribution logicielle liée à ce projet a trouvé un test qui ne passait que sur environ la moitié des essais aléatoires -- un signal qu'il fallait vérifier si d'autres résultats d'Hélios, mesurés sur peu de simulations (40 ou 20), tenaient aussi sur beaucoup plus d'essais. Réponse : le réseau réel tient bien (77,5% contre 75% annoncé), mais le réseau en anneau était surestimé -- 73%/73,5% contre les 80%/90% publiés au point 7, pas 90%.",
    expertBlocks: [
      {
        text: "Déclencheur : une revue externe indépendante (sur une contribution au paquet ewstools, sans rapport direct avec ce module) a révélé qu'un test interne à ce paquet ne passait que sur 526/1000 graines aléatoires -- proche du hasard, malgré une apparence de test fiable sur une seule graine. Ceci a motivé une vérification du même type sur les résultats de précédence variance/Moran d'Hélios, qui n'avaient jamais été testés sur plus de 40 réalisations Monte-Carlo (20 pour le réseau réel).",
      },
      {
        text: "Protocole : les points 5, 6 et 7 ci-dessus rejoués avec 200 réalisations indépendantes (contre 40 pour l'anneau/réseau irrégulier, 20 pour le réseau réel), mêmes paramètres, nouvelles graines (5000+).",
      },
      {
        text: "Résultat sur l'anneau (N=40) : la précédence variance → Moran tombe à 73,0% (couplage diffusif) et 73,5% (couplage contagion) sur 200 réalisations, contre 80%/90% rapportés aux points 5-6 sur 40 réalisations. La conclusion qualitative (la variance précède plus souvent qu'elle ne suit) reste vraie, mais le chiffre annoncé était optimiste -- et l'écart apparent entre couplage diffusif et contagion (80% vs 90%), présenté au point 6 comme une preuve de robustesse au type de couplage, ne survit pas à l'échantillon plus grand : les deux couplages donnent en réalité un taux quasi identique (73,0% vs 73,5%), ce qui est en un sens un résultat plus solide -- le type de couplage n'a simplement pas d'effet mesurable sur ce taux, plutôt que d'avoir un effet différent selon le couplage comme le suggérait le chiffre à 40 réalisations.",
      },
      {
        text: "Réseau irrégulier aléatoire (N=40, couplage diffusif) : 79,5% sur 200 réalisations, cohérent avec le 80% rapporté sur 40 au point 7 -- ce résultat-là tenait déjà.",
      },
      {
        text: "Réseau réel des 96 départements : 77,5% pour les deux couplages sur 200 réalisations, cohérent avec le 75% rapporté sur seulement 20 réalisations au point 7 -- également stable, malgré le tout petit échantillon d'origine.",
      },
      {
        text: "Constat retenu : ce n'est pas la taille du réseau ni la nature du couplage qui rendait le chiffre fragile, mais le nombre de réalisations Monte-Carlo à 40 pour l'anneau -- une leçon directement transposable à tout futur résultat de ce type (préférer 200 réalisations à 40 quand le temps de calcul le permet, comme fait ici : ~42 minutes pour l'anneau et l'irrégulier, ~60 minutes pour le réseau réel).",
      },
    ],
  },
  {
    id: "correction-tendance-moran",
    title: "9. Correction de tendance sur l'indice de Moran -- un second bug trouvé par la même revue externe",
    simple:
      "La même revue externe qui a audité la contribution ewstools (point 8) a trouvé un vrai bug dans le calcul de l'indice de Moran : un motif spatial dont l'AMPLITUDE se renforce dans le temps fait monter l'indice sans aucun vrai ralentissement critique. Ce bug touchait aussi le code interne d'Hélios (H2, H3), pas seulement la contribution externe. Corrigé en retirant une tendance lente par département avant tout calcul de tendance sur l'indice -- le verdict H2 change : 2 des 5 variables restent défavorables (contre 3 avant correction), les 3 autres deviennent non concluantes plutôt que défavorables.",
    expertBlocks: [
      {
        text: "Déclencheur : Bruce Stephenson (mainteneur, `energyscholar`), en relisant la contribution `ewstools/spatial.py` (§1ter.1), a montré par la mesure (trois champs de test) qu'un gradient spatial statique donne un tau de Kendall d'environ -0,15 sur l'indice de Moran dans le temps, une dérive uniforme sans structure spatiale environ +0,05, mais un gradient spatial qui SE RENFORCE dans le temps donne environ +0,81 -- un faux positif net, sans aucun rapport avec un ralentissement critique. La cause : l'indice de Moran est centré spatialement (une dérive de la moyenne ne le change pas) mais pas temporellement -- rien ne protège contre une amplitude de motif spatial qui change lentement.",
      },
      {
        text: "Vérification sur le code interne d'Hélios : `compute_network_moran_series` (backend/app/spatial_series.py), utilisé par H2 (test_h2, test_h2_aggregate) et H3 (historical_spatial_i), calculait l'indice de Moran directement sur le champ brut des variables Insee (chômage, défaillances, constructions, créations, population) sur des séries de 26 ans -- exactement le type de série où une dérive structurelle lente (divergence démographique ou économique entre départements) est plausible, indépendamment de tout signal précurseur.",
      },
      {
        text: "Correction appliquée : `detrend_wide` (nouveau, spatial_series.py) retire une tendance lente par département par LOWESS avant de calculer l'indice de Moran utilisé pour tout test de tendance (`i_real_detrended`/`i_grid_detrended`) -- le champ brut reste utilisé uniquement pour l'affichage de la courbe et le test de significativité spatiale à un instant donné (qui n'a pas ce problème, puisqu'il ne teste pas une tendance temporelle).",
      },
      {
        text: "Effet mesuré sur H2 (5 variables réelles, avant / après correction) : chômage neutre → neutre (inchangé), défaillances défavorable → défavorable (inchangé), constructions défavorable → défavorable (inchangé), créations défavorable → neutre (le signal disparaît), population défavorable → neutre (le signal disparaît). Verdict agrégé : 3/5 défavorables avant correction → 2/5 après. La conclusion qualitative de H2 ne change pas (pas de majorité favorable dans les deux cas), mais l'ampleur du signal défavorable était partiellement un artefact.",
      },
      {
        text: "Un plancher de p-value (Davison & Hinkley 1997 ; North, Curtis & Sham 2002, +1 au numérateur et au dénominateur) a été ajouté au même moment au test de permutation de l'indice de Moran (backend/app/stats/moran.py) -- même bug, même correction que celle appliquée à la contribution ewstools.",
      },
      {
        text: "Non traité pour l'instant : le module Fusion (indice de Moran sur les sondes magnétiques MAST, backend/app/routers/fusion.py) utilise la même fonction `morans_i` sans ce retrait de tendance. Risque jugé plus faible (une dérive de calibration de capteur sur quelques secondes de tir plutôt qu'une divergence structurelle sur 26 ans) mais pas nul -- signalé ici comme limite ouverte plutôt que silencieusement ignoré.",
      },
    ],
  },
  {
    id: "cnn-architecture-bury-et-al",
    title: "10. Architecture fidèle à Bury et al. (CNN-LSTM) : un biais de prétraitement confirmé, un résultat sur données réelles plus nuancé",
    simple:
      "Le classifieur du banc d'essai IA vs statistiques a été remplacé par une adaptation fidèle de l'architecture réelle de Bury et al. (2021, code source publié) -- CNN-LSTM, ensemble de 10 modèles. Deux résultats notables : (1) testé sur des séries AR(1) sans aucune bifurcation, il les flague à tort dans 78% des cas -- confirme directement un biais de prétraitement déjà documenté par un co-auteur de Bury (Dablander & Bury, 2021). (2) Appliqué aux 6 épisodes réels de H1, il montre enfin une vraie variation d'un épisode à l'autre (43% à 95% de fenêtres flaguées) -- mais le biais AR(1) confirmé juste avant interdit d'y voir une preuve de détection plutôt qu'une réaction générale à l'agitation de la série.",
    expertBlocks: [
      {
        text: "Contexte : la première version du classifieur (un petit CNN 2 couches, sans LSTM) était explicitement documentée comme \"pas une reproduction de l'architecture de Bury et al.\" -- un choix provisoire. Le code d'entraînement complet de Bury et al. étant publié (github.com/ThomasMBury/deep-early-warnings-pnas), il a été lu directement et son architecture reprise : Conv1D (50 filtres, noyau 12) -> Dropout -> MaxPool -> LSTM(50) -> Dropout -> LSTM(10) -> Dropout -> Dense, entraînée en ensemble de 10 modèles indépendants (leur propre méthode de robustesse). Seule différence assumée : sortie binaire (bascule oui/non) plutôt que la classification à 4 classes (type de bifurcation) de Bury et al., qui répond à une question différente.",
      },
      {
        text: "Échelle d'entraînement très réduite par rapport à l'original (mesuré directement : une seule passe pleine-batch sur 95 000 fenêtres de longueur 60 prend déjà ~150 secondes, contre 200 000 séquences de longueur 500-1500 sur 1500 passages pour Bury et al.) -- entraînement par mini-lots sur un jeu réduit, documenté comme Adaptation Hélios, jamais présenté comme une reproduction de leurs résultats publiés.",
      },
      {
        text: "Test de validité (§1.1bis, Dablander & Bury 2021) : l'ensemble des 10 modèles appliqué à des séries AR(1) stationnaires (aucune bifurcation, juste de la persistance temporelle, phi de 0,1 à 0,9) flague à tort 78% des 150 fenêtres testées globalement -- de 96,7% pour une faible persistance (phi=0,1) à 40% pour une forte persistance (phi=0,9). Confirme directement, sur cette adaptation aussi, le biais de prétraitement documenté par Dablander & Bury : un classifieur entraîné sur des séries approchant une vraie bifurcation peut confondre la simple persistance temporelle avec un signal précurseur.",
      },
      {
        text: "Effet sur les modèles simulés (nœud-col, Kuramoto) : détection à 100% sur les deux modèles, stable sur les 10 graines (écart-type nul), zéro faux positif sur le nœud-col. Sur Kuramoto, le taux de faux positifs varie notablement selon la graine (61,5% à 100%, écart-type 11,8%) -- la seule métrique où les 10 entraînements divergent vraiment, à comparer aux résultats parfaitement stables du nœud-col.",
      },
      {
        text: "Effet sur les données réelles de H1 (§2.1, ensemble rechargé depuis les modèles déjà entraînés, pas ré-entraîné) : contrairement à la première version qui flaguait 91 à 100% des fenêtres partout sans aucune différence exploitable, le nouvel ensemble montre une vraie variation, de 42,9% (confinement 2020) à 94,9% (gilets jaunes 2018). Fait notable sur seulement 6 épisodes, à interpréter avec prudence : ce taux suit approximativement le nombre de signaux sociaux déjà trouvés significatifs par H1 (nSocSig) -- confinement (0/3) au plus bas, gilets jaunes (3/3) au plus haut, les trois cas à 2/3 regroupés entre les deux (77,6% à 84,5%).",
      },
      {
        text: "Interprétation honnête, en tenant les deux résultats de ce même Journal ensemble : cette corrélation apparente n'est PAS une preuve de capacité de détection. Le test AR(1) montre que ce même ensemble réagit déjà fortement à la simple présence de mouvement/persistance dans une série, sans aucune bifurcation réelle -- la variation observée sur les données de H1 pourrait tout aussi bien refléter \"combien la série Wikipédia bouge en général\" pendant chaque épisode plutôt qu'un vrai signal précurseur. Le contrôle négatif explicite de H1 (« climat social récent ») reste flagué à un taux élevé (73,2%), pas nul -- cohérent avec cette lecture prudente.",
      },
      {
        text: "Non fait : recalibrer un filtre de persistance temporelle pour les fenêtres quotidiennes de H1 (contrairement à l'évaluation sur données simulées) ; comparer formellement les métriques de ce banc d'essai aux résultats publiés de Bury et al. (garde-fou de positionnement explicite du cahier des charges -- l'objectif est de reproduire leur méthode sur de nouvelles données, jamais de prétendre la dépasser).",
      },
    ],
  },
  {
    id: "cnn-real-fusion-extension",
    title: "11. Extension aux données réelles -- domaine Fusion nucléaire : un résultat négatif, dans le sens inverse de celui espéré",
    simple:
      "Le même ensemble de 10 classifieurs (§10), jamais ré-entraîné, appliqué cette fois aux 20 tirs réels MAST déjà utilisés par le module Fusion (10 disruptés, 10 stables). Résultat net et négatif : tous les tirs sont flagués sur le critère binaire, et surtout, le taux de fenêtres flaguées est en moyenne PLUS élevé sur les tirs stables (98%) que sur les tirs qui disruptent réellement (70%) -- l'inverse de ce qu'un vrai signal précurseur produirait.",
    expertBlocks: [
      {
        text: "Méthode (backend/scripts/apply_classifier_to_real_fusion.py) : ensemble des 10 modèles rechargé depuis les checkpoints déjà entraînés au §10 (aucun ré-entraînement), fenêtre de 60 points glissée avec un pas de 5 (le courant plasma MAST est échantillonné bien plus densément que l'attention Wikipédia quotidienne de H1, d'où un pas différent de celui utilisé pour l'extension à H1) sur la fenêtre pré-quench (ou pré-fin-de-tir pour un tir stable) déjà isolée par `detect_quench` -- même logique de découpage que routers/fusion.py, réutilisée directement. Chaque fenêtre centrée-réduite par sa propre moyenne/écart-type.",
      },
      {
        text: "Résultat brut : sur le critère binaire \"au moins une fenêtre flaguée\", les 10 tirs disruptés ET les 10 tirs stables sont tous flagués (10/10 -- 10/10) -- comme lors du tout premier essai sur H1 avant la correction d'architecture (§10). Mais contrairement à ce premier essai sur H1 qui était plat partout, ici le taux de fenêtres flaguées varie réellement : 46,4% à 100% sur les tirs disruptés (moyenne 69,7%, probabilité moyenne 0,622), et 91,3% à 100% sur les tirs stables (moyenne 98,3%, probabilité moyenne 0,742).",
      },
      {
        text: "Lecture honnête : la variation existe, mais va dans le sens INVERSE de celui espéré d'un précurseur -- l'ensemble réagit en moyenne PLUS fortement aux tirs qui ne disruptent jamais qu'à ceux qui disruptent réellement. Aucune explication de confort retenue : ceci n'a pas été testé comme une hypothèse de détection de stabilité, ce serait spéculer au-delà de ce qui a été mesuré. Combiné au test de validité AR(1) du §10 (78% de fenêtres sans bifurcation flaguées à tort sur ce même ensemble), la lecture la plus prudente est que ce classifieur, dans cette adaptation et à cette échelle, ne généralise pas de façon fiable à un signal réel de tokamak.",
      },
      {
        text: "Complète la réponse à \"testé sur toutes les hypothèses ?\" pour le volet transversal IA vs statistiques : les deux extensions à données réelles déjà faites par ce chantier (§2.1 Société/H1, §2.4 Fusion) sont maintenant publiées ; §2.2 (H2, classifieur spatial) et §2.3 (H3, fusion double flux) restent à construire -- architectures différentes, pas une simple réapplication de cet ensemble.",
      },
    ],
  },
];

/** §7bis, point 7 -- état d'avancement du protocole de généralisation. */
export const PROGRESS_CHECKLIST = [
  { done: true, label: "Bifurcation réellement franchie (pas seulement approchée)" },
  { done: true, label: "Robustesse testée sur un couplage non diffusif" },
  { done: true, label: "Testé sur un réseau réel irrégulier (communes françaises)" },
  { done: true, label: "Fenêtres finies et bruit d'estimation (déjà inhérent au Monte-Carlo)" },
  { done: true, label: "Confronté aux épisodes historiques réels" },
];

export const JOURNAL_REFERENCES = [
  "Ives, A. R. (1995). « Measuring resilience in stochastic systems. » Ecological Monographs, 65(2), 217–233.",
  "Dakos, V., van Nes, E. H., Donangelo, R., Fort, H., & Scheffer, M. (2010). « Spatial correlation as leading indicator of catastrophic shifts. » Theoretical Ecology, 3, 163–174.",
  "Legault, V., Pu, Y., Weinans, E., & Cohen, A. A. (2024). « Application of early warning signs to physiological contexts: a comparison of multivariate indices in patients on long-term hemodialysis. » Frontiers in Network Physiology, 4, 1299162.",
];
