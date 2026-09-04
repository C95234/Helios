import produitMd from "../data/cahierDesCharges/cahier-des-charges-helios.md?raw";
import restructurationMd from "../data/cahierDesCharges/cahier-des-charges-restructuration.md?raw";

export default function CahierDesCharges() {
  return (
    <div className="page page-cahier-des-charges">
      <h1>Cahier des charges</h1>
      <p className="lede">
        Page technique, destinée aux développeurs et à toute relecture du projet : les deux documents de
        cadrage tels qu'ils ont servi de brief, reproduits sans modification.
      </p>

      <section>
        <h2>Cahier des charges produit</h2>
        <pre className="cahier-des-charges-text">{produitMd}</pre>
      </section>

      <section>
        <h2>Cahier des charges de restructuration du site</h2>
        <pre className="cahier-des-charges-text">{restructurationMd}</pre>
      </section>
    </div>
  );
}
