const OUTCOME_LABEL = { favorable: "Favorable", against: "Contre", neutral: "Neutre", na: "Non calculable" };

/** Badge compact favorable/contre/neutre/non-calculable, utilisé dans les
 * tableaux de résultats -- extrait pour être partagé entre les pages Résultats et Bilan. */
export default function VerdictBadge({ outcome }) {
  return <span className={`verdict-badge verdict-badge--${outcome}`}>{OUTCOME_LABEL[outcome]}</span>;
}
