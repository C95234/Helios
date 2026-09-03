/**
 * Export du rapport complet -- cahier des charges §7 : "Export du rapport
 * complet (PDF/Markdown)" pour chaque hypothèse (H1, H2, H3).
 *
 * Markdown : généré côté client à partir des mêmes données que la page
 * (résultat + data/methods.js + data/interpretation.js), téléchargé
 * directement -- jamais un second exemplaire du contenu à maintenir.
 * PDF : impression du navigateur (voir le bloc @media print de
 * styles.css) plutôt qu'une bibliothèque dédiée -- le rendu LaTeX déjà à
 * l'écran (KaTeX) s'imprime fidèlement sans recalcul ni rasterisation.
 */
import { METHODS } from "./data/methods.js";
import { INTERPRETATION } from "./data/interpretation.js";

export function formatGeneratedAt() {
  return new Date().toLocaleString("fr-FR", { dateStyle: "long", timeStyle: "short" });
}

export function methodMarkdown(methodKey) {
  const m = METHODS[methodKey];
  if (!m) return "";
  const lines = [`### ${m.label}`, "", m.simple, "", `Formule : $$${m.formula}$$`, ""];
  if (m.derivationSteps) {
    for (const step of m.derivationSteps) {
      lines.push(step.tex ? `$$${step.tex}$$` : step.text, "");
    }
  } else if (m.detail) {
    lines.push(m.detail, "");
  }
  lines.push("Références :");
  for (const ref of m.references) lines.push(`- ${ref}`);
  lines.push("");
  return lines.join("\n");
}

export function interpretationMarkdown(hypothesis, outcome) {
  const data = INTERPRETATION[hypothesis];
  if (!data) return "";
  const lines = ["## Interprétation", ""];
  const info = data.outcomes?.[outcome];
  if (info) lines.push(`**${info.title}**`, "", info.text, "");
  if (data.limits) {
    lines.push("### Limites propres à cette mesure", "");
    for (const l of data.limits) lines.push(`- ${l}`);
    lines.push("");
  }
  if (data.commonMistakes) {
    lines.push("### Ce que ce résultat ne veut PAS dire", "");
    for (const mistake of data.commonMistakes) lines.push(`- ${mistake}`);
    lines.push("");
  }
  return lines.join("\n");
}

export function disclaimerMarkdown(nEpisodes, causalDisclaimer) {
  const lines = ["## Avertissement", "", causalDisclaimer, ""];
  if (nEpisodes < 5) {
    lines.push(
      `**Résultat préliminaire**, calculé sur ${nEpisodes} épisode${nEpisodes > 1 ? "s" : ""} -- à confirmer sur davantage de cas avant toute conclusion ferme (§5.7 : au moins 5 épisodes indépendants).`,
      ""
    );
  }
  return lines.join("\n");
}

export function downloadMarkdown(filename, content) {
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export function slugify(text) {
  return text
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");
}
