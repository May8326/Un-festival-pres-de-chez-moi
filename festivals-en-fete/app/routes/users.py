from flask import url_for, render_template, redirect, request, flash
from ..models.users import Users
from ..models.database import relation_user_favori
from ..models.formulaires import AjoutUtilisateur, Connexion, SuppressionUtilisateur, ModificationUtilisateur
from ..utils.transformations import clean_arg
from app.app import app, db
from flask_login import login_user, logout_user, current_user
from app.app import login
from flask_login import login_required
from werkzeug.security import check_password_hash
from sqlalchemy import delete

# Route pour ajouter un utilisateur
@app.route("/festivalchezmoi/utilisateurs/ajout", methods=["GET", "POST"])
def ajout_utilisateur():
    form = AjoutUtilisateur()  # Formulaire pour l'ajout d'utilisateur

    if form.validate_on_submit():  # Si le formulaire est valide
        # Appel de la méthode d'ajout d'utilisateur avec les données nettoyées
        statut, donnees = Users.ajout(
            prenom=clean_arg(request.form.get("prenom", None)),  # Remplacez identifiant par prenom
            password=clean_arg(request.form.get("password", None)),
            email=clean_arg(request.form.get("email", None))  # Ajoutez l'email si nécessaire
        )

        if statut is True:  # Si l'ajout est réussi
            flash("Ajout effectué", "success")  # Message de succès
            return redirect(url_for("accueil"))  # Redirection vers la page d'accueil
        else:  # Si l'ajout échoue
            flash(",".join(donnees), "error")  # Afficher les erreurs
            return render_template("pages/ajout_utilisateur.html", form=form)
    else:
        # Afficher le formulaire d'ajout d'utilisateur
        return render_template("pages/ajout_utilisateur.html", form=form)

# Route pour la connexion d'un utilisateur
@app.route("/festivalchezmoi/utilisateurs/connexion", methods=["GET", "POST"])
def connexion():
    form = Connexion()  # Formulaire de connexion

    if current_user.is_authenticated is True:  # Si l'utilisateur est déjà connecté
        flash("Vous êtes déjà connecté", "info")  # Message d'information
        return redirect(url_for("accueil"))  # Redirection vers la page d'accueil

    if form.validate_on_submit():  # Si le formulaire est valide
        # Récupérer et nettoyer les données du formulaire
        prenom = clean_arg(request.form.get("prenom", None))
        password = clean_arg(request.form.get("password", None))

        # Identification de l'utilisateur
        utilisateur = Users.identification(prenom=prenom, password=password)
        if utilisateur:  # Si l'utilisateur est trouvé
            flash("Connexion effectuée", "success")  # Message de succès
            login_user(utilisateur)  # Connexion de l'utilisateur
            return redirect(url_for("accueil"))  # Redirection vers la page d'accueil
        else:  # Si l'identification échoue
            flash("Les identifiants n'ont pas été reconnus", "error")  # Message d'erreur
            return render_template("pages/connexion.html", form=form)

    # Afficher le formulaire de connexion
    return render_template("pages/connexion.html", form=form)

# Route pour la déconnexion d'un utilisateur
@app.route("/festivalchezmoi/utilisateurs/deconnexion", methods=["POST", "GET"])
def deconnexion():
    if current_user.is_authenticated is True:  # Si l'utilisateur est connecté
        logout_user()  # Déconnexion de l'utilisateur
    flash("Vous êtes déconnecté", "info")  # Message d'information
    return redirect(url_for("accueil"))  # Redirection vers la page d'accueil

# Route pour afficher la page mon_compte.html
@app.route("/festivalchezmoi/utilisateurs/mon_compte", methods=["GET", "POST"])
@login_required
def mon_compte():
    """
    Affiche les informations de l'utilisateur connecté et permet de modifier ses informations.
    """
    form = ModificationUtilisateur()  # Créez une instance du formulaire

    if form.validate_on_submit():  # Si le formulaire est soumis et valide
        try:
            # Mise à jour des informations utilisateur
            current_user.prenom = form.prenom.data
            if form.email.data:
                current_user.email = form.email.data

            db.session.commit()
            flash("Vos informations ont été mises à jour avec succès.", "success")
            return redirect(url_for("mon_compte"))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erreur lors de la modification des informations utilisateur : {str(e)}")
            flash("Une erreur s'est produite lors de la mise à jour de vos informations.", "error")

    # Pré-remplir le formulaire avec les informations actuelles
    form.prenom.data = current_user.prenom
    form.email.data = current_user.email

    return render_template("pages/mon_compte.html", user=current_user, form=form)  # Transmettez le formulaire au template

# Route pour modifier les informations d'un utilisateur
@app.route("/festivalchezmoi/utilisateurs/modifier", methods=["GET", "POST"])
@login_required
def modifier_utilisateur():
    """
    Permet à l'utilisateur connecté de modifier ses informations personnelles.
    """
    form = ModificationUtilisateur()

    if form.validate_on_submit():
        try:
            # Mise à jour des informations utilisateur
            current_user.prenom = form.prenom.data
            if form.email.data:
                current_user.email = form.email.data

            db.session.commit()
            flash("Vos informations ont été mises à jour avec succès.", "success")
            return redirect(url_for("mon_compte"))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erreur lors de la modification des informations utilisateur : {str(e)}")
            flash("Une erreur s'est produite lors de la mise à jour de vos informations.", "error")

    # Pré-remplir le formulaire avec les informations actuelles
    form.prenom.data = current_user.prenom
    form.email.data = current_user.email

    return render_template("pages/modification_utilisateur.html", form=form)

# Route pour supprimer un utilisateur
@app.route("/festivalchezmoi/suppression/utilisateur", methods=['GET', 'POST'])
@login_required
def suppression_utilisateur():
    """Route pour supprimer un compte utilisateur."""
    form = SuppressionUtilisateur()
    
    if form.validate_on_submit():
        try:
            # Vérifier que l'utilisateur correspond bien à l'utilisateur connecté
            user = Users.query.filter_by(prenom=form.prenom.data).first()
            
            if not user or user.id != current_user.id:
                flash("Utilisateur introuvable ou vous n'avez pas les droits pour cette action.", "error")
                return redirect(url_for("mon_compte"))
            
            # Vérifier le mot de passe
            if not check_password_hash(user.password, form.password.data):
                flash("Mot de passe incorrect.", "error")
                return render_template("pages/suppression_utilisateur.html", form=form)
            
            # Récupérer l'ID de l'utilisateur avant de le supprimer
            user_id = user.id
            
            # Supprimer d'abord les favoris de l'utilisateur
            db.session.execute(
                relation_user_favori.delete().where(relation_user_favori.c.user_id == user_id)
            )
            
            # Déconnecter l'utilisateur avant suppression
            logout_user()
            
            # Supprimer l'utilisateur
            db.session.delete(user)
            db.session.commit()
            
            flash("Votre compte a été supprimé avec succès.", "success")
            return redirect(url_for("accueil"))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erreur lors de la suppression du compte: {str(e)}", exc_info=True)
            flash(f"Une erreur s'est produite lors de la suppression de votre compte. Veuillez réessayer.", "error")
            return render_template("pages/suppression_utilisateur.html", form=form)
    
    return render_template("pages/suppression_utilisateur.html", form=form)

# Configuration de la vue de connexion pour Flask-Login
login.login_view = 'connexion'