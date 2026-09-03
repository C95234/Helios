import { downloadMarkdown } from "../report.js";

/**
 * Export du rapport complet -- §7 : PDF (impression navigateur, voir le
 * bloc @media print de styles.css) et Markdown (généré à la demande,
 * jamais stocké).
 */
export default function ReportExport({ buildMarkdown, filenameBase }) {
  return (
    <div className="report-export">
      <button type="button" className="cta secondary" onClick={() => downloadMarkdown(`${filenameBase}.md`, buildMarkdown())}>
        Télécharger le rapport (Markdown)
      </button>
      <button type="button" className="cta secondary" onClick={() => window.print()}>
        Exporter en PDF
      </button>
    </div>
  );
}
