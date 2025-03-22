from ..app import app, db

# Déclaration des tables de relation
festival_monuments_geopoint = db.Table(
    "festival_monuments_geopoint", db.Model.metadata,
    db.Column('id_monument_historique', db.Integer, db.ForeignKey('lieu_monument_historique.id_monument_historique'), primary_key=True),
    db.Column('id_festival', db.Integer, db.ForeignKey('titre_festival_data_gouv.id_festival'), primary_key=True),
    db.Column('distance', db.Float)
)

class Commune(db.Model):
    __tablename__ = 'correspondance_communes'

    id_commune = db.Column(db.Integer, primary_key=True, unique=True)
    code_commune_INSEE = db.Column(db.Integer)
    code_postal = db.Column(db.Integer)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    nom_commune = db.Column(db.String(30))
    nom_commune_complet = db.Column(db.String(30))
    code_departement = db.Column(db.Integer)
    nom_departement = db.Column(db.String(30))
    code_region = db.Column(db.Integer)
    nom_region = db.Column(db.String(30))

    festivals = db.relationship("LieuFestival", backref="commune", lazy=True)
    monuments = db.relationship("LieuMonumentHistorique", backref="commune", lazy=True)

class Festival(db.Model):
    __tablename__ = 'titre_festival_data_gouv'

    id_festival = db.Column(db.Integer, primary_key=True)
    nom_festival = db.Column(db.String)
    
    contact = db.relationship("ContactFestival", backref="festival", uselist=False)
    dates = db.relationship("DateFestival", backref="festival", uselist=False)
    lieu = db.relationship("LieuFestival", backref="festival", uselist=False)
    type = db.relationship("TypeFestival", backref="festival", uselist=False)
    monuments = db.relationship("MonumentHistorique", secondary=festival_monuments_geopoint, backref="festivals")

class ContactFestival(db.Model):
    __tablename__ = 'contact_festival'

    id_festival = db.Column(db.Integer, db.ForeignKey('titre_festival_data_gouv.id_festival'))
    site_internet_festival = db.Column(db.String(30))
    adresse_mail_festival = db.Column(db.String(30))
    
    festival = db.relationship("Festival", backref="contact")
    
class DateFestival(db.Model):
    __tablename__ = 'date_festival'

    id_festival = db.Column(db.Integer, db.ForeignKey('titre_festival_data_gouv.id_festival'), primary_key=True)
    annee_creation_festival = db.Column(db.String)
    periode_principale_deroulement_festival = db.Column(db.String)
    
    festival = db.relationship("Festival", backref="dates")
    
class LieuFestival(db.Model):
    __tablename__ = 'lieu_festival'

    id_festival = db.Column(db.Integer, db.ForeignKey('titre_festival_data_gouv.id_festival'), primary_key=True)
    code_insee_commune_festival = db.Column(db.Integer, db.ForeignKey('correspondance_communes.code_commune_INSEE'))
    latitude_festival = db.Column(db.Float)
    longitude_festival = db.Column(db.Float)
    
    festival = db.relationship("Festival", backref="lieu")
    commune = db.relationship("Commune", backref="festivals")
    
class TypeFestival(db.Model):
    __tablename__ = 'type_festival'

    id_festival = db.Column(db.Integer, db.ForeignKey('titre_festival_data_gouv.id_festival'), primary_key=True)
    discipline_dominante_festival = db.Column(db.String)
    
    festival = db.relationship("Festival", backref="type")
    
class MonumentHistorique(db.Model):
    __tablename__ = 'lieu_monument_historique'

    id_monument_historique = db.Column(db.Integer, primary_key=True)
    code_insee_edifice_lors_de_protection = db.Column(db.Integer, db.ForeignKey('correspondance_communes.code_commune_INSEE'))
    latitude_monument_historique = db.Column(db.Float)
    longitude_monument_historique = db.Column(db.Float)
    
    aspects_juridiques = db.relationship("AspectJuridiqueMonumentHistorique", backref="monument", uselist=False)
    commune = db.relationship("Commune", backref="monuments")
    festivals = db.relationship("Festival", secondary=festival_monument_relation, backref="monuments")
    
class AspectJuridiqueMonumentHistorique(db.Model):
    __tablename__ = 'aspect_juridique_monument_historique'
    
    id_monument_historique = db.Column(db.Integer, db.ForeignKey('lieu_monument_historique.id_monument_historique'), primary_key=True)
    statut_juridique_edifice = db.Column(db.String)
    
    monument = db.relationship("MonumentHistorique", backref="aspects_juridiques")
