/**
 * Historique local des résultats -- persistance simple côté navigateur
 * (localStorage), sans backend ni compte. Propre à cet appareil/navigateur :
 * un autre poste ne verra pas cet historique. Best-effort : si le quota est
 * dépassé ou localStorage indisponible, on échoue silencieusement plutôt que
 * de casser la page -- l'historique est un confort, pas une garantie.
 */
const MAX_ENTRIES = 8;
const PREFIX = "helios_history_";

function keyFor(page) {
  return `${PREFIX}${page}`;
}

export function saveToHistory(page, entry) {
  try {
    const key = keyFor(page);
    const existing = JSON.parse(localStorage.getItem(key) || "[]");
    const updated = [{ ...entry, savedAt: new Date().toISOString() }, ...existing].slice(0, MAX_ENTRIES);
    localStorage.setItem(key, JSON.stringify(updated));
  } catch (e) {
    console.warn("Historique non sauvegardé (quota ou localStorage indisponible)", e);
  }
}

export function loadHistory(page) {
  try {
    return JSON.parse(localStorage.getItem(keyFor(page)) || "[]");
  } catch (e) {
    return [];
  }
}

export function clearHistory(page) {
  try {
    localStorage.removeItem(keyFor(page));
  } catch (e) {
    // ignore
  }
}

export function formatSavedAt(iso) {
  try {
    return new Date(iso).toLocaleString("fr-FR", { dateStyle: "short", timeStyle: "short" });
  } catch (e) {
    return iso;
  }
}
