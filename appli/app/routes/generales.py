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
        
@app.route("/utilisateurs/ajout", methods=['GET', 'POST'])
def ajout_utilisateur(page=1): #nom du formulaire auquel on renvoie, avec l'adresse, GET envoi formulaire, c'est sur ça que ça va faire unpost 
    form = AjoutUtilisateur()  # Instance du formulaire AjoutUtilisateur

    if form.validate_on_submit():  # Si le formulaire est valide (POST et toutes les validations passent)
        prenom = form.prenom.data
        password = form.password.data

        # Vérifier si un utilisateur avec le même prénom existe déjà
        if Users.query.filter_by(prenom=prenom).first():
            flash("Un utilisateur avec ce prénom existe déjà.", "danger")
            return redirect(url_for("ajout_utilisateur"))

        # Créer un nouvel utilisateur
        nouvel_utilisateur = Users(
            prenom=prenom,
            password=generate_password_hash(password)  # Hacher le mot de passe
        )
        try:
            db.session.add(nouvel_utilisateur)
            db.session.commit()
            flash("Utilisateur créé avec succès !", "success")
            return redirect(url_for("liste_utilisateurs"))  # Rediriger vers la liste des utilisateurs
        except Exception as e:
            flash(f"Erreur lors de la création de l'utilisateur : {str(e)}", "danger")
            db.session.rollback()

    return render_template("pages/ajout_utilisateur.html", form=form)  # Afficher le formulaire (GET)
