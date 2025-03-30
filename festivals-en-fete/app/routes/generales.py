# Importation des modules nécessaires
from app.app import app  # Importation de l'application Flask
from flask import render_template, request, flash, redirect, url_for, abort  # Fonctions Flask pour gérer les requêtes et réponses
from sqlalchemy import or_, func, and_  # Fonctions SQLAlchemy pour construire des requêtes
from ..app import db, login  # Base de données et gestion des connexions utilisateur
from ..models.users import Users  # Modèle utilisateur
from werkzeug.security import generate_password_hash, check_password_hash  # Gestion des mots de passe
from flask_login import login_user, logout_user, login_required, current_user  # Gestion des sessions utilisateur

# Importation des modèles et utilitaires spécifiques à l'application
from ..models.database import Commune, Festival, DateFestival, LieuFestival, TypeFestival, relation_user_favori, MonumentHistorique, festival_monuments_geopoint
from ..models.formulaires import Recherche  # Formulaire de recherche
from ..utils.transformations import clean_arg  # Nettoyage des arguments
from ..utils.proximite import proximite  # Calcul de proximité géographique
from ..utils.pagination import Pagination, args_to_dict  # Gestion de la pagination
from sqlalchemy.dialects import sqlite  # Pour compiler les requêtes SQL avec les valeurs réelles

# Route pour rediriger vers la page d'accueil principale
@app.route("/")
def accueil():
    return redirect(url_for("accueil_festivalchezmoi"))  # Redirection vers la page d'accueil spécifique

# Route pour afficher la page d'accueil avec un formulaire de recherche
@app.route("/festivalchezmoi/accueil", methods=['GET'])
def accueil_festivalchezmoi():
    form = Recherche()  # Création d'une instance du formulaire de recherche
    return render_template("/pages/accueil.html", form=form)  # Rendu de la page d'accueil avec le formulaire

