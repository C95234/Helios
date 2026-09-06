/**
 * Bilan publié -- resultats des tests H1/H2/H3/H4/H5/Fusion, pour publier
 * des conclusions honnetes -- pas seulement l'historique personnel de
 * chaque visiteur (page /mon-historique, propre a chaque navigateur).
 *
 * H1, H2, H3, H5, Fusion sont desormais rafraichis AUTOMATIQUEMENT
 * (backend/scripts/refresh_results.py, planifie par
 * .github/workflows/refresh-results.yml et grow-mast-battery.yml) --
 * ce fichier ne fait qu'importer et ré-exporter les JSON generes sous
 * ./results/, pour que les pages Résultat n'aient rien a changer.
 * H4 (simulation pure, aucune donnee externe) et les extensions Google
 * Trends (accès non officiel, exclu du rafraîchissement automatique --
 * voir garde-fous) restent manuscrits, mis à jour à la main si besoin.
 */
import h1 from "./results/h1.json";
import h2 from "./results/h2.json";
import h3 from "./results/h3.json";
import h5 from "./results/h5.json";
import fusion from "./results/fusion.json";

export const GENERATED_AT = "3 septembre 2026";

export const H1_PHENOMENA = h1.phenomena;
export const H1_SUMMARY = h1.summary;
export const H1_REFRESHED_AT = h1.refreshedAt;

export const H2_RESULT = h2.result;
export const H2_MORAN_SERIES = h2.moranSeries;
export const H2_AGGREGATE = h2.aggregate;
export const H2_REFRESHED_AT = h2.refreshedAt;

export const H3_PHENOMENA = h3.phenomena;
export const H3_UNAVAILABLE = h3.unavailable;
export const H3_SUMMARY = h3.summary;
export const H3_REFRESHED_AT = h3.refreshedAt;

// rControlled/rUncontrolled : une seule graine (celle figee a l'origine).
// nSeedsUnderThreshold/nSeeds : controle de robustesse sur 30 graines
// independantes par configuration (backend/scripts/h4_seed_robustness.py),
// mene apres avoir remarque que la relation beta/efficacite n'etait pas
// monotone sur une seule graine -- voir les limites de H4Result.jsx.
export const H4_CONFIGS = [
  { name: "K=2K_c, β=2 (référence)", n: 40, kOverKc: 2.0, beta: 2, rUncontrolled: 0.963, rControlled: 0.284, nSeedsUnderThreshold: 30, nSeeds: 30 },
  { name: "K=3K_c, β=2", n: 40, kOverKc: 3.0, beta: 2, rUncontrolled: 0.985, rControlled: 0.31, nSeedsUnderThreshold: 30, nSeeds: 30 },
  { name: "K=5K_c, β=2 (couplage fort)", n: 40, kOverKc: 5.0, beta: 2, rUncontrolled: 0.995, rControlled: 0.361, nSeedsUnderThreshold: 15, nSeeds: 30 },
  { name: "K=3K_c, β=0,5 (contrôle faible)", n: 40, kOverKc: 3.0, beta: 0.5, rUncontrolled: 0.985, rControlled: 0.432, nSeedsUnderThreshold: 30, nSeeds: 30 },
  { name: "K=3K_c, β=1", n: 40, kOverKc: 3.0, beta: 1, rUncontrolled: 0.985, rControlled: 0.357, nSeedsUnderThreshold: 30, nSeeds: 30 },
  { name: "K=3K_c, β=4 (contrôle fort)", n: 40, kOverKc: 3.0, beta: 4, rUncontrolled: 0.985, rControlled: 0.413, nSeedsUnderThreshold: 30, nSeeds: 30 },
  { name: "Petit réseau", n: 15, kOverKc: 3.0, beta: 2, rUncontrolled: 0.982, rControlled: 0.457, nSeedsUnderThreshold: 24, nSeeds: 30 },
  { name: "Grand réseau", n: 80, kOverKc: 3.0, beta: 2, rUncontrolled: 0.987, rControlled: 0.253, nSeedsUnderThreshold: 30, nSeeds: 30 },
];

export const H4_R_THRESHOLD = 0.5;
// Robuste = controle sous le seuil sur au moins 90% des 30 graines testees.
export const H4_SUMMARY = { nConfigs: 8, nRobust: 6, nPartial: 1, nUnreliable: 1 };

// Extension H1 -- Google Trends comme troisieme signal social, en plus de
// Wikipedia. Derogation documentee au §6 (acces non officiel, voir
// backend/app/connectors/google_trends.py) : le sujet direct du phenomene
// + un panier FIXE de 5 termes "obliques" (proxies de tension economique/
// psychologique, memes termes pour tous les phenomenes, choisis avant tout
// resultat pour eviter le biais de selection a posteriori).
// Exclu du rafraichissement automatique (decision utilisateur) : un appel
// automatique et repete escaladerait la derogation ToS ponctuelle deja
// assumee -- reste rafraichissable seulement a la main.
export const TRENDS_OBLIQUE_TERMS = ["recherche emploi", "assurance chômage", "anxiété", "vente maison", "prêt personnel"];

export const TRENDS_RESULTS = [
  { label: "Mouvement social 2018 (« gilets jaunes »)", nTested: 6, nSig: 0, sigTerms: [], status: "ok" },
  { label: "Tension sanitaire 2020 (premier confinement)", nTested: 6, nSig: 2, sigTerms: ["vente maison", "prêt personnel"], status: "ok" },
  { label: "Climat social récent (témoin, sans événement)", nTested: 5, nSig: 1, sigTerms: ["prêt personnel"], status: "ok" },
  { label: "Attentats du 13 novembre 2015", nTested: 5, nSig: 1, sigTerms: ["assurance chômage"], status: "ok" },
  { label: "Mouvement social contre la réforme des retraites 2023", nTested: 0, nSig: 0, sigTerms: [], status: "blocked" },
  { label: "Attentat de Nice, juillet 2016", nTested: 0, nSig: 0, sigTerms: [], status: "blocked" },
];

