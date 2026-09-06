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

      <section>
        <h2>Deux contributions concrètes</h2>
        <p>
          Le pilier « un outil de recherche réutilisable » ci-dessus ne reste pas une affirmation abstraite :
          deux preuves concrètes, de nature différente.
        </p>
        <div className="card-list">
          <div className="bilan-card">
            <h3>
              <Link to="/positionnement/ewstools">Contribution à ewstools (outil open source)</Link>
            </h3>
            <p>
              Indicateur spatial (indice de Moran) et combinaison d'indicateurs corrélés (méthode empirique de
              Brown), absents du paquet de référence pour les signaux précurseurs. Pull request soumise,
              en attente de revue -- jamais présentée comme fusionnée avant de l'être réellement.
            </p>
          </div>
          <div className="bilan-card">
            <h3>
              <Link to="/positionnement/hopfieldkit">hopfieldkit -- paquet Python</Link>
            </h3>
            <p>
              Apprentissage hebbien, démonstration de convergence, théorie de la capacité, diagnostics des
              limites connues, et un second mode d'apprentissage par descente de gradient comparé
              empiriquement à la règle de Hebb (Gardner 1988). Code complet et testé, développé en paquet
              autonome faute d'outil de référence équivalent existant pour les réseaux de Hopfield en Python.
            </p>
          </div>
        </div>
      </section>

      <p className="text-muted">
        Voir aussi <Link to="/bilan">le Bilan</Link> pour la synthèse points forts / points faibles, et{" "}
        <Link to="/resultats">Résultats</Link> pour le détail par hypothèse.
      </p>
    </div>
  );
}
