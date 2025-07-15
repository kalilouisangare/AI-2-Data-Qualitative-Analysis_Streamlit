Exemple Concret
Imaginons que votre texte transcrit soit le suivant :

"L'accueil était bon, je suis très satisfait du projet. Mon collègue est aussi content. Les résultats apportent beaucoup de joie à la communauté. Cependant, le transport était difficile. Le déplacement vers le site a pris du temps, mais ce n'est pas la faute du projet."

Sans regroupement, le nuage de mots montrerait "projet", "satisfait", "content", "joie", "transport", "déplacement" comme des mots distincts de taille similaire.
Maintenant, utilisons le regroupement. Dans la zone de texte "Regroupement de synonymes", vous pourriez écrire :
Generated code {
satisfaction: satisfait, content, joie, heureux
déplacement: transport, déplacement }

Ce qui se passe en arrière-plan (dans le code) :

1.Lecture des règles : Le code lit vos règles et crée une "carte de remplacement". Il sait maintenant que chaque fois qu'il verra "satisfait", "content" ou "joie", il devra le remplacer par "satisfaction". De même pour "transport" qui deviendra "déplacement".

2.Remplacement : Le code parcourt votre texte original et applique ces remplacements. Le texte devient :
"L'accueil était bon, je suis très satisfaction du projet. Mon collègue est aussi satisfaction. Les résultats apportent beaucoup de satisfaction à la communauté. Cependant, le déplacement était difficile. Le déplacement vers le site a pris du temps, mais ce n'est pas la faute du projet."

3.Lemmatisation : Ensuite, le code applique la lemmatisation (comme d'habitude). Par exemple, "résultats" deviendrait "résultat".

4.Génération du nuage de mots : Le nuage est créé à partir de ce texte transformé.
Résultat final dans le nuage de mots :

-Le mot "satisfaction" apparaîtra très gros, car il compte pour 3 occurrences.
-Le mot "déplacement" apparaîtra plus gros, car il compte pour 2 occurrences.
-Le mot "projet" apparaîtra aussi, avec ses 2 occurrences.

Vous avez transformé une simple analyse de fréquence de mots en une analyse de fréquence de concepts, ce qui est beaucoup plus puissant pour l'analyse qualitative.

Conseil : N'hésitez pas à utiliser des formes de base pour vos mots cibles (ex: "satisfaction" plutôt que "satisfait") car la lemmatisation qui suit aidera à regrouper les variantes (comme "satisfaits", "satisfaire", etc.) sous cette même racine.