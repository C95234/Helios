/**
 * Positionnement scientifique honnête -- cahier des charges Helios §1bis.
 * Contenu centralisé : la home et le Bilan en portent chacun une
 * reformulation courte qui renvoie ici, jamais une redite complète
 * (règle de non-duplication, restructuration §3).
 */
export const POSITIONING_SHORT =
  "Hélios n'invente ni nouvelle théorie ni nouvelle méthode : chaque outil utilisé (signaux précurseurs, criticité, synchronisation, indice de Moran) est déjà établi dans la littérature. Sa contribution réelle tient à quatre choses -- réplication sur un domaine jamais testé, publication de résultats négatifs, un outil réutilisable, de la médiation scientifique -- jamais une « découverte ».";

export const CONTRIBUTIONS = [
  {
    title: "De la réplication",
    text: "Les théories mobilisées (signaux précurseurs, criticité, synchronisation) ont été testées sur une poignée de domaines (écologie, épidémiologie, finance, neurosciences). Personne n'avait testé leur généralisation à des données socio-territoriales françaises combinant Insee et réseaux sociaux ouverts. La réplication sur un nouveau domaine est une contribution scientifique réelle, quoique modeste -- c'est l'écrasante majorité du travail scientifique publié chaque année, loin du mythe de la découverte spectaculaire.",
  },
  {
    title: "Des résultats négatifs documentés",
    text: "La littérature publiée est structurellement biaisée vers les résultats positifs (biais de publication). Un résultat négatif obtenu avec un protocole rigoureux et publié tel quel (voir le Bilan) corrige, à très petite échelle, ce biais.",
  },
  {
    title: "Un outil réutilisable et reproductible",
    text: "Le pipeline (connecteurs de données, tests statistiques calibrés, garde-fous, scripts versionnés) reste utilisable par quiconque voudrait tester un nouvel épisode, sans dépendre de qui a testé quoi en premier.",
  },
  {
    title: "De la médiation scientifique",
    text: "Le Journal de recherche, le cours de statistiques et la démo interactive font circuler des méthodes réelles (signaux précurseurs, tests par permutation, indice de Moran) vers un public qui n'y aurait pas accès autrement.",
  },
];

export const NOT_A_DISCOVERY =
  "Ce que ce projet n'apporte pas : une nouvelle théorie, une nouvelle méthode mathématique, ou une découverte au sens où on l'entend pour un prix scientifique majeur. Le mot « découverte » n'est jamais utilisé pour décrire un résultat du projet -- ni sur le site, ni dans les rapports générés, ni dans le Journal de recherche.";
