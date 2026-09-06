/**
 * Reseaux de Hopfield appliques aux groupes sociaux -- transcription du
 * document fourni par l'utilisateur (cours_hopfield_social.tex/.pdf),
 * page Methode. Analogie pedagogique explicite, pas un modele
 * sociologique valide -- voir la mise en garde en fin de page (rendue a
 * part dans HopfieldSocial.jsx, pas ici, sur le modele des bandeaux de
 * portee de Fusion/Plasma).
 *
 * Meme convention de bloc que coursStatistiques.js :
 * { type, title, body, proof?, correction? }
 */

export const HOPFIELD_SECTIONS = [
  {
    id: "neurone-social",
    number: 1,
    title: "Le neurone social",
    blocks: [
      {
        type: "definition",
        title: "État d'un groupe",
        body: [
          {
            text: "On représente un ensemble de $N$ territoires (ou groupes) par un vecteur d'états $s = (s_1,\\dots,s_N)$, où $s_i \\in \\{-1,+1\\}$ : $s_i=+1$ signifie que le territoire $i$ adhère à une norme sociale donnée (calme, conformité), $s_i=-1$ qu'il s'en écarte (mobilisation, résistance). Une configuration sociale est un choix particulier de ce vecteur.",
          },
        ],
      },
      {
        type: "remarque",
        body: [
          {
            text: "C'est une simplification radicale -- un territoire réel n'est pas binaire. Mais c'est exactement la simplification que fait tout réseau de neurones formel (McCulloch & Pitts, 1943) pour un neurone biologique lui aussi bien plus complexe. Le pouvoir du modèle vient de ce qu'on peut en tirer malgré cette simplicité, pas de son réalisme.",
          },
        ],
      },
    ],
  },
  {
    id: "regle-hebb",
    number: 2,
    title: "La règle de Hebb : mémoriser des configurations passées",
    blocks: [
      {
        type: "definition",
        title: "Apprentissage hebbien",
        body: [
          {
            text: "Pour mémoriser $p$ configurations sociales observées par le passé $\\xi^1,\\dots,\\xi^p$ (chacune un vecteur de $\\{-1,+1\\}^N$), on construit une matrice de liens $W$ par :",
          },
          { tex: "w_{ij} = \\frac{1}{N}\\sum_{\\mu=1}^p \\xi_i^\\mu \\xi_j^\\mu \\quad (i\\neq j), \\qquad w_{ii}=0", block: true },
        ],
      },
      {
        type: "remarque",
        body: [
          {
            text: "C'est la traduction mathématique exacte du principe évoqué dans le roman : si deux territoires $i$ et $j$ ont souvent été dans le même état lors des configurations passées, $\\xi_i^\\mu\\xi_j^\\mu$ vaut souvent $+1$ (même signe) et leur lien $w_{ij}$ se renforce positivement. S'ils ont souvent été opposés, le lien devient négatif. « Les neurones qui s'activent ensemble se connectent ensemble » (Hebb, 1949).",
          },
        ],
      },
      {
        type: "exemple",
        title: "Deux configurations, quatre territoires",
        body: [
          { text: "On observe deux configurations sociales passées sur 4 territoires :" },
          { tex: "\\xi^1 = (+1,+1,+1,+1) \\quad \\text{(société apaisée)}, \\qquad \\xi^2 = (+1,+1,-1,-1) \\quad \\text{(fracture nord-sud)}", block: true },
          { text: "Calcul de la matrice des liens $W$, pour chaque paire $(i,j)$ : on somme $\\xi_i^\\mu\\xi_j^\\mu$ sur les deux configurations, puis on divise par $N=4$." },
          {
            table: {
              headers: ["Paire", "Somme", "w_ij"],
              rows: [
                ["(1,2)", "(+1)(+1)+(+1)(+1) = 2", "0,5"],
                ["(3,4)", "(+1)(+1)+(-1)(-1) = 2", "0,5"],
                ["(1,3)", "(+1)(+1)+(+1)(-1) = 0", "0"],
                ["(1,4), (2,3), (2,4)", "0", "0"],
              ],
            },
          },
          {
            text: "Les territoires 1-2 se renforcent mutuellement, les territoires 3-4 aussi, mais les deux paires restent indépendantes -- exactement la structure des deux configurations mémorisées.",
          },
        ],
      },
      {
        type: "exercice",
        title: "Trois configurations",
        body: [
          {
            text: "Ajouter une troisième configuration observée, $\\xi^3=(+1,-1,+1,-1)$, aux deux précédentes. Recalculer $w_{12}$ et $w_{13}$.",
          },
        ],
        correction: [
          {
            tex: "w_{12} : (+1)(+1)+(+1)(+1)+(+1)(-1) = 1+1-1=1 \\Rightarrow w_{12}=1/4=0{,}25",
            block: true,
          },
          { text: "(le lien s'affaiblit : les territoires 1 et 2 ne sont plus toujours dans le même état)." },
          {
            tex: "w_{13} : (+1)(+1)+(+1)(-1)+(+1)(+1)=1-1+1=1 \\Rightarrow w_{13}=0{,}25",
            block: true,
          },
          { text: "(un lien apparaît là où il n'y en avait pas : la nouvelle configuration a créé une corrélation qui n'existait pas avant)." },
        ],
      },
    ],
  },
  {
    id: "dynamique-energie",
    number: 3,
    title: "La dynamique du groupe et la fonction d'énergie",
    blocks: [
      {
        type: "definition",
        title: "Règle de mise à jour",
        body: [
          {
            text: "Un territoire ajuste son état selon l'influence pondérée de tous les autres (son champ local) :",
          },
          {
            tex: "h_i = \\sum_{j\\neq i} w_{ij}s_j, \\qquad s_i \\leftarrow \\begin{cases}+1 & \\text{si } h_i \\ge 0\\\\ -1 & \\text{sinon}\\end{cases}",
            block: true,
          },
          { text: "La mise à jour est asynchrone : on met à jour un territoire à la fois, en recalculant avant de passer au suivant." },
        ],
      },
      {
        type: "definition",
        title: "Fonction d'énergie",
        body: [{ tex: "E(s) = -\\frac12\\sum_{i\\neq j} w_{ij}\\,s_i s_j", block: true }],
      },
      {
        type: "theoreme",
        title: "Convergence vers un état stable",
        body: [
          {
            text: "Avec des liens symétriques ($w_{ij}=w_{ji}$) et une mise à jour asynchrone, $E$ ne peut jamais augmenter : le groupe converge toujours, en un nombre fini d'étapes, vers une configuration stable (un attracteur).",
          },
        ],
        proof: [
          {
            text: "Isolons dans $E$ les termes impliquant le territoire $i$ qu'on s'apprête à mettre à jour. Par symétrie des liens, chaque paire $(i,j)$ apparaît deux fois dans la somme double, donc :",
          },
          {
            tex: "E(s) = \\underbrace{-\\frac12\\sum_{j\\neq i,\\,k\\neq i} w_{jk}s_js_k}_{=:C,\\ \\text{ne dépend pas de } s_i} - \\ s_i\\sum_{j\\neq i} w_{ij}s_j = C - s_i h_i",
            block: true,
          },
          {
            text: "Seul le second terme dépend de $s_i$. Si la mise à jour change $s_i$ (de $s_i^{\\text{avant}}$ à $s_i^{\\text{après}}$), la variation d'énergie vaut :",
          },
          { tex: "\\Delta E = -\\big(s_i^{\\text{après}}-s_i^{\\text{avant}}\\big)\\,h_i", block: true },
          {
            text: "Or la règle de mise à jour fixe $s_i^{\\text{après}} = \\text{signe}(h_i)$. Si $s_i$ change réellement, c'est que $s_i^{\\text{avant}} = -\\text{signe}(h_i)$, donc $s_i^{\\text{après}}-s_i^{\\text{avant}} = 2\\,\\text{signe}(h_i)$, d'où :",
          },
          { tex: "\\Delta E = -2\\,\\text{signe}(h_i)\\cdot h_i = -2|h_i| \\le 0", block: true },
          {
            text: "Chaque changement fait donc strictement diminuer $E$ (ou la laisse inchangée si $h_i=0$). Comme il n'existe que $2^N$ configurations possibles, $E$ est bornée : la suite des valeurs de $E$ ne peut décroître indéfiniment, le processus s'arrête donc nécessairement sur une configuration où plus aucune mise à jour ne change quoi que ce soit -- un état stable.",
          },
        ],
      },
      {
        type: "remarque",
        title: "Point crucial pour la suite",
        body: [
          {
            text: "Ce théorème dit que le groupe converge toujours vers un état stable -- mais ne dit rien sur lequel. L'ordre dans lequel les territoires se mettent à jour peut déterminer vers quel attracteur le système converge, comme le montre l'exemple ci-dessous.",
          },
        ],
      },
      {
        type: "exemple",
        title: "Reconnaître une configuration à partir d'un signal partiel",
        body: [
          {
            text: "Reprenons le réseau à 4 territoires du §2 (motifs $\\xi^1,\\xi^2$ seuls, $w_{12}=w_{34}=0{,}5$, autres liens nuls). Un rapport erroné indique l'état $s=(-1,+1,-1,-1)$ -- le territoire 1 est mal classé (il devrait valoir $+1$ pour correspondre à $\\xi^2$). Mise à jour dans l'ordre $1,2,3,4$ :",
          },
          {
            text: "Territoire 1 : $h_1 = w_{12}s_2 = 0{,}5\\times(+1)=0{,}5\\ge0 \\Rightarrow s_1 \\leftarrow +1$. Le vecteur devient $(+1,+1,-1,-1)=\\xi^2$ exactement.",
          },
          {
            text: "Territoires 2, 3, 4 : en recalculant, $h_2=0{,}5>0$ ($s_2$ inchangé), $h_3=w_{34}s_4=-0{,}5<0$ ($s_3$ inchangé), $h_4=-0{,}5<0$ ($s_4$ inchangé). Plus aucun changement : le réseau a retrouvé exactement la configuration « fracture nord-sud » à partir d'un signal partiellement erroné. L'énergie est passée de $E=0$ (état corrompu) à $E=-1$ (état retrouvé) -- conforme au théorème. Vérifié numériquement (`backend/scripts/hopfield_social.py`) : état reconnu $(+1,+1,-1,-1)$, énergie $-1{,}00$.",
          },
        ],
      },
      {
        type: "remarque",
        title: "Un attracteur « parasite », à connaître",
        body: [
          {
            text: "Si on avait mis à jour dans un ordre différent (le territoire 2 avant le territoire 1), le calcul aurait pu converger vers $(-1,-1,-1,-1)$ -- l'exact négatif de $\\xi^1$. C'est un résultat général et documenté des réseaux de Hopfield à liens symétriques : le négatif de tout motif mémorisé est, lui aussi, toujours un état stable. Ce n'est pas un défaut d'implémentation, c'est une propriété du modèle, à connaître avant de l'utiliser pour interpréter un vrai résultat. Vérifié numériquement avec un ordre de mise à jour aléatoire : état reconnu $(-1,-1,-1,-1)$, exactement le négatif de « société apaisée ».",
          },
        ],
      },
      {
        type: "exercice",
        title: "Un autre signal partiel",
        body: [
          {
            text: "Même réseau. Un rapport indique $s=(+1,+1,+1,-1)$. Mettre à jour le territoire 3, puis le territoire 4 (dans cet ordre). Vers quelle configuration converge-t-on ?",
          },
        ],
        correction: [
          {
            text: "Territoire 3 : $h_3 = w_{34}s_4 = 0{,}5\\times(-1)=-0{,}5<0 \\Rightarrow s_3\\leftarrow -1$. Le vecteur devient $(+1,+1,-1,-1)$.",
          },
          {
            text: "Territoire 4 : $h_4=w_{34}s_3=-0{,}5<0$, $s_4$ déjà $-1$, inchangé. On converge vers $\\xi^2$ (fracture nord-sud) -- ce signal partiel penchait déjà du bon côté, quel que soit l'ordre choisi ici.",
          },
        ],
      },
    ],
  },
  {
    id: "bascule",
    number: 4,
    title: "Bascule : quand un état stable cesse de l'être",
    blocks: [
      {
        type: "remarque",
        title: "Lien avec H1-H5",
        body: [
          {
            text: "Dans le roman, Hélios ne se contente pas de reconnaître un état : il détecte le moment où un état qui semblait stable ne l'est plus. Si de nouveaux événements viennent contredire un motif appris, les liens $w_{ij}$ évoluent (nouvelle passe d'apprentissage hebbien). Un territoire $i$ dont le champ local $h_i$ pour un motif $\\xi^\\mu$ donné se rapproche de $0$ voit son état devenir de moins en moins fermement maintenu par ses voisins -- une petite perturbation suffit alors à le faire basculer. C'est très exactement le même phénomène que le ralentissement critique du cours de statistiques (la valeur propre $\\lambda\\to0^-$) -- ici transposé à un système discret. Ce n'est pas un nouveau théorème, c'est la même logique, dans un langage différent.",
          },
        ],
      },
      {
        type: "exemple",
        title: "Un lien qui s'affaiblit jusqu'à la bascule",
        body: [
          {
            text: "Dans le réseau à 4 territoires, supposons que de nouveaux événements fassent passer $w_{34}$ progressivement de $0{,}5$ à $0{,}05$ (les territoires 3 et 4 se découplent). Pour l'état $s_3=-1$ (avec $s_4=-1$ fixé) :",
          },
          {
            text: "Avec $w_{34}=0{,}5$ : $h_3 = 0{,}5\\times(-1)=-0{,}5$ -- état fermement maintenu ($|h_3|$ grand).",
          },
          {
            text: "Avec $w_{34}=0{,}05$ : $h_3=0{,}05\\times(-1)=-0{,}05$ -- état à peine maintenu : une perturbation extérieure de $0{,}06$ suffit à faire basculer $s_3$ vers $+1$. La taille du champ local joue ici exactement le rôle que jouait $|\\lambda|$ dans le modèle continu -- sa diminution est le signal précurseur.",
          },
        ],
      },
    ],
  },
  {
    id: "capacite-memoire",
    number: 5,
    title: "Combien de configurations un groupe peut-il retenir ?",
    blocks: [
      {
        type: "remarque",
        body: [
          {
            text: "On admet ce résultat (sa démonstration complète relève de la mécanique statistique, hors de portée ici), mais on peut en comprendre l'origine.",
          },
        ],
      },
      {
        type: "theoreme",
        title: "Seuils de capacité",
        body: [
          {
            text: "Reprenons le champ local pour un territoire $i$, quand l'état courant est exactement un motif mémorisé $\\xi^\\mu$ :",
          },
          {
            tex: "h_i = \\sum_{j\\neq i}w_{ij}\\xi_j^\\mu = \\underbrace{\\xi_i^\\mu\\cdot\\frac{N-1}{N}}_{\\text{signal}} + \\underbrace{\\frac1N\\sum_{\\nu\\neq\\mu}\\xi_i^\\nu\\sum_{j\\neq i}\\xi_j^\\nu\\xi_j^\\mu}_{\\text{bruit de diaphonie}}",
            block: true,
          },
          {
            text: "Le premier terme reconstruit correctement $\\xi_i^\\mu$. Le second -- la diaphonie entre motifs -- est une somme d'environ $(p-1)(N-1)$ termes $\\pm1$ globalement aléatoires si les motifs ne se ressemblent pas : son ordre de grandeur (écart-type) croît comme $\\sqrt{p/N}$. Le rappel reste fiable tant que ce bruit reste petit devant le signal (qui vaut $\\approx1$), soit $p \\ll N$. Une analyse plus poussée (méthode des répliques, mécanique statistique) donne les seuils précis :",
          },
          {
            table: {
              headers: ["Estimation", "Formule", "Nature"],
              rows: [
                ["Hopfield (1982)", "p_max ≈ N / (4 ln N)", "première estimation, borne prudente"],
                ["Amit, Gutfreund & Sompolinsky (1985)", "p_max ≈ 0,138 N", "résultat affiné par la méthode des répliques"],
              ],
            },
          },
        ],
      },
      {
        type: "exemple",
        title: "Vérification numérique",
        body: [
          {
            text: "Pour $N=100$ territoires, la démonstration numérique jointe (`backend/scripts/hopfield_social.py`, graine fixée à 42 pour la reproductibilité) mesure le taux de rappel correct pour $p$ allant de 1 à 25 motifs aléatoires, sur 30 tirages à chaque fois, avec 15% de bits corrompus au départ.",
          },
          {
            text: "Résultat réellement obtenu en relançant le script : le taux reste proche de 100% jusqu'à $p\\approx10$ (avec de légères baisses ponctuelles à $p=5$ et $p=9$, 97%), puis décroît de façon assez régulière -- 80% à $p=11$, 67% à $p=14$, franchissant la moitié (50%) à $p=16$, pour tomber autour de 10-17% au-delà de $p=19$. La chute se situe donc un peu au-delà du seuil AGS ($\\approx13{,}8$) plutôt que pile dessus, mais dans le bon ordre de grandeur, et très largement au-delà du seuil prudent de Hopfield ($\\approx5{,}4$) -- cohérent avec le fait que ce dernier est documenté comme une borne conservatrice, pas une estimation précise.",
          },
        ],
      },
      {
        type: "exercice",
        title: "Ordre de grandeur pour un plus grand groupe",
        body: [{ text: "Pour $N=1000$ territoires, calculer les deux estimations de capacité." }],
        correction: [
          {
            tex: "p_{\\max}\\approx \\dfrac{1000}{4\\ln 1000} = \\dfrac{1000}{4\\times6{,}908}\\approx36 \\ \\text{(Hopfield 1982)}, \\qquad p_{\\max}\\approx0{,}138\\times1000=138 \\ \\text{(AGS 1985)}",
            block: true,
          },
          {
            text: "Même en multipliant la taille du groupe par 10, on ne peut retenir qu'environ 4 fois plus de configurations distinctes avec la borne prudente -- la capacité croît moins vite que la taille du groupe ne le suggérerait naïvement.",
          },
        ],
      },
    ],
  },
];

export const HOPFIELD_REFERENCES = [
  "Hebb, D. O. (1949). The Organization of Behavior.",
  "Hopfield, J. J. (1982). « Neural networks and physical systems with emergent collective computational abilities. » PNAS, 79(8).",
  "Amit, D. J., Gutfreund, H., & Sompolinsky, H. (1985). « Storing infinite numbers of patterns in a spin-glass model of neural networks. » Physical Review Letters, 55(14).",
  "McCulloch, W. S., & Pitts, W. (1943). « A logical calculus of the ideas immanent in nervous activity. » Bulletin of Mathematical Biophysics, 5.",
];
