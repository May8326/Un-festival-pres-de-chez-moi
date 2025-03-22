# Nom des variables à utiliser

| action | nom de la variable |
| --- | --- |

# Noms des tables dans la base de donnée

| Classe                              | Table                           | Colonnes                                                                                   |
|-------------------------------------|---------------------------------|--------------------------------------------------------------------------------------------|
| -                                   | `festival_monuments_geopoint`   | `id_monument_historique`, `id_festival`, `distance`                                         |
| `Commune`                           | `correspondance_communes`       | `id_commune`, `code_commune_INSEE`, `code_postal`, `latitude`, `longitude`, `nom_commune`, `nom_commune_complet`, `code_departement`, `nom_departement`, `code_region`, `nom_region` |
| `Festival`                          | `titre_festival_data_gouv`      | `id_festival`, `nom_festival`                                                              |
| `ContactFestival`                   | `contact_festival`              | `id_festival`, `site_internet_festival`, `adresse_mail_festival`                           |
| `DateFestival`                      | `date_festival`                 | `id_festival`, `annee_creation_festival`, `periode_principale_deroulement_festival`         |
| `LieuFestival`                      | `lieu_festival`                 | `id_festival`, `code_insee_commune_festival`, `latitude_festival`, `longitude_festival`     |
| `TypeFestival`                      | `type_festival`                 | `id_festival`, `discipline_dominante_festival`                                              |
| `MonumentHistorique`                | `lieu_monument_historique`      | `id_monument_historique`, `code_insee_edifice_lors_de_protection`, `latitude_monument_historique`, `longitude_monument_historique` |
| `AspectJuridiqueMonumentHistorique` | `aspect_juridique_monument_historique` | `id_monument_historique`, `statut_juridique_edifice`                                    |