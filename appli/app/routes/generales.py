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
   

@app.route("/recherche", methods=['GET', 'POST'])
@app.route("/recherche/<int:page>", methods=['GET', 'POST'])
def recherche(page=1):  # Ajout d'une valeur par défaut pour `page`
    form = Recherche()
    donnees = []

    try:
        if form.validate_on_submit() or request.method == 'GET':  # Inclure les requêtes GET pour la pagination
            nom_fest = clean_arg(request.form.get("nom", None))
            periode = clean_arg(request.form.get("periode", None))
            discipline = clean_arg(request.form.get("discipline", None))
            lieu_pre_traitement = clean_arg(request.form.get("lieu", None))
            dist = clean_arg(request.form.get("dist", None))

            app.logger.info(f"Recherche avec : nom={nom_fest}, periode={periode}, discipline={discipline}, lieu={lieu_pre_traitement}, dist={dist}")

            if nom_fest or periode or discipline or lieu_pre_traitement:
                query_results = Festival.query

                if nom_fest:
                    query_results = query_results.filter(Festival.nom_festival.ilike(f"%{nom_fest}%"))
                if periode:
                    query_results = query_results.join(DateFestival).filter(
                        DateFestival.periode_principale_deroulement_festival.ilike(f"%{periode}%")
                    )
                if discipline:
                    query_results = query_results.join(TypeFestival).filter(
                        TypeFestival.discipline_dominante_festival.ilike(f"%{discipline}%")
                    )
                if lieu_pre_traitement:
                    lieux = proximite(lieu_pre_traitement, dist)
                    app.logger.info(f"Lieux trouvés pour {lieu_pre_traitement} : {lieux}")
                    if lieux:
                        query_results = query_results.join(LieuFestival).join(Commune).filter(
                            Commune.nom_commune.in_(lieux)
                        )
                    else:
                        app.logger.warning(f"Aucun lieu trouvé pour {lieu_pre_traitement} dans un rayon de {dist} km.")

                app.logger.info(f"Requête générée : {query_results}")
                donnees = query_results.paginate(page=page, per_page=app.config["RESULTATS_PER_PAGE"])

                # Log des résultats
                app.logger.info(f"Résultats trouvés : {donnees.items}")

                form.nom.data = nom_fest
                form.periode.data = periode
                form.discipline.data = discipline
                form.lieu.data = lieu_pre_traitement
    except Exception as e:
        app.logger.error(f"Erreur lors de la recherche : {str(e)}", exc_info=True)
        flash(f"La recherche a rencontré une erreur : {str(e)}", "info")

    return render_template("/pages/resultats.html", form=form, donnees=donnees)

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

@app.route("/test_bdd")
def test_bdd():
    try:
        # Vérifier les données dans la table Commune
        communes = db.session.query(Commune).limit(10).all()
        communes_data = [{"id": c.id_commune, "nom": c.nom_commune} for c in communes]

        # Vérifier les données dans la table Festival
        festivals = db.session.query(Festival).limit(10).all()
        festivals_data = [{"id": f.id_festival, "nom": f.nom_festival} for f in festivals]

        # Vérifier les données dans la table MonumentHistorique
        monuments = db.session.query(MonumentHistorique).limit(10).all()
        monuments_data = [{"id": m.id_monument_historique, "nom": m.nom_monument} for m in monuments]

        # Vérifier les jointures entre Festival et Commune via LieuFestival
        jointures = (
            db.session.query(Festival, Commune)
            .select_from(Festival)
            .join(LieuFestival, Festival.id_festival == LieuFestival.id_festival)
            .join(Commune, LieuFestival.id_commune == Commune.id_commune)
            .limit(10)
            .all()
        )
        jointures_data = [
            {"festival": f.nom_festival, "commune": c.nom_commune} for f, c in jointures
        ]

        app.logger.info(f"Jointures Festival-Commune : {jointures}")

        return {
            "communes": communes_data,
            "festivals": festivals_data,
            "monuments": monuments_data,
            "jointures": jointures_data,
        }
    except Exception as e:
        app.logger.error(f"Erreur dans /test_bdd : {str(e)}", exc_info=True)
        return {"error": str(e)}, 500