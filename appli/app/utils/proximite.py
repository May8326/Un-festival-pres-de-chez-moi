from ..models.database import Commune
from geopy.distance import geodesic

def proximite(nom_ville, dist):
    """
    Trouve les communes proches d'une ville donnée dans un rayon spécifié.

    :param nom_ville: Nom de la commune de départ.
    :param dist: Distance maximale en kilomètres.
    :return: Liste des noms des communes dans le rayon spécifié.
    """
    try:
        # Récupérer les coordonnées de la commune de départ
        commune_depart = Commune.query.filter(Commune.nom_commune.like(f"{nom_ville}")).first()
        if not commune_depart:
            print(f"Aucune commune trouvée pour le nom : {nom_ville}")
            return []

        coord_depart = (commune_depart.geocodage_latitude_commune, commune_depart.geocodage_longitude_commune)
        print(f"Coordonnées de la commune de départ ({nom_ville}) : {coord_depart}")

        # Trouver toutes les communes
        communes = Commune.query.all()
        communes_proches = []

        for commune in communes:
            coord_commune = (commune.geocodage_latitude_commune, commune.geocodage_longitude_commune)
    
            distance = geodesic(coord_depart, coord_commune)
            # print(commune.nom_commune, distance)
            if distance < float(dist):
                communes_proches.append(commune.nom_commune)

        print(f"Communes proches trouvées : {communes_proches}")
        return communes_proches

    except Exception as e:
        print(f"Erreur dans la fonction proximite : {e}")
        return []