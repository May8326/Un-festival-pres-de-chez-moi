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
