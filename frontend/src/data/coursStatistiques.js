/**
 * Cours de statistiques appliquees -- transcription integrale du document
 * fourni par l'utilisateur (cours-statistiques-helios.pdf), pour la
 * section Methode de la restructuration du site (cahier des charges de
 * restructuration §2.4). Chaque notion : definition, demonstration quand
 * possible avec les outils de terminale, exemple resolu, exercice corrige.
 *
 * Convention de bloc : { type, title, body, proof?, correction? }
 * - body : tableau de { text } (prose, $...$ pour LaTeX inline) ou
 *   { tex, block:true } (formule en bloc) ou { table:{headers, rows} }
 * - proof / correction : meme forme que body, affiches dans un sous-bloc
 */

export const COURS_SECTIONS = [
  {
    id: "esperance-variance",
    number: 1,
    title: "Variable aléatoire, espérance, variance",
    blocks: [
      {
        type: "definition",
        title: "Espérance et variance",
        body: [
          { text: "Pour une variable aléatoire $X$ prenant les valeurs $x_1,\\dots,x_n$ avec probabilités $p_1,\\dots,p_n$ :" },
          { tex: "E(X) = \\sum_i p_i x_i, \\qquad \\text{Var}(X) = E\\big[(X-E(X))^2\\big] = E(X^2) - E(X)^2", block: true },
          { text: "L'écart-type est $\\sigma(X) = \\sqrt{\\text{Var}(X)}$." },
        ],
      },
      {
        type: "propriete",
        title: "Linéarité de l'espérance",
        body: [{ tex: "\\text{Pour toutes variables aléatoires } X, Y \\text{ et réels } a,b : \\quad E(aX+bY) = aE(X) + bE(Y)", block: true }],
        proof: [
          { tex: "E(aX+bY) = \\sum_i p_i(ax_i+by_i) = a\\sum_i p_i x_i + b\\sum_i p_i y_i = aE(X)+bE(Y)", block: true },
          { text: "en utilisant simplement la distributivité de la somme." },
        ],
      },
      {
        type: "theoreme",
        title: "Variance d'une somme de variables indépendantes",
        body: [{ tex: "\\text{Si } X \\text{ et } Y \\text{ sont indépendantes, alors } \\text{Var}(X+Y) = \\text{Var}(X) + \\text{Var}(Y)", block: true }],
        proof: [
          { text: "Notons $\\mu_X = E(X)$, $\\mu_Y = E(Y)$. On développe :" },
          { tex: "\\text{Var}(X+Y) = E\\big[(X+Y-\\mu_X-\\mu_Y)^2\\big] = E\\big[(X-\\mu_X)^2\\big] + E\\big[(Y-\\mu_Y)^2\\big] + 2E\\big[(X-\\mu_X)(Y-\\mu_Y)\\big]", block: true },
          { text: "Le dernier terme est la covariance de $X$ et $Y$ (voir §2). Or si $X$ et $Y$ sont indépendantes, $E[(X-\\mu_X)(Y-\\mu_Y)] = E(X-\\mu_X)\\cdot E(Y-\\mu_Y) = 0 \\times 0 = 0$ (l'espérance d'un produit de variables indépendantes est le produit des espérances). Il reste Var(X+Y) = Var(X) + Var(Y)." },
        ],
      },
      {
        type: "exemple",
        title: "Deux dés",
        body: [
          { text: "On lance deux dés équilibrés indépendants $D_1, D_2$. On sait que $E(D_1)=3{,}5$ et $\\text{Var}(D_1) = \\frac{35}{12}$ (calcul classique, admis). Quelle est la variance de la somme $S = D_1+D_2$ ?" },
          { text: "Par le théorème précédent, comme $D_1$ et $D_2$ sont indépendants :" },
          { tex: "\\text{Var}(S) = \\text{Var}(D_1)+\\text{Var}(D_2) = \\frac{35}{12}+\\frac{35}{12} = \\frac{35}{6} \\approx 5{,}83", block: true },
        ],
      },
      {
        type: "exercice",
        title: "Trois mesures indépendantes",
        body: [
          { text: "Une grandeur est mesurée trois fois de façon indépendante, chaque mesure ayant un écart-type de $\\sigma=2$. Quelle est la variance, puis l'écart-type, de la moyenne des trois mesures $M = \\frac{X_1+X_2+X_3}{3}$ ?" },
        ],
        correction: [
          { text: "On utilise $\\text{Var}(aX)=a^2\\text{Var}(X)$ (propriété de terminale) et l'indépendance :" },
          { tex: "\\text{Var}(M) = \\text{Var}\\Big(\\tfrac{1}{3}(X_1+X_2+X_3)\\Big) = \\tfrac{1}{9}\\big(\\text{Var}(X_1)+\\text{Var}(X_2)+\\text{Var}(X_3)\\big) = \\tfrac{1}{9}(4+4+4) = \\tfrac{12}{9} = \\tfrac{4}{3}", block: true },
          { text: "Donc $\\sigma(M) = \\sqrt{4/3} \\approx 1{,}15$. Point important : la moyenne de plusieurs mesures indépendantes est plus précise (écart-type plus petit) que chaque mesure individuelle — c'est le principe même de l'échantillonnage statistique." },
        ],
      },
    ],
  },
  {
    id: "covariance-correlation",
    number: 2,
    title: "Covariance et corrélation",
    blocks: [
      {
        type: "definition",
        title: "Covariance et coefficient de corrélation",
        body: [
          { text: "Pour deux séries de données $(x_i)$ et $(y_i)$, $i=1,\\dots,n$, de moyennes $\\bar{x}, \\bar{y}$ :" },
          { tex: "\\text{Cov}(x,y) = \\frac{1}{n}\\sum_i (x_i-\\bar{x})(y_i-\\bar{y}), \\qquad r = \\frac{\\text{Cov}(x,y)}{\\sigma(x)\\,\\sigma(y)}", block: true },
          { text: "$r$ est le coefficient de corrélation de Pearson." },
        ],
      },
      {
        type: "theoreme",
        title: "r est toujours compris entre −1 et 1",
        body: [{ text: "Pour toutes séries $(x_i)$ et $(y_i)$ non constantes, $-1 \\le r \\le 1$." }],
        proof: [
          { text: "Posons $u_i = x_i-\\bar{x}$ et $v_i = y_i-\\bar{y}$, vus comme deux vecteurs $\\vec{u},\\vec{v}\\in\\mathbb{R}^n$. Le produit scalaire vérifie $\\vec{u}\\cdot\\vec{v} = \\|\\vec{u}\\|\\|\\vec{v}\\|\\cos\\theta$, donc $|\\vec{u}\\cdot\\vec{v}| \\le \\|\\vec{u}\\|\\|\\vec{v}\\|$ (inégalité de Cauchy-Schwarz) — conséquence directe de $|\\cos\\theta|\\le 1$, notion vue en spécialité mathématiques." },
          { text: "Ici, $\\vec{u}\\cdot\\vec{v} = \\sum_i u_i v_i = n\\,\\text{Cov}(x,y)$, et $\\|\\vec{u}\\| = \\sqrt{\\sum_i u_i^2} = \\sqrt{n}\\,\\sigma(x)$, de même $\\|\\vec{v}\\| = \\sqrt{n}\\,\\sigma(y)$. L'inégalité de Cauchy-Schwarz donne :" },
          { tex: "n\\,|\\text{Cov}(x,y)| \\le \\sqrt{n}\\,\\sigma(x)\\cdot\\sqrt{n}\\,\\sigma(y) = n\\,\\sigma(x)\\sigma(y)", block: true },
          { text: "donc $|\\text{Cov}(x,y)| \\le \\sigma(x)\\sigma(y)$, c'est-à-dire $|r|\\le 1$." },
        ],
      },
      {
        type: "exemple",
        title: "Corrélation entre deux petites séries",
        body: [
          { text: "On mesure $x=(1,2,3,4)$ et $y=(2,3,5,4)$. Calculer $r$." },
          { text: "$\\bar{x}=2{,}5$, $\\bar{y}=3{,}5$. Écarts : $u=(-1{,}5;-0{,}5;0{,}5;1{,}5)$, $v=(-1{,}5;-0{,}5;1{,}5;0{,}5)$." },
          { tex: "\\text{Cov} = \\tfrac{1}{4}\\big[2{,}25+0{,}25+0{,}75+0{,}75\\big] = 1{,}0, \\qquad \\sigma(x)^2 = \\sigma(y)^2 = 1{,}25", block: true },
          { tex: "r = \\frac{1{,}0}{1{,}25} = 0{,}8", block: true },
          { text: "Forte corrélation positive : $x$ et $y$ augmentent globalement ensemble." },
        ],
      },
      {
        type: "exercice",
        title: "Corrélation nulle malgré un lien",
        body: [{ text: "Soit $x=(-2,-1,0,1,2)$ et $y=(4,1,0,1,4)$ (on a $y=x^2$). Calculer $r$ et commenter." }],
        correction: [
          { text: "$\\bar{x}=0$, $\\bar{y}=2$. Écarts en $x$ : $(-2,-1,0,1,2)$. Écarts en $y$ : $(2,-1,-2,-1,2)$." },
          { tex: "\\text{Cov} = \\tfrac{1}{5}\\big[-4+1+0-1+4\\big] = 0 \\quad\\Rightarrow\\quad r = 0", block: true },
          { text: "Aucune corrélation linéaire, alors même que $y$ dépend entièrement de $x$ (par $y=x^2$). C'est un piège classique : $r$ ne détecte que les liens linéaires. Un lien fort mais non linéaire (ici, symétrique) peut donner $r=0$. C'est pourquoi Hélios ne se contente jamais d'un seul indicateur." },
        ],
      },
    ],
  },
  {
    id: "autocorrelation",
    number: 3,
    title: "Autocorrélation d'une série temporelle",
    blocks: [
      {
        type: "definition",
        title: "Autocorrélation à lag 1",
        body: [
          { text: "Pour une série temporelle $(x_1,\\dots,x_n)$, l'autocorrélation à lag 1 (notée AC1) est le coefficient de corrélation de Pearson entre la série et elle-même décalée d'un pas :" },
          { tex: "\\text{AC1} = \\text{corrélation entre } (x_1,\\dots,x_{n-1}) \\text{ et } (x_2,\\dots,x_n)", block: true },
        ],
      },
      {
        type: "remarque",
        title: null,
        body: [
          { text: "On démontre dans le polycopié « Des suites au ralentissement critique » (à paraître) que pour un système qui revient vers un équilibre avec un facteur $q = 1+\\lambda\\Delta t$ à chaque étape, AC1 = $q$ exactement en régime stationnaire. Quand $\\lambda \\to 0^-$ (bascule proche), AC1 $\\to 1$." },
        ],
      },
      {
        type: "exemple",
        title: "AC1 sur une petite série",
        body: [
          { text: "Soit la série $x=(1,3,2,5,4,7)$. Calculer AC1." },
          { text: "On forme les deux séries décalées : $A=(1,3,2,5,4)$ et $B=(3,2,5,4,7)$. $\\bar{A}=3$, $\\bar{B}=4{,}2$." },
          { tex: "\\text{Cov} = \\tfrac{1}{5}[2{,}4+0-0{,}8-0{,}4+2{,}8] = 0{,}8, \\qquad \\sigma(A)=\\sqrt{2},\\ \\sigma(B)\\approx 1{,}72", block: true },
          { tex: "\\text{AC1} = \\frac{0{,}8}{\\sqrt{2}\\times 1{,}72} \\approx 0{,}33", block: true },
          { text: "Une autocorrélation modérée : la série garde un peu de mémoire d'un instant sur l'autre, sans être proche d'une bascule (AC1 loin de 1)." },
        ],
      },
    ],
  },
  {
    id: "tester-hypothese",
    number: 4,
    title: "Tester une hypothèse",
    blocks: [
      {
        type: "definition",
        title: "Hypothèse nulle, p-value",
        body: [
          { text: "$H_0$ est l'hypothèse selon laquelle il n'y a « rien de spécial » (le hasard seul explique l'observation). La p-value est la probabilité, si $H_0$ était vraie, d'observer une statistique au moins aussi extrême que celle réellement mesurée. On rejette $H_0$ si la p-value est inférieure à un seuil $\\alpha$ fixé à l'avance (souvent 5%)." },
        ],
      },
      {
        type: "remarque",
        title: null,
        body: [
          { text: "Deux erreurs sont possibles : rejeter $H_0$ à tort (faux positif, erreur de première espèce) ou ne pas la rejeter alors qu'elle est fausse (faux négatif, erreur de seconde espèce). Baisser $\\alpha$ réduit les faux positifs mais augmente les faux négatifs — c'est un compromis, jamais un réglage neutre." },
        ],
      },
      {
        type: "exemple",
        title: "Une pièce est-elle truquée ?",
        body: [
          { text: "On lance une pièce 10 fois et on obtient 8 faces. $H_0$ : la pièce est équilibrée ($p=0{,}5$). Calculer la p-value (test unilatéral, $H_1: p>0{,}5$)." },
          { text: "On veut $P(X\\ge 8)$ où $X\\sim\\mathcal{B}(10\\,;0{,}5)$ :" },
          { tex: "P(X\\ge 8) = \\frac{\\binom{10}{8}+\\binom{10}{9}+\\binom{10}{10}}{2^{10}} = \\frac{45+10+1}{1024} = \\frac{56}{1024} \\approx 0{,}055", block: true },
          { text: "La p-value (≈5,5%) est supérieure au seuil classique de 5% : on ne rejette pas $H_0$. Huit faces sur dix « semble » beaucoup, mais ce n'est statistiquement pas assez extrême pour conclure que la pièce est truquée." },
        ],
      },
      {
        type: "exercice",
        title: "Un second lancer",
        body: [
          { text: "Même situation, mais avec 12 lancers et 10 faces obtenues. Calculer $P(X\\ge 10)$ pour $X\\sim\\mathcal{B}(12\\,;0{,}5)$ et conclure au seuil 5%. On donne $\\binom{12}{10}=66$, $\\binom{12}{11}=12$, $\\binom{12}{12}=1$, $2^{12}=4096$." },
        ],
        correction: [
          { tex: "P(X\\ge 10) = \\frac{66+12+1}{4096} = \\frac{79}{4096} \\approx 0{,}0193", block: true },
          { text: "La p-value (≈1,93%) est inférieure à 5% : on rejette $H_0$, la pièce semble bien truquée. Comparé à l'exercice précédent, une proportion de faces légèrement plus élevée (10/12≈83% contre 8/10=80%) mais sur davantage de lancers suffit à faire basculer la conclusion — la taille de l'échantillon compte autant que la proportion observée." },
        ],
      },
    ],
  },
  {
    id: "tests-permutation",
    number: 5,
    title: "Tests par permutation",
    blocks: [
      {
        type: "remarque",
        title: null,
        body: [{ text: "Dans Hélios, la distribution de $H_0$ n'est presque jamais une loi connue à l'avance (comme la loi binomiale du §4) : elle est obtenue en simulant des données de substitution." }],
      },
      {
        type: "definition",
        title: "Test par permutation",
        body: [
          { text: "Pour tester si une statistique observée $S_{\\text{obs}}$ (calculée sur des données $x,y$) révèle un vrai lien plutôt que du hasard, on mélange aléatoirement l'ordre de $y$ pour casser tout lien réel tout en gardant les mêmes valeurs, on recalcule la statistique sur chacune des $n!$ réorganisations possibles, puis :" },
          { tex: "p\\text{-value} = \\frac{\\#\\{\\text{réorganisations donnant une statistique} \\ge S_{\\text{obs}}\\}}{n!}", block: true },
        ],
      },
      {
        type: "theoreme",
        title: "Validité exacte du test par permutation",
        body: [{ text: "Sous $H_0$ (aucun vrai lien entre $x$ et $y$), la p-value obtenue par permutation suit exactement une loi uniforme sur $\\{1/n!, 2/n!, \\dots, 1\\}$ — ce n'est pas une approximation." }],
        proof: [
          { text: "Sous $H_0$, l'ordre de $y$ associé à $x$ est purement le fruit du hasard : les $n!$ réorganisations possibles de $y$ (y compris l'ordre réellement observé) sont donc toutes équiprobables — elles auraient chacune pu être l'ordre observé. La statistique calculée sur l'ordre réellement observé est donc un tirage uniforme parmi les $n!$ valeurs possibles. Le rang de $S_{\\text{obs}}$ parmi ces $n!$ valeurs suit donc une loi uniforme sur $\\{1,\\dots,n!\\}$, ce qui donne exactement le résultat annoncé pour la p-value." },
        ],
      },
      {
        type: "exemple",
        title: "Un cas extrême, calculable entièrement",
        body: [
          { text: "Soit $x=(1,2,3,4)$ et $y=(1,2,3,4)$ (corrélation observée $r_{\\text{obs}}=1$, lien parfait). Quelle est la p-value par permutation ?" },
          { text: "Il y a $4!=24$ réorganisations possibles de $y$. Le coefficient $r=1$ exactement si et seulement si $y$ est rangé dans le même ordre croissant que $x$ — ce qui n'arrive que pour une seule réorganisation parmi les 24 :" },
          { tex: "p\\text{-value} = \\frac{1}{24} \\approx 0{,}042", block: true },
          { text: "C'est la plus petite p-value atteignable avec seulement 4 points — un résultat important en pratique : avec peu de données, même un lien parfait ne peut pas donner une p-value arbitrairement petite. C'est exactement pourquoi le cahier des charges d'Hélios impose un minimum de 5 épisodes indépendants avant d'accepter un verdict « confirmée »." },
        ],
      },
      {
        type: "exercice",
        title: "Compter les cas favorables",
        body: [
          { text: "Avec $x=(1,2,3)$ (donc $3!=6$ réorganisations de $y$ possibles), combien de réorganisations de $y=(1,2,3)$ donnent une corrélation $r\\ge 0$ ? En déduire la p-value pour un test « $r$ est-il positif ou nul ? » (on admettra que $r\\ge 0$ correspond aux réorganisations où $y$ n'est pas dans l'ordre strictement décroissant)." },
        ],
        correction: [
          { text: "Les $3!=6$ réorganisations de $(1,2,3)$ sont : $(1,2,3), (1,3,2), (2,1,3), (2,3,1), (3,1,2), (3,2,1)$. Seule la dernière, $(3,2,1)$, est dans l'ordre strictement décroissant et donne $r=-1<0$. Les 5 autres donnent $r\\ge 0$." },
          { tex: "p\\text{-value} = \\frac{5}{6} \\approx 0{,}83", block: true },
          { text: "Une p-value très élevée : ce n'est pas surprenant, puisqu'on demande simplement $r\\ge 0$, une condition peu exigeante que la plupart des réorganisations satisfont déjà par hasard." },
        ],
      },
    ],
  },
  {
    id: "kendall",
    number: 6,
    title: "Le tau de Kendall",
    blocks: [
      {
        type: "definition",
        title: "Tau de Kendall",
        body: [
          { text: "Pour une série $(t_i, y_i)$, une paire $(i,j)$ est concordante si $y$ varie dans le même sens que $t$ (les deux augmentent ou les deux diminuent), discordante sinon. Avec $C$ le nombre de paires concordantes et $D$ le nombre de paires discordantes, sur $n$ points ($\\binom{n}{2}$ paires au total) :" },
          { tex: "\\tau = \\frac{C-D}{\\binom{n}{2}}", block: true },
        ],
      },
      {
        type: "remarque",
        title: null,
        body: [{ text: "$\\tau$ est utilisé plutôt que $r$ (Pearson) pour détecter une tendance (monotone, pas forcément linéaire) — exactement ce qu'on veut savoir pour un indicateur précurseur : monte-t-il globalement, sans exiger que la hausse soit parfaitement rectiligne ?" }],
      },
      {
        type: "exemple",
        title: "Calcul complet sur 5 points",
        body: [
          { text: "Pour $t=(1,2,3,4,5)$ et $y=(2,1,4,3,5)$, calculer $\\tau$. Il y a $\\binom{5}{2}=10$ paires." },
          {
            table: {
              headers: ["Paire", "Variation de y", "Type"],
              rows: [
                ["(1,2)", "2 → 1", "discordante"],
                ["(1,3)", "2 → 4", "concordante"],
                ["(1,4)", "2 → 3", "concordante"],
                ["(1,5)", "2 → 5", "concordante"],
                ["(2,3)", "1 → 4", "concordante"],
                ["(2,4)", "1 → 3", "concordante"],
                ["(2,5)", "1 → 5", "concordante"],
                ["(3,4)", "4 → 3", "discordante"],
                ["(3,5)", "4 → 5", "concordante"],
                ["(4,5)", "3 → 5", "concordante"],
              ],
            },
          },
          { text: "On compte $C=8$ concordantes, $D=2$ discordantes (total 10, cohérent)." },
          { tex: "\\tau = \\frac{8-2}{10} = 0{,}6", block: true },
          { text: "Une tendance globale nettement croissante, malgré deux inversions locales." },
        ],
      },
      {
        type: "exercice",
        title: "Une série sans tendance",
        body: [{ text: "Pour $t=(1,2,3,4)$ et $y=(3,1,4,2)$, calculer $\\tau$ et commenter le résultat." }],
        correction: [
          { text: "Les $\\binom{4}{2}=6$ paires : (1,2) discordante, (1,3) concordante, (1,4) discordante, (2,3) concordante, (2,4) concordante, (3,4) discordante. $C=3$, $D=3$." },
          { tex: "\\tau = \\frac{3-3}{6} = 0", block: true },
          { text: "Aucune tendance monotone détectable — les hausses et les baisses se compensent exactement. C'est le comportement attendu sous $H_0$ en moyenne : une série sans vraie tendance a un $\\tau$ proche de 0 (mais rarement exactement 0 avec de vraies données bruitées, d'où la nécessité du test de significativité du §4/§5 appliqué à $\\tau$ plutôt que de juger sur sa seule valeur)." },
        ],
      },
    ],
  },
  {
    id: "moran",
    number: 7,
    title: "Statistique spatiale : l'indice de Moran",
    blocks: [
      {
        type: "definition",
        title: "Indice de Moran",
        body: [
          { text: "Pour des valeurs $(x_i)$ réparties sur $N$ territoires, avec $w_{ij}=1$ si $i,j$ sont voisins (0 sinon) et $S_0=\\sum_{i,j} w_{ij}$ :" },
          { tex: "I = \\frac{N}{S_0} \\cdot \\frac{\\sum_{i,j} w_{ij}(x_i-\\bar{x})(x_j-\\bar{x})}{\\sum_i (x_i-\\bar{x})^2}", block: true },
        ],
      },
      {
        type: "remarque",
        title: null,
        body: [{ text: "C'est la même construction que la covariance/corrélation du §2, mais entre chaque territoire et ses voisins directs plutôt qu'entre deux instants ou deux séries. $I$ proche de 1 : les voisins se ressemblent fortement. $I$ proche de 0 : pas de structure spatiale. $I$ négatif : les voisins ont tendance à être opposés (structure en damier)." }],
      },
      {
        type: "exemple",
        title: "Calcul exact sur une chaîne de 4 territoires",
        body: [
          { text: "Quatre territoires en chaîne (1-2-3-4, chacun voisin du suivant seulement), avec valeurs $x=(1,2,3,4)$. Calculer $I$." },
          { text: "$\\bar{x}=2{,}5$. Écarts : $d=(-1{,}5;-0{,}5;0{,}5;1{,}5)$. Les paires de voisins (comptées deux fois chacune) : $S_0=2\\times 3=6$." },
          { tex: "\\text{Numérateur} = 2[d_1d_2+d_2d_3+d_3d_4] = 2[0{,}75-0{,}25+0{,}75] = 2{,}5, \\qquad \\text{Dénominateur} = 5", block: true },
          { tex: "I = \\frac{4}{6}\\times\\frac{2{,}5}{5} = \\frac{1}{3}", block: true },
          { text: "Une valeur positive modérée : les territoires voisins se ressemblent partiellement, cohérent avec une série qui augmente régulièrement le long de la chaîne." },
        ],
      },
      {
        type: "exercice",
        title: "Le cas extrême en damier",
        body: [{ text: "Quatre territoires en chaîne comme ci-dessus, mais avec $x=(1,-1,1,-1)$ (alternance stricte). Calculer $I$ et interpréter le signe." }],
        correction: [
          { text: "$\\bar{x}=0$. Écarts : $d=(1,-1,1,-1)$ (inchangés). $S_0=6$ comme avant." },
          { tex: "\\text{Numérateur} = 2[(1)(-1)+(-1)(1)+(1)(-1)] = -6, \\qquad \\text{Dénominateur} = 4", block: true },
          { tex: "I = \\frac{4}{6}\\times\\frac{-6}{4} = -1", block: true },
          { text: "$I=-1$ : corrélation spatiale négative parfaite, chaque territoire est systématiquement opposé à son voisin — la signature exacte d'un damier. Le test de significativité de $I$ suit le même principe par permutation que le §5 : mélanger $x$ entre les territoires (en gardant la structure du réseau fixe) et comparer $I_{\\text{obs}}$ à la distribution obtenue." },
        ],
      },
    ],
  },
  {
    id: "fisher",
    number: 8,
    title: "Combiner plusieurs tests : la méthode de Fisher",
    blocks: [
      {
        type: "remarque",
        title: null,
        body: [{ text: "Si on dispose de plusieurs p-values indépendantes $p_1,\\dots,p_k$ testant des aspects différents d'une même question, comment les combiner en une seule conclusion ?" }],
      },
      {
        type: "theoreme",
        title: "Sous H0, −2ln(p) suit une loi χ² à 2 degrés de liberté",
        body: [{ text: "Si $P$ est une p-value sous $H_0$ (donc $P\\sim\\mathcal{U}(0,1)$), alors $T=-2\\ln(P)$ suit une loi exponentielle de moyenne 2, c'est-à-dire une loi du $\\chi^2$ à 2 degrés de liberté." }],
        proof: [
          { text: "On calcule la fonction de répartition de $T$, pour $x\\ge 0$ :" },
          { tex: "P(T\\le x) = P(-2\\ln P \\le x) = P\\big(P \\ge e^{-x/2}\\big)", block: true },
          { text: "Comme $P\\sim\\mathcal{U}(0,1)$, pour $a\\in[0,1]$ : $P(P\\ge a)=1-a$. Avec $a=e^{-x/2}\\in[0,1]$ (car $x\\ge0$) :" },
          { tex: "P(T\\le x) = 1-e^{-x/2}", block: true },
          { text: "C'est exactement la fonction de répartition d'une loi exponentielle de paramètre 1/2 (moyenne 2) — qui est, par définition, la loi $\\chi^2$ à 2 degrés de liberté." },
        ],
      },
      {
        type: "remarque",
        title: null,
        body: [
          { text: "Une propriété admise (additivité du $\\chi^2$) : la somme de $k$ variables $\\chi^2(2)$ indépendantes suit une loi $\\chi^2(2k)$. On combine donc $k$ p-values indépendantes via :" },
          { tex: "T = -2\\sum_{i=1}^k \\ln(p_i) \\sim \\chi^2(2k)", block: true },
          { text: "C'est la méthode de Fisher (1925)." },
        ],
      },
      {
        type: "propriete",
        title: "Fonction de survie du χ²(4), calculable explicitement",
        body: [
          { text: "Pour $X\\sim\\chi^2(4)$ (donc $X=T_1+T_2$, somme de deux $\\chi^2(2)$ indépendantes) :" },
          { tex: "P(X>x) = e^{-x/2}\\Big(1+\\frac{x}{2}\\Big)", block: true },
          { text: "On admet cette formule (elle se retrouve via la loi Gamma, hors programme), mais elle permet de calculer une p-value combinée exactement, sans table." },
        ],
      },
      {
        type: "exemple",
        title: "Deux résultats individuellement non significatifs, ensemble si",
        body: [
          { text: "On a deux p-values indépendantes $p_1=0{,}05$ et $p_2=0{,}10$ (aucune n'est très petite). Calculer la p-value combinée par la méthode de Fisher." },
          { text: "$\\ln(0{,}05)\\approx-2{,}996$, $\\ln(0{,}10)\\approx-2{,}303$." },
          { tex: "T = -2(\\ln(0{,}05)+\\ln(0{,}10)) = 10{,}60", block: true },
          { tex: "p_{\\text{combinée}} = e^{-5{,}30}(1+5{,}30) \\approx 0{,}0315", block: true },
          { text: "La p-value combinée (≈3,15%) est inférieure à 5%, alors qu'aucune des deux p-values individuelles ne l'était : combiner des indices faibles mais convergents peut révéler un signal invisible dans chacun séparément. C'est tout l'intérêt du module H3 d'Hélios — mais voir la mise en garde ci-dessous." },
        ],
      },
      {
        type: "exercice",
        title: "Deux p-values très différentes",
        body: [{ text: "Combiner $p_1=0{,}5$ (aucun signal) et $p_2=0{,}5$ (aucun signal non plus) par la méthode de Fisher. Le résultat est-il surprenant ?" }],
        correction: [
          { tex: "T = -2\\times 2\\times\\ln(0{,}5) = 2{,}773, \\qquad p_{\\text{combinée}} = e^{-1{,}386}(1+1{,}386) \\approx 0{,}597", block: true },
          { text: "Sans surprise, combiner deux résultats totalement neutres donne une p-value combinée toujours proche de 0,5-0,6 (pas de signal artificiel créé à partir de rien). La méthode de Fisher amplifie un vrai signal partagé, elle n'en invente pas." },
        ],
      },
      {
        type: "remarque",
        title: "Mise en garde essentielle",
        body: [
          { text: "Toute cette section suppose les p-values indépendantes. Dans Hélios, l'indicateur temporel et l'indicateur spatial sont calculés sur le même système sous-jacent : ils sont corrélés. Utiliser directement la loi $\\chi^2(2k)$ sous-estime ou surestime alors le vrai taux de faux positifs. La méthode réellement utilisée (méthode empirique de Brown, Poole et al. 2016) remplace le seuil théorique $\\chi^2(2k)$ par un seuil calibré sur des données de substitution qui préservent la corrélation réelle entre les indicateurs — c'est un raffinement du principe démontré ici, pas une méthode différente." },
        ],
      },
    ],
  },
];

