# Importation des modules nécessaires
from app.app import app
from flask import render_template, request, flash, redirect, url_for, abort
from sqlalchemy import or_, func
from ..app import db, login
from ..models.users import Users
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

from ..models.database import Commune, Festival, DateFestival, LieuFestival, TypeFestival
from ..models.formulaires import Recherche
from ..utils.transformations import clean_arg
from ..utils.pagination import Pagination
from sqlalchemy.dialects import sqlite  # Import pour compiler la requête SQL avec les valeurs réelles

# Route pour rediriger vers la page d'accueil principale
@app.route("/")
def accueil():
    return redirect(url_for("accueil_festivalchezmoi"))

# Route pour afficher la page d'accueil avec un formulaire de recherche
@app.route("/festivalchezmoi/accueil", methods=['GET'])
def accueil_festivalchezmoi():
    form = Recherche()  # Création d'une instance du formulaire de recherche
    return render_template("/pages/accueil.html", form=form)

# Route pour effectuer une recherche avec ou sans pagination
@app.route("/recherche", methods=['GET', 'POST'])
@app.route("/recherche/<int:page>", methods=['GET', 'POST'])
def recherche(page=1):
    form = Recherche()  # Création d'une instance du formulaire de recherche
    donnees = []  # Liste pour stocker les résultats de la recherche

    try:
        # Vérification si le formulaire est soumis ou si la méthode est GET
        if form.validate_on_submit() or request.method == 'GET':
            # Récupération des paramètres de recherche
            nom_fest = clean_arg(request.form.get("nom", None))
            periodes = request.form.getlist("periode")  # Périodes sélectionnées
            disciplines = request.form.getlist("discipline")  # Disciplines sélectionnées
            lieu_pre_traitement = clean_arg(request.form.get("lieu", None))

            # Log des paramètres de recherche
            app.logger.info(f"Recherche avec : nom={nom_fest}, periodes={periodes}, disciplines={disciplines}, lieu={lieu_pre_traitement}")

            # Construction de la requête SQLAlchemy
            query_results = db.session.query(
                Festival.nom_festival,
                Commune.nom_commune,
                TypeFestival.discipline_dominante_festival,
                DateFestival.periode_principale_deroulement_festival
            ).distinct()
            query_results = query_results.join(DateFestival, Festival.id_festival == DateFestival.id_festival, isouter=True)
            query_results = query_results.join(TypeFestival, Festival.id_festival == TypeFestival.id_festival, isouter=True)
            query_results = query_results.join(LieuFestival, Festival.id_festival == LieuFestival.id_festival, isouter=True)
            query_results = query_results.join(Commune, LieuFestival.id_commune == Commune.id_commune, isouter=True)

            # Application des filtres de recherche
            if nom_fest:
                query_results = query_results.filter(func.lower(Festival.nom_festival).like(f"%{nom_fest.lower()}%"))
            if periodes:
                query_results = query_results.filter(DateFestival.periode_principale_deroulement_festival.in_(periodes))
            if disciplines:
                query_results = query_results.filter(TypeFestival.discipline_dominante_festival.in_(disciplines))
            if lieu_pre_traitement:
                # Filtrage par lieu en ignorant les espaces
                query_results = query_results.filter(
                    func.replace(func.lower(Commune.nom_commune), ' ', '').like(f"%{lieu_pre_traitement.lower().replace(' ', '')}%")
                )
                app.logger.info(f"Filtrage par lieu (sans espaces) : {lieu_pre_traitement.lower().replace(' ', '')}")

            # Gestion de la pagination
            per_page = app.config["RESULTATS_PER_PAGE"]
            all_results = query_results.all()
            total = len(all_results)
            start = (page - 1) * per_page
            end = start + per_page
            donnees = Pagination(all_results[start:end], page, per_page, total)

            # Log des résultats paginés
            app.logger.info(f"Résultats trouvés (page {page}) : {donnees.items}")

            # Pré-remplissage du formulaire avec les valeurs saisies
            form.nom.data = nom_fest
            form.periode.data = periodes
            form.discipline.data = disciplines
            form.lieu.data = lieu_pre_traitement
    except Exception as e:
        # Gestion des erreurs et affichage d'un message à l'utilisateur
        app.logger.error(f"Erreur lors de la recherche : {str(e)}", exc_info=True)
        flash(f"La recherche a rencontré une erreur : {str(e)}", "info")

    # Rendu de la page des résultats avec les données et le formulaire
    return render_template("/pages/resultats.html", form=form, donnees=donnees)

# Route pour effectuer une recherche rapide
@app.route("/recherche_rapide")
@app.route("/recherche_rapide/resultat")
def recherche_rapide():
    chaine = request.args.get("chaine", None)  # Récupération de la chaîne de recherche
    try:
        if chaine:
            # Requêtes SQL pour rechercher dans les ressources et les cartes associées aux festivals
            resources = db.session.execute("""select a.id from Festival a 
                inner join Festival_resources b on b.id = a.id 
                inner join resources c on c.name = b.resource and (c.name like '%"""+chaine+"""%' or  c.id like '%"""+chaine+"""%')
                """).fetchall()
            
            maps = db.session.execute("""select a.id from Festival a 
                inner join Festival_map b on b.id = a.id 
                inner join map  c on c.name = b.map_ref and (c.name like '%"""+chaine+"""%' or  c.id like '%"""+chaine+"""%')
                """).fetchall()

            # Filtrage des festivals correspondant à la chaîne de recherche
            resultats = Festival.query.\
                filter(
                    or_(
                        Festival.name.ilike("%"+chaine+"%"),
                        Festival.type.ilike("%"+chaine+"%"),
                        Festival.Introduction.ilike("%"+chaine+"%"),
                        Festival.id.in_([r.id for r in resources] + [m.id for m in maps])
                    )
                ).\
                distinct(Festival.name).\
                order_by(Festival.name).\
                paginate(page=page, per_page=app.config["PAYS_PER_PAGE"])
        else:
            resultats = None
            
        # Rendu de la page des résultats de recherche rapide
        return render_template("pages/resultats_recherche_pays.html", 
                sous_titre= "Recherche | " + chaine, 
                donnees=resultats,
                requete=chaine)
    
    except Exception as e:
        # Gestion des erreurs
        print(e)
        abort(500)

# Route pour déboguer les données en affichant un échantillon des tables
@app.route("/debug_donnees")
def debug_donnees():
    try:
        # Récupération des données des différentes tables
        festivals = db.session.query(Festival).limit(15).all()
        dates = db.session.query(DateFestival).limit(15).all()
        types = db.session.query(TypeFestival).limit(15).all()
        lieux = db.session.query(LieuFestival).limit(15).all()
        communes = db.session.query(Commune).limit(15).all()

        # Organisation des données dans un dictionnaire
        donnees = {
            "festivals": [{"id": f.id_festival, "nom": f.nom_festival} for f in festivals],
            "dates": [{"id": d.id_festival, "periode": d.periode_principale_deroulement_festival} for d in dates],
            "types": [{"id": t.id_festival, "discipline": t.discipline_dominante_festival} for t in types],
            "lieux": [{"id": l.id_festival, "commune_id": l.id_commune} for l in lieux],
            "communes": [{"id": c.id_commune, "nom": c.nom_commune} for c in communes],
        }

        # Log des données récupérées
        app.logger.info(f"Données récupérées : {donnees}")

        # Retour des données sous forme de réponse JSON
        return donnees, 200
    except Exception as e:
        # Gestion des erreurs
        app.logger.error(f"Erreur dans /debug_donnees : {str(e)}", exc_info=True)
        return {"error": str(e)}, 500
