# Cahier des charges — Hélios
## Plateforme de détection et de test de signaux précurseurs de bascules collectives

---

## 1. Positionnement

**Ce que c'est** : un outil de recherche et de vulgarisation qui calcule,
sur des séries temporelles et des réseaux territoriaux réels, les
indicateurs statistiques de "ralentissement critique" qui précèdent
généralement une rupture ou un changement d'état d'un système complexe —
méthode issue de la littérature sur les transitions critiques (écologie,
épidémiologie, sociophysique) — puis teste trois hypothèses de recherche
originales sur des données réelles et en tire une conclusion honnête.

**Ce que ce n'est pas** : un outil d'identification, de profilage ou de
surveillance de personnes. Le produit travaille exclusivement sur des
**données agrégées** (comptages, indices, séries officielles), jamais sur
des données nominatives individuelles. Cette limite est structurelle
(§7), pas seulement déclarative.

**Origine et ambition** : le projet est inspiré d'un roman dans lequel
deux chercheurs, Moussa et Louise, construisent un outil pour détecter
des signes de bascule sociale avant qu'ils ne deviennent visibles.
L'ambition ici est de transformer cette intuition fictionnelle en une
véritable démarche scientifique testable : contribuer, même modestement,
à la recherche sur l'incertitude dans les projets de risque, en
croisant les statistiques officielles (lentes, fiables) et les signaux
sociaux (rapides, bruités mais précoces).

**Objectif pour l'auteur du projet** : produire un logiciel fonctionnel,
pédagogique et défendable scientifiquement, utilisable comme démonstration
de compétence (freelance/portfolio) et, si les résultats s'y prêtent,
comme point de départ d'une communication à la communauté de recherche.

---

## 1bis. Positionnement scientifique honnête — ce que le projet apporte réellement

