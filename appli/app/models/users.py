#from ..app import app
from app.app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import ForeignKey, Column, Integer, String, Text, Table
from app.models.database import relation_user_favori
from flask import flash

class Users(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    prenom = db.Column(db.Text, nullable=False)
    password = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(30), nullable=True, unique=True)

    # Relation many to many avec les festivals (favoris)
    favoris = db.relationship(
        'Festival', 
        secondary=relation_user_favori, 
        backref='utilisateurs_favoris'
        
    )


    @staticmethod
    def identification(identifier, password):
        """
        Permet l'identification par prénom ou adresse e-mail.
        """
        utilisateur = Users.query.filter(
            db.or_(Users.prenom == identifier, Users.email == identifier)
        ).first()
        if utilisateur and check_password_hash(utilisateur.password, password):
            flash("Vous êtes connecté", "success")
            return utilisateur
        
        else:
            flash("Identifiant ou mot de passe incorrect", "error")
            return None

    @staticmethod
    def ajout(prenom, password, email=None):
        """
        Ajoute un nouvel utilisateur avec un prénom, un mot de passe et une adresse e-mail optionnelle.
        """
        erreurs = []
        if not prenom:
            erreurs.append("Le prénom est vide")
        if not password or len(password) < 6:
            erreurs.append("Le mot de passe est vide ou trop court")
        if email and not "@" in email:
            erreurs.append("L'adresse e-mail est invalide")

        unique_prenom = Users.query.filter(Users.prenom == prenom).count()
        if unique_prenom > 0:
            erreurs.append("Le prénom existe déjà")

        if email:
            unique_email = Users.query.filter(Users.email == email).count()
            if unique_email > 0:
                erreurs.append("L'adresse e-mail existe déjà")

        if len(erreurs) > 0:
            return False, erreurs
        
        utilisateur = Users(
            prenom=prenom,
            password=generate_password_hash(password),
            email=email
        )

        try:
            db.session.add(utilisateur)
            db.session.commit()
            return True, utilisateur
        except Exception as erreur:
            return False, [str(erreur)]
        
    def get_id(self):
        return self.id
    
@login.user_loader
def load_by_id(id):
    return Users.query.get(int(id))