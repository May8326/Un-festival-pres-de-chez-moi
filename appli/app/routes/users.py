from flask import url_for, render_template, redirect, request, flash
from ..models.users import Users
from ..models.formulaires import AjoutUtilisateur, Connexion, SuppressionUtilisateur, ModificationUtilisateur
from ..utils.transformations import  clean_arg
from app.app import app
from flask_login import login_user, logout_user, current_user
from app.app import login

@app.route("/festivalchezmoi/utilisateurs/ajout", methods=["GET", "POST"])
def ajout_utilisateur():
    form = AjoutUtilisateur()

    if form.validate_on_submit():
        statut, donnees = Users.ajout(
            identifiant=clean_arg(request.form.get("prenom", None)),
            password=clean_arg(request.form.get("password", None))
        )
        if statut is True:
            flash("Ajout effectué", "success")
            return redirect(url_for("accueil"))
        else:
            flash(",".join(donnees), "error")
            return render_template("/pages/ajout_utilisateur.html", form=form)
    else:
        return render_template("/pages/ajout_utilisateur.html", form=form)
    
@app.route("/festivalchezmoi/utilisateurs/connexion", methods=["GET","POST"])
def connexion():
    form = Connexion()

    if current_user.is_authenticated is True:
        flash("Vous êtes déjà connecté", "info")
        return redirect(url_for("accueil"))

    if form.validate_on_submit():
        utilisateur = Users.identification(
            identifiant=clean_arg(request.form.get("adresse email", None)),
            password=clean_arg(request.form.get("password", None))
        )
        if utilisateur:
            flash("Connexion effectuée", "success")
            login_user(utilisateur)
            return redirect(url_for("accueil"))
        else:
            flash("Les identifiants n'ont pas été reconnus", "error")
            return render_template("/pages/connexion.html", form=form)

    else:
        return render_template("/pages/connexion.html", form=form)

@app.route("/festivalchezmoi/utilisateurs/deconnexion", methods=["POST", "GET"])
def deconnexion():
    if current_user.is_authenticated is True:
        logout_user()
    flash("Vous êtes déconnecté", "info")
    return redirect(url_for("accueil"))

# VOIR SI ON AJOUTE UNE PAGE D'AFFICHAGE DU COMPTE UTILISATEUR

# @app.route("/utilisateurs/mon_compte", methods=["GET"])
# def mon_compte():
#     if current_user.is_authenticated is False:
#         flash("Vous devez être connecté pour accéder à cette page", "warning")
#         return redirect(url_for("connexion"))
#     else:
#         return render_template("pages/mon_compte.html")
#         flash("Vous êtes sur votre compte", "info")
#     return render_template("pages/compte.html", form=form)

@app.route("/festivalchezmoi/utilisateurs/modification", methods=["GET", "POST"])
def modification():
    form = ModificationUtilisateur()

    if form.validate_on_submit():
        statut, donnees = Users.modification(
            identifiant=clean_arg(request.form.get("adresse email", None)),
            password=clean_arg(request.form.get("password", None))
        )
        if statut is True:
            flash("Modification effectuée", "success")
            return redirect(url_for("accueil"))
        else:
            flash(",".join(donnees), "error")
            return render_template("/pages/modification_utilisateur.html", form=form)
    else:
        return render_template("/pages/modification_utilisateur.html", form=form)
    
@app.route("/festivalchezmoi/utilisateurs/suppression", methods=["GET", "POST"])
def suppression():
    form = SuppressionUtilisateur()

    if form.validate_on_submit():
        statut, donnees = Users.suppression(
            identifiant=clean_arg(request.form.get("prenom", None)),
            password=clean_arg(request.form.get("password", None))
        )
        if statut is True:
            flash("Suppression effectuée", "success")
            return redirect(url_for("accueil"))
        else:
            flash(",".join(donnees), "error")
            return render_template("/pages/suppression_utilisateur.html", form=form)
    else:
        return render_template("/pages/suppression_utilisateur.html", form=form)


login.login_view = 'connexion'