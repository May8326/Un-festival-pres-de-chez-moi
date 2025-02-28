# Requête wikidata

Requête effectuée pour récupérer les nombres de followers des festivals français lorsqu'ils sont renseignés, ainsi que les sites internet des festivals.

Celle-ci devait inclure le nombre de participants aux festivals, mais cette donnée n'étant jamais renseignée ne pourra pas être utilisée.

```sparql
# Cette requête permet de récupérer tous les festivals français enregistrés dans wikidata, 
# ainsi que le nombre de participants et de followers sur les réseaux sociaux (tous réseaux confondus)
# quand ils sont renseignés.


# En têtes de l'output et regroupement des colonnes par festival
# (pour supprimer le bruit des festivals enregistrés plusieurs fois pour chaque année où ils ont eu lieu)
SELECT 
  ?festival 
  ?festivalLabel 
  (SAMPLE(?participants) AS ?participants) 
  (SAMPLE(?website) AS ?website) 
  (SAMPLE(?followers) AS ?followers) 

WHERE {
  # Sélectionne toutes les entités de nature ou de sous-classe "festival" situés en France
  ?festival wdt:P31/wdt:P279* wd:Q132241.
  ?festival wdt:P17 wd:Q142.
  
  # Recherche de la date de fin des festivals pour pouvoir les filtrer
  # et harmoniser les résultats avec la bdd d'origine
  OPTIONAL { ?festival wdt:P582 ?endTime. }
  
  # Exclut les festivals dont la date de fin renseignée est antérieure au 1ᵉʳ janvier 2019
  FILTER(!bound(?endTime) || ?endTime >= "2019-01-01T00:00:00Z"^^xsd:dateTime)
    
  # Récupère le nombre de participants aux festivals quand il est renseigné
  # (laissé car on aurait aimé le trouvé, mais n'est apparemment pas renseigné sur wikidata)
  OPTIONAL {
    ?festival wdt:56512863 ?participants.
  }
  
  # Récupère le site officiel du festival quand il est renseigné
  OPTIONAL { ?festival wdt:P856 ?website. }
  
  # Récupère le nombre de followers sur les réseaux sociaux quand il est renseigné
  OPTIONAL { ?festival wdt:P8687 ?followers. }
  
  # Pour éviter d'avoir des festivalLabel avec l'id wikidata du festival quand wikidata ne le trouve pas,
  # lui indique de chercher d'abord en français, puis en anglais, puis de détecter lui-même la langue la plus appropriée.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "fr, en,[AUTO_LANGUAGE]". }
}

GROUP BY ?festival ?festivalLabel
```