# Route pour effectuer une recherche avec ou sans pagination
@app.route("/festivalchezmoi/recherche", methods=['GET', 'POST'])
@app.route("/festivalchezmoi/recherche/<int:page>", methods=['GET', 'POST'])
def recherche(page=1):
    # Initialisation des variables
    form = Recherche()  # Formulaire de recherche
    donnees = []  # Résultats paginés
    festivals_coords = []  # Coordonnées des festivals
    monuments_coords = []  # Coordonnées des monuments

    try:
        # Récupération et nettoyage des paramètres de recherche
        nom_fest = clean_arg(request.form.get("nom", request.args.get("nom", None)))
    
        periodes = request.form.getlist("periode") or request.args.getlist("periode")
        
        disciplines = request.form.getlist("discipline") or request.args.getlist("discipline")
        lieu_pre_traitement = clean_arg(request.form.get("lieu", request.args.get("lieu", None)))
        
        # Validation des périodes et disciplines pour correspondre aux valeurs en base de données
        periodes_valides = [p for p in periodes if p in ['Avant-saison (1er janvier - 20 juin)', 'Saison (21 Juin - 5 Septembre)', 'Après-saison (6 septembre - 31 décembre)']]
        disciplines_valides = [d for d in disciplines if d in ['Arts visuels, art numériques', 'Cinéma, audiovisuel', 'Livre, littérature', 'Musique', 'Spectacle vivant', 'Pluridisciplinaire']]

        # Construction de la requête SQLAlchemy pour récupérer les festivals
        query_results = db.session.query(
            Festival.id_festival,
            Festival.nom_festival,
            Commune.nom_commune,
            TypeFestival.discipline_dominante_festival,
            DateFestival.periode_principale_deroulement_festival,
            LieuFestival.latitude_festival,
            LieuFestival.longitude_festival
        ).distinct()
        
        # Ici, remplacer base_query par query_results
        query_results = query_results.join(DateFestival, Festival.id_festival == DateFestival.id_festival, isouter=True)
        query_results = query_results.join(TypeFestival, Festival.id_festival == TypeFestival.id_festival, isouter=True)
        query_results = query_results.join(LieuFestival, Festival.id_festival == LieuFestival.id_festival, isouter=True)
        query_results = query_results.join(Commune, LieuFestival.id_commune == Commune.id_commune, isouter=True)

        # Application des filtres de recherche
        if nom_fest:
            query_results = query_results.filter(func.lower(Festival.nom_festival).like(f"%{nom_fest.lower()}%"))
            app.logger.info(f"Filtre appliqué pour nom: {nom_fest}")
        
        if periodes_valides:
            periode_filters = []
            for periode in periodes_valides:
                    periode_filters.append(DateFestival.periode_principale_deroulement_festival.like(f"%{periode}%"))
                    app.logger.info(f"Filtre préparé pour période: {periode}")
            
            if periode_filters:
                query_results = query_results.filter(or_(*periode_filters))
                app.logger.info(f"Filtres de période appliqués: {periode_filters}")
            
            # periode_filters = []
            for periode in periodes_valides:
                periode_filters.append(DateFestival.periode_principale_deroulement_festival.like(f"%{periode}%"))
            
            if periode_filters:
                query_results = query_results.filter(or_(*periode_filters))
                app.logger.info(f"Filtres de période appliqués: {periode_filters}")
        
        if disciplines_valides:
            discipline_filters = []
            for discipline in disciplines_valides:
                    discipline_filters.append(TypeFestival.discipline_dominante_festival.like(f"%{discipline}%"))
                    app.logger.info(f"Filtre préparé pour discipline: {discipline}")
            
            if discipline_filters:
                query_results = query_results.filter(or_(*discipline_filters))
                app.logger.info(f"Filtres de discipline appliqués: {discipline_filters}")
            
            # discipline_filters = []
            for discipline in disciplines_valides:
                discipline_filters.append(TypeFestival.discipline_dominante_festival.like(f"%{discipline}%"))
            
            if discipline_filters:
                query_results = query_results.filter(or_(*discipline_filters))
                app.logger.info(f"Filtres de discipline appliqués: {discipline_filters}")
        
        if lieu_pre_traitement:
            lieux_post_traitement = proximite(lieu_pre_traitement, 20)
            app.logger.info(f'Lieux trouvés: {lieux_post_traitement}')
            
            if not lieux_post_traitement:
                flash(f"Aucun lieu trouvé correspondant à '{lieu_pre_traitement}'.", "warning")
                return render_template(
            "/pages/resultats.html",
            form=form,
            donnees=[],
            nom=nom_fest,
            periodes=periodes_valides,
            disciplines=disciplines_valides,
            lieu=lieu_pre_traitement,
            festivals_coords=[],
            monuments_coords=[]
        )
            query_results = query_results.filter(or_(*[Commune.nom_commune.like(f"{lieu}") for lieu in lieux_post_traitement]))
        if form.discipline.data:
            query_results = query_results.filter(
                and_(*[TypeFestival.discipline_dominante_festival.ilike(f"%{discipline}%") for discipline in form.discipline.data])
            )

        if form.periode.data:
            query_results = query_results.filter(
                and_(*[DateFestival.periode_principale_deroulement_festival.ilike(f"%{periode}%") for periode in form.periode.data])
            )
        if form.nom.data:
            query_results = query_results.filter(
                and_(*[Festival.nom_festival.ilike(f"%{nom}%") for nom in form.nom.data])
            )
        if form.lieu.data:
            query_results = query_results.filter(
                and_(*[Commune.nom_commune.ilike(f"%{lieu}%") for lieu in form.lieu.data]))
        # Pagination des résultats
        per_page = app.config["RESULTATS_PER_PAGE"]
        all_results = query_results.all()
        total = len(all_results)
        start = (page - 1) * per_page
        end = start + per_page
        donnees_items = all_results[start:end]
        donnees = Pagination(donnees_items, page, per_page, total)

        # Récupération des coordonnées des festivals et des monuments proches
        for festival in all_results:
            if festival[5] and festival[6]:  # Vérification des coordonnées
                festivals_coords.append({
                    "id": festival[0],
                    "nom": festival[1],
                    "latitude": festival[5],
                    "longitude": festival[6]
                })
        monuments_dict = {}
        for festival in festivals_coords:
            monuments_proches = db.session.query(
                MonumentHistorique.id_monument_historique,
                MonumentHistorique.titre_editorial_de_la_notice.label("nom_monument"),
                MonumentHistorique.latitude_monument_historique,
                MonumentHistorique.longitude_monument_historique
            ).join(
                festival_monuments_geopoint,
                MonumentHistorique.id_monument_historique == festival_monuments_geopoint.c.id_monument_historique
            ).filter(
                festival_monuments_geopoint.c.id_festival == festival["id"],
                festival_monuments_geopoint.c.distance <= 10  # Distance max de 10km
            ).all()
            for monument in monuments_proches:
                if monument[2] and monument[3]:  # Vérification des coordonnées
                    monument_id = monument[0]
                    if monument_id not in monuments_dict:
                        monuments_dict[monument_id] = {
                            "id": monument_id,
                            "nom": monument[1],
                            "latitude": monument[2],
                            "longitude": monument[3]
                        }
        monuments_coords = list(monuments_dict.values())

        # Pré-remplissage du formulaire avec les données de recherche
        form.nom.data = nom_fest
        form.periode.data = periodes_valides
        form.discipline.data = disciplines_valides
        form.lieu.data = lieu_pre_traitement

    except Exception as e:
        # Gestion des erreurs
        app.logger.error(f"Erreur lors de la recherche : {str(e)}", exc_info=True)
        flash(f"La recherche a rencontré une erreur : {str(e)}", "error")

    # Rendu de la page des résultats
    return render_template(
        "/pages/resultats.html",
        form=form,
        donnees=donnees,
        nom=nom_fest,
        periodes=periodes_valides,
        disciplines=disciplines_valides,
        lieu=lieu_pre_traitement,
        festivals_coords=festivals_coords,
        monuments_coords=monuments_coords
    )

# Route pour effectuer une recherche rapide
# @app.route("/festivalchezmoi/recherche_rapide")
# @app.route("/festivalchezmoi/recherche_rapide/resultat")
# def recherche_rapide():
#     chaine = request.args.get("chaine", None)  # Récupération de la chaîne de recherche
#     try:
#         page = request.args.get("page", 1, type=int)  # Récupération de la page
#         if chaine:
#             # Recherche dans les ressources et cartes associées aux festivals
#             resources = db.session.execute("""...""").fetchall()
#             maps = db.session.execute("""...""").fetchall()
#             resultats = Festival.query.filter(...).paginate(page=page, per_page=app.config["PAYS_PER_PAGE"])
#         else:
#             resultats = None
#         return render_template("pages/resultats_recherche_pays.html", sous_titre="Recherche | " + chaine, donnees=resultats, requete=chaine)
#     except Exception as e:
#         print(e)
#         abort(500)

# Route pour déboguer les données en affichant un échantillon des tables
# @app.route("/festivalchezmoi/debug_donnees")
# def debug_donnees():
#     try:
#         # Récupération des données des tables principales
#         festivals = db.session.query(Festival).limit(15).all()
#         dates = db.session.query(DateFestival).limit(15).all()
#         types = db.session.query(TypeFestival).limit(15).all()
#         lieux = db.session.query(LieuFestival).limit(15).all()
#         communes = db.session.query(Commune).limit(15).all()

#         # Organisation des données dans un dictionnaire
#         donnees = {
#             "festivals": [{"id": f.id_festival, "nom": f.nom_festival} for f in festivals],
#             "dates": [{"id": d.id_festival, "periode": d.periode_principale_deroulement_festival} for d in dates],
#             "types": [{"id": t.id_festival, "discipline": t.discipline_dominante_festival} for t in types],
#             "lieux": [{"id": l.id_festival, "commune_id": l.id_commune} for l in lieux],
#             "communes": [{"id": c.id_commune, "nom": c.nom_commune} for c in communes],
#             "is_favori": [
#                 {
#                     "id": f.id_festival,
#                     "favori": f.id_festival in {
#                         fav.id_festival for fav in db.session.query(relation_user_favori)
#                         .filter(relation_user_favori.c.user_id == current_user.id)
#                         .all()
#                     }
#                 }
#                 for f in festivals
#             ]
#         }
#         return donnees, 200
#     except Exception as e:
#         app.logger.error(f"Erreur dans /debug_donnees : {str(e)}", exc_info=True)
#         return {"error": str(e)}, 500
