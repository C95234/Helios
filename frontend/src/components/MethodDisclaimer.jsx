/** Clause de non-interprétation causale + garde-fou du nombre d'épisodes (§9.12, §7). */
export default function MethodDisclaimer({ nEpisodes = 1 }) {
  return (
    <div className="disclaimer">
      <p>
        <strong>À lire avant d'interpréter ce résultat :</strong> un signal précurseur indique une perte
        de résilience statistique, pas une prédiction certaine ni une cause identifiée.
      </p>
      {nEpisodes < 5 && (
        <p className="disclaimer-preliminary">
          Résultat préliminaire, calculé sur {nEpisodes} épisode{nEpisodes > 1 ? "s" : ""} — à confirmer sur
          davantage de cas avant toute conclusion ferme.
        </p>
      )}
    </div>
  );
}
