/**
 * Bilan publié -- resultats des tests H1/H2/H3/H4 lances sur un maximum de
 * cas disponibles (6 phenomenes pour H1, 26 ans de donnees pour H2, 4
 * phenomenes calculables sur 6 pour H3, 8 configurations simulees pour H4),
 * pour publier des conclusions honnetes -- pas seulement l'historique
 * personnel de chaque visiteur (page /bilan, propre a chaque navigateur).
 *
 * Contenu fige (resultats calcules une fois, verifies, puis integres ici),
 * meme logique que le Journal de recherche : visible par n'importe quel
 * visiteur du site, sans dependre du localStorage de qui que ce soit.
 * Genere le 3 septembre 2026.
 */

export const GENERATED_AT = "3 septembre 2026";

export const H1_PHENOMENA = [
  { label: "Attentats du 13 novembre 2015", nOffSig: 0, nOff: 38, nSocSig: 3, nSoc: 3, decalageJours: null, outcome: "favorable" },
  { label: "Attentat de Nice, juillet 2016", nOffSig: 4, nOff: 38, nSocSig: 2, nSoc: 3, decalageJours: -13, outcome: "against" },
  { label: "Mouvement social contre la réforme des retraites 2023", nOffSig: 5, nOff: 38, nSocSig: 2, nSoc: 3, decalageJours: -52, outcome: "against" },
  { label: "Mouvement social 2018 (« gilets jaunes »)", nOffSig: 4, nOff: 38, nSocSig: 3, nSoc: 3, decalageJours: -56, outcome: "against" },
  { label: "Tension sanitaire 2020 (premier confinement)", nOffSig: 12, nOff: 38, nSocSig: 0, nSoc: 3, decalageJours: null, outcome: "against" },
  { label: "Climat social récent (fenêtre glissante la plus récente)", nOffSig: 8, nOff: 39, nSocSig: 1, nSoc: 3, decalageJours: -201, outcome: "against" },
];

export const H1_SUMMARY = { favorable: 1, against: 5, neutral: 0, nPhenomena: 6 };

export const H2_RESULT = {
  periodStart: "2000-01-01",
  periodEnd: "2026-01-01",
  nUnits: 96,
  nQuarters: 105,
  nEdgesRealNetwork: 238,
  realNetwork: { trendTau: -0.213, trendP: 0.932, trendSig: false, latestI: 0.362, latestP: 0.0, latestSig: true },
  controlGrid: { trendTau: 0.413, trendP: 0.124, trendSig: false, latestI: 0.04, latestP: 0.227, latestSig: false },
  realMean: 0.375,
  realStd: 0.022,
  gridMean: -0.012,
  gridStd: 0.038,
  nRealAboveGrid: 105,
  nQuartersTotal: 105,
};

// Serie complete, un point par trimestre (2000-01 a 2026-01), memes donnees que /tester-h2.
export const H2_MORAN_SERIES = {
  dates: ["2000-01-01","2000-04-01","2000-07-01","2000-10-01","2001-01-01","2001-04-01","2001-07-01","2001-10-01","2002-01-01","2002-04-01","2002-07-01","2002-10-01","2003-01-01","2003-04-01","2003-07-01","2003-10-01","2004-01-01","2004-04-01","2004-07-01","2004-10-01","2005-01-01","2005-04-01","2005-07-01","2005-10-01","2006-01-01","2006-04-01","2006-07-01","2006-10-01","2007-01-01","2007-04-01","2007-07-01","2007-10-01","2008-01-01","2008-04-01","2008-07-01","2008-10-01","2009-01-01","2009-04-01","2009-07-01","2009-10-01","2010-01-01","2010-04-01","2010-07-01","2010-10-01","2011-01-01","2011-04-01","2011-07-01","2011-10-01","2012-01-01","2012-04-01","2012-07-01","2012-10-01","2013-01-01","2013-04-01","2013-07-01","2013-10-01","2014-01-01","2014-04-01","2014-07-01","2014-10-01","2015-01-01","2015-04-01","2015-07-01","2015-10-01","2016-01-01","2016-04-01","2016-07-01","2016-10-01","2017-01-01","2017-04-01","2017-07-01","2017-10-01","2018-01-01","2018-04-01","2018-07-01","2018-10-01","2019-01-01","2019-04-01","2019-07-01","2019-10-01","2020-01-01","2020-04-01","2020-07-01","2020-10-01","2021-01-01","2021-04-01","2021-07-01","2021-10-01","2022-01-01","2022-04-01","2022-07-01","2022-10-01","2023-01-01","2023-04-01","2023-07-01","2023-10-01","2024-01-01","2024-04-01","2024-07-01","2024-10-01","2025-01-01","2025-04-01","2025-07-01","2025-10-01","2026-01-01"],
  real: [0.409899,0.414479,0.42031,0.421184,0.422711,0.427194,0.412736,0.399378,0.390321,0.374617,0.368282,0.355884,0.352378,0.338043,0.340628,0.320279,0.326533,0.330083,0.342737,0.346663,0.352681,0.355551,0.361114,0.364275,0.368335,0.374565,0.377241,0.38094,0.38677,0.393079,0.391385,0.403585,0.40911,0.407664,0.403876,0.390083,0.382911,0.381858,0.38485,0.383971,0.376786,0.38955,0.396789,0.397201,0.397208,0.393286,0.392984,0.396734,0.392844,0.387162,0.382002,0.386445,0.392984,0.38994,0.386238,0.38333,0.378336,0.375072,0.370836,0.364855,0.366171,0.364397,0.364837,0.367312,0.356308,0.353373,0.355734,0.358448,0.362684,0.368374,0.37771,0.377026,0.374597,0.374977,0.374228,0.368709,0.37274,0.360148,0.357576,0.343357,0.343315,0.322289,0.347426,0.366534,0.359409,0.375225,0.390676,0.385146,0.382419,0.381049,0.369827,0.384443,0.382621,0.386599,0.382939,0.375631,0.367517,0.359758,0.360805,0.355741,0.361929,0.363369,0.366066,0.360051,0.362469],
  grid: [0.01417,0.007045,0.015606,0.026859,0.042719,0.046196,0.02645,0.012021,-0.004721,-0.005649,-0.00304,-0.01061,-0.019701,-0.022103,-0.01494,-0.037737,-0.041949,-0.040048,-0.042299,-0.045327,-0.055726,-0.047496,-0.045184,-0.054589,-0.058787,-0.066608,-0.066127,-0.059592,-0.045945,-0.039185,-0.04371,-0.04722,-0.034745,-0.035473,-0.034367,-0.043139,-0.060127,-0.075897,-0.086771,-0.091025,-0.089223,-0.081898,-0.075806,-0.056222,-0.040648,-0.033382,-0.024496,-0.014877,-0.017523,-0.017963,-0.031753,-0.039556,-0.037511,-0.043363,-0.039887,-0.036512,-0.037378,-0.042271,-0.035659,-0.031636,-0.026407,-0.019738,-0.021026,-0.017887,-0.021154,-0.021378,-0.017742,-0.014729,-0.004075,-0.007298,0.003329,0.012696,0.008628,0.005762,0.000022,0.006543,0.010322,0.004603,0.003821,0.010731,0.005809,-0.018211,-0.001991,0.028555,0.012112,0.025014,0.027212,0.038783,0.044268,0.046664,0.052649,0.054686,0.051316,0.044372,0.045853,0.051456,0.04663,0.044726,0.029783,0.03896,0.033922,0.03287,0.040787,0.030463,0.04026],
};

export const H3_PHENOMENA = [
  { label: "Mouvement social 2018 (« gilets jaunes »)", tau: 0.966, moran: 0.36, pJoint: 0.04, sig: true },
  { label: "Mouvement social contre la réforme des retraites 2023", tau: 0.733, moran: 0.383, pJoint: 0.112, sig: false },
  { label: "Climat social récent", tau: 0.062, moran: 0.362, pJoint: 0.535, sig: false },
  { label: "Tension sanitaire 2020 (premier confinement)", tau: 0.143, moran: 0.347, pJoint: 0.704, sig: false },
];

export const H3_UNAVAILABLE = [
  { label: "Attentats du 13 novembre 2015", reason: "fenêtre de ~7 mois, insuffisante pour la composante temporelle (8 points mensuels minimum)" },
  { label: "Attentat de Nice, juillet 2016", reason: "fenêtre de ~7 mois, insuffisante pour la composante temporelle (8 points mensuels minimum)" },
];

export const H3_SUMMARY = { favorable: 1, neutral: 3, unavailable: 2, nCalculable: 4 };

export const H4_CONFIGS = [
  { name: "K=2K_c, β=2 (référence)", n: 40, kOverKc: 2.0, beta: 2, rUncontrolled: 0.963, rControlled: 0.284 },
  { name: "K=3K_c, β=2", n: 40, kOverKc: 3.0, beta: 2, rUncontrolled: 0.985, rControlled: 0.31 },
  { name: "K=5K_c, β=2 (couplage fort)", n: 40, kOverKc: 5.0, beta: 2, rUncontrolled: 0.995, rControlled: 0.361 },
  { name: "K=3K_c, β=0,5 (contrôle faible)", n: 40, kOverKc: 3.0, beta: 0.5, rUncontrolled: 0.985, rControlled: 0.432 },
  { name: "K=3K_c, β=1", n: 40, kOverKc: 3.0, beta: 1, rUncontrolled: 0.985, rControlled: 0.357 },
  { name: "K=3K_c, β=4 (contrôle fort)", n: 40, kOverKc: 3.0, beta: 4, rUncontrolled: 0.985, rControlled: 0.413 },
  { name: "Petit réseau", n: 15, kOverKc: 3.0, beta: 2, rUncontrolled: 0.982, rControlled: 0.457 },
  { name: "Grand réseau", n: 80, kOverKc: 3.0, beta: 2, rUncontrolled: 0.987, rControlled: 0.253 },
];

export const H4_R_THRESHOLD = 0.5;
export const H4_SUMMARY = { nConfigs: 8, nUnderThreshold: 8 };

// Extension H1 -- Google Trends comme troisieme signal social, en plus de
// Wikipedia. Derogation documentee au §6 (acces non officiel, voir
// backend/app/connectors/google_trends.py) : le sujet direct du phenomene
// + un panier FIXE de 5 termes "obliques" (proxies de tension economique/
// psychologique, memes termes pour tous les phenomenes, choisis avant tout
// resultat pour eviter le biais de selection a posteriori).
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
// connecte). Resultat fige d'un appel a /api/hypotheses/h5 (graine par
// defaut = 42, reproductible) -- l'outil interactif ci-dessous relance le
// meme calcul en direct.
export const H5_RESULT = {
  alpha: 5.9081,
  xmin: 1.6,
  ksStatistic: 0.1533,
  nTail: 41,
  nTotal: 8323,
  nDepartments: 96,
  nQuarters: 105,
  periodStart: "2000-01-01",
  periodEnd: "2026-01-01",
  pPlausibility: 0.01,
  nSynthetic: 200,
  lognormal: { r: -2.0677, pValue: 0.2406, favorsPowerLaw: false },
  exponential: { r: -1.4936, pValue: 0.0365, favorsPowerLaw: false },
  verdict: "against",
};
