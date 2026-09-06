/** Badge de statut pour une contribution externe (PR / paquet publié) --
 * distinct de VerdictBadge (favorable/against/neutral) : ici l'échelle est
 * un statut administratif (soumis / en attente / fusionné / non retenu, ou
 * code complet / publié), pas un verdict de test statistique. */
export default function StatusBadge({ label, tone = "neutral" }) {
  return <span className={`status-badge status-badge--${tone}`}>{label}</span>;
}
