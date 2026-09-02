import { NavLink, Route, Routes } from "react-router-dom";
import Home from "./pages/Home.jsx";
import Demo from "./pages/Demo.jsx";
import Analyze from "./pages/Analyze.jsx";
import Hypotheses from "./pages/Hypotheses.jsx";
import TestH1 from "./pages/TestH1.jsx";
import TestH2 from "./pages/TestH2.jsx";
import TestH3 from "./pages/TestH3.jsx";
import Donnees from "./pages/Donnees.jsx";

export default function App() {
  return (
    <div className="app-shell">
      <header className="topbar">
        <NavLink to="/" className="brand">
          Hélios
        </NavLink>
        <nav>
          <NavLink to="/" end>
            Accueil
          </NavLink>
          <NavLink to="/demo">Démo</NavLink>
          <NavLink to="/hypotheses">Les 3 hypothèses</NavLink>
          <NavLink to="/tester-h1">Tester H1</NavLink>
          <NavLink to="/tester-h2">Tester H2</NavLink>
          <NavLink to="/tester-h3">Tester H3</NavLink>
          <NavLink to="/analyser">Analyser une série INSEE</NavLink>
          <NavLink to="/donnees">Données & méthode</NavLink>
        </nav>
      </header>

      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/demo" element={<Demo />} />
          <Route path="/hypotheses" element={<Hypotheses />} />
          <Route path="/tester-h1" element={<TestH1 />} />
          <Route path="/tester-h2" element={<TestH2 />} />
          <Route path="/tester-h3" element={<TestH3 />} />
          <Route path="/analyser" element={<Analyze />} />
          <Route path="/donnees" element={<Donnees />} />
        </Routes>
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
