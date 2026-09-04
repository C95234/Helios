import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import Home from "./pages/Home.jsx";
import Positionnement from "./pages/Positionnement.jsx";
import Comprendre from "./pages/Comprendre.jsx";
import Resultats from "./pages/Resultats.jsx";
import H1Result from "./pages/resultats/H1Result.jsx";
import H2Result from "./pages/resultats/H2Result.jsx";
import H3Result from "./pages/resultats/H3Result.jsx";
import H4Result from "./pages/resultats/H4Result.jsx";
import H5Result from "./pages/resultats/H5Result.jsx";
import FusionResult from "./pages/resultats/FusionResult.jsx";
import Methode from "./pages/Methode.jsx";
import CoursStatistiques from "./pages/CoursStatistiques.jsx";
import SuitesRalentissement from "./pages/SuitesRalentissement.jsx";
import Bibliographie from "./pages/Bibliographie.jsx";
import JournalRecherche from "./pages/JournalRecherche.jsx";
import Bilan from "./pages/Bilan.jsx";
import Roman from "./pages/Roman.jsx";
import GardeFous from "./pages/GardeFous.jsx";
import MonHistorique from "./pages/MonHistorique.jsx";
import Analyze from "./pages/Analyze.jsx";
import CahierDesCharges from "./pages/CahierDesCharges.jsx";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/positionnement" element={<Positionnement />} />
        <Route path="/comprendre" element={<Comprendre />} />
        <Route path="/resultats" element={<Resultats />} />
        <Route path="/resultats/h1" element={<H1Result />} />
        <Route path="/resultats/h2" element={<H2Result />} />
        <Route path="/resultats/h3" element={<H3Result />} />
        <Route path="/resultats/h4" element={<H4Result />} />
        <Route path="/resultats/h5" element={<H5Result />} />
        <Route path="/resultats/fusion" element={<FusionResult />} />
        <Route path="/methode" element={<Methode />} />
        <Route path="/methode/cours-statistiques" element={<CoursStatistiques />} />
        <Route path="/methode/suites-ralentissement-critique" element={<SuitesRalentissement />} />
        <Route path="/methode/bibliographie" element={<Bibliographie />} />
        <Route path="/journal" element={<JournalRecherche />} />
        <Route path="/bilan" element={<Bilan />} />
        <Route path="/roman" element={<Roman />} />
        <Route path="/garde-fous" element={<GardeFous />} />
        <Route path="/mon-historique" element={<MonHistorique />} />
        <Route path="/analyser" element={<Analyze />} />
        <Route path="/dev/cahier-des-charges" element={<CahierDesCharges />} />

        {/* Redirections depuis les anciennes routes -- ne jamais casser un lien déjà partagé */}
        <Route path="/demo" element={<Navigate to="/comprendre" replace />} />
        <Route path="/hypotheses" element={<Navigate to="/resultats" replace />} />
        <Route path="/tester-h1" element={<Navigate to="/resultats/h1" replace />} />
        <Route path="/tester-h2" element={<Navigate to="/resultats/h2" replace />} />
        <Route path="/tester-h3" element={<Navigate to="/resultats/h3" replace />} />
        <Route path="/tester-h4" element={<Navigate to="/resultats/h4" replace />} />
        <Route path="/journal-recherche" element={<Navigate to="/journal" replace />} />
        <Route path="/conclusions" element={<Navigate to="/bilan" replace />} />
        <Route path="/donnees" element={<Navigate to="/methode" replace />} />
      </Route>
    </Routes>
  );
}
