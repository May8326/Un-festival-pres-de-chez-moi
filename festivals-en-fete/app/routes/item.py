from flask import render_template, abort
from app.app import app, db
from ..models.database import Festival, Commune, MonumentHistorique

# Définition de la route pour afficher les détails d'un item (festival, commune ou monument)
@app.route("/festivalchezmoi/item/<item_type>/<int:item_id>", methods=["GET"])
def item_details(item_type, item_id):
    """
    Affiche les informations détaillées d'un item (festival, commune ou monument).
    """
    item = None  # Variable pour stocker l'item récupéré
    item_details = {}  # Dictionnaire pour stocker les détails de l'item

    try:
        # Vérifie le type d'item et récupère les données correspondantes
        if item_type == "festival":
            # Récupération d'un festival par son ID
            item = db.session.query(Festival).get(item_id)
            if item:
                # Construction des détails du festival
                item_details = {
                    "Nom": item.nom_festival,
                    "Lieu": item.lieu.commune.nom_commune if item.lieu and item.lieu.commune else "Non renseigné",
                    "Envergure": item.lieu.envergure_territoriale_festival if item.lieu else "Non renseigné",
                    "Adresse": item.lieu.adresse_postale_festival if item.lieu else "Non renseigné",
                    "Ville": item.lieu.commune.nom_commune if item.lieu and item.lieu.commune else "Non renseigné",
                    "Dates": item.dates.periode_principale_deroulement_festival if item.dates else "Non renseigné",
                    "Année de création": item.dates.annee_creation_festival if item.dates else "Non renseigné",
                    "Décennie de création": item.dates.decennie_creation_festival if item.dates else "Non renseigné",
                    "Type": item.type.discipline_dominante_festival if item.type else "Non renseigné",
                    # Sous-catégories du festival
                    "Sous-catégories": {
                        "Spectacle vivant": item.type.sous_categorie_spectacle_vivant if item.type else None,
                        "Musique": item.type.sous_categorie_musique if item.type else None,
                        "Cinéma et audiovisuel": item.type.sous_categorie_cinema_et_audiovisuel if item.type else None,
                        "Arts visuels et numériques": item.type.sous_categorie_arts_visuels_et_numeriques if item.type else None,
                        "Livre et littérature": item.type.sous_categorie_livre_et_litterature if item.type else None
                    },
                    # Informations de contact
                    "Contact": {
                        "Site Internet": item.contact.site_internet_festival if item.contact and item.contact.site_internet_festival else None,
                        "Email": item.contact.adresse_mail_festival if item.contact and item.contact.adresse_mail_festival else None
                    }
                }
        elif item_type == "commune":
            # Récupération d'une commune par son ID
            item = db.session.query(Commune).get(item_id)
            if item:
                # Construction des détails de la commune
                item_details = {
                    "Nom": item.nom_commune,
                    "Département": item.nom_departement,
                    "Région": item.nom_region,
                    "Latitude": item.geocodage_latitude_commune,
                    "Longitude": item.geocodage_longitude_commune
                }
        elif item_type == "monument":
            # Récupération d'un monument historique par son ID
            item = db.session.query(MonumentHistorique).get(item_id)
            if item:
                # Construction des détails du monument
                item_details = {
                    "Nom": item.nom_monument,
                    "Lieu": item.commune.nom_commune if item.commune else "Non renseigné",
                    "Datation": item.dates.datation_edifice if item.dates else "Non renseigné",
                    "Historique": item.dates.historique if item.dates else "Non renseigné",
                    # Liens externes associés au monument
                    "Liens": {
                        "Externe": item.contact.lien_internet_externe if item.contact and item.contact.lien_internet_externe else None,
                        "Palissy": item.contact.lien_internet_vers_base_palissy if item.contact and item.contact.lien_internet_vers_base_palissy else None,
                        "Base Archiv": item.contact.lien_internet_vers_base_archiv_mh if item.contact and item.contact.lien_internet_vers_base_archiv_mh else None
                    }
                }
        else:
            # Si le type d'item est inconnu, retourne une erreur 404
            abort(404)

        # Si aucun item n'a été trouvé, retourne une erreur 404
        if not item:
            app.logger.error(f"Item introuvable : type={item_type}, id={item_id}")
            abort(404)

        # Rend la page HTML avec les détails de l'item
        return render_template("pages/item.html", item=item, item_type=item_type, item_details=item_details)

    except Exception as e:
        # En cas d'erreur, log l'exception et retourne une erreur 500
        app.logger.error(f"Erreur lors de la récupération des détails de l'item : {str(e)}", exc_info=True)
        abort(500)
