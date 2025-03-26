from flask import url_for, render_template, redirect, request, flash
from ..models.users import Users
from ..models.formulaires import AjoutUtilisateur
from ..utils.transformations import  clean_arg
from app.app import app

@app.route("/utilisateurs/ajout", methods=["GET", "POST"])
def ajout_utilisateur():
    form = AjoutUtilisateur()

    if form.validate_on_submit():
        statut, donnees = Users.ajout(
            prenom=clean_arg(request.form.get("prenom", None)),
            password=clean_arg(request.form.get("password", None))
        )
        if statut is True:
            flash("Ajout effectué", "success")
            return redirect(url_for("accueil"))
        else:
            flash(",".join(donnees), "error")
            return render_template("pages/ajout_utilisateur.html", form=form)
    else:
        return render_template("pages/ajout_utilisateur.html", form=form)
    
"""
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
"""