from ..app import app, db
from flask import render_template, request, flash, redirect, url_for, abort
from sqlalchemy import or_

from ..models.database import Commune, Festival, ContactFestival, DateFestival, LieuFestival, TypeFestival, MonumentHistorique,AspectJuridiqueMonumentHistorique
from ..models.formulaires import RechercheFestivalMonument, AjoutFavori, ModificationFavori, SuppressionFavori, AjoutUtilisateur, Recherche

@app.route("/")
def accueil():
    return render_template ("/templates/") #à compléter avec le nom du template d'accueil

#Ce qui suit est un WIP
@app.route("/resultats", methods=['GET', 'POST'])
def recherche(resultats):
    form = Recherche()