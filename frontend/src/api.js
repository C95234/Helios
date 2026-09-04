// En dev, le proxy Vite redirige "/api" vers le backend local (vite.config.js).
// En production, VITE_API_BASE_URL pointe vers l'URL reelle du backend deploye
// si frontend et backend ne sont pas servis depuis le meme domaine ; sinon,
// laisser vide pour continuer a utiliser un chemin relatif "/api" (utile si un
// reverse proxy unique sert les deux, cf. docker-compose.yml).
const BASE = `${import.meta.env.VITE_API_BASE_URL ?? ""}/api`;

async function getJson(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Erreur ${res.status}`);
  }
  return res.json();
}

export const api = {
  getDemo: (seed) => getJson(`/demo/simulated?seed=${seed}`),
  getCatalog: () => getJson(`/series/insee/catalog`),
  analyzeInsee: (idbank, window) => getJson(`/analyze/insee/${idbank}?window=${window}`),
  getPhenomena: () => getJson(`/hypotheses/phenomena`),
  testH1: (phenomenon) => getJson(`/hypotheses/h1?phenomenon=${phenomenon}`),
  testH1Aggregate: () => getJson(`/hypotheses/h1/aggregate?n_surrogates=100`),
  testH2: () => getJson(`/hypotheses/h2`),
  testH3: (phenomenon) => getJson(`/hypotheses/h3?phenomenon=${phenomenon}`),
  simulateH4: (params) => getJson(`/hypotheses/h4?${new URLSearchParams(params).toString()}`),
  testH5: () => getJson(`/hypotheses/h5`),
  getConnectors: () => getJson(`/connectors`),
  getGuardrails: () => getJson(`/connectors/guardrails`),
};
