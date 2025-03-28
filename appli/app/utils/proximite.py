from ..models.database import Commune
from geopy import distance
def proximite(nom_ville, dist)->list:
    coordonees_ville = (float((Commune.latitude).filter(Commune.nom_commune.ilike("%"+nom_ville+"%"))), float((Commune.longitude).filter(Commune.nom_commune.ilike("%"+nom_ville+"%"))))
    liste_villes = []
    for x in Commune.nom_commune :
        coordonees_x=(float((Commune.latitude).filter(Commune.nom_commune.ilike("%"+x+"%"))), float((Commune.longitude).filter(Commune.nom_commune.ilike("%"+x+"%"))))
        if distance.distance(coordonees_ville, coordonees_x).km < dist :
            liste_villes.append(x)
        else:
            pass
    return liste_villes

""" 

from geopy.distance import geodesic
from app.models.database import Commune

def proximite(lieu, distance_max):
"""
 #   Trouve les communes proches d'un lieu donné dans un rayon spécifié.
#
#   :param lieu: Nom de la commune de départ.
#  :param distance_max: Distance maximale en kilomètres.
# :return: Liste des GeoPoints des communes dans le rayon spécifié.
"""
    try:
        # Récupérer les coordonnées de la commune de départ
        commune_depart = Commune.query.filter(Commune.nom_commune.ilike(f"%{lieu}%")).first()
        if not commune_depart:
            return []

        coord_depart = (commune_depart.geocodage_latitude_commune, commune_depart.geocodage_longitude_commune)

        # Trouver toutes les communes
        communes = Commune.query.all()
        communes_proches = []

        for commune in communes:
            coord_commune = (commune.geocodage_latitude_commune, commune.geocodage_longitude_commune)
            distance = geodesic(coord_depart, coord_commune).kilometers

            if distance <= float(distance_max):
                communes_proches.append(commune.GeoPoint_commune)

        return communes_proches

    except Exception as e:
        print(f"Erreur dans la fonction proximite : {e}")
        return []

"""