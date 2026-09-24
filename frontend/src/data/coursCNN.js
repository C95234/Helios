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
          { text: "Le classifieur comparé à l'indicateur classique (page Résultat du banc d'essai) empile deux couches de convolution (8 puis 16 filtres, noyau de taille 5) chacune suivie d'un ReLU et d'un sous-échantillonnage par maximum (\"max pooling\", divise la longueur par 2 en gardant la valeur la plus forte de chaque paire), puis aplatit le résultat en un vecteur passé à deux couches pleinement connectées (32 puis 1 sortie) :" },
          { tex: "\\text{Conv}_8 \\to \\text{ReLU} \\to \\text{Pool}_2 \\to \\text{Conv}_{16} \\to \\text{ReLU} \\to \\text{Pool}_2 \\to \\text{Aplatir} \\to \\text{Dense}_{32} \\to \\text{ReLU} \\to \\text{Dense}_1", block: true },
          { text: "Volontairement modeste (2 couches de convolution, quelques milliers de paramètres) -- pas une reproduction de l'architecture de Bury et al. (2021), qui empile davantage de couches et vise en plus à identifier le type de bifurcation. Code exact : backend/app/ml_benchmark.py, classe SimpleCNN1D." },
        ],
      },
      {
        type: "exemple",
        title: "Une passe avant complète, à la main, sur un réseau jouet",
        body: [
          { text: "Pour suivre le calcul de bout en bout sans planche à calculer, on réduit l'architecture ci-dessus à une seule couche de convolution (un filtre, pas huit) suivie d'un ReLU, d'un max pooling, puis d'une couche dense à une sortie -- même enchaînement d'opérations, en miniature." },
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
];

export const CNN_REFERENCES = [
  "Rumelhart, D. E., Hinton, G. E., & Williams, R. J. (1986). « Learning representations by back-propagating errors. » Nature, 323, 533-536.",
  "Kingma, D. P., & Ba, J. (2015). « Adam: A Method for Stochastic Optimization. » 3rd International Conference on Learning Representations (ICLR).",
  "Bury, T. M., Sujith, R. I., Pavithran, I., Scheffer, M., Lenton, T. M., Anand, M., & Bauch, C. T. (2021). « Deep learning for early warning signals of tipping points. » Proceedings of the National Academy of Sciences, 118(39), e2106140118.",
  "Gardner, E. (1988). « The space of interactions in neural network models. » Journal of Physics A, 21(1), 257–270.",
];
