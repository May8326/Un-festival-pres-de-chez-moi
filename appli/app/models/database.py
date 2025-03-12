from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Association Tables
festival_commune = db.Table(
    'festival_commune',
    db.Column('id_festival', db.Integer, db.ForeignKey('festival.id'), primary_key=True),
    db.Column('id_commune', db.Integer, db.ForeignKey('commune.id'), primary_key=True)
)

class Commune(db.Model):
    __tablename__ = 'commune'
    id = db.Column(db.Integer, primary_key=True)
    code_insee = db.Column(db.Integer, unique=True, nullable=False)
    nom = db.Column(db.String(255), nullable=False)
    code_departement = db.Column(db.Integer)
    code_region = db.Column(db.Integer)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    festivals = db.relationship('Festival', secondary=festival_commune, back_populates='communes')

class Festival(db.Model):
    __tablename__ = 'festival'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(255), nullable=False)
    annee_creation = db.Column(db.String(10))
    periode_principale = db.Column(db.String(100))
    discipline_dominante = db.Column(db.String(255))

    communes = db.relationship('Commune', secondary=festival_commune, back_populates='festivals')

class MonumentHistorique(db.Model):
    __tablename__ = 'monument_historique'
    id = db.Column(db.Integer, primary_key=True)
    denomination = db.Column(db.String(255))
    domaine = db.Column(db.String(255))
    statut_juridique = db.Column(db.String(255))
    precision_protection = db.Column(db.String(255))
    siecle_construction = db.Column(db.String(50))
    historique = db.Column(db.Text)
    auteur = db.Column(db.String(255))
    adresse = db.Column(db.String(255))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    id_commune = db.Column(db.Integer, db.ForeignKey('commune.id'))

    commune = db.relationship('Commune', back_populates='monuments')

Commune.monuments = db.relationship('MonumentHistorique', back_populates='commune')