Chaque piste scientifique explorée pendant la conception de ce projet
(signaux précurseurs, criticité auto-organisée, contrôle de
synchronisation, apprentissage sur graphe, thermodynamique, théorie de
l'information) s'est révélée, en vérifiant la littérature, appartenir à
un champ de recherche mature et déjà actif — parfois depuis plusieurs
décennies. **Ce n'est pas un accident** : le roman dont s'inspire le
projet mobilise lui-même de vraies théories établies, donc toute piste
qu'il évoque renvoie nécessairement à un champ existant. Le projet doit
être positionné en conséquence, durablement, pas seulement dans une
conversation de conception.

**Ce que ce projet apporte réellement à la recherche, dans l'ordre
d'importance** :

1. **De la réplication.** Les théories mobilisées (signaux précurseurs,
   criticité, synchronisation) ont été testées sur une poignée de
   domaines (écologie, épidémiologie, finance, neurosciences). Personne
   n'avait testé leur généralisation à des données socio-territoriales
   françaises combinant Insee et réseaux sociaux ouverts. La
   réplication sur un nouveau domaine est une contribution scientifique
   réelle, quoique modeste — c'est l'écrasante majorité du travail
   scientifique publié chaque année, loin du mythe de la découverte
   spectaculaire.
2. **Des résultats négatifs documentés.** La littérature publiée est
   structurellement biaisée vers les résultats positifs (biais de
   publication). Un résultat négatif obtenu avec un protocole rigoureux
   et publié tel quel (voir Bilan) corrige, à très petite échelle, ce
   biais.
3. **Un outil réutilisable et reproductible.** Le pipeline (connecteurs
   de données, tests statistiques calibrés, garde-fous, scripts
   versionnés) reste utilisable par quiconque voudrait tester un
   nouvel épisode, sans dépendre de qui a testé quoi en premier.
4. **De la médiation scientifique.** Le Journal de recherche, le cours
   de statistiques et la démo interactive font circuler des méthodes
   réelles (signaux précurseurs, tests par permutation, indice de
   Moran) vers un public qui n'y aurait pas accès autrement.

**Ce que ce projet n'apporte pas, à énoncer explicitement partout où
le positionnement scientifique est présenté** : une nouvelle théorie,
une nouvelle méthode mathématique, ou une découverte au sens où on
l'entend pour un prix scientifique majeur. Le mot « découverte »
ne doit jamais être utilisé pour décrire un résultat du projet, ni sur
le site, ni dans les rapports générés, ni dans le Journal de recherche.

**Garde-fou de positionnement (contraignant, pas seulement rédactionnel)** :
toute page de résultat (§4, gabarit du cahier des charges de
restructuration) et toute génération de rapport doit situer son
contenu dans l'une des quatre catégories ci-dessus — jamais formulé
comme une contribution théorique nouvelle. La page d'accueil (§2) et
la page Bilan doivent chacune contenir, en clair, une reformulation de
ce positionnement en une ou deux phrases.

---

## 2. Page d'accueil

**Objectif** : donner envie de comprendre, sans exiger de bagage
scientifique, et sans déflorer l'intrigue du roman qui a inspiré le
projet.

**Contenu** :
1. Une accroche courte : l'idée qu'un système social, comme un
   écosystème, envoie des signes avant de basculer d'un état à un autre —
   et qu'on peut apprendre à les lire.
2. Une mention discrète de l'origine du projet (Moussa et Louise, sans
   résumer l'intrigue ni révéler les enjeux narratifs).
3. Un bouton "Voir un exemple" renvoyant vers une démo interactive
   (réseau simulé + indicateurs qui montent avant une bascule visible).
4. Une explication en 3 étapes, en langage courant : *1. On rassemble des
   données publiques. 2. On cherche des signes de fébrilité avant une
   rupture. 3. On vérifie si ces signes se confirment vraiment.*

**Ton** : pédagogique, jamais anxiogène. Le texte ne doit jamais suggérer
que l'outil "surveille" ou "prédit" au sens fort — il teste une méthode.

---

## 3. Principe transversal de vulgarisation

Chaque résultat affiché existe à deux niveaux, activables par un simple
bouton, jamais dans deux pages séparées :

- **Mode simplifié** (par défaut) : une phrase en langage courant (ex.
  "le signal de tension sociale a augmenté plus vite que d'habitude sur
  cette période"), une jauge visuelle, pas de formule.
- **Mode expert** : pas seulement la formule finale — la **démonstration
  complète**, étape par étape, de pourquoi elle fonctionne. Une formule
  affichée sans dérivation n'est pas considérée comme du mode expert
  conforme. Le contenu exact de chaque démonstration est fourni au §5
  (5.1bis, 5.6, 5.9) et doit être repris tel quel dans l'interface,
  avec rendu LaTeX (KaTeX ou MathJax), pas en texte brut.

Aucun résultat n'est affiché uniquement sous forme technique, et aucune
démonstration experte ne s'arrête à la formule sans expliquer d'où elle
vient : ce sont deux règles de conception, pas des fonctionnalités
optionnelles.

---

## 4. Utilisateurs et cas d'usage

| Utilisateur | Besoin | Données |
|---|---|---|
| Chercheur | Tester la méthode sur un corpus public | Séries dérivées de données publiques ouvertes |
| Journaliste data | Repérer un point de bascule dans une tendance | Import CSV depuis ses propres sources |
| Grand public / lecteur du roman | Comprendre le concept en le manipulant | Démo pédagogique, aucune donnée réelle requise |
| Consultant/PME (usage secondaire) | Suivre la résilience d'un indicateur métier | Import CSV/API propriétaire du client |

Dans tous les cas, l'unité d'analyse est une série ou un territoire
agrégé, jamais un individu identifié.

---

## 5. Fondements théoriques et hypothèses de recherche

### 5.1 Signaux précurseurs temporels

Sur une série $x_t$, dans une fenêtre glissante de taille $w$ :
- Variance glissante : $\text{Var}_w(x_t)$
- Autocorrélation à lag-1 : $\text{AC1}_w(x_t) = \text{Corr}(x_t, x_{t-1})$

Base théorique : près d'une bifurcation, le système linéarisé récupère de
plus en plus lentement après une perturbation, ce qui se traduit
mécaniquement par une hausse de la variance et de l'autocorrélation.

### 5.1bis Démonstration (contenu obligatoire du mode expert)

Soit un système dynamique $dx = f(x,\mu)\,dt + \sigma\,dW$, au voisinage
d'un équilibre stable $x^*$. En linéarisant autour de $x^*$ :
$$dx \approx \lambda(\mu)(x-x^*)\,dt + \sigma\,dW, \qquad \lambda(\mu) = \frac{\partial f}{\partial x}\Big|_{x^*} < 0$$
C'est un processus d'Ornstein-Uhlenbeck. Sa variance stationnaire et son
autocorrélation à lag-1 (temps discret, pas $\Delta t$) ont une forme
connue :
$$\text{Var}(x) = \frac{\sigma^2}{2|\lambda|}, \qquad \text{AC1} = e^{\lambda \Delta t} \approx 1 + \lambda \Delta t$$
Près d'une bifurcation (fold/transcritique), $\lambda \to 0^-$ : le
dénominateur de la variance s'effondre (variance $\to \infty$) et
$\text{AC1} \to 1$. C'est ce mécanisme — pas une corrélation empirique
observée a posteriori — qui justifie que ces deux indicateurs montent
avant une rupture. Référence : Ives (1995), Scheffer et al. (2009).

### 5.2 Signaux précurseurs spatiaux — indice de Moran

$$I_t = \frac{N}{\sum_{i,j} w_{ij}} \cdot \frac{\sum_{i,j} w_{ij}(x_i(t)-\bar{x}(t))(x_j(t)-\bar{x}(t))}{\sum_i (x_i(t)-\bar{x}(t))^2}$$

où $w_{ij}=1$ si les territoires $i,j$ sont voisins. Une hausse de $I_t$
dans le temps indique une synchronisation croissante entre territoires
voisins, signal précurseur documenté en écologie spatiale (Kéfi et al.,
Dakos et al.).

### 5.3 Fusion multi-fréquence (nowcasting)

Modèle à espace d'états :
- État latent : $z_t = A z_{t-1} + w_t$
- Observation officielle (mensuelle/trimestrielle, INSEE) : $y_t^{INSEE} = H_1 z_t + \varepsilon_1$, observée par intermittence
- Observation sociale (quotidienne) : $y_t^{social} = H_2 z_t + \varepsilon_2$, observée en continu

Un filtre de Kalman (ou équivalent bayésien) réestime en continu l'état
de risque latent, recalé à chaque publication officielle.

### 5.4 Test de significativité

Toute tendance détectée est testée par le tau de Kendall entre
l'indicateur et le temps, comparé à une distribution nulle obtenue par
données de substitution (surrogate data), suivant la méthode standard de
la littérature EWS (Dakos et al., 2012). Sans ce test, une hausse de
variance observée pourrait être due au hasard.

### 5.5 Les hypothèses à tester

**H1 — Décalage temporel** : les indicateurs précurseurs calculés sur les
signaux sociaux se déclenchent statistiquement avant ceux calculés sur
les statistiques officielles, pour un même événement de rupture
territoriale réel.

**H2 — Robustesse sur réseau réel** (créneau identifié dans la
littérature : la quasi-totalité des études EWS spatiaux sont validées sur
des grilles régulières idéalisées, pas sur des réseaux réels irréguliers
comme les communes françaises) : l'indice de Moran se comporte
différemment sur le réseau réel (tailles et topologie hétérogènes) que
sur une grille régulière de contrôle de même taille.

**H3 — Indicateur joint** : combiner une tendance temporelle
significative ET une tendance spatiale significative réduit les faux
positifs par rapport à chaque indicateur pris isolément.

**H4 — Contrôle actif** (simulation pédagogique, pas un test empirique
— voir §5.8) : un couplage adaptatif peut maintenir un réseau
d'oscillateurs sous le seuil de synchronisation sans supprimer les
fluctuations locales.

**H5 — Criticité auto-organisée** (voir §5.9) : les tailles
d'événements du système observé suivent une loi de puissance,
signature d'un système qui se maintient spontanément à la limite de la
stabilité plutôt que d'approcher une bascule unique.

### 5.6 Modèle formel pour H3 — statistique jointe

**Cadrage honnête** : cette construction n'est pas une originalité du
projet — c'est une méthode déjà publiée et implémentée, la **méthode
empirique de Brown** (Empirical Brown's Method, Poole et al., 2016), qui
combine des p-values corrélées via une distribution nulle empirique.
Ce que fait ce paragraphe est de documenter comment l'appliquer à notre
cas (indicateur temporel + indicateur spatial), pas de la reconstruire
comme si elle était nouvelle. Utiliser directement l'implémentation
existante (packages disponibles) est préférable à la ré-implémenter.

**Construction** :

1. Pour chaque indicateur précurseur $i$ (ex. tendance temporelle AC1,
   tendance spatiale de l'indice de Moran), calculer sa p-value $p_i$ par
   rapport à une distribution nulle obtenue par données de substitution
   (méthode déjà utilisée au §5.4, appliquée séparément à chaque
   indicateur).
2. Combiner les p-values selon la statistique de Fisher :
   $$T = -2\sum_{i=1}^{k} \ln(p_i)$$
3. **Ne pas** utiliser la loi du χ² théorique à $2k$ degrés de liberté
   (elle suppose l'indépendance des indicateurs, hypothèse fausse ici :
   variance, autocorrélation et indice de Moran sont calculés sur le même
   système sous-jacent).
4. Calibrer $T$ empiriquement : générer $M$ jeux de données de
   substitution qui préservent la corrélation croisée entre les séries
   (surrogates à phase aléatoire appliqués simultanément à l'ensemble des
   séries couplées, pas indicateur par indicateur), recalculer
   $T_{surrogate}$ sur chacun, puis :
   $$p_{joint} = \frac{\#\{T_{surrogate} \geq T_{observé}\}}{M}$$
5. Ce $p_{joint}$ est le verdict testé pour H3 (§7), avec la même règle
   de prudence : jamais de "confirmée" sur un seul épisode.

**Démonstration (contenu obligatoire du mode expert)** : sous H0, si les
$p_i$ sont indépendantes et uniformes sur $[0,1]$, alors $-2\ln(p_i)$
suit une loi $\chi^2$ à 2 degrés de liberté (transformation standard
d'une uniforme). La somme de $k$ variables $\chi^2(2)$ indépendantes suit
une $\chi^2(2k)$ — c'est la justification de la loi de Fisher (1925).
Mais quand les $p_i$ sont corrélées, $\text{Var}(T) \neq \text{Var}$
théorique de la $\chi^2(2k)$ : la covariance entre les termes
$-2\ln(p_i)$ n'est plus nulle, donc utiliser le seuil théorique sous- ou
sur-estime le vrai taux de faux positifs selon le signe de cette
covariance. C'est exactement pourquoi l'étape 4 remplace le seuil
théorique par un seuil empirique — la démonstration doit montrer ce
raisonnement, pas seulement l'affirmer.

### 5.6bis Résultat préliminaire — l'indicateur temporel précède-t-il toujours le spatial ?

**Postulat testé** : pour un réseau d'oscillateurs stochastiques couplés
(processus d'Ornstein-Uhlenbeck couplés par le Laplacien du graphe,
$dy = (\Lambda - \beta L)y\,dt + \sigma\,dW$) approchant une bifurcation,
la relation entre l'indicateur temporel (AC1 agrégée) et l'indicateur
spatial (indice de Moran) peut être établie analytiquement/numériquement
via l'équation de Lyapunov stationnaire $A\Sigma+\Sigma A^T+\sigma^2I=0$,
avec $A=\Lambda-\beta L$.

**Méthode** : résolution numérique exacte de cette équation (pas
d'approximation à la main) sur un réseau en anneau ($N=40$), en faisant
varier la taille $|S|$ d'un sous-ensemble de nœuds dont la stabilité
locale $\lambda_S$ se rapproche de 0, pour $|S|$ allant d'un seul nœud
(bifurcation très localisée) à $N$ (bifurcation homogène).

**Erreur initiale corrigée** : un raisonnement qualitatif préalable
avait conclu à tort que (a) le cas homogène ne produirait aucune
tendance sur l'indice de Moran, et (b) qu'une bifurcation localisée
ferait apparaître le signal spatial avant le signal temporel. Le calcul
exact contredit les deux points : c'était une confusion entre "le terme
correctif tend vers zéro" et "pas de tendance", alors que ce terme qui
s'annule est justement ce qui pousse l'indice de Moran vers son maximum.
Ceci illustre pourquoi ce protocole exige une validation numérique et
non une simple dérivation verbale.

**Résultat numérique obtenu** (réseau en anneau, $\beta=0{,}6$,
$\Delta t=0{,}5$, sigma=1) : dans toutes les configurations testées
(bifurcation localisée sur 1 nœud jusqu'à homogène sur les 40),
l'indicateur temporel franchit son seuil de déclenchement avant
l'indicateur spatial. Même dans le cas homogène, l'indice de Moran
montre une tendance forte (+170% sur la plage testée, contre +62% pour
l'indicateur temporel) mais plus tardive.

**Implication pour H3** : la valeur ajoutée d'un indicateur joint
(§5.6) dépend de l'existence de régimes où les deux signaux sont
réellement complémentaires plutôt qu'un simple décalage temporel l'un
de l'autre. Ce point doit être vérifié — pas supposé — avant d'attendre
un gain de H3 sur données réelles.

**Statut** : résultat préliminaire, valable pour la topologie et les
paramètres testés uniquement. Une analyse de sensibilité sur $\beta$
(force du couplage) et la topologie du réseau (anneau vs réseau réel
irrégulier) est nécessaire avant toute généralisation — voir §5.6ter.

### 5.6ter Balayage de sensibilité — robustesse du résultat

**Ce qui a été balayé** : le couplage $\beta \in \{0{,}1;\,0{,}3;\,0{,}6;\,1;\,2;\,4\}$,
la topologie (anneau régulier vs 5 réseaux irréguliers aléatoires
distincts, connexité garantie), et la taille du patch instable
($2{,}5\%$ à $100\%$ du réseau).

**Résultat** : la précédence de l'indicateur temporel sur l'indicateur
spatial (§5.6bis) est robuste sur l'ensemble de ce balayage — 16
configurations sur 17 confirment "AC1 précède", la seule exception
(patch de $2{,}5\%$, un seul nœud) donnant un résultat simultané,
probablement une limite de résolution numérique plutôt qu'un vrai
contre-exemple.

**Portée réelle de ce résultat — à ne pas dépasser** : il est établi
uniquement pour la classe de modèles testée : un réseau d'Ornstein-
Uhlenbeck **linéaire**, à couplage **diffusif** (Laplacien), avec un
seul pas d'échantillonnage temporel testé ($\Delta t=0{,}5$). Il ne dit
rien sur : les dynamiques non linéaires proches d'un vrai point de
bifurcation (saddle-node), les couplages non diffusifs, ou une
variation de $\Delta t$. Il ne doit donc pas être présenté comme une loi
générale, mais comme une observation robuste dans un modèle simplifié,
qui doit tempérer les attentes sur H3 : construire l'indicateur joint
sans vérifier au préalable, sur les données réelles visées, que les deux
signaux ne sont pas simplement l'un une version retardée de l'autre.

**Reproductibilité** : script de calcul (équation de Lyapunov stationnaire,
`scipy.linalg.solve_continuous_lyapunov`) disponible séparément ; à
intégrer au dépôt du projet comme test de non-régression pour ce
résultat, pas comme fonctionnalité du produit livré.

### 5.6quater Validation sur un vrai basculement (Monte-Carlo, dynamique non linéaire)

**Limite du résultat précédent** : les §5.6bis/ter reposaient sur un
système linéaire qui *s'approche* de l'instabilité sans jamais
réellement basculer (l'équation de Lyapunov n'est définie que pour un
système stable). Il fallait vérifier si la précédence tenait sur un vrai
basculement.

**Modèle** : bifurcation nœud-col (saddle-node) par nœud, couplée
diffusivement sur le réseau, avec bruit :
$$dx_i = \big(\mu(t) + x_i^2 - \beta(Lx)_i\big)dt + \sigma\,dW_i$$
$\mu(t)$ croît lentement de $-2$ vers $0$ puis au-delà : les deux points
d'équilibre (stable/instable) fusionnent en $\mu=0$ et disparaissent,
provoquant l'échappement (le vrai basculement). Réseau en anneau,
$N=40$, $\beta=0{,}6$, 40 réalisations Monte-Carlo indépendantes.

**Résultat** : les 40 réalisations basculent réellement, au voisinage du
point critique attendu ($t\approx406$ contre $t_{\text{théorique}}=400$).
Détection par franchissement de seuil (3 écarts-types au-dessus de la
ligne de base) : la **variance** précède l'indice de **Moran** dans
**32/40 cas (80%)**, avec une avance moyenne nettement supérieure
(≈284 unités de temps contre ≈152). Ce résultat confirme, dans un
régime de basculement réel, la conclusion préliminaire des §5.6bis/ter.

**Découverte secondaire, non planifiée** : l'**autocorrélation** (AC1),
utilisée comme indicateur temporel de référence pour H1 (§5.1), se
révèle ici un détecteur nettement plus faible que la variance — seules
11/40 réalisations franchissent son seuil de détection avant la
bascule, avec une avance moyenne bien plus courte. Cette faiblesse
relative de l'AC1 par rapport à la variance sur données bruitées est
cohérente avec un résultat déjà documenté dans la littérature clinique
(indicateurs EWS multivariés en hémodialyse). **Conséquence à traiter** :
le module H1 (§5.1, §7) devrait comparer explicitement variance et AC1
sur les données réelles plutôt que présumer l'AC1 comme référence par
défaut.

**Limites encore ouvertes** : ce test ne couvre que le couplage
diffusif et la topologie en anneau ; les points 2 (couplage non
diffusif/Kuramoto) et 3 (réseau réel irrégulier) du protocole de
généralisation restent à mener avant toute conclusion définitive.

### 5.6quinquies Robustesse au type de couplage (non diffusif)

**Test** : même modèle (bifurcation nœud-col, réseau en anneau, $N=40$,
40 réalisations), mais couplage remplacé par une forme saturante de type
contagion plutôt que diffusive linéaire :
$$dx_i = \Big(\mu(t) + x_i^2 + \beta\sum_j W_{ij}\tanh(x_j-x_i)\Big)dt + \sigma\,dW_i$$
Contrairement au couplage diffusif (§5.6quater), l'influence d'un voisin
sature ici pour les grands écarts plutôt que de croître linéairement —
un régime qualitativement différent, plus proche d'une dynamique de
contagion/seuil.

**Résultat** : la précédence tient toujours — la variance précède
l'indice de Moran dans **36/40 cas (90%)**, avec un délai d'anticipation
du même ordre de grandeur qu'avec le couplage diffusif (≈288 contre
≈155 unités de temps). L'autocorrélation reste un détecteur faible
(13/40 détections). **Ce résultat n'est donc pas un artefact du
couplage diffusif linéaire** : il tient sous un type de couplage
qualitativement différent.

**Ce qui reste à faire avant généralisation complète** : réseau réel
irrégulier (communes françaises) en régime de basculement effectif
(pas seulement en régime linéaire stationnaire comme au §5.6ter), et
in fine la confrontation aux données réelles (§5.7).

### 5.7 Protocole de validation

Épisodes historiques réels servant de vérité terrain (liste à compléter
au fil du projet, minimum 5 épisodes indépendants avant toute conclusion
ferme) :
- Choc de chômage 2008-2009 (série INSEE trimestrielle par département)
- Mouvement social de 2018 (rupture datée, hétérogène par département)
- Tension sociale/sanitaire 2020

Pour chaque épisode : calculer les indicateurs sur la période précédente,
tester leur significativité (§5.4), puis comparer selon H1/H2/H3.

### 5.8 H4 — Contrôle actif de la synchronisation (inspiré du RCA)

**Nature différente des trois premières hypothèses** : H1-H3 sont des
hypothèses empiriques, testées contre des données réelles et un verdict
statistique. H4 n'est **pas testable de la même façon** — on ne peut pas
réellement intervenir sur une société pour vérifier si le contrôle
fonctionne. C'est une **démonstration de principe en simulation**,
utile pour la vulgarisation et pour illustrer un mécanisme réel de
physique des systèmes couplés, mais elle ne doit jamais être présentée
avec le même statut de preuve que H1-H3. Le module H4 est un simulateur
pédagogique, pas un test statistique.

**Cadrage honnête** : le modèle de Kuramoto (1975) et le contrôle de la
synchronisation d'oscillateurs couplés sont des champs établis depuis
50 ans (appliqués aux réseaux électriques, à la stimulation cérébrale
contre les crises d'épilepsie/Parkinson). L'apport ici est de transposer
ce mécanisme, en simulation, à un système socio-territorial illustratif
— pas de créer une nouvelle théorie physique.

**Modèle** — pour $N$ oscillateurs de phase $\theta_i(t)$ et de
fréquence propre $\omega_i$ :
$$\frac{d\theta_i}{dt} = \omega_i + \frac{K}{N}\sum_{j=1}^N \sin(\theta_j - \theta_i)$$
Paramètre d'ordre (mesure de synchronisation globale, $r \in [0,1]$) :
$$r\,e^{i\psi} = \frac{1}{N}\sum_{j=1}^N e^{i\theta_j}$$

**Démonstration (contenu obligatoire du mode expert)** : en réécrivant le
couplage en fonction du paramètre d'ordre, l'équation devient
$\dot\theta_i = \omega_i + Kr\sin(\psi - \theta_i)$ — chaque oscillateur
ne "voit" que le champ moyen $r$. À l'équilibre auto-cohérent, pour une
distribution de fréquences $g(\omega)$ symétrique et unimodale, il existe
un couplage critique :
$$K_c = \frac{2}{\pi g(0)}$$
En dessous de $K_c$, $r \to 0$ (incohérence) ; au-dessus, $r$ devient
positif de façon continue mais avec une dérivée infinie en $K_c$ — c'est
une transition de phase, la version continue de la bascule (Kuramoto,
1975 ; Strogatz, 2000, revue de référence).

**Le principe du RCA en langage de modèle** : au lieu de subir cette
transition (laisser $K$ fixe et voir $r$ s'emballer), on introduit un
couplage adaptatif $K_{ij}(t)$ qui diminue localement dès qu'une paire
d'oscillateurs approche du verrouillage de phase (proportionnel à
$-\beta \, d|\theta_i-\theta_j|/dt$ quand cet écart se réduit trop vite),
inspiré des méthodes de désynchronisation utilisées en neurostimulation
(Popovych & Tass). L'objectif du contrôle n'est pas $r=0$ (rigidité
totale, coûteuse) ni $r=1$ (synchronisation/bascule) mais un maintien de
$r$ sous un seuil $r_c$ choisi, en laissant les oscillations locales
vivre. C'est la traduction mathématique directe de la scène du roman :
ne pas supprimer les turbulences, empêcher leur synchronisation.

**Sortie pédagogique attendue** : deux simulations comparées côte à côte
— sans contrôle ($K$ fixe, $r(t)$ qui s'emballe vers 1) et avec contrôle
adaptatif ($r(t)$ maintenu sous $r_c$ malgré les mêmes perturbations) —
exactement le contraste montré dans le roman entre les anciens modèles
de fusion et le RCA.

### 5.9 H5 — Signature de criticité auto-organisée (SOC)

**Nature de cette hypothèse** : contrairement à H1-H3 (une bascule
ponctuelle qu'on cherche à détecter à l'avance) et à H4 (une simulation
de contrôle), H5 teste si le système observé se comporte comme un
système en **criticité auto-organisée** — un état où le système se
maintient spontanément à la limite de la stabilité, produisant des
événements de toutes tailles selon une loi de puissance, sans jamais
"basculer" une fois pour toutes (Bak, Tang & Wiesenfeld, 1987). C'est
une hypothèse empirique, testable et falsifiable, au même titre que
H1-H3 — mais elle ne dit pas la même chose : H1-H4 cherchent une bascule
unique, H5 demande si le système vit en permanence dans un régime de
bascules de toutes tailles.

**Cadrage honnête** : la criticité auto-organisée est un champ mature
(près de 40 ans), déjà appliqué aux grèves, aux guerres, aux conflits
sociaux. L'apport ici est, comme pour H1-H3, une application à un
nouveau domaine (données socio-territoriales françaises) — pas une
nouvelle théorie. Un point d'honnêteté supplémentaire, propre à ce
champ précis : l'ajustement d'une loi de puissance est notoirement
sujet à de faux positifs quand il est fait par simple régression sur un
graphe log-log — un résultat démontré par Touboul & Destexhe (2010),
qui montrent que de purs processus stochastiques sans vraie criticité
produisent des courbes log-log trompeusement rectilignes. §5.9.2 impose
donc la méthode rigoureuse (Clauset, Shalizi & Newman, 2009), pas
l'ajustement visuel.

#### 5.9.1 Définition et estimation

Une loi de puissance (cas continu, $x\ge x_{\min}$) a pour densité~:
$$p(x) = \frac{\alpha-1}{x_{\min}}\left(\frac{x}{x_{\min}}\right)^{-\alpha}$$

**Démonstration (contenu obligatoire du mode expert) — estimateur du
maximum de vraisemblance de $\alpha$** : pour $n$ observations
$x_1,\dots,x_n \ge x_{\min}$ supposées indépendantes, la
log-vraisemblance vaut~:
$$\ln L(\alpha) = n\ln(\alpha-1) - n\ln(x_{\min}) - \alpha\sum_{i=1}^n \ln\!\left(\frac{x_i}{x_{\min}}\right)$$
En dérivant par rapport à $\alpha$ et en annulant~:
$$\frac{d\ln L}{d\alpha} = \frac{n}{\alpha-1} - \sum_i \ln\!\left(\frac{x_i}{x_{\min}}\right) = 0 \ \Longrightarrow\ \hat\alpha = 1 + \frac{n}{\displaystyle\sum_{i=1}^n \ln(x_i/x_{\min})}$$
C'est l'estimateur de Clauset, Shalizi & Newman (2009) — obtenu par un
simple calcul de dérivée, sans ajustement graphique.

#### 5.9.2 Test de la plausibilité du modèle (et non simple "ajustement")

**Erreur à ne jamais commettre** : un ajustement qui "a l'air droit" sur
un graphe log-log ne prouve rien (§5.9, cadrage honnête). La méthode
correcte, qui réutilise exactement la logique déjà enseignée au §5 du
cours de statistiques (test par permutation/données de substitution)~:

1. Estimer $\hat\alpha$ et $x_{\min}$ par maximum de vraisemblance
   (§5.9.1).
2. Calculer la statistique de Kolmogorov-Smirnov $D_{\text{obs}}$ entre
   la fonction de répartition empirique des données et celle du modèle
   ajusté.
3. Générer un grand nombre de jeux de données synthétiques tirés du
   modèle de loi de puissance ajusté lui-même, réajuster $\hat\alpha$
   sur chacun, et calculer leur propre statistique $D_{\text{synth}}$.
4. La p-value est la fraction des jeux synthétiques donnant
   $D_{\text{synth}} \ge D_{\text{obs}}$ — exactement le même principe
   que le test par permutation du cours (\S5), appliqué ici à la
   qualité d'ajustement plutôt qu'à une corrélation. Une p-value élevée
   (par convention $>0{,}1$) signifie que la loi de puissance est un
   modèle plausible ; une p-value faible la rejette.
5. **Comparaison de modèles, obligatoire avant toute conclusion** :
   comparer par un test du rapport de vraisemblance la loi de puissance
   à des modèles alternatifs plausibles (log-normale, exponentielle) —
   un ajustement "acceptable" à l'étape 4 ne veut rien dire si une
   loi log-normale s'ajuste tout aussi bien ou mieux.

#### 5.9.3 Application prévue

Tailles d'événements candidates, à partir des connecteurs déjà
spécifiés (§6) : nombre de mentions GDELT/Reddit dans un sursaut
d'activité au-dessus d'un seuil, ou amplitude des chocs successifs
d'une série Insee (variations trimestrielles du chômage). Verdict rendu
selon le même gabarit que H1-H4 (§7bis), avec les mêmes garde-fous de
prudence statistique (§9.8) : jamais de verdict "confirmée" sur une
seule série.

---

## 6. Connecteurs de données normalisés

Tous les connecteurs alimentent un schéma commun :
`(source, territoire_ou_portee, date, indicateur, valeur, métadonnées)`.

| Connecteur | Ce qu'il apporte | Accès | Contrainte |
|---|---|---|---|
| INSEE — API BDM | Séries chronologiques officielles | Ouvert, sans clé | Aucune |
| INSEE — Données locales | Indicateurs territoriaux (commune/département) | Ouvert | Seuil de population minimal à l'affichage (§7) |
| Réseaux sociaux — sources ouvertes | Volume, sentiment, structure de réseau agrégée (ex. SNAP Reddit Hyperlink Network, GDELT) | Fichiers ouverts, sans scraping | Aucun scraping de plateforme non autorisée |
| Tendances de recherche | Intérêt de recherche agrégé | API officielle Google Trends (accès alpha restreint en 2026) | Connecteur désactivé tant que l'accès officiel n'est pas obtenu ; pas de contournement |
| Marchés financiers | Indices publics de volatilité (proxy de tension économique) | API officielle avec clé (ex. Alpha Vantage, Euronext) | Aucune donnée de compte/position individuelle |

**Principe directeur** : si une source n'offre pas d'accès conforme à ses
propres conditions d'utilisation, elle est exclue du produit, même si
elle serait techniquement récupérable. C'est un garde-fou de conception,
non contournable ultérieurement.

Chaque connecteur est un module indépendant (`fetch()`, `normalize()`) :
ajouter une source ne doit jamais modifier le cœur du système.

---

## 7. Module de test des hypothèses

**Sortie du module**, pour chaque hypothèse (H1, H2, H3) :
- Un verdict : *confirmée / infirmée / non concluante sur cette période*,
  jamais formulé de façon plus catégorique que ne le permet le test
  statistique.
- Mode simplifié : une phrase de conclusion en langage courant.
- Mode expert : statistique de test, p-value ou intervalle de confiance,
  méthode de données de substitution utilisée.
- Export du rapport complet (PDF/Markdown).

**Garde-fou méthodologique** : le module indique systématiquement le
nombre d'épisodes indépendants testés. En dessous de 5 épisodes, mention
automatique "résultat préliminaire, à confirmer sur davantage de cas" —
jamais de verdict "confirmée" sur un seul épisode.

---

## 7bis. Module "Journal de recherche" (obligatoire, visible dans le logiciel)

**Principe** : tout ce qui a été établi mathématiquement pendant la
conception du projet (§5.6bis à §5.6quinquies) doit être visible et
lisible **dans le logiciel lui-même**, pas seulement dans ce document
de conception. C'est une page dédiée, accessible depuis la page
d'accueil (§2), présentée comme le récit du raisonnement scientifique
— y compris l'erreur corrigée, qui doit rester visible plutôt
qu'être effacée. Montrer qu'un raisonnement a été corrigé par le calcul
est un contenu pédagogique en soi, pas une faiblesse à cacher.

**Contenu exact à afficher, dans l'ordre, avec bascule
simplifié/expert (§3) à chaque étape :**

1. **Le postulat de départ** : la question posée (l'indicateur temporel
   précède-t-il toujours l'indicateur spatial, et pourquoi).
2. **Le modèle** : réseau d'oscillateurs stochastiques couplés
   approchant une bifurcation (§5.6bis) — formule en mode expert,
   description en une phrase en mode simplifié.
3. **L'erreur initiale et sa correction** : présentée explicitement
   ("un premier raisonnement qualitatif concluait à tort que... ; le
   calcul exact a montré que...") — pas reformulée pour effacer l'erreur.
4. **Le résultat sur système linéaire stationnaire** (§5.6bis/ter) et
   sa portée limitée assumée.
5. **La validation Monte-Carlo sur un vrai basculement** (§5.6quater) :
   variance précède Moran dans 80% des cas, découverte secondaire sur
   la faiblesse de l'autocorrélation comme détecteur.
6. **La robustesse au type de couplage** (§5.6quinquies) : le résultat
   tient aussi sous couplage non diffusif (90% des cas).
7. **État d'avancement du protocole de généralisation**, sous forme de
   liste cochable visible par l'utilisateur :
   - [x] Bifurcation réellement franchie (pas seulement approchée)
   - [x] Robustesse testée sur un couplage non diffusif
   - [ ] Testé sur un réseau réel irrégulier (communes françaises)
   - [x] Fenêtres finies et bruit d'estimation (déjà inhérent au Monte-Carlo)
   - [ ] Confronté aux épisodes historiques réels (§5.7)

**Instructions pour la suite de l'implémentation (à exécuter avec accès
réseau, donc par Claude Code et non dans un environnement sans accès
internet)** :

1. Récupérer la carte de contiguïté réelle des communes ou départements
   français (contours administratifs INSEE/IGN — Admin Express ou COG),
   construire le Laplacien du graphe réel correspondant.
2. Rejouer exactement le test de basculement du §5.6quater/quinquies
   (bifurcation nœud-col, réalisations Monte-Carlo, détection par
   franchissement de seuil) en remplaçant le réseau en anneau par ce
   graphe réel, et vérifier si la précédence variance/Moran tient.
3. Utiliser les connecteurs déjà spécifiés (§6) pour récupérer les
   séries réelles des épisodes historiques (§5.7 : chômage 2008-2009,
   2018, 2020) et y appliquer le test de précédence, pas seulement les
   modules H1/H2/H3 déjà prévus.
4. Publier ces résultats supplémentaires dans le module "Journal de
   recherche" en respectant le même format (postulat → méthode →
   résultat → limites), qu'ils confirment ou contredisent les
   résultats précédents — un résultat contraire doit être publié avec
   la même visibilité qu'un résultat confirmatif, jamais filtré.
5. Le script `lyapunov_precedence_check.py` fourni en annexe contient
   déjà le code des étapes 5.6bis à 5.6quinquies : l'étendre plutôt que
   le réécrire, pour garder la continuité et la reproductibilité du
   raisonnement.

---

## 8. Architecture technique

- **Backend** : Python (FastAPI), pandas/numpy/statsmodels/scipy pour les
  calculs et tests statistiques
- **Frontend** : React, bascule simplifié/expert au niveau de chaque
  composant de résultat
- **Base de données** : PostgreSQL (comptes, historique d'analyses,
  cache des connecteurs)
- **Auth** : JWT, RBAC utilisateur/administrateur
- **Déploiement** : conteneurisé (Docker), secrets hors code (secrets
  manager), jamais en dur

---

## 9. Garde-fous techniques et éthiques

Non négociables, à traduire en tests automatisés avant toute livraison,
pas seulement documentés :

1. **Refus structurel des données nominatives** : le schéma d'ingestion
   n'accepte que des colonnes numériques + date + territoire. Toute
   colonne contenant un identifiant personnel détectable (email, nom
   propre utilisé comme identifiant unique, ID utilisateur explicite) est
   **rejetée à l'import** avec message clair.
2. **Anonymisation par défaut** : seuil de k-anonymat (k ≥ 20
   observations) avant tout calcul ou export par sous-groupe. Pour les
   données territoriales, affichage bloqué en dessous d'un seuil de
   population communale (ex. 2 000 habitants) pour éviter toute
   ré-identification indirecte.
3. **Conformité des connecteurs** : aucune source intégrée sans API
   officielle ou jeu de données ouvert conforme aux conditions
   d'utilisation de son éditeur. Un connecteur non conforme n'est pas
   développé, même en usage interne/test.
4. **Rate limiting** sur l'API du produit (ex. 100 requêtes/min/compte).
5. **Chiffrement** en transit (TLS) et au repos, purge automatique des
   fichiers importés après un délai configurable.
6. **Journalisation d'audit** (qui, quand, quoi) sans jamais stocker le
   contenu des données dans les logs.
7. **Validation stricte des entrées** : pas d'exécution de code arbitraire
   depuis les fichiers importés (pas de pickle, pas d'eval), protection
   contre les injections (ORM paramétré).
8. **Prudence statistique obligatoire** : le module d'hypothèses ne peut
   jamais afficher "confirmée" sans mention du nombre d'épisodes testés
   et du test de significativité utilisé.
9. **Séparation des environnements** dev/staging/prod, secrets distincts.
10. **Tests automatisés (CI)** sur : rejet des colonnes nominatives,
    exactitude des calculs statistiques (comparaison à des valeurs de
    référence scipy/statsmodels), isolation multi-tenant.
11. **CGU explicites** interdisant tout usage de ciblage, profilage ou
    surveillance d'individus ou de groupes identifiables, ou toute prise
    de décision automatisée affectant des personnes sans supervision
    humaine.
12. **Clause de non-interprétation causale** affichée sur chaque rapport :
    un signal précurseur indique une perte de résilience statistique, pas
    une prédiction certaine ni une cause identifiée.
13. **Transparence de méthode** : documentation publique de la méthode
    statistique, condition de crédibilité pour un usage journalistique ou
    académique.

---

## 10. Roadmap

- **MVP** : page d'accueil + démo pédagogique + connecteur INSEE seul +
  indicateurs temporels (§5.1) + mode simplifié/expert avec
  démonstrations complètes (§3) + module "Journal de recherche" (§7bis)
  avec le contenu déjà établi (§5.6bis à quinquies), état d'avancement
  inclus.
- **V1** : connecteurs réseaux sociaux ouverts (SNAP, GDELT) + test H1.
- **V2** : indice de Moran sur réseau territorial réel + test H2 + tâche
  1-2 du §7bis (réseau réel des communes, rejeu du test de basculement).
- **V3** : indicateur joint + test H3 + rapport exportable complet +
  tâche 3-4 du §7bis (confrontation aux épisodes historiques réels).
- **V4** : simulateur H4 (Kuramoto + contrôle adaptatif), clairement
  distingué des modules H1-H3 comme démonstration pédagogique et non
  comme test statistique.
- **V5** : module H5 (§5.9) — estimation par maximum de vraisemblance,
  test de plausibilité par bootstrap (§5.9.2), comparaison de modèles
  (loi de puissance vs log-normale vs exponentielle) avant tout verdict.
- **V6 (conditionnelle)** : connecteurs marchés financiers et Trends,
  uniquement si accès API officiel obtenu dans le respect du §6 et §9.3.

---

## 11. Critères d'acceptation

- [ ] La page d'accueil est compréhensible par un lecteur sans formation
      scientifique (test de lecture par une personne extérieure au projet).
- [ ] Aucun résultat n'est affichable sans son équivalent en mode
      simplifié.
- [ ] Un fichier contenant une colonne identifiable est rejeté avec un
      message explicite, jamais silencieusement ignoré.
- [ ] Les indicateurs calculés correspondent aux valeurs de référence
      statsmodels/scipy à ±1e-6 près.
- [ ] Un compte utilisateur ne peut jamais accéder aux données importées
      par un autre compte (test d'isolation automatisé).
- [ ] L'API refuse au-delà du taux limite configuré (test de charge).
- [ ] Le module d'hypothèses refuse d'émettre un verdict "confirmée" sur
      un seul épisode testé.
- [ ] Aucun connecteur n'est intégré sans documentation de conformité
      (lien vers les conditions d'utilisation de la source).
- [ ] Chaque résultat en mode expert affiche une démonstration complète
      (pas seulement la formule finale) — vérifié par relecture du
      contenu affiché face au §5 de ce document.
- [ ] Le module H4 affiche en permanence une mention le distinguant de
      H1-H3 ("simulation pédagogique, non testée empiriquement"), jamais
      de verdict "confirmée/infirmée" comme pour les autres hypothèses.
- [ ] Le module "Journal de recherche" (§7bis) est accessible depuis la
      page d'accueil et affiche l'intégralité du contenu du §5.6bis à
      §5.6quinquies, y compris l'erreur de raisonnement corrigée —
      vérifié par relecture face à ce document.
- [ ] La liste d'avancement du protocole de généralisation (§7bis,
      point 7) est visible et à jour, pas seulement mentionnée dans la
      documentation technique interne.
- [ ] Le mot "découverte" n'apparaît nulle part sur le site ni dans les
      rapports générés pour décrire un résultat du projet (§1bis) —
      vérifié par recherche de texte sur l'ensemble du contenu généré.
- [ ] Le module H5 n'affiche jamais un ajustement de loi de puissance
      basé sur une simple régression log-log — seule la méthode par
      maximum de vraisemblance (§5.9.1) et le test de plausibilité par
      bootstrap (§5.9.2) sont utilisés, vérifié par relecture du code.
- [ ] Le module H5 affiche systématiquement la comparaison à au moins
      un modèle alternatif (log-normale ou exponentielle) avant tout
      verdict — jamais un verdict basé sur la seule plausibilité de la
      loi de puissance isolée.
- [ ] La page d'accueil et la page Bilan contiennent chacune une
      reformulation explicite du positionnement scientifique du §1bis
      (réplication, résultats négatifs, outil réutilisable, médiation).

---

## 12. Bibliographie

Toute affirmation théorique du §5 doit être accompagnée de sa référence
exacte dans l'interface (mode expert), pas seulement d'un nom d'auteur :

- Ives, A. R. (1995). "Measuring resilience in stochastic systems." *Ecological Monographs*, 65(2), 217–233.
- Scheffer, M., Bascompte, J., Brock, W. A., Brovkin, V., Carpenter, S. R., Dakos, V., Held, H., van Nes, E. H., Rietkerk, M., & Sugihara, G. (2009). "Early-warning signals for critical transitions." *Nature*, 461, 53–59.
- Dakos, V., Carpenter, S. R., Brock, W. A., Ellison, A. M., Guttal, V., Ives, A. R., Kéfi, S., Livina, V., Seekell, D. A., van Nes, E. H., & Scheffer, M. (2012). "Methods for Detecting Early Warnings of Critical Transitions in Time Series Illustrated Using Simulated Ecological Data." *PLoS ONE*, 7(7), e41010.
- Fisher, R. A. (1925). *Statistical Methods for Research Workers*. Oliver and Boyd.
- Brown, M. B. (1975). "A method for combining non-independent, one-sided tests of significance." *Biometrics*, 31(4), 987–992.
- Poole, W., Gibbs, D. L., Shmulevich, I., Bernard, B., & Knijnenburg, T. A. (2016). "Combining dependent P-values with an empirical adaptation of Brown's method." *Bioinformatics*, 32(17), i430–i436. — méthode directement réutilisée pour H3 (Empirical Brown's Method), pas reconstruite.
- Legault, V., Pu, Y., Weinans, E., & Cohen, A. A. (2024). "Application of early warning signs to physiological contexts: a comparison of multivariate indices in patients on long-term hemodialysis." *Frontiers in Network Physiology*, 4, 1299162. — source de la comparaison variance/autocorrélation citée au §5.6quater.
- Bak, P., Tang, C., & Wiesenfeld, K. (1987). "Self-organized criticality: An explanation of the 1/f noise." *Physical Review Letters*, 59(4), 381–384. — fondement théorique de H5.
- Clauset, A., Shalizi, C. R., & Newman, M. E. J. (2009). "Power-Law Distributions in Empirical Data." *SIAM Review*, 51(4), 661–703. — méthode d'estimation et de test utilisée pour H5 (§5.9.1-5.9.2).
- Touboul, J., & Destexhe, A. (2010). "Can Power-Law Scaling and Neuronal Avalanches Arise from Stochastic Dynamics?" *PLoS ONE*, 5(2), e9448. — mise en garde méthodologique citée au §5.9 (cadrage honnête).
- Dakos, V., van Nes, E. H., Donangelo, R., Fort, H., & Scheffer, M. (2010). "Spatial correlation as leading indicator of catastrophic shifts." *Theoretical Ecology*, 3, 163–174.
- MacLaren, N. G., Aihara, K., & Masuda, N. (2025). "Applicability of spatial early warning signals to complex network dynamics." *Journal of the Royal Society Interface*, 22(226), 20240696. — source du créneau identifié pour H2 (les EWS spatiaux sont validés presque exclusivement sur des grilles régulières, pas sur des réseaux réels irréguliers).
- Kuramoto, Y. (1975). "Self-entrainment of a population of coupled non-linear oscillators." In *International Symposium on Mathematical Problems in Theoretical Physics*, Lecture Notes in Physics, 39, 420–422.
- Strogatz, S. H. (2000). "From Kuramoto to Crawford: exploring the onset of synchronization in populations of coupled oscillators." *Physica D*, 143(1-4), 1–20.
- Popovych, O. V., & Tass, P. A. (2012). "Desynchronizing electrical and sensory coordinated reset neuromodulation." *Frontiers in Human Neuroscience*, 6, 58. — inspiration du principe de contrôle adaptatif utilisé pour H4, transposé ici en simulation, pas appliqué tel quel.

**Règle de citation** : aucune formule ou démonstration affichée en mode
expert ne doit apparaître sans la référence correspondante visible dans
l'interface (§3), au même titre que le texte de la démonstration
elle-même.

---

*Document destiné à être fourni tel quel comme brief à Claude Code. Les
garde-fous du §9 doivent être traduits en tests automatisés avant qu'un
connecteur ou une fonctionnalité ne soit considéré comme livré.*
