from app.app import app
from flask import render_template, request, flash, redirect, url_for, abort
from sqlalchemy import or_

from ..models.database import Commune, Festival, ContactFestival, DateFestival, LieuFestival, TypeFestival, MonumentHistorique,AspectJuridiqueMonumentHistorique
from ..models.formulaires import RechercheFestivalMonument, AjoutFavori, ModificationFavori, SuppressionFavori, AjoutUtilisateur, Recherche
from ..utils.transformations import clean_arg
from ..utils.proximite import proximite

@app.route("/")
def accueil():
    return redirect(url_for("accueil_festivalchezmoi"))

@app.route("/festivalchezmoi/accueil")
def accueil_festivalchezmoi():
    return render_template ("/pages/accueil.html")
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
            donnees = query_results.paginate(per_page=app.config["FESTIVALS_PER_PAGE"])
    except Exception as e:
        flash("La recherche a rencontré une erreur "+ str(e), "info")