import { Link } from "react-router-dom";
import { CONTRIBUTIONS, NOT_A_DISCOVERY, POSITIONING_SHORT } from "../data/positionnement.js";

export default function Positionnement() {
  return (
    <div className="page page-positionnement">
      <h1>Ce que le projet apporte à la recherche</h1>
      <p className="lede">{POSITIONING_SHORT}</p>

      <section>
        <h2>Cadrage honnête</h2>
        <p>
          Chaque piste explorée pendant la conception d'Hélios (signaux précurseurs, criticité auto-organisée,
          contrôle de synchronisation) s'est révélée, en vérifiant la littérature, appartenir à un champ de
          recherche mature et déjà actif -- parfois depuis plusieurs décennies. Ce n'est pas un accident : le{" "}
          <Link to="/roman">roman</Link> dont s'inspire le projet mobilise lui-même de vraies théories établies,
          donc toute piste qu'il évoque renvoie nécessairement à un champ existant. Le positionnement ci-dessous
          en tient compte, durablement -- pas seulement pour une conversation de conception.
        </p>
      </section>

      <section>
        <h2>Dans l'ordre d'importance</h2>
        <div className="card-list">
          {CONTRIBUTIONS.map((c, i) => (
            <div className="bilan-card" key={c.title}>
              <h3>
                {i + 1}. {c.title}
              </h3>
              <p>{c.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2>Ce que ce projet n'apporte pas</h2>
        <p>{NOT_A_DISCOVERY}</p>
      </section>

      <p className="text-muted">
        Voir aussi <Link to="/bilan">le Bilan</Link> pour la synthèse points forts / points faibles, et{" "}
        <Link to="/resultats">Résultats</Link> pour le détail par hypothèse.
      </p>
    </div>
  );
}