export const TRENDS_SUMMARY = {
  nPhenomenaWithData: 4,
  nPhenomenaBlocked: 2,
  nTermsTestedTotal: 22,
  nTermsSignificantTotal: 3,
};

// H5 -- criticite auto-organisee (§5.9). Source reelle : amplitude des chocs
// trimestriels de chomage departemental (Insee), seule source disponible
// parmi celles envisagees au §5.9.3 (GDELT rate-limite, Reddit/SNAP jamais
// connecte). Rafraichi automatiquement (voir en-tete de fichier) -- l'outil
// interactif de la page relance aussi le meme calcul en direct.
export const H5_RESULT = h5;
export const H5_REFRESHED_AT = h5.refreshedAt;

// Domaine Fusion nucleaire -- detection sur donnees de tokamak (§7ter). Rafraichi
// automatiquement sur la batterie curatee de app/data/mast_shots.json
// (voir en-tete de fichier) -- l'outil "tester en direct" de la page
// relance le meme calcul, tir par tir, sur MAST en direct.
export const FUSION_RESULT = fusion;
export const FUSION_REFRESHED_AT = fusion.refreshedAt;

// Troisieme domaine -- modele reduit de physique des plasmas, bilan de
// puissance 0-D, seuil d'ignition (§7quater). Simulation pure (aucune
// donnee externe, contrairement a Fusion) -- exclue du rafraichissement
// automatique comme H4, valeurs gelees apres une execution reelle en local
// (20 realisations : 10 "ignited" seeds 0-9, 10 "stable" seeds 10000-10009,
// n_surrogates=200). L'outil "tester en direct" de la page relance le meme
// calcul avec de nouvelles graines.
export const PLASMA_RESULT = {
  nRuns: 20,
  nIgnited: 10,
  nStable: 10,
  nIgnitedWithPrecursor: 10,
  nStableFalsePositive: 0,
  verdict: "favorable",
  runs: [
    { seed: 0, scenario: "ignited", ignited: true, tIgnition: 5.998, peakTemperatureKev: 30.14, varianceSig: true, ac1Sig: false, precursor: true },
    { seed: 1, scenario: "ignited", ignited: true, tIgnition: 5.944, peakTemperatureKev: 30.18, varianceSig: true, ac1Sig: false, precursor: true },
    { seed: 2, scenario: "ignited", ignited: true, tIgnition: 6.014, peakTemperatureKev: 30.05, varianceSig: true, ac1Sig: false, precursor: true },
    { seed: 3, scenario: "ignited", ignited: true, tIgnition: 5.910, peakTemperatureKev: 30.10, varianceSig: true, ac1Sig: false, precursor: true },
    { seed: 4, scenario: "ignited", ignited: true, tIgnition: 5.948, peakTemperatureKev: 30.03, varianceSig: true, ac1Sig: false, precursor: true },
    { seed: 5, scenario: "ignited", ignited: true, tIgnition: 5.908, peakTemperatureKev: 30.01, varianceSig: true, ac1Sig: false, precursor: true },
    { seed: 6, scenario: "ignited", ignited: true, tIgnition: 5.908, peakTemperatureKev: 30.08, varianceSig: true, ac1Sig: false, precursor: true },
    { seed: 7, scenario: "ignited", ignited: true, tIgnition: 5.976, peakTemperatureKev: 30.01, varianceSig: true, ac1Sig: false, precursor: true },
    { seed: 8, scenario: "ignited", ignited: true, tIgnition: 5.992, peakTemperatureKev: 30.14, varianceSig: true, ac1Sig: false, precursor: true },
    { seed: 9, scenario: "ignited", ignited: true, tIgnition: 5.918, peakTemperatureKev: 30.16, varianceSig: true, ac1Sig: false, precursor: true },
    { seed: 10000, scenario: "stable", ignited: false, tIgnition: null, peakTemperatureKev: 1.50, varianceSig: false, ac1Sig: false, precursor: false },
    { seed: 10001, scenario: "stable", ignited: false, tIgnition: null, peakTemperatureKev: 1.50, varianceSig: false, ac1Sig: false, precursor: false },
    { seed: 10002, scenario: "stable", ignited: false, tIgnition: null, peakTemperatureKev: 1.50, varianceSig: false, ac1Sig: false, precursor: false },
    { seed: 10003, scenario: "stable", ignited: false, tIgnition: null, peakTemperatureKev: 1.51, varianceSig: false, ac1Sig: false, precursor: false },
    { seed: 10004, scenario: "stable", ignited: false, tIgnition: null, peakTemperatureKev: 1.52, varianceSig: false, ac1Sig: false, precursor: false },
    { seed: 10005, scenario: "stable", ignited: false, tIgnition: null, peakTemperatureKev: 1.51, varianceSig: false, ac1Sig: false, precursor: false },
    { seed: 10006, scenario: "stable", ignited: false, tIgnition: null, peakTemperatureKev: 1.50, varianceSig: false, ac1Sig: false, precursor: false },
    { seed: 10007, scenario: "stable", ignited: false, tIgnition: null, peakTemperatureKev: 1.51, varianceSig: false, ac1Sig: false, precursor: false },
    { seed: 10008, scenario: "stable", ignited: false, tIgnition: null, peakTemperatureKev: 1.51, varianceSig: false, ac1Sig: false, precursor: false },
    { seed: 10009, scenario: "stable", ignited: false, tIgnition: null, peakTemperatureKev: 1.50, varianceSig: false, ac1Sig: false, precursor: false },
  ],
};
