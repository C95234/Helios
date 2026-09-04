import { NavLink, Outlet } from "react-router-dom";

/**
 * En-tete/navigation/pied de page communs -- cahier des charges de
 * restructuration §3 : navigation persistante identique sur toutes les
 * pages, generee une seule fois plutot que redefinie par page.
 *
 * 7 sections primaires (§2) + 2 pages secondaires (historique personnel,
 * analyse libre) -- presentes partout mais visuellement distinctes,
 * jamais dans la navigation principale a 7 entrees.
 */
export default function Layout() {
  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar-main-row">
          <NavLink to="/" className="brand">
            Hélios
          </NavLink>
          <nav>
            <NavLink to="/" end>
              Accueil
            </NavLink>
            <NavLink to="/comprendre">Comprendre</NavLink>
            <NavLink to="/resultats">Résultats</NavLink>
            <NavLink to="/methode">Méthode</NavLink>
            <NavLink to="/journal">Journal de recherche</NavLink>
            <NavLink to="/bilan">Bilan</NavLink>
            <NavLink to="/roman">Le roman</NavLink>
            <NavLink to="/garde-fous">Garde-fous</NavLink>
          </nav>
        </div>
        <nav className="topbar-secondary">
          <NavLink to="/mon-historique">Mon historique</NavLink>
          <NavLink to="/analyser">Analyser une série</NavLink>
        </nav>
      </header>

      <main>
        <Outlet />
      </main>

      <footer className="site-footer">
        <p>
          Hélios est un outil de recherche et de vulgarisation. Il ne surveille ni ne profile personne :
          il travaille exclusivement sur des données agrégées.
        </p>
      </footer>
    </div>
  );
}
