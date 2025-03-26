from app.app import app
from flask import render_template, request, flash, redirect, url_for, abort
from sqlalchemy import or_
from ..app import db, login
from ..models.users import Users
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

from ..models.database import Commune, Festival, ContactFestival, DateFestival, LieuFestival, TypeFestival, MonumentHistorique,AspectJuridiqueMonumentHistorique
from ..models.formulaires import RechercheFestivalMonument, AjoutFavori, ModificationFavori, SuppressionFavori, AjoutUtilisateur, Recherche
from ..utils.transformations import clean_arg
from ..utils.proximite import proximite

@app.route("/")
def accueil():
    return redirect(url_for("accueil_festivalchezmoi"))


@app.route("/festivalchezmoi/accueil", methods = ['GET', 'POST'])
def accueil_festivalchezmoi():

    form = Recherche()
    # try:
    #     if form.validate_on_submit():
    #         nom_fest =  clean_arg(request.form.get("nom", None))
    #         periode =  clean_arg(request.form.get("periode", None))
    #         discipline =  clean_arg(request.form.get("discipline", None))
    #         lieu_pre_traitement = clean_arg(request.form.get("lieu",None))
    #         dist = clean_arg(request.form.get("dist", None))

    #         if nom_fest or periode or discipline or lieu_pre_traitement:
    #             query_results = Festival.query

    #             if nom_fest :
    #                 query_results = query_results.filter(Festival.nom_festival.ilike("%"+nom_fest+"%"))
    #             if periode:
    #                 query_results = query_results.filter(Festival.dates.ilike(periode))
    #             if discipline:
    #                 query_results = query_results.filter(Festival.type.ilike(discipline))
    #             if lieu_pre_traitement:
    #                 lieux = proximite(lieu_pre_traitement,dist) #on appelle la fonction qui trouve les villes à moins de dist km
    #                 for i in lieux:
    #                     query_results = query_results.filter(Festival.lieu.ilike(i))
    #         donnees = query_results.paginate(per_page=app.config["RESULTATS_PER_PAGE"])
    # except Exception as e:
    #     flash("La recherche a rencontré une erreur "+ str(e), "info")
    return render_template ("/pages/accueil.html",form=form)
#Ce qui suit est un WIP
@app.route("/resultats", methods=['GET', 'POST'])

def recherche(resultats):
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
    except Exception as e:
        flash("La recherche a rencontré une erreur "+ str(e), "info")

    return render_template ("/pages/accueil.html",form=form, donnees = donnees )
        

# ROUTE A COMPLETER
@app.route("/recherche_rapide")
@app.route("/recherche_rapide/<int:page>")
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