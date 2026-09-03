/**
 * Classement d'un résultat en favorable / contre / neutre pour une hypothèse
 * donnée -- logique partagée entre les pages de test individuelles et la
 * page Bilan, pour ne jamais avoir deux critères différents du même verdict.
 */
export function h1Outcome(result) {
  const peakedBefore = result.decalage_jours !== null && result.decalage_jours > 0;
  const peakedAfter = result.decalage_jours !== null && result.decalage_jours < 0;
  const favorable = peakedBefore || (result.n_social_significant > 0 && result.n_official_significant === 0);
  const against = peakedAfter || (result.n_official_significant > 0 && result.n_social_significant === 0);
  if (favorable && !against) return "favorable";
  if (against && !favorable) return "against";
  return "neutral";
}

export function h2Outcome(result) {
  const realSig = result.real_network.trend.significant_at_0_05;
  const gridSig = result.control_grid.trend.significant_at_0_05;
  return realSig !== gridSig ? "favorable" : "neutral";
}

export function h3Outcome(result) {
  return result.significant_at_0_05 ? "favorable" : "neutral";
}
