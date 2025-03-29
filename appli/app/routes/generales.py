# Importation des modules nécessaires
from app.app import app
from flask import render_template, request, flash, redirect, url_for, abort
from sqlalchemy import or_, func, and_, distinct
from ..app import db, login
from ..models.users import Users
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

from ..models.database import Commune, Festival, DateFestival, LieuFestival, TypeFestival, relation_user_favori
from ..models.formulaires import Recherche
from ..utils.transformations import clean_arg
from ..utils.proximite import proximite, proximite_geo
from ..utils.pagination import Pagination, args_to_dict
from sqlalchemy.dialects import sqlite  # Import pour compiler la requête SQL avec les valeurs réelles
from sqlalchemy.orm import joinedload

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
    geo_data = None

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

        # Construction de la requête SQLAlchemy OPTIMISÉE
        # 1. Utilisation de joinedload pour les jointures gourmandes
        # 2. Sélection uniquement des colonnes nécessaires
        base_query = db.session.query(
            Festival.id_festival,
            Festival.nom_festival,
            Commune.nom_commune,
            TypeFestival.discipline_dominante_festival,
            DateFestival.periode_principale_deroulement_festival
        ).distinct()
        
        # Utilisation de jointures avec l'option joinedload
        base_query = base_query.options(
            joinedload(Festival.dates),
            joinedload(Festival.type),
            joinedload(Festival.lieu).joinedload(LieuFestival.commune)
        )
        
        # Jointures optimisées en utilisant 'JOIN' plutôt que 'LEFT JOIN' quand possible
        base_query = base_query.join(
            DateFestival, Festival.id_festival == DateFestival.id_festival
        ).join(
            TypeFestival, Festival.id_festival == TypeFestival.id_festival
        ).join(
            LieuFestival, Festival.id_festival == LieuFestival.id_festival
        ).join(
            Commune, LieuFestival.id_commune == Commune.id_commune
        )

        # Création d'une liste de filtres à appliquer
        filters = []
        
        # Application des filtres avec des méthodes optimisées
        if nom_fest:
            filters.append(func.lower(Festival.nom_festival).like(f"%{nom_fest.lower()}%"))
            
        if periodes_valides:
            periode_filters = [DateFestival.periode_principale_deroulement_festival.like(f"%{p}%") for p in periodes_valides]
            if periode_filters:
                filters.append(or_(*periode_filters))

        if disciplines_valides:
            discipline_filters = [TypeFestival.discipline_dominante_festival.like(f"%{d}%") for d in disciplines_valides]
            if discipline_filters:
                filters.append(or_(*discipline_filters))
                
        if lieu_pre_traitement:
            # Optimisation par mise en cache des résultats de proximite
            from functools import lru_cache
            
            @lru_cache(maxsize=128)
            def get_lieux_proches(nom_ville, distance):
                return proximite(nom_ville, distance)
            
            lieux_post_traitement = get_lieux_proches(lieu_pre_traitement, 20)
            if lieux_post_traitement:
                lieux_filter = [Commune.nom_commune.like(f"{i}") for i in lieux_post_traitement]
                filters.append(or_(*lieux_filter))
                
            # Pareil pour les données géographiques
            @lru_cache(maxsize=128)
            def get_geo_data(nom_ville, distance):
                return proximite_geo(nom_ville, distance)
            
            geo_data = get_geo_data(lieu_pre_traitement, 20)

        # Appliquer tous les filtres à la fois
        if filters:
            base_query = base_query.filter(and_(*filters))

        # Optimisation de la pagination
        # Utiliser une requête COUNT distincte pour le comptage total
        count_q = db.session.query(func.count(distinct(Festival.id_festival)))
        
        # Appliquer les mêmes filtres à la requête de comptage
        if filters:
            count_q = count_q.select_from(
                Festival
            ).join(
                DateFestival, Festival.id_festival == DateFestival.id_festival
            ).join(
                TypeFestival, Festival.id_festival == TypeFestival.id_festival
            ).join(
                LieuFestival, Festival.id_festival == LieuFestival.id_festival
            ).join(
                Commune, LieuFestival.id_commune == Commune.id_commune
            ).filter(and_(*filters))
            
        total = count_q.scalar()
        
        # Pagination
        per_page = app.config["RESULTATS_PER_PAGE"]
        offset = (page - 1) * per_page
        
        # Appliquer limit et offset directement sur la requête
        donnees_items = base_query.limit(per_page).offset(offset).all()
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
        lieu=lieu_pre_traitement,
        geo_data=geo_data  # Passer les données géographiques au template
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
