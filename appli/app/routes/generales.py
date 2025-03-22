from ..app import app, db
from flask import render_template, request, flash, redirect, url_for, abort
from sqlalchemy import or_

from ..models.database import Commune, Festival, ContactFestival, DateFestival, LieuFestival, TypeFestival, MonumentHistorique,AspectJuridiqueMonumentHistorique
from ..models.formulaires import RechercheFestivalMonument, AjoutFavori, ModificationFavori, SuppressionFavori, AjoutUtilisateur, Recherche
from ..utils.transformations import clean_arg

@app.route("/")
def accueil():
    return render_template ("/templates/") #à compléter avec le nom du template d'accueil

#Ce qui suit est un WIP
@app.route("/resultats", methods=['GET', 'POST'])
def recherche(resultats):
    form = Recherche()

    # initialisation des données de retour dans le cas où il n'y ait pas de requête
    donnees = []

    try:
        if form.validate_on_submit():
            nom_festival =  clean_arg(request.form.get("nom", None))
            periode =  clean_arg(request.form.get("periode", None))
            discipline =  clean_arg(request.form.get("discipline", None))
            lieu_pre_traitement = clean_arg(request.form.get("lieu",None))

            if nom_festival or periode or discipline or lieu_pre_traitement:
                query_results = Festival.query