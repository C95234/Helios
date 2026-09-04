import { BIBLIOGRAPHY } from "../data/methods.js";

export default function Bibliographie() {
  return (
    <div className="page page-bibliographie">
      <h1>Bibliographie complète</h1>
      <p className="lede">
        Toute affirmation théorique du projet est accompagnée de sa référence exacte dans l'interface (mode
        expert), pas seulement d'un nom d'auteur.
      </p>
      <ol className="bibliography-list">
        {BIBLIOGRAPHY.map((ref, i) => (
          <li key={i}>{ref}</li>
        ))}
      </ol>
    </div>
  );
}
