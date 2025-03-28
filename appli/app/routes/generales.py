from app.app import app
from flask import render_template, request, flash, redirect, url_for, abort
from sqlalchemy import or_, func
from ..app import db, login
from ..models.users import Users
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

from ..models.database import festival_monuments_geopoint, Commune, Festival, ContactFestival, DateFestival, LieuFestival, TypeFestival, MonumentHistorique,AspectJuridiqueMonumentHistorique
from ..models.formulaires import RechercheFestivalMonument, AjoutFavori, ModificationFavori, SuppressionFavori, AjoutUtilisateur, Recherche
from ..utils.transformations import clean_arg
from ..utils.proximite import proximite

@app.route("/")
def accueil():
    return redirect(url_for("accueil_festivalchezmoi"))


@app.route("/festivalchezmoi/accueil", methods = ['GET'])
def accueil_festivalchezmoi():

    form = Recherche() #     flash("La recherche a rencontré une erreur "+ str(e), "info")
    return render_template ("/pages/accueil.html",form=form)
   

@app.route("/recherche", methods = ['GET', 'POST'])
@app.route("/recherche/<int:page>", methods= [ 'GET', 'POST'])

def recherche():
    form = Recherche()

    # initialisation des données de retour dans le cas où il n'y ait pas de requête
    donnees = []

    try:
        if form.validate_on_submit():
            nom_fest =  clean_arg(request.form.get("nom", None))
            periode =  clean_arg(request.form.get("periode", None))
            discipline =  clean_arg(request.form.get("discipline", None))
            lieu_pre_traitement = clean_arg(request.form.get("lieu",None))
            dist = clean_arg(request.form.get("dist", None))

            if nom_fest or periode or discipline or lieu_pre_traitement:
                query_results = Festival.query

                if nom_fest :
                    query_results = query_results.filter(Festival.nom_festival.ilike("%"+nom_fest+"%"))
                if periode:
                    query_results = query_results.filter(Festival.dates.ilike(periode))
                if discipline:
                    query_results = query_results.filter(Festival.type.ilike(discipline))
                if lieu_pre_traitement:
                    lieux = proximite(lieu_pre_traitement,dist) #on appelle la fonction qui trouve les villes à moins de dist km
                    for i in lieux:
                        query_results = query_results.filter(Festival.lieu.ilike(i))
                donnees = query_results.paginate(per_page=app.config["RESULTATS_PER_PAGE"])
            #preremplissage à gérer?
                form.nom.data = nom_fest
                form.periode.data= periode
                form.discipline.data= discipline
                form.lieu.data = lieu_pre_traitement
    except Exception as e:
        flash("La recherche a rencontré une erreur "+ str(e), "info")

    return render_template ("/pages/resultats.html", form=form, donnees = donnees )
        

# ROUTE A COMPLETER
@app.route("/recherche_rapide")
@app.route("/recherche_rapide/resultat")
def recherche_rapide():
    chaine =  request.args.get("chaine", None)
    try: 

        if chaine:
            resources = db.session.execute("""select a.id from Festival a 
                inner join Festival_resources b on b.id = a.id 
                inner join resources c on c.name = b.resource and (c.name like '%"""+chaine+"""%' or  c.id like '%"""+chaine+"""%')
                """).fetchall()
            
            maps = db.session.execute("""select a.id from Festival a 
                inner join Festival_map b on b.id = a.id 
                inner join map  c on c.name = b.map_ref and (c.name like '%"""+chaine+"""%' or  c.id like '%"""+chaine+"""%')
                """).fetchall()

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
            
        return render_template("pages/resultats_recherche_pays.html", 
                sous_titre= "Recherche | " + chaine, 
                donnees=resultats,
                requete=chaine)
    
    except Exception as e:
        print(e)
        abort(500)


@app.route("/resultats", methods=["GET", "POST"])
def resultats():
    form = Recherche()
    festivals = []
    monuments = []

    try:
        if form.validate_on_submit():
            lieu = form.lieu.data
            distance = form.dist.data or 10  # Distance par défaut : 10 km
            nom = form.nom.data
            periode = form.periode.data
            discipline = form.discipline.data

            app.logger.info(f"Recherche effectuée avec : lieu={lieu}, distance={distance}, nom={nom}, periode={periode}, discipline={discipline}")

            # Construction de la requête de base pour les festivals
            query_festivals = db.session.query(Festival)

            # Filtres conditionnels
            if lieu:
                # Jointure avec LieuFestival et Commune
                query_festivals = query_festivals.join(LieuFestival).join(Commune).filter(
                    func.lower(Commune.nom_commune).like(f"%{lieu.lower()}%")
                )

            if nom:
                # Recherche sur le nom du festival
                query_festivals = query_festivals.filter(
                    func.lower(Festival.nom_festival).like(f"%{nom.lower()}%")
                )

            if periode:
                # Jointure avec DateFestival
                query_festivals = query_festivals.join(DateFestival).filter(
                    func.lower(DateFestival.periode_principale_deroulement_festival).like(f"%{periode.lower()}%")
                )

            if discipline:
                # Jointure avec TypeFestival
                query_festivals = query_festivals.join(TypeFestival).filter(
                    func.lower(TypeFestival.discipline_dominante_festival).like(f"%{discipline.lower()}%")
                )

            # Exécution de la requête
            festivals = query_festivals.distinct().all()

            # Requête similaire pour les monuments
            query_monuments = db.session.query(MonumentHistorique)

            if lieu:
                query_monuments = query_monuments.join(Commune).filter(
                    func.lower(Commune.nom_commune).like(f"%{lieu.lower()}%")
                )

            monuments = query_monuments.distinct().all()

            app.logger.info(f"Festivals trouvés : {len(festivals)}, Monuments trouvés : {len(monuments)}")

            return render_template(
                "pages/resultats.html",
                form=form,
                festivals=festivals,
                monuments=monuments
            )
        
        else:
            # Gestion des erreurs de validation du formulaire
            for field, errors in form.errors.items():
                for error in errors:
                    app.logger.warning(f"Erreur de validation pour {field}: {error}")
                    flash(f"Erreur dans le champ {getattr(form, field).label.text}: {error}", "warning")

            return render_template("pages/resultats.html", form=form, festivals=[], monuments=[])

    except Exception as e:
        app.logger.error(f"Une erreur est survenue : {str(e)}", exc_info=True)
        flash(f"Une erreur est survenue : {str(e)}", "danger")
        return render_template("pages/resultats.html", form=form, festivals=[], monuments=[])

    # Retour par défaut si aucune condition n'est remplie
    return render_template("pages/resultats.html", form=form, festivals=[], monuments=[])