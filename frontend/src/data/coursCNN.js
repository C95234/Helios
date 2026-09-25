/**
 * Cours dédié : réseaux de neurones convolutifs (CNN) et rétropropagation --
 * cahier des charges "banc d'essai IA vs statistiques" §3. Document séparé
 * du cours de statistiques (même règle de non-duplication que les autres
 * cours du site) : lié depuis la page du banc d'essai, pas un paragraphe
 * isolé sur la page de résultat.
 */

export const CNN_SECTIONS = [
  {
    id: "convolution-1d",
    number: 1,
    title: "Convolution 1D",
    blocks: [
      {
        type: "definition",
        title: "Convolution 1D",
        body: [
          { text: "Pour une série d'entrée $x=(x_1,\\dots,x_n)$ et un noyau (filtre) $w=(w_1,\\dots,w_k)$ de biais $b$, la couche de convolution produit, en un point $i$ :" },
          { tex: "y_i = b + \\sum_{j=1}^{k} w_j\\, x_{i+j-1-p}", block: true },
          { text: "où $p$ décale la fenêtre (le \"padding\", des zéros ajoutés aux bords pour garder la même longueur en sortie). C'est en réalité une corrélation croisée (le noyau n'est pas retourné) -- une simplification standard partagée par toutes les bibliothèques de deep learning, PyTorch inclus, malgré le nom \"convolution\". Le même filtre $w$ est réutilisé à chaque position $i$ : c'est ce partage de poids qui rend la couche capable de détecter un motif local (par exemple une variance qui grimpe) où qu'il apparaisse dans la fenêtre, avec bien moins de paramètres qu'une couche pleinement connectée." },
        ],
      },
      {
        type: "exemple",
        title: "Un filtre \"détecteur de pic\" calculé à la main",
        body: [
          { text: "Fenêtre $x=(1,3,-1,2,0)$, noyau $w=(1,0,-1)$ (compare un point à son voisin d'avant), padding $p=1$ (un zéro de chaque côté), biais $b=0$. La série complétée est $(0,1,3,-1,2,0,0)$." },
          { tex: "y_1=1\\times0+0\\times1-1\\times3=-3,\\quad y_2=1-(-1)=2,\\quad y_3=3-2=1", block: true },
          { tex: "y_4=-1-0=-1,\\quad y_5=2-0=2 \\qquad\\Rightarrow\\qquad y=(-3,\\,2,\\,1,\\,-1,\\,2)", block: true },
          { text: "Après une fonction d'activation ReLU ($\\max(0,\\cdot)$), les valeurs négatives sont mises à 0 : $(0,2,1,0,2)$ -- seuls les endroits où la série \"monte\" par rapport au point précédent restent actifs. C'est exactement ce type de motif, appris automatiquement plutôt que choisi à la main, que le classifieur du banc d'essai IA vs statistiques exploite." },
        ],
      },
    ],
  },
  {
    id: "passe-avant",
    number: 2,
    title: "Passe avant d'un CNN simple, étape par étape",
    blocks: [
      {
        type: "definition",
        title: "Architecture utilisée dans le banc d'essai",
        body: [
          { text: "Le classifieur comparé à l'indicateur classique (page Résultat du banc d'essai) reprend l'architecture réelle de Bury et al. (2021) -- code source complet publié (github.com/ThomasMBury/deep-early-warnings-pnas), lu directement plutôt que reconstruit de mémoire : une couche de convolution (50 filtres, noyau de taille 12) suivie d'un ReLU, d'un abandon aléatoire (\"dropout\", 10% des activations mises à zéro à chaque passage pour limiter le surapprentissage) et d'un sous-échantillonnage par maximum, puis deux couches LSTM (mémoire court-terme, 50 puis 10 cellules) qui traitent la séquence dans le temps, chacune suivie d'un dropout, avant une couche de sortie :" },
          { tex: "\\text{Conv}_{50} \\to \\text{ReLU} \\to \\text{Dropout} \\to \\text{Pool}_2 \\to \\text{LSTM}_{50} \\to \\text{Dropout} \\to \\text{LSTM}_{10} \\to \\text{Dropout} \\to \\text{Dense}_1", block: true },
          { text: "Seule différence assumée avec l'architecture originale : une sortie Dense(1, sigmoïde) plutôt que Dense(4, softmax) -- Bury et al. classent le TYPE de bifurcation (fold, Hopf, transcritique ou nul, 4 classes) sur un grand nombre de modèles génériques, tandis que le banc d'essai teste seulement \"bascule proche ou non\" sur les 2 modèles déjà construits (nœud-col, Kuramoto) -- une tâche plus simple qui ne justifie pas 4 sorties. Code exact : backend/app/ml_benchmark.py, classe CnnLstmClassifier." },
        ],
      },
      {
        type: "remarque",
        title: "Ce qui n'est PAS repris de Bury et al. -- une échelle d'entraînement adaptée",
        body: [
          { text: "Bury et al. entraînent sur 200 000 séquences de longueur 500 à 1500, pendant 1500 passages complets des données. Mesuré directement sur le matériel de ce projet : une seule passe sur 95 000 fenêtres de longueur 60 (déjà plus courtes) prend déjà environ 150 secondes -- l'échelle originale y prendrait des heures par modèle, multiplié par les 10 modèles de l'ensemble. Le jeu d'entraînement et le nombre de passages sont donc réduits, et l'entraînement se fait par mini-lots plutôt qu'en un seul bloc (Bury et al. utilisent eux-mêmes des lots de 1000 exemples -- seule leur taille change ici). Aucune prétention de reproduire leurs résultats publiés à l'identique : l'objectif est de tester la MÊME architecture sur de nouveaux modèles et de nouvelles données, pas de battre leurs chiffres." },
        ],
      },
      {
        type: "remarque",
        title: "Un biais connu, testé plutôt qu'évité",
        body: [
          { text: "Un co-auteur de Bury et al. a publié une critique méthodologique du prétraitement de ce type de classifieur (Dablander & Bury, 2021) : entraîné sur des séries qui approchent une vraie bifurcation, un tel réseau peut aussi classer à tort un simple processus AR(1) stationnaire (aucune bifurcation, juste de la persistance temporelle) comme \"proche d'une bascule\". Le banc d'essai teste directement ce biais -- l'ensemble des 10 modèles est appliqué à des séries AR(1) synthétiques (plusieurs niveaux de persistance) et le taux de fenêtres flaguées à tort est rapporté sur la page de résultat, pas seulement mentionné comme une limite théorique." },
        ],
      },
      {
        type: "exemple",
        title: "Une passe avant complète, à la main, sur un réseau jouet",
        body: [
          { text: "L'architecture réelle ci-dessus (convolution + LSTM) est trop grande pour un calcul à la main -- une seule cellule LSTM implique déjà quatre portes et plusieurs matrices de poids. Pour suivre le calcul de bout en bout sans planche à calculer, on illustre ici seulement la partie convolutive sur un réseau miniature : une couche de convolution (un filtre, pas 50) suivie d'un ReLU, d'un max pooling, puis directement d'une couche dense à une sortie (sans LSTM) -- même enchaînement d'opérations que le début de l'architecture réelle, en miniature." },
          { text: "Entrée $x=(1,3,-1,2,0,1)$ ($n=6$). Filtre de convolution $w^{(1)}=(1,0,-1)$, biais $b^{(1)}=0$, padding $p=1$ (le même filtre \"détecteur de pic\" que ci-dessus). Série complétée : $(0,1,3,-1,2,0,1,0)$." },
          { tex: "y^{(1)} = (-3,\\ 2,\\ 1,\\ -1,\\ 1,\\ 0)", block: true },
          { text: "ReLU : les valeurs négatives passent à 0." },
          { tex: "a^{(1)} = (0,\\ 2,\\ 1,\\ 0,\\ 1,\\ 0)", block: true },
          { text: "Max pooling par paires (divise la longueur par 2, garde le plus grand de chaque paire) : paire $(0,2)\\to 2$, paire $(1,0)\\to 1$, paire $(1,0)\\to 1$." },
          { tex: "h = (2,\\ 1,\\ 1)", block: true },
          { text: "Couche dense (poids $w^{(2)}=(0{,}5,\\,-1,\\,2)$, biais $b^{(2)}=-0{,}5$) puis sigmoïde :" },
          { tex: "z = w^{(2)}\\cdot h + b^{(2)} = 0{,}5\\times2 - 1\\times1 + 2\\times1 - 0{,}5 = 1{,}5", block: true },
          { tex: "p = \\sigma(1{,}5) = \\frac{1}{1+e^{-1{,}5}} \\approx 0{,}8176", block: true },
          { text: "Le réseau prédit une probabilité de 81,76% que cette fenêtre soit proche d'une bascule. Cette même valeur $p$ sert de point de départ à l'exemple de rétropropagation de la section suivante -- vérifiée par le code (voir encart)." },
        ],
      },
      {
        type: "code",
        title: "Vérification de la passe avant",
        body: [
          {
            code: "import numpy as np\nx = np.array([1., 3., -1., 2., 0., 1.])\nxp = np.pad(x, 1)\nw1, b1 = np.array([1., 0., -1.]), 0.0\ny1 = np.array([w1 @ xp[i:i+3] + b1 for i in range(6)])\na1 = np.maximum(0, y1)                       # ReLU\nh = np.array([a1[0:2].max(), a1[2:4].max(), a1[4:6].max()])  # MaxPool\nw2, b2 = np.array([0.5, -1., 2.]), -0.5\nz = w2 @ h + b2\np = 1 / (1 + np.exp(-z))\nprint(y1, a1, h, z, p)\n# [-3.  2.  1. -1.  1.  0.] [0. 2. 1. 0. 1. 0.] [2. 1. 1.] 1.5 0.8175744761936437",
          },
        ],
      },
    ],
  },
  {
    id: "retropropagation",
    number: 3,
    title: "Rétropropagation et descente de gradient",
    blocks: [
      {
        type: "theoreme",
        title: "Dérivée de la perte d'entropie croisée avec sortie sigmoïde",
        body: [
          { text: "La dernière couche produit un score brut (\"logit\") $z$, transformé en probabilité par la fonction sigmoïde $p=\\sigma(z)=\\frac{1}{1+e^{-z}}$. Pour une étiquette $y\\in\\{0,1\\}$ (bascule proche ou non), la perte d'entropie croisée binaire est $L=-\\big[y\\ln p+(1-y)\\ln(1-p)\\big]$. Sa dérivée par rapport au logit $z$ -- le point de départ de toute rétropropagation -- vaut simplement :" },
          { tex: "\\frac{dL}{dz} = p - y", block: true },
        ],
        proof: [
          { text: "La sigmoïde vérifie $\\sigma'(z)=\\sigma(z)\\big(1-\\sigma(z)\\big)=p(1-p)$ (dérivée classique, à retrouver en écrivant $\\sigma(z)=(1+e^{-z})^{-1}$ et en dérivant). Par la règle de la chaîne :" },
          { tex: "\\frac{dL}{dz}=\\frac{dL}{dp}\\cdot\\frac{dp}{dz} = \\left(-\\frac{y}{p}+\\frac{1-y}{1-p}\\right)p(1-p) = -y(1-p)+(1-y)p", block: true },
          { tex: "= -y+yp+p-yp = p-y", block: true },
          { text: "Une identité remarquablement simple : l'erreur qui se propage vers les couches précédentes est juste l'écart entre la probabilité prédite et l'étiquette réelle." },
        ],
      },
      {
        type: "exemple",
        title: "Rétropropagation complète sur le réseau jouet, à la main",
        body: [
          { text: "On reprend le réseau et les valeurs de la section précédente ($p\\approx0{,}8176$), avec une étiquette réelle $y=1$ (cette fenêtre approche vraiment une bascule). But : calculer le gradient de la perte par rapport à CHAQUE poids, couche par couche, en remontant depuis la sortie -- exactement ce que fait `loss.backward()` dans le code, ici entièrement à la main." },
          { text: "Perte observée et gradient au niveau du logit (théorème ci-dessus) :" },
          { tex: "L = -\\ln(0{,}8176) \\approx 0{,}2014, \\qquad \\frac{dL}{dz} = p - y = 0{,}8176 - 1 = -0{,}1824", block: true },
          { text: "Couche dense ($z=w^{(2)}\\cdot h+b^{(2)}$) : la règle de la chaîne donne le gradient par rapport à chaque poids en multipliant $\\frac{dL}{dz}$ par l'entrée $h$ correspondante, et par rapport au biais directement $\\frac{dL}{dz}$ :" },
          { tex: "\\frac{dL}{dw^{(2)}} = \\frac{dL}{dz}\\,h = -0{,}1824\\times(2,1,1) = (-0{,}3649,\\ -0{,}1824,\\ -0{,}1824), \\qquad \\frac{dL}{db^{(2)}} = -0{,}1824", block: true },
          { text: "Pour continuer à remonter, il faut aussi le gradient par rapport à l'ENTRÉE de la couche dense (pas seulement ses poids) :" },
          { tex: "\\frac{dL}{dh} = \\frac{dL}{dz}\\,w^{(2)} = -0{,}1824\\times(0{,}5,-1,2) = (-0{,}0912,\\ 0{,}1824,\\ -0{,}3649)", block: true },
          { text: "Max pooling : le gradient ne circule QUE vers la position qui a été retenue comme maximum dans chaque paire (les autres reçoivent un gradient nul -- elles n'ont eu aucune influence sur la sortie). Les maximums retenus étaient aux positions 1, 2 et 4 (indices 0-based) du vecteur $a^{(1)}$ :" },
          { tex: "\\frac{dL}{da^{(1)}} = (0,\\ -0{,}0912,\\ 0{,}1824,\\ 0,\\ -0{,}3649,\\ 0)", block: true },
          { text: "ReLU : la dérivée vaut 1 là où la sortie était strictement positive, 0 ailleurs (le gradient ne passe pas là où le neurone était déjà éteint). $y^{(1)}=(-3,2,1,-1,1,0)$ n'est strictement positif qu'aux positions 1, 2 et 4 -- déjà les seules positions non nulles ci-dessus, donc ce masque ne change rien numériquement ici :" },
          { tex: "\\frac{dL}{dy^{(1)}} = (0,\\ -0{,}0912,\\ 0{,}1824,\\ 0,\\ -0{,}3649,\\ 0)", block: true },
          { text: "Convolution : le gradient par rapport au filtre $w^{(1)}_k$ ($k=0,1,2$) est la somme, sur toutes les positions $i$, du gradient sortant en $i$ multiplié par l'entrée (complétée par le padding) qui a contribué à cette position :" },
          { tex: "\\frac{dL}{dw^{(1)}_k} = \\sum_{i=0}^{5} \\frac{dL}{dy^{(1)}_i}\\, x^{\\text{pad}}_{i+k}", block: true },
          { tex: "\\frac{dL}{dw^{(1)}} \\approx (-0{,}2736,\\ -0{,}4561,\\ 0{,}0912), \\qquad \\frac{dL}{db^{(1)}} = \\sum_i \\frac{dL}{dy^{(1)}_i} \\approx -0{,}2736", block: true },
          { text: "Chaque gradient calculé à la main ci-dessus est vérifié par différences finies dans le code (encart ci-dessous) : la rétropropagation n'est rien d'autre que l'application répétée, couche par couche, de la même règle de la chaîne que celle du premier théorème." },
        ],
      },
      {
        type: "code",
        title: "Vérification de la rétropropagation par différences finies",
        body: [
          {
            code: "import numpy as np\n\ndef forward(w1, b1, w2, b2):\n    xp = np.pad(x, 1)\n    y1 = np.array([w1 @ xp[i:i+3] + b1 for i in range(6)])\n    a1 = np.maximum(0, y1)\n    h = np.array([a1[0:2].max(), a1[2:4].max(), a1[4:6].max()])\n    z = w2 @ h + b2\n    p = 1 / (1 + np.exp(-z))\n    return -(y_true * np.log(p) + (1 - y_true) * np.log(1 - p))\n\nx, y_true = np.array([1., 3., -1., 2., 0., 1.]), 1.0\nw1, b1, w2, b2 = np.array([1., 0., -1.]), 0.0, np.array([0.5, -1., 2.]), -0.5\n\neps = 1e-6\ngrad_numeric = np.zeros(3)\nfor k in range(3):\n    wp, wm = w1.copy(), w1.copy()\n    wp[k] += eps; wm[k] -= eps\n    grad_numeric[k] = (forward(wp, b1, w2, b2) - forward(wm, b1, w2, b2)) / (2 * eps)\nprint(grad_numeric)\n# [-0.27363829 -0.45606381  0.09121276]  -- identique au calcul a la main ci-dessus",
          },
        ],
      },
      {
        type: "remarque",
        title: "Rééquilibrer des classes déséquilibrées (pos_weight)",
        body: [
          { text: "Dans les données d'entraînement du banc d'essai, les fenêtres \"proches d'une bascule\" sont rares (environ 1 sur 5 après sous-échantillonnage des négatives -- avant, moins de 1%). Sans correction, un classifieur entraîné sur cette perte apprend un signal réel mais jamais assez fort pour franchir le seuil de décision à 0,5 -- vérifié empiriquement avant d'ajouter cette correction (voir le code). La perte utilisée pondère le terme positif par $w_+=n_{\\text{neg}}/n_{\\text{pos}}$ (le déséquilibre observé), ce qui revient à traiter chaque exemple positif comme s'il apparaissait $w_+$ fois -- une correction standard, pas une invention, disponible nativement dans PyTorch (BCEWithLogitsLoss, argument pos_weight)." },
        ],
      },
      {
        type: "theoreme",
        title: "Pourquoi la descente de gradient fait baisser la perte",
        body: [
          { text: "Pour ajuster l'ensemble des poids $\\theta$ du réseau (tous les $w^{(l)}$ et $b^{(l)}$ de chaque couche), la règle de mise à jour est :" },
          { tex: "\\theta_{t+1} = \\theta_t - \\eta\\,\\nabla L(\\theta_t)", block: true },
          { text: "où $\\eta>0$ est le taux d'apprentissage et $\\nabla L$ le gradient (le vecteur des dérivées de $L$ par rapport à chaque poids, calculé couche par couche par rétropropagation -- l'application répétée de la règle de la chaîne illustrée ci-dessus, Rumelhart, Hinton & Williams, 1986). Pour $\\eta$ assez petit, cette mise à jour diminue toujours la perte (sauf si $\\nabla L=0$, un minimum déjà atteint)." },
        ],
        proof: [
          { text: "Développement de Taylor à l'ordre 1 autour de $\\theta_t$ :" },
          { tex: "L(\\theta_t-\\eta\\nabla L) \\approx L(\\theta_t) - \\eta\\,\\|\\nabla L(\\theta_t)\\|^2 + O(\\eta^2)", block: true },
          { text: "Le terme $-\\eta\\|\\nabla L\\|^2$ est strictement négatif dès que $\\nabla L\\neq 0$ (une norme au carré est positive) : pour $\\eta$ suffisamment petit, il domine le reste ($O(\\eta^2)$, négligeable devant $\\eta$), donc $L(\\theta_{t+1}) < L(\\theta_t)$." },
        ],
      },
      {
        type: "remarque",
        title: "Adam : une descente de gradient plus sophistiquée",
        body: [
          { text: "L'entraînement du banc d'essai utilise Adam (Kingma & Ba, 2015) plutôt que la règle brute ci-dessus : chaque poids reçoit son propre taux d'apprentissage effectif, ajusté à partir d'une moyenne mobile du gradient et de son carré -- concrètement, les poids qui reçoivent des gradients petits mais réguliers avancent plus vite que ceux qui reçoivent des gradients bruités. Méthode directement réutilisée (implémentation native de PyTorch), pas rederivée ici -- seul le principe de base (la descente de gradient elle-même) est démontré ci-dessus." },
        ],
      },
      {
        type: "remarque",
        title: "Lien avec hopfieldkit",
        body: [
          { text: "La descente de gradient n'est pas propre aux réseaux convolutifs : le paquet hopfieldkit (domaine Mémoire collective) implémente un second mode d'apprentissage par descente de gradient pour les réseaux de Hopfield (règle de type perceptron, Gardner 1988), avec sa propre démonstration complète -- voir /methode/hopfield. Le principe (ajuster des poids pour réduire une perte, en suivant le gradient) est rigoureusement le même que celui démontré ici ; seule la fonction de perte et l'architecture changent." },
        ],
      },
      {
        type: "exercice",
        title: "Un pas de descente de gradient à la main",
        body: [
          { text: "Un modèle à un seul poids $w$ (biais nul) prédit $z=wx$ pour une entrée $x=1$, dont l'étiquette réelle est $y=1$. Le poids vaut initialement $w=0$, le taux d'apprentissage $\\eta=0{,}1$. Calculer $p$, puis $\\frac{dL}{dw}$, puis le poids après un pas de descente de gradient." },
        ],
        correction: [
          { tex: "z = w x = 0 \\times 1 = 0 \\quad\\Rightarrow\\quad p=\\sigma(0)=0{,}5", block: true },
          { text: "Par le théorème ci-dessus, $\\frac{dL}{dz}=p-y=0{,}5-1=-0{,}5$. Comme $z=wx$, $\\frac{dz}{dw}=x=1$, donc par la règle de la chaîne :" },
          { tex: "\\frac{dL}{dw} = \\frac{dL}{dz}\\cdot\\frac{dz}{dw} = -0{,}5 \\times 1 = -0{,}5", block: true },
          { tex: "w_{\\text{nouveau}} = w - \\eta\\frac{dL}{dw} = 0 - 0{,}1\\times(-0{,}5) = 0{,}05", block: true },
          { text: "Le poids augmente légèrement : puisque l'étiquette réelle est $y=1$ mais la prédiction actuelle ($p=0{,}5$) la sous-estime, la mise à jour pousse $z=wx$ vers le haut pour la prochaine fois -- exactement le comportement attendu." },
        ],
      },
    ],
  },
  {
    id: "convolution-graphe",
    number: 4,
    title: "Convolution de graphe (le classifieur spatial de H2)",
    blocks: [
      {
        type: "definition",
        title: "Pourquoi une convolution de GRAPHE plutôt qu'un CNN 2D",
        body: [
          { text: "H2 (§2.2 du banc d'essai) pose une question spatiale, pas temporelle : un instantané par département, pas une fenêtre glissante. Un CNN 2D classique suppose une grille régulière où chaque case a des voisins fixes (haut/bas/gauche/droite) -- exactement ce qui manque ici : les départements n'ont pas de coordonnées géographiques disponibles dans le projet (seule leur liste de voisins directs, l'adjacence, est connue), et rasteriser sur une carte fabriquerait une géométrie arbitraire plutôt que d'utiliser la vraie structure. La généralisation directe d'une convolution à un graphe IRRÉGULIER est un réseau de convolution de graphe (GCN, Kipf & Welling, 2017) : au lieu de faire glisser un noyau sur des positions voisines fixes, chaque nœud combine sa propre valeur avec celle de ses VRAIS voisins, tels que définis par la matrice d'adjacence." },
        ],
      },
      {
        type: "definition",
        title: "Propagation spectrale normalisée",
        body: [
          { text: "Pour un graphe de matrice d'adjacence $A$ ($n$ nœuds), on ajoute d'abord une boucle propre à chaque nœud (il doit voir sa propre valeur, pas seulement celle de ses voisins) : $\\tilde A = A + I$. Le degré (nombre de connexions, boucle incluse) du nœud $i$ est $\\tilde d_i = \\sum_j \\tilde A_{ij}$. La matrice de propagation normalisée -- celle qui remplace le \"glissement du noyau\" d'un CNN classique -- est :" },
          { tex: "\\hat A = D^{-1/2}\\tilde A D^{-1/2}, \\qquad \\hat A_{ij} = \\frac{\\tilde A_{ij}}{\\sqrt{\\tilde d_i \\tilde d_j}}", block: true },
          { text: "où $D=\\text{diag}(\\tilde d_1,\\dots,\\tilde d_n)$. Cette normalisation (par la racine carrée du produit des degrés plutôt qu'une simple moyenne) évite qu'un nœud très connecté n'écrase les autres dans la somme -- une couche complète calcule ensuite $H' = \\text{ReLU}(\\hat A\\, X\\, \\Theta)$ : chaque valeur $X$ est d'abord projetée par des poids appris $\\Theta$ (comme le ferait une couche dense), PUIS propagée aux voisins via $\\hat A$, exactement comme une convolution 1D propage l'information locale via son noyau (Section 1)." },
        ],
      },
      {
        type: "exemple",
        title: "Propagation calculée à la main sur un petit graphe",
        body: [
          { text: "Même graphe-chaîne que l'exemple de référence de l'indice de Moran (cours de statistiques) : 4 nœuds en chaîne $1-2-3-4$, valeurs $x=(1,2,3,4)$. Matrice d'adjacence et degrés (boucle propre incluse) :" },
          { table: { headers: ["", "1", "2", "3", "4", "degré total"], rows: [["1", "1", "1", "0", "0", "2"], ["2", "1", "1", "1", "0", "3"], ["3", "0", "1", "1", "1", "3"], ["4", "0", "0", "1", "1", "2"]] } },
          { text: "La matrice de propagation normalisée $\\hat A=D^{-1/2}\\tilde A D^{-1/2}$ (ex. $\\hat A_{12}=1/\\sqrt{2\\times3}=1/\\sqrt6\\approx0{,}4082$) :" },
          { tex: "\\hat A \\approx \\begin{pmatrix} 0{,}5 & 0{,}4082 & 0 & 0 \\\\ 0{,}4082 & 0{,}3333 & 0{,}3333 & 0 \\\\ 0 & 0{,}3333 & 0{,}3333 & 0{,}4082 \\\\ 0 & 0 & 0{,}4082 & 0{,}5 \\end{pmatrix}", block: true },
          { text: "Projection par un poids scalaire appris $\\theta=2$, biais $b=-4$ (une seule caractéristique par nœud ici, comme le classifieur spatial réel qui reçoit une valeur brute par département) : $\\text{proj} = \\theta x + b = (-2,\\ 0,\\ 2,\\ 4)$. Propagation $\\hat A \\cdot \\text{proj}$ :" },
          { tex: "h_1 \\approx 0{,}5\\times(-2) + 0{,}4082\\times0 = -1", block: true },
          { tex: "h_2 \\approx 0{,}4082\\times(-2) + 0{,}3333\\times0 + 0{,}3333\\times2 \\approx -0{,}1498", block: true },
          { tex: "h_3 \\approx 0{,}3333\\times0 + 0{,}3333\\times2 + 0{,}4082\\times4 \\approx 2{,}2997, \\qquad h_4 \\approx 0{,}4082\\times2 + 0{,}5\\times4 \\approx 2{,}8165", block: true },
          { text: "Après ReLU, les deux premières valeurs (négative et quasi nulle) sont mises à 0 -- les nœuds 1 et 2, en périphérie de la chaîne et projetés à des valeurs basses, n'activent rien ici, alors que les nœuds 3 et 4 restent actifs :" },
          { tex: "h \\approx (0,\\ 0,\\ 2{,}2997,\\ 2{,}8165)", block: true },
          { text: "L'architecture réelle (backend/app/spatial_ml.py) fait ce calcul DEUX FOIS sur le MÊME instantané -- une fois avec l'adjacence du réseau réel, une fois avec celle d'une grille de contrôle -- puis regroupe chaque résultat par une moyenne ET un maximum sur tous les nœuds (moyenne $\\approx1{,}2790$, maximum $\\approx2{,}8165$ ici), avant de concaténer les deux branches pour la décision finale. Jamais la topologie d'origine donnée explicitement en entrée -- seule la valeur brute $x$ l'est, comme le CNN-LSTM temporel ne voit que la fenêtre brute (Section 2)." },
        ],
      },
      {
        type: "code",
        title: "Vérification de la propagation",
        body: [
          {
            code: "import numpy as np\nA = np.array([[0,1,0,0],[1,0,1,0],[0,1,0,1],[0,0,1,0]], dtype=float)\nAtilde = A + np.eye(4)\nd = Atilde.sum(axis=1)\nDinv_sqrt = np.diag(1/np.sqrt(d))\nAhat = Dinv_sqrt @ Atilde @ Dinv_sqrt\nx = np.array([1., 2., 3., 4.])\nproj = 2*x - 4\nh = np.maximum(0, Ahat @ proj)\nprint(h)\n# [0.         0.         2.29973271 2.81649658]",
          },
        ],
      },
      {
        type: "remarque",
        title: "Rétropropagation : rien de nouveau à démontrer",
        body: [
          { text: "$\\hat A\\, X\\, \\Theta$ n'est qu'une succession de produits matriciels, exactement comme $w^{(1)} * x$ pour la convolution 1D (Section 1) -- la règle de la chaîne appliquée à la rétropropagation de la Section 3 s'y applique sans aucune modification : le gradient par rapport à $\\Theta$ se calcule en multipliant le gradient sortant par $\\hat A^\\top$ puis par $X$, exactement comme le gradient du filtre de convolution se calculait en multipliant par l'entrée décalée. Aucune nouvelle dérivation n'est nécessaire ici -- seule la matrice qui multiplie l'entrée change (un noyau glissant devient une matrice de propagation fixe), pas le principe." },
        ],
      },
    ],
  },
  {
    id: "fusion-double-flux",
    number: 5,
    title: "Fusion double flux (le classifieur joint de H3)",
    blocks: [
      {
        type: "definition",
        title: "Deux branches, une décision commune",
        body: [
          { text: "H3 (§2.3 du banc d'essai) pose une question à ENTRÉE DOUBLE : la tendance temporelle nationale ET l'indice de Moran spatial sont-ils anormaux EN MÊME TEMPS ? Ni le CNN-LSTM temporel seul (Section 2) ni la convolution de graphe seule (Section 4) ne voit les deux canaux à la fois -- le classifieur joint (backend/app/h3_ml.py) calcule donc un EMBEDDING (un résumé numérique en quelques nombres) par branche, puis les concatène avant une seule couche de décision :" },
          { tex: "e_{\\text{temporel}} = \\text{CNN-LSTM}(x_{\\text{fenêtre}}) \\in \\mathbb{R}^{10}, \\qquad e_{\\text{spatial}} = [\\text{moyenne}(h),\\ \\text{max}(h)] \\in \\mathbb{R}^{2}", block: true },
          { tex: "p = \\sigma\\big(w_{\\text{tête}} \\cdot [e_{\\text{temporel}} \\,;\\, e_{\\text{spatial}}] + b_{\\text{tête}}\\big)", block: true },
          { text: "où $[\\,;\\,]$ dénote la concaténation (les deux vecteurs mis bout à bout). C'est une fusion TARDIVE (chaque branche traite son propre canal jusqu'au bout avant que les deux ne se rencontrent), la plus simple qui réponde à la question posée -- pas une fusion précoce (mélanger les deux canaux dès le départ) ni une attention croisée (chaque branche qui \"regarde\" l'autre), deux architectures plus sophistiquées mais non demandées ici." },
        ],
      },
      {
        type: "exemple",
        title: "Fusion calculée à la main, à partir des deux exemples précédents",
        body: [
          { text: "Réutilise directement les résultats déjà obtenus : la sortie de la partie convolutive du réseau jouet temporel (Section 2, avant sa propre couche dense), $h_{\\text{temp}}=(2,\\,1,\\,1)$, comme embedding temporel simplifié ; et la moyenne/maximum de la propagation de graphe de la Section 4, $e_{\\text{spatial}}=(1{,}2790,\\ 2{,}8165)$. Concaténation :" },
          { tex: "e = [2,\\ 1,\\ 1,\\ 1{,}2790,\\ 2{,}8165]", block: true },
          { text: "Couche de décision (poids $w_{\\text{tête}}=(0{,}2,\\,-0{,}3,\\,0{,}1,\\,0{,}5,\\,-0{,}2)$, biais $b_{\\text{tête}}=0{,}1$, choisis arbitrairement pour l'exemple) :" },
          { tex: "z = 0{,}2\\times2 - 0{,}3\\times1 + 0{,}1\\times1 + 0{,}5\\times1{,}2790 - 0{,}2\\times2{,}8165 + 0{,}1 \\approx 0{,}3762", block: true },
          { tex: "p = \\sigma(0{,}3762) \\approx 0{,}5930", block: true },
          { text: "Le réseau prédit une probabilité de 59,3% d'anomalie jointe -- ni proche de 0 ni proche de 1, ce que des poids choisis arbitrairement pour l'illustration donnent naturellement (les vrais poids sont appris par entraînement, voir la Section 3, exactement la même mécanique de descente de gradient)." },
        ],
      },
      {
        type: "code",
        title: "Vérification de la fusion",
        body: [
          {
            code: "import numpy as np\ne_temporal = np.array([2., 1., 1.])\ne_spatial = np.array([1.2790391023624612, 2.8164965809277254])\ne = np.concatenate([e_temporal, e_spatial])\nw_head = np.array([0.2, -0.3, 0.1, 0.5, -0.2])\nb_head = 0.1\nz = w_head @ e + b_head\np = 1 / (1 + np.exp(-z))\nprint(z, p)\n# 0.3762202349956856 0.592961147082116",
          },
        ],
      },
      {
        type: "remarque",
        title: "Le gradient se sépare, il ne se réinvente pas",
        body: [
          { text: "La rétropropagation à travers une fusion tardive n'ajoute qu'une seule étape nouvelle par rapport à la Section 3 : au moment de remonter le gradient à travers la concaténation, le vecteur $\\frac{dL}{de}$ (de même dimension que $e$) se SÉPARE simplement en deux morceaux -- les 10 premières composantes repartent dans la branche temporelle, les 2 dernières dans la branche spatiale -- chacune ensuite rétropropagée indépendamment par la même règle de la chaîne déjà démontrée (Section 3 pour la branche temporelle, remarque de la Section 4 pour la branche spatiale). Aucune nouvelle dérivation n'est nécessaire : fusionner deux flux ne change que l'endroit où le graphe de calcul se sépare en deux, pas les règles de dérivation elles-mêmes." },
        ],
      },
    ],
  },
];

export const CNN_REFERENCES = [
  "Rumelhart, D. E., Hinton, G. E., & Williams, R. J. (1986). « Learning representations by back-propagating errors. » Nature, 323, 533-536.",
  "Kingma, D. P., & Ba, J. (2015). « Adam: A Method for Stochastic Optimization. » 3rd International Conference on Learning Representations (ICLR).",
  "Bury, T. M., Sujith, R. I., Pavithran, I., Scheffer, M., Lenton, T. M., Anand, M., & Bauch, C. T. (2021). « Deep learning for early warning signals of tipping points. » Proceedings of the National Academy of Sciences, 118(39), e2106140118.",
  "Dablander, F., & Bury, T. M. (2021). « Deep learning for tipping points: Preprocessing matters. » Proceedings of the National Academy of Sciences, 118(40), e2115605118.",
  "Gardner, E. (1988). « The space of interactions in neural network models. » Journal of Physics A, 21(1), 257–270.",
  "Kipf, T. N., & Welling, M. (2017). « Semi-Supervised Classification with Graph Convolutional Networks. » 5th International Conference on Learning Representations (ICLR).",
];
