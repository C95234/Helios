/**
 * Pédagogie d'INTERPRÉTATION des résultats par hypothèse -- distincte de la
 * pédagogie de MÉTHODE (data/methods.js, qui explique comment un chiffre est
 * calculé). Ici : que veut dire un verdict concret, qu'est-ce qu'il ne veut
 * PAS dire, et quelles sont les limites propres à la façon dont chaque
 * hypothèse est mise en œuvre dans Hélios.
 */
export const INTERPRETATION = {
  h1: {
    outcomes: {
      favorable: {
        title: "Quand un résultat va dans le sens de H1",
        text: "Le signal social est devenu statistiquement fébrile avant le signal officiel, ou seul. Ça veut dire : sur CE phénomène précis, l'attention/l'engagement en ligne a réagi plus tôt que les statistiques économiques officielles. Ça ne veut pas dire que H1 est vraie en général, ni que le signal social a « prédit » quoi que ce soit.",
      },
      against: {
        title: "Quand un résultat va à l'encontre de H1",
        text: "Le signal officiel est devenu significatif avant le signal social, ou seul. Sur ce cas, les statistiques officielles ont réagi aussi vite (ou plus vite) que l'attention en ligne -- ce qui n'est pas ce qu'anticipe H1. Un seul cas contraire n'invalide pas non plus H1 en général.",
      },
      neutral: {
        title: "Quand aucun signal ne devient significatif",
        text: "Souvent parce que le phénomène n'a pas produit une rupture assez forte pour l'indicateur choisi (ex. un choc localisé ne bouge pas une moyenne nationale), ou parce que la fenêtre temporelle ou la fenêtre glissante ne capture pas le bon moment. Ce n'est pas un résultat « négatif » pour H1 -- c'est un résultat qui ne dit rien.",
      },
    },
    limits: [
      "La comparaison de timing repose sur la date du PIC de l'indicateur (un maximum simple), pas sur un test statistique formel de décalage -- c'est un indice descriptif, explicitement présenté comme tel.",
      "Un seul phénomène ne prouve rien. Le protocole (§5.7) exige au moins 5 épisodes indépendants avant toute conclusion ferme -- et les phénomènes curatés ici sont choisis à la main (ruptures documentées), pas tirés au hasard, donc jamais un échantillon statistiquement représentatif.",
      "Certains phénomènes se chevauchent avec d'autres événements (ex. le confinement de 2020 coïncide avec un choc sanitaire ET économique) : un signal significatif ne peut pas être attribué avec certitude à un seul facteur.",
      "Tester ~40 signaux officiels par phénomène augmente le risque qu'un signal ressorte significatif par pur hasard (voir la page Données & méthode) -- c'est pourquoi le compte complet (X/Y) est toujours affiché, jamais un signal isolé.",
    ],
    commonMistakes: [
      "« H1 est confirmée » -- faux, même si plusieurs cas vont dans ce sens : aucun verdict ferme n'est émis avant 5 épisodes indépendants, et Hélios ne l'affiche jamais tel quel.",
      "« Le signal social a précédé l'officiel de X jours, donc il l'a causé » -- faux : un décalage temporel n'est pas une preuve de causalité. Les deux signaux peuvent réagir à un même choc sous-jacent à des vitesses différentes, sans lien causal entre eux.",
      "« Ce signal est significatif, donc il annonçait la bascule » -- faux : la significativité dit que la tendance dépasse ce que le hasard produirait sur CETTE période -- pas qu'elle a une valeur prédictive testée à l'avance.",
    ],
  },
  h2: {
    outcomes: {
      favorable: {
        title: "Quand le réseau réel se comporte différemment de la grille",
        text: "La topologie réelle (qui est voisin de qui) change le résultat du test par rapport à une grille artificielle avec les mêmes valeurs. Ça veut dire : la géographie compte pour ce test statistique précis -- pas que la France est « proche d'une bascule ».",
      },
      neutral: {
        title: "Quand les deux réseaux donnent le même verdict",
        text: "Sur ce cas, la topologie ne change pas le verdict de significativité (les deux réseaux sont significatifs, ou ni l'un ni l'autre). Ça n'invalide pas H2 en général -- ça veut dire que sur CETTE variable et cette période, l'effet de topologie n'est pas assez fort pour changer la conclusion finale, même s'il peut changer l'ampleur du résultat (l'écart-type du hasard, par exemple).",
      },
    },
    limits: [
      "La grille de contrôle replace les MÊMES valeurs dans un ordre arbitraire (l'ordre des codes postaux), pas selon une géographie fictive alternative construite exprès -- un choix qui tend à maximiser la différence observée, à interpréter avec prudence plutôt que comme une preuve définitive.",
      "Une seule variable (le taux de chômage départemental) est testée ici. H2 pourrait se comporter différemment avec un autre indicateur territorial -- rien ne garantit que la conclusion se généralise.",
      "Le test de tendance (l'indice de Moran augmente-t-il dans le temps ?) et le test de permutation sur le dernier trimestre (les voisins se ressemblent-ils, à cet instant, plus que le hasard ?) répondent à deux questions différentes -- ne pas les confondre : le premier est le signal précurseur au sens du §5.2, le second est une photographie ponctuelle.",
    ],
    commonMistakes: [
      "« L'indice de Moran est significatif, donc c'est un signal précurseur » -- faux : un indice de Moran élevé et stable indique une structure spatiale persistante (le chômage est structurellement différent au nord et au sud), pas une bascule en cours. Seule une HAUSSE de cet indice dans le temps est un signal précurseur -- c'est ce que teste la tendance, pas le simple constat qu'il est non nul.",
      "« Le réseau réel est toujours plus significatif que la grille, donc H2 est prouvée » -- faux : un seul indicateur, sur une seule période, ne constitue jamais une preuve -- voir §5.7.",
    ],
  },
  h3: {
    outcomes: {
      favorable: {
        title: "Quand la combinaison est plus inhabituelle que l'historique",
        text: "Le signal temporel national ET le signal spatial départemental, pris ensemble, sont plus extrêmes que la quasi-totalité des trimestres comparables des 26 dernières années. Ça veut dire : sur CE phénomène, les deux dimensions (quand, où) racontent une histoire cohérente de rupture -- pas que l'une des deux suffirait seule à le dire.",
      },
      neutral: {
        title: "Quand la combinaison reste dans la norme historique",
        text: "Même si l'un des deux signaux (temporel ou spatial) est notable isolément, leur combinaison ne se distingue pas franchement du reste de l'historique. Ça ne réfute pas H3 en général -- ça dit juste que sur ce cas, la fusion des deux indicateurs n'apporte pas un signal plus net que d'habitude.",
      },
    },
    limits: [
      "La p-value spatiale est un INSTANTANÉ (le trimestre le plus proche du phénomène), pas une vraie tendance spatiale comme le §5.6 le prévoit à l'origine -- adaptation nécessaire car le chômage départemental n'est publié que trimestriellement (3-4 points sur la fenêtre d'un phénomène, insuffisant pour une tendance).",
      "La loi nulle de la statistique combinée est calibrée par comparaison à l'historique réel 2000-2026 (bootstrap couplé par période), pas par génération de données de substitution synthétiques -- un choix méthodologique différent de H1/H2, documenté comme tel, pas une simple extension de leurs surrogates.",
      "Le signal national (confiance des ménages) et le signal spatial (chômage départemental) sont deux variables économiques différentes, à deux échelles géographiques différentes -- une corrélation entre elles est plausible mais n'est ni prouvée ni exclue par ce test.",
      "Un seul phénomène ne prouve rien -- voir §5.7 : au moins 5 épisodes indépendants avant toute conclusion ferme.",
    ],
    commonMistakes: [
      "« p_joint est petit, donc H3 est confirmée » -- faux : un seul cas isolé, jamais un verdict ferme avant 5 épisodes indépendants.",
      "« Le signal temporel et le signal spatial se sont produits ensemble, donc l'un a causé l'autre » -- faux : la méthode mesure une coïncidence statistique inhabituelle, pas un lien de causalité entre les deux dimensions.",
    ],
  },
};
