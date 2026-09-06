import { Link } from "react-router-dom";

const VERDICT_LABEL = {
  favorable: "Favorable",
  against: "Va à l'encontre",
  neutral: "Non concluant",
  preliminary: "Préliminaire",
  simulation: "Non testée empiriquement",
};

/**
 * Gabarit obligatoire pour toute page de résultat (H1-H4, futur H5) --
 * cahier des charges de restructuration §4. Le contenu de démonstration
 * mathématique n'est JAMAIS reproduit ici : uniquement un lien vers la
 * section Méthode (§2, règle de non-duplication).
 */
export default function ResultPageTemplate({
  code,
  title,
  catchyTitle,
  domain,
  verdict,
  nEpisodes,
  episodesLabel,
  summary,
  postulateSimple,
  postulateExpert,
  resultText,
  methodLink,
  limits,
  journalLink,
  showLiveSection = true,
  children,
}) {
  return (
    <div className={`page page-resultat page-resultat-${code.toLowerCase()}`}>
      {domain && (
        <p className="breadcrumb">
          <Link to={domain.to}>{domain.name}</Link> <span aria-hidden="true">›</span> {title}
        </p>
      )}

      <div className={`verdict-banner verdict-banner--${verdict}`}>
        <span className="verdict-banner-code">{code}</span>
        <span className="verdict-banner-label">{VERDICT_LABEL[verdict]}</span>
        <span className="verdict-banner-episodes">
          {episodesLabel
            ? episodesLabel
            : verdict === "simulation"
              ? "simulation, jamais un verdict statistique"
              : `${nEpisodes} épisode${nEpisodes > 1 ? "s" : ""} testé${nEpisodes > 1 ? "s" : ""}`}
        </span>
      </div>

      <h1>{catchyTitle ?? title}</h1>
      {catchyTitle && <p className="technical-subtitle">{title}</p>}
      <p className="lede">{summary}</p>

      <section>
        <h2>Le postulat</h2>
        <p>{postulateSimple}</p>
        {postulateExpert && <p className="text-muted">{postulateExpert}</p>}
      </section>

      <section>
        <h2>Le résultat obtenu</h2>
        {resultText}
        {methodLink && (
          <p>
            <Link to={methodLink.to}>{methodLink.label} →</Link>
          </p>
        )}
      </section>

      {limits?.length > 0 && (
        <section>
          <h2>Limites</h2>
          <ul>
            {limits.map((l, i) => (
              <li key={i}>{l}</li>
            ))}
          </ul>
        </section>
      )}

      {journalLink && (
        <p className="text-muted">
          <Link to={journalLink.to}>{journalLink.label} →</Link>
        </p>
      )}

      {showLiveSection && (
        <>
          <hr className="divider" />
          <h2>Tester ce résultat en direct</h2>
        </>
      )}
      {children}
    </div>
  );
}
