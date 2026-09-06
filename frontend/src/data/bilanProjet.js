/**
 * Contenu du nouveau Bilan (§2.6 de la restructuration) -- synthese
 * honnete points forts/points faibles du projet, adaptee de la revue
 * "Revue du projet Helios" deja redigee cette session (artifact Claude).
 * Mise a jour a chaque round de tests -- generee le 3 septembre 2026.
 */

export const SCORECARD = [
  { dim: "Rigueur statistique", verdict: "strong", label: "Solide", note: "Chaque indicateur vérifié contre une valeur de référence (statsmodels, calcul à la main) à ±1e-6. Tests par substitution/permutation, pas de p-value « brute »." },
  { dim: "Honnêteté scientifique", verdict: "strong", label: "Très solide", note: "Aucun verdict « confirmée » forcé. Une erreur de raisonnement gardée visible plutôt qu'effacée. H4 jamais confondue avec un test statistique." },
  { dim: "Couverture des tests", verdict: "mixed", label: "Correcte, mais limitée", note: "6 phénomènes pour H1/H3 (curatés à la main), 5 variables réelles pour H2 (chômage, défaillances, logements, créations, population). Sous le seuil de significativité pratique d'un vrai échantillon." },
  { dim: "Résultats obtenus", verdict: "weak", label: "Majoritairement négatifs", note: "Aucune des 3 hypothèses réelles n'est confirmée sur ce round. H1 va à l'encontre du sens attendu dans 5 cas sur 6, H2 dans 3 des 5 variables testées." },
  { dim: "Reproductibilité", verdict: "strong", label: "Bonne", note: "46 tests automatisés, scripts de recherche versionnés, déviations documentées dans le code lui-même, pas seulement en prose." },
  { dim: "Fidélité au cahier des charges", verdict: "mixed", label: "Presque complète", note: "§1-§7bis, §9, §11-§12 couverts. §8 (comptes, PostgreSQL, JWT) volontairement non implémenté -- écart assumé, pas oublié." },
];

export const STRENGTHS = [
  { title: "Honnêteté au cœur du design, pas en façade", text: "Ce round de tests ne confirme aucune des trois hypothèses réelles -- et c'est publié tel quel, avec un graphique, un tableau et une synthèse qui disent explicitement « ça ne va pas dans le sens attendu ». Rien n'est édulcoré pour paraître plus concluant." },
  { title: "Les erreurs restent visibles", text: "Le Journal de recherche documente un raisonnement initial faux et sa correction par le calcul exact -- gardé en l'état plutôt qu'effacé." },
  { title: "Déviations toujours documentées, jamais silencieuses", text: "Chaque écart au cahier des charges (calibration H3 par bootstrap, règle de contrôle H4 réécrite, dérogation Google Trends) est expliqué dans le code et l'interface -- jamais juste « fait différemment » sans le dire." },
  { title: "Recherche poussée au-delà du minimum", text: "Le protocole de généralisation est allé jusqu'au bout : réseau réel des 96 départements, confrontation à 3 épisodes historiques réels -- pas seulement de la simulation." },
  { title: "Pédagogie à deux niveaux, partout, sans exception", text: "Chaque résultat a sa phrase en langage courant ET sa démonstration mathématique complète en mode expert." },
];

export const WEAKNESSES = [
  { title: "Échantillon petit et curaté, structurellement", text: "6 phénomènes pour H1/H3, choisis à la main. Même au-dessus du seuil de 5 épisodes, ce n'est pas un échantillon représentatif. H2 teste désormais 5 variables réelles, mais sur le même territoire et à peu près la même période -- pas 5 systèmes indépendants." },
  { title: "Aucune des trois hypothèses réelles n'est soutenue par ce round", text: "C'est un résultat honnête, pas un problème de méthode -- mais ça reste la conclusion factuelle. Le projet démontre une méthode rigoureuse plus qu'il ne prouve la thèse qu'il teste." },
  { title: "La calibration H3 reste un problème de recherche ouvert", text: "Le bootstrap couplé par période est une adaptation raisonnable, mais pas la méthode originale (surrogates à phase aléatoire couplés) -- contourné plutôt que résolu." },
  { title: "La reproduction du protocole de recherche est qualitative, pas exacte", text: "Sans script original, la calibration a dû être devinée puis ajustée empiriquement (87,5% contre 80/90% documentés) -- dans le bon sens, pas une validation au chiffre près." },
  { title: "Couverture des sources sociales limitée dans le temps", text: "Wikipédia ne couvre que juillet 2015 et après ; Google Trends et Bluesky non plus n'ont d'historique utile avant les phénomènes les plus anciens testés." },
  { title: "Écart assumé avec l'architecture cible", text: "Le cahier des charges prévoit comptes utilisateurs, PostgreSQL, JWT/RBAC -- l'app reste stateless. Un choix de scope défendable, mais un vrai écart si l'objectif est un produit multi-utilisateurs." },
];

export const CONCLUSION =
  "Le projet est méthodologiquement plus solide que ses résultats ne sont concluants -- et c'est cohérent avec ce qu'il prétend être : un outil qui teste honnêtement, pas un outil qui cherche à confirmer. La rigueur (vérifications numériques, démonstrations complètes, garde-fous testés, erreurs gardées visibles) est le vrai acquis de cette phase. La faiblesse structurelle -- peu de cas testables, aucune hypothèse franchement confirmée -- n'est pas un défaut de conception : c'est la limite honnête de ce que les données publiques disponibles permettent aujourd'hui, explicitement nommée plutôt que masquée.";
