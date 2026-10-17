"""Module « vulnérabilité » : à quel point un système est-il proche du seuil où une étincelle ordinaire suffit ?

Moteur générique (note « Vulnérabilité d'une contagion sociale », v3.1) : le cœur de calcul ne suppose rien
du domaine ; seuls le modèle de bruit (`bruits`) et le modèle d'observation (`observation`) changent d'un
domaine à l'autre.

Statut : module de recherche hors-ligne, branche `vulnerabilite-epidemies`. Il n'est branché ni sur l'API,
ni sur le rafraîchissement automatique, ni sur le site (cahier des charges, règle 4).
"""