export const COURS_BILAN = [
  { notion: "Variance, covariance", role: "Brique de base de tout indicateur statistique" },
  { notion: "Corrélation de Pearson", role: "Mesure de lien linéaire entre deux séries" },
  { notion: "Autocorrélation (AC1)", role: "Indicateur précurseur temporel (module H1)" },
  { notion: "Test d'hypothèse, p-value", role: "Juger si une tendance est significative" },
  { notion: "Test par permutation", role: "Calculer une p-value sans supposer de loi théorique" },
  { notion: "Tau de Kendall", role: "Détecter une tendance monotone (module H1/H3)" },
  { notion: "Indice de Moran", role: "Indicateur précurseur spatial (module H2)" },
  { notion: "Méthode de Fisher / Brown", role: "Combiner plusieurs indicateurs (module H3)" },
];

export const COURS_REFERENCES = [
  "Fisher, R. A. (1925). Statistical Methods for Research Workers.",
  "Brown, M. B. (1975). « A method for combining non-independent, one-sided tests of significance. » Biometrika, 31(4).",
  "Poole, W. et al. (2016). « Combining dependent P-values with an empirical adaptation of Brown's method. » Bioinformatics, 32(17).",
  "Moran, P. A. P. (1950). « Notes on continuous stochastic phenomena. » Biometrika, 37.",
  "Kendall, M. G. (1938). « A new measure of rank correlation. » Biometrika, 30(1-2).",
  "Dakos, V. et al. (2012). « Methods for Detecting Early Warnings of Critical Transitions in Time Series. » PLoS ONE, 7(7).",
];
