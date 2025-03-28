from app.app import db, login, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import or_
from flask import flash

# Définition de la classe Users qui représente la table "users" dans la base de données
class Users(db.Model, UserMixin):
    __tablename__ = "users"  # Nom de la table dans la base de données

    # Définition des colonnes de la table
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)  # Identifiant unique
    prenom = db.Column(db.Text, nullable=False)  # Prénom de l'utilisateur
    password = db.Column(db.String(100), nullable=False)  # Mot de passe (haché)
    email = db.Column(db.String(30), nullable=True, unique=True)  # Adresse e-mail (optionnelle et unique)

    # Relation many-to-many avec la table "Festival" via une table d'association
    favoris = db.relationship(
        'Festival', 
        secondary='relation_user_favori', 
        backref='utilisateurs_favoris'
    )

    # Méthode statique pour l'identification d'un utilisateur
    @staticmethod
    def identification(identifier, password):
        """
        Permet l'identification par prénom ou adresse e-mail.
        """
        # Recherche d'un utilisateur par prénom ou e-mail
        utilisateur = Users.query.filter(
            or_(Users.prenom == identifier, Users.email == identifier)
        ).first()
        # Vérification du mot de passe
        if utilisateur and check_password_hash(utilisateur.password, password):
            flash("Vous êtes connecté", "success")  # Message de succès
            return utilisateur
        else:
            flash("Identifiant ou mot de passe incorrect", "error")  # Message d'erreur
            return None

    # Méthode statique pour ajouter un nouvel utilisateur
    @staticmethod
    def ajout(prenom, password, email=None):
        """
        Ajoute un nouvel utilisateur avec un prénom, un mot de passe et une adresse e-mail optionnelle.
        """
        erreurs = []  # Liste pour stocker les erreurs

        # Vérification des champs
        if not prenom:
            erreurs.append("Le prénom est vide")
        if not password or len(password) < 6:
            erreurs.append("Le mot de passe est vide ou trop court")
        if email and "@" not in email:
            erreurs.append("L'adresse e-mail est invalide")

        # Vérification de l'unicité du prénom
        unique_prenom = Users.query.filter(Users.prenom == prenom).count()
        if unique_prenom > 0:
            erreurs.append("Le prénom existe déjà")

        # Vérification de l'unicité de l'e-mail
        if email:
            unique_email = Users.query.filter(Users.email == email).count()
            if unique_email > 0:
                erreurs.append("L'adresse e-mail existe déjà")

        # Si des erreurs sont présentes, retourner False et la liste des erreurs
        if len(erreurs) > 0:
            return False, erreurs
        
        # Création d'un nouvel utilisateur
        utilisateur = Users(
            prenom=prenom,
            password=generate_password_hash(password),  # Hachage du mot de passe
            email=email
        )

        # Ajout de l'utilisateur à la base de données
        try:
            db.session.add(utilisateur)
            db.session.commit()
            return True, utilisateur  # Retourne True et l'utilisateur créé
        except Exception as erreur:
            db.session.rollback()  # Annule les changements en cas d'erreur
            return False, [str(erreur)]  # Retourne False et l'erreur

    # Méthode pour obtenir l'identifiant de l'utilisateur (nécessaire pour Flask-Login)
    def get_id(self):
        return str(self.id)  # Convertir en chaîne pour Flask-Login
    
# Fonction pour charger un utilisateur par son identifiant (nécessaire pour Flask-Login)
@login.user_loader
def load_by_id(id):
    return Users.query.get(int(id))

# Création des tables dans la base de données
with app.app_context():
     db.create_all()