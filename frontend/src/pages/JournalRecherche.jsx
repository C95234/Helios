import { useState } from "react";
import { Link } from "react-router-dom";
import Math from "../components/Math.jsx";
import { TextWithMath } from "../components/MethodNote.jsx";
import { JOURNAL_SECTIONS, PROGRESS_CHECKLIST, JOURNAL_REFERENCES } from "../data/journal.js";

function JournalSection({ section }) {
  const [expertMode, setExpertMode] = useState(false);

  return (
    <div className="journal-section">
      <div className="result-card-header">
        <h2>{section.title}</h2>
        <button type="button" className="mode-toggle" onClick={() => setExpertMode((v) => !v)} aria-pressed={expertMode}>
          {expertMode ? "Mode simplifié" : "Mode expert"}
        </button>
      </div>

      {!expertMode && <p>{section.simple}</p>}

      {expertMode && (
        <div className="journal-expert-block">
          {section.expertBlocks.map((block, i) =>
            block.tex ? (
              <Math key={i} tex={block.tex} block={block.block} />
            ) : (
              <p key={i}>
                <TextWithMath text={block.text} />
              </p>
            )
          )}
        </div>
      )}
    </div>
  );
}

export default function JournalRecherche() {
  return (
    <div className="page page-journal">
      <h1>Journal de recherche</h1>
      <p className="lede">
        Tout ce qui a été établi mathématiquement pendant la conception de Hélios -- y compris un
        raisonnement initial corrigé par le calcul -- est visible ici plutôt que réservé à un document
        interne. Ce travail a précédé et motivé l'hypothèse H3 (§5.6) : avant de construire un indicateur
        combinant signal temporel et signal spatial, il fallait vérifier que ces deux signaux ne sont pas
        simplement l'un une version retardée de l'autre.
      </p>

      {JOURNAL_SECTIONS.map((section) => (
        <JournalSection key={section.id} section={section} />
      ))}

      <section className="journal-section">
        <h2>8. État d'avancement du protocole de généralisation</h2>
        <p className="text-muted">
          Ce que ce travail couvre aujourd'hui, et ce qu'il reste à faire avant de pouvoir généraliser ces
          résultats aux données réelles visées par H3.
        </p>
        <ul className="journal-checklist">
          {PROGRESS_CHECKLIST.map((item, i) => (
            <li key={i} className={item.done ? "journal-check-done" : "journal-check-pending"}>
              <span className="journal-check-box">{item.done ? "✓" : "—"}</span>
              {item.label}
            </li>
          ))}
        </ul>
      </section>

      <section className="journal-section">
        <h2>Ce que ça implique pour H3</h2>
        <p>
          La valeur ajoutée d'un indicateur joint (§5.6) dépend de l'existence de régimes où les deux
          signaux sont réellement complémentaires plutôt qu'un simple décalage temporel l'un de l'autre. En
          simulation, sur toutes les configurations testées (anneau, réseau irrégulier, réseau réel des
          départements, deux régimes de couplage), le signal temporel précède le signal spatial dans une
          nette majorité des cas (75% à 90% selon la configuration) -- jamais dans 100% des cas. Sur les 3
          seuls épisodes historiques réels disponibles, l'exception se manifeste concrètement : 2 précèdent
          par le temporel, 1 (les gilets jaunes de 2018) par le spatial. Cela n'invalide pas H3, mais en
          précise le sens attendu -- une tendance dominante, pas une règle absolue.{" "}
          <Link to="/tester-h3">Voir le test H3 sur des phénomènes réels</Link>.
        </p>
      </section>

      <section className="journal-section">
        <h2>Références citées dans ce journal</h2>
        <ol className="bibliography-list">
          {JOURNAL_REFERENCES.map((ref, i) => (
            <li key={i}>{ref}</li>
          ))}
        </ol>
      </section>
    </div>
  );
}
