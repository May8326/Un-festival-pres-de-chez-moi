#from ..app import app
from app.app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import ForeignKey
from app.models.database import relation_user_favori

class Users(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    prenom = db.Column(db.Text, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    # Relation many to many avec les festivals (favoris)
    favoris = db.relationship(
        'Festival', 
        secondary=relation_user_favori, 
        backref='utilisateurs_favoris'
        
    )


    @staticmethod
    def identification(prenom, password):
        utilisateur = Users.query.filter(Users.prenom == prenom).first()
        if utilisateur and check_password_hash(utilisateur.password, password):
            return utilisateur
        return None

    @staticmethod
    def ajout(prenom, password):
        erreurs = []
        if not prenom:
            erreurs.append("Le prénom est vide")
        if not password or len(password) < 6:
            erreurs.append("Le mot de passe est vide ou trop court")

        unique = Users.query.filter(
            db.or_(Users.prenom == prenom)
        ).count()
        if unique > 0:
            erreurs.append("Le prénom existe déjà")

        if len(erreurs) > 0:
            return False, erreurs
        
        utilisateur = Users(
            prenom=prenom,
            password=generate_password_hash(password)
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