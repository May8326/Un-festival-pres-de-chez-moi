# Importation des modules nécessaires
from app.app import app
from flask import render_template, request, flash, redirect, url_for, abort
from sqlalchemy import or_, func, and_
from ..app import db, login
from ..models.users import Users
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

from ..models.database import Commune, Festival, DateFestival, LieuFestival, TypeFestival, relation_user_favori
from ..models.formulaires import Recherche
from ..utils.transformations import clean_arg
from ..utils.pagination import Pagination, args_to_dict
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
@app.route("/festivalchezmoi/recherche", methods=['GET', 'POST'])
@app.route("/festivalchezmoi/recherche/<int:page>", methods=['GET', 'POST'])
def recherche(page=1):
    
    form = Recherche()
    donnees = []

    try:
        # Récupération des paramètres de recherche depuis le formulaire ou les arguments GET
        nom_fest = clean_arg(request.form.get("nom", request.args.get("nom", None)))
        periodes = request.form.getlist("periode") or request.args.getlist("periode")
        disciplines = request.form.getlist("discipline") or request.args.getlist("discipline")
        lieu_pre_traitement = clean_arg(request.form.get("lieu", request.args.get("lieu", None)))

        # Log des données brutes du formulaire pour débogage
        app.logger.info(f"Données brutes du formulaire : nom={nom_fest}, periodes={periodes}, disciplines={disciplines}, lieu={lieu_pre_traitement}")
        

        # Validation des périodes et disciplines
        # IMPORTANT: Ajustez ces valeurs pour qu'elles correspondent exactement aux valeurs dans la base de données
        periodes_valides = [p for p in periodes if p in ['Avant-Saison (1 Janvier-20 Juin)', 'Saison (21 Juin-5 Septembre)', 'Après-saison (6 septembre - 31 décembre)']]
        
        # Assurez-vous que ces valeurs correspondent exactement à celles dans votre base de données
        disciplines_valides = [d for d in disciplines if d in ['arts visuels', 'cinéma', 'livre', 'musique', 'spectacle vivant', 'autre']]
        
        # Log après validation
        app.logger.info(f"Après validation : nom={nom_fest}, periodes={periodes_valides}, disciplines={disciplines_valides}, lieu={lieu_pre_traitement}")

        # Construction de la requête SQLAlchemy
        query_results = db.session.query(
            Festival.id_festival,
            Festival.nom_festival,
            Commune.nom_commune,
            TypeFestival.discipline_dominante_festival,
            DateFestival.periode_principale_deroulement_festival
        ).distinct()
        query_results = query_results.join(DateFestival, Festival.id_festival == DateFestival.id_festival, isouter=True)
        query_results = query_results.join(TypeFestival, Festival.id_festival == TypeFestival.id_festival, isouter=True)
        query_results = query_results.join(LieuFestival, Festival.id_festival == LieuFestival.id_festival, isouter=True)
        query_results = query_results.join(Commune, LieuFestival.id_commune == Commune.id_commune, isouter=True)

        # Force une exécution pour obtenir la requête SQL actuelle
        app.logger.info(f"Requête SQL avant filtres: {query_results}")

        # Application des filtres avec vérification des valeurs
        if nom_fest:
            query_results = query_results.filter(func.lower(Festival.nom_festival).like(f"%{nom_fest.lower()}%"))
            app.logger.info(f"Filtre appliqué pour nom: {nom_fest}")
            
        if periodes_valides:
            # Créer une condition OR pour les périodes
            periode_filters = []
            for periode in periodes_valides:
                periode_filters.append(DateFestival.periode_principale_deroulement_festival.like(f"%{periode}%"))
                app.logger.info(f"Filtre préparé pour période: {periode}")
            
            if periode_filters:
                query_results = query_results.filter(or_(*periode_filters))
                app.logger.info(f"Filtres de période appliqués: {periode_filters}")

        if disciplines_valides:
            # Créer une condition OR pour les disciplines
            discipline_filters = []
            for discipline in disciplines_valides:
                discipline_filters.append(TypeFestival.discipline_dominante_festival.like(f"%{discipline}%"))
                app.logger.info(f"Filtre préparé pour discipline: {discipline}")
            
            if discipline_filters:
                query_results = query_results.filter(or_(*discipline_filters))
                app.logger.info(f"Filtres de discipline appliqués: {discipline_filters}")
                
        if lieu_pre_traitement:
            query_results = query_results.filter(
                func.replace(func.lower(Commune.nom_commune), ' ', '').like(f"%{lieu_pre_traitement.lower().replace(' ', '')}%")
            )
            app.logger.info(f"Filtre appliqué pour lieu: {lieu_pre_traitement}")

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
                and_(*[Commune.nom_commune.ilike(f"%{lieu}%") for lieu in form.lieu.data])
            )
        # Log de la requête SQL après application des filtres
        app.logger.info(f"Requête SQL après application des filtres: {query_results}")
        # Log des valeurs des filtres appliqués
        app.logger.info(f"Filtres appliqués : nom={nom_fest}, periodes={periodes_valides}, disciplines={disciplines_valides}, lieu={lieu_pre_traitement}")


        # Imprimer la requête SQL générée avec les valeurs
        compiled_query = query_results.statement.compile(
            dialect=sqlite.dialect(),
            compile_kwargs={"literal_binds": True}
        )
        app.logger.info(f"Requête SQL compilée: {compiled_query}")

        # Pagination
        per_page = app.config["RESULTATS_PER_PAGE"]
        all_results = query_results.all()
        total = len(all_results)
        start = (page - 1) * per_page
        end = start + per_page

        donnees_items = all_results[start:end]
        donnees = Pagination(donnees_items, page, per_page, total)

        # Pré-remplissage du formulaire
        form.nom.data = nom_fest
        form.periode.data = periodes_valides
        form.discipline.data = disciplines_valides
        form.lieu.data = lieu_pre_traitement

    except Exception as e:
        app.logger.error(f"Erreur lors de la recherche : {str(e)}", exc_info=True)
        flash(f"La recherche a rencontré une erreur : {str(e)}", "error")

    return render_template(
        "/pages/resultats.html",
        form=form,
        donnees=donnees,
        nom=nom_fest,
        periodes=periodes_valides,
        disciplines=disciplines_valides,
        lieu=lieu_pre_traitement
    )

# Route pour effectuer une recherche rapide
@app.route("/festivalchezmoi/recherche_rapide")
@app.route("/festivalchezmoi/recherche_rapide/resultat")
def recherche_rapide():
    chaine = request.args.get("chaine", None)  # Récupération de la chaîne de recherche
    try:
        page = request.args.get("page", 1, type=int)  # Récupération de la page avec une valeur par défaut
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
@app.route("/festivalchezmoi/debug_donnees")
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
            "is_favori": [
                {
                    "id": f.id_festival,
                    "favori": f.id_festival in {
                        fav.id_festival for fav in db.session.query(relation_user_favori)
                        .filter(relation_user_favori.c.user_id == current_user.id)
                        .all()
                    }
                }
                for f in festivals
            ]
        }

        # Log des données récupérées
        app.logger.info(f"Données récupérées : {donnees}")

        # Retour des données sous forme de réponse JSON
        return donnees, 200
    except Exception as e:
        # Gestion des erreurs
        app.logger.error(f"Erreur dans /debug_donnees : {str(e)}", exc_info=True)
        return {"error": str(e)}, 500
