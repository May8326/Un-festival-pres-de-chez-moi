from app.app import db
from app.models.users import Users

# Déclaration des tables de relation
festival_monuments_geopoint = db.Table(
    "festival_monuments_geopoint", db.Model.metadata,
    db.Column('id_monument_historique', db.Integer, db.ForeignKey('lieu_monument_historique.id_monument_historique'), primary_key=True),
    db.Column('id_festival', db.Integer, db.ForeignKey('titre_festival_data_gouv.id_festival'), primary_key=True),
    db.Column('distance', db.Float),
    db.Column('GeoPoint_monument', db.Text(50)),
    db.Column('GeoPoint_festival', db.Text(50))
)

# table de relation many to many pour la gestion des favoris
relation_user_favori = db.Table('relation_user_favori', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('id_festival', db.Integer, db.ForeignKey('titre_festival_data_gouv.id_festival'), primary_key=True),
    db.Column('id_monument_historique', db.Integer, db.ForeignKey('lieu_monument_historique.id_monument_historique'), primary_key=True),
    db.Column('id_commune', db.Integer, db.ForeignKey('communes.id_commune'), primary_key=True)
)


class Commune(db.Model):
    __tablename__ = 'communes'

    id_code_insee_commune = db.Column(db.Integer)
    geocodage_latitude_commune = db.Column(db.Float)
    geocodage_longitude_commune = db.Column(db.Float)
    code_commune = db.Column(db.Integer)
    nom_commune = db.Column(db.String(30))
    code_departement = db.Column(db.Integer)
    nom_departement = db.Column(db.String(30))
    code_region = db.Column(db.Integer)
    nom_region = db.Column(db.String(30))
    id_commune = db.Column(db.Integer, primary_key=True, unique=True)

    lieux_festivals = db.relationship("LieuFestival", back_populates="commune")
    monuments = db.relationship("MonumentHistorique", back_populates="commune", lazy=True)

class Festival(db.Model):
    __tablename__ = 'titre_festival_data_gouv'

    id_festival = db.Column(db.Integer, primary_key=True)
    nom_festival = db.Column(db.String)
    
    contact = db.relationship("ContactFestival", back_populates="festival", uselist=False)
    dates = db.relationship("DateFestival", back_populates="festival", uselist=False)
    lieu = db.relationship("LieuFestival", back_populates="festival", uselist=False)
    type = db.relationship("TypeFestival", back_populates="festival", uselist=False)
    monuments = db.relationship("MonumentHistorique", secondary=festival_monuments_geopoint, back_populates="festivals")

class ContactFestival(db.Model):
    __tablename__ = 'contact_festival'

    id_festival = db.Column(db.Integer, db.ForeignKey('titre_festival_data_gouv.id_festival'), primary_key=True)
    site_internet_festival = db.Column(db.String(30))
    adresse_mail_festival = db.Column(db.String(30))
    
    festival = db.relationship("Festival", back_populates="contact")
    
class DateFestival(db.Model):
    __tablename__ = 'date_festival'

    id_festival = db.Column(db.Integer, db.ForeignKey('titre_festival_data_gouv.id_festival'), primary_key=True)
    annee_creation_festival = db.Column(db.String)
    periode_principale_deroulement_festival = db.Column(db.String)
    
    festival = db.relationship("Festival", back_populates="dates")
    
class LieuFestival(db.Model):
    __tablename__ = 'lieu_festival'

    #id_festival = db.Column(db.Integer, db.ForeignKey('titre_festival_data_gouv.id_festival'), primary_key=True)
    #code_insee_commune_festival = db.Column(db.Integer, db.ForeignKey('communes.id_code_insee_commune'))
    
    # ces trois lignes sont une correction proposée par copilot
    id_lieu_festival = db.Column(db.Integer, primary_key=True)
    id_festival = db.Column(db.Integer, db.ForeignKey('titre_festival_data_gouv.id_festival'))
    id_commune = db.Column(db.Integer, db.ForeignKey('communes.id_commune'))
    
    latitude_festival = db.Column(db.Float)
    longitude_festival = db.Column(db.Float)
    
    festival = db.relationship("Festival", back_populates="lieu")
    # cette ligne est une correction proposée par copilot
    commune = db.relationship("Commune", back_populates="lieux_festivals")
    
class TypeFestival(db.Model):
    __tablename__ = 'type_festival'

    id_festival = db.Column(db.Integer, db.ForeignKey('titre_festival_data_gouv.id_festival'), primary_key=True)
    discipline_dominante_festival = db.Column(db.String)
    
    festival = db.relationship("Festival", back_populates="type")
    
class MonumentHistorique(db.Model):
    __tablename__ = 'lieu_monument_historique'

    id_monument_historique = db.Column(db.Integer, primary_key=True)
    code_insee_edifice_lors_de_protection = db.Column(db.Integer, db.ForeignKey('communes.id_code_insee_commune'))
    latitude_monument_historique = db.Column(db.Float)
    longitude_monument_historique = db.Column(db.Float)
    
    aspects_juridiques = db.relationship("AspectJuridiqueMonumentHistorique", back_populates="monument", uselist=False)
    commune = db.relationship("Commune", back_populates="monuments")
    festivals = db.relationship("Festival", secondary=festival_monuments_geopoint, back_populates="monuments")
    
class AspectJuridiqueMonumentHistorique(db.Model):
    __tablename__ = 'aspect_juridique_monument_historique'
    
    id_monument_historique = db.Column(db.Integer, db.ForeignKey('lieu_monument_historique.id_monument_historique'), primary_key=True)
    statut_juridique_edifice = db.Column(db.String)
    
    monument = db.relationship("MonumentHistorique", back_populates="aspects_juridiques")

"""
class Favoris(db.Model):
    __tablename__ = 'favoris'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.User.id'), nullable=False)
    festival_id = db.Column(db.Integer, db.ForeignKey('titre_festival_data_gouv.id_festival'), nullable=True)
    monument_id = db.Column(db.Integer, db.ForeignKey('lieu_monument_historique.id_monument_historique'), nullable=True)

    user = db.relationship("User", back_populates="favoris")
    festival = db.relationship("Festival", back_populates="favoris")
    monument = db.relationship("MonumentHistorique", back_populates="favoris")
"""