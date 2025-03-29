from ..models.database import Commune, Festival, MonumentHistorique, LieuFestival
from geopy.distance import geodesic
from sqlalchemy import func
from .cache import cache_result

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

        # print(f"Communes proches trouvées : {communes_proches}")
        return communes_proches

    except Exception as e:
        print(f"Erreur dans la fonction proximite : {e}")
        return []

@cache_result(timeout=600)  # Cache pour 10 minutes
def proximite_geo(nom_ville, dist):
    """
    Trouve les éléments (festivals et monuments) proches d'une ville donnée et renvoie leurs coordonnées.
    Les résultats sont mis en cache pour améliorer les performances.

    :param nom_ville: Nom de la commune de départ.
    :param dist: Distance maximale en kilomètres.
    :return: Dictionnaire avec les festivals et monuments proches avec leurs coordonnées.
    """
    try:
        # Récupérer les coordonnées de la commune de départ
        commune_depart = Commune.query.filter(Commune.nom_commune.like(f"{nom_ville}")).first()
        if not commune_depart:
            print(f"Aucune commune trouvée pour le nom : {nom_ville}")
            return {"festivals": [], "monuments": []}

        coord_depart = (commune_depart.geocodage_latitude_commune, commune_depart.geocodage_longitude_commune)
        
        # Listes pour stocker les éléments proches
        festivals_proches = []
        monuments_proches = []
        
        # Trouver les festivals proches
        festivals = Festival.query.join(LieuFestival).filter(LieuFestival.latitude_festival.isnot(None), 
                                                             LieuFestival.longitude_festival.isnot(None)).all()
        
        for festival in festivals:
            if festival.lieu and festival.lieu.latitude_festival and festival.lieu.longitude_festival:
                coord_festival = (festival.lieu.latitude_festival, festival.lieu.longitude_festival)
                distance = geodesic(coord_depart, coord_festival).kilometers
                
                if distance < float(dist):
                    festivals_proches.append({
                        "id": festival.id_festival,
                        "nom": festival.nom_festival,
                        "lat": festival.lieu.latitude_festival,
                        "lon": festival.lieu.longitude_festival,
                        "type": "festival",
                        "distance": round(distance, 2)
                    })
        
        # Trouver les monuments proches
        monuments = MonumentHistorique.query.filter(MonumentHistorique.latitude_monument_historique.isnot(None),
                                                    MonumentHistorique.longitude_monument_historique.isnot(None)).all()
        
        for monument in monuments:
            if monument.latitude_monument_historique and monument.longitude_monument_historique:
                coord_monument = (monument.latitude_monument_historique, monument.longitude_monument_historique)
                distance = geodesic(coord_depart, coord_monument).kilometers
                
                if distance < float(dist):
                    monuments_proches.append({
                        "id": monument.id_monument_historique,
                        "nom": monument.nom_monument,
                        "lat": monument.latitude_monument_historique,
                        "lon": monument.longitude_monument_historique,
                        "type": "monument",
                        "distance": round(distance, 2)
                    })
        
        return {
            "centre": {
                "nom": commune_depart.nom_commune,
                "lat": commune_depart.geocodage_latitude_commune,
                "lon": commune_depart.geocodage_longitude_commune
            },
            "festivals": festivals_proches,
            "monuments": monuments_proches
        }
        
    except Exception as e:
        print(f"Erreur dans la fonction proximite_geo : {e}")
        return {"festivals": [], "monuments": []}