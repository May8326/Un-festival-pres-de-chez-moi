from app.app import db
"""
Structure de la base de données :
Cette base de données est conçue pour gérer des informations sur les festivals, les monuments historiques et leurs relations avec les communes et les utilisateurs. Voici un aperçu de la structure :
1. Commune :
    - Représente une commune géographique avec des attributs tels que le nom, le département, la région et la géolocalisation.
    - Relations :
      - lieux_festivals : Lien vers les festivals organisés dans la commune.
      - monuments : Lien vers les monuments historiques situés dans la commune.
2. Festival :
    - Représente un festival avec des attributs tels que le nom et des relations avec ses contacts, dates, emplacement, type et monuments associés.
    - Relations :
      - contact : Informations de contact du festival.
      - dates : Informations liées aux dates du festival.
      - lieu : Détails sur l'emplacement du festival.
      - type : Type et catégorie du festival.
      - monuments : Relation many-to-many avec les monuments historiques.
3. ContactFestival :
    - Stocke les informations de contact d'un festival, telles que le site web et l'email.
    - Relation :
      - festival : Lien vers le festival associé.
4. DateFestival :
    - Stocke les informations liées aux dates d'un festival, telles que l'année de création et la période principale de déroulement.
    - Relation :
      - festival : Lien vers le festival associé.
5. LieuFestival :
    - Représente l'emplacement d'un festival, y compris la géolocalisation et les détails de l'adresse.
    - Relations :
      - festival : Lien vers le festival associé.
      - commune : Lien vers la commune où le festival est organisé.
6. TypeFestival :
    - Représente le type et les sous-catégories d'un festival, comme la discipline dominante et les catégories spécifiques.
    - Relation :
      - festival : Lien vers le festival associé.
7. MonumentHistorique :
    - Représente un monument historique avec des attributs tels que le nom, l'adresse, la géolocalisation et la commune associée.
    - Relations :
      - aspects_juridiques : Aspects juridiques du monument.
      - commune : Lien vers la commune où le monument est situé.
      - festivals : Relation many-to-many avec les festivals.
      - contact : Informations de contact du monument.
      - dates : Informations liées aux dates du monument.
      - personnes : Personnes associées au monument.
      - types : Type et classification du monument.
8. AspectJuridiqueMonumentHistorique :
    - Stocke les informations juridiques sur un monument historique, comme son statut juridique.
    - Relation :
      - monument : Lien vers le monument associé.
9. ContactMonumentHistorique :
    - Stocke les informations de contact d'un monument historique, comme des liens externes.
    - Relation :
      - monument : Lien vers le monument associé.
10. DateMonumentHistorique :
     - Stocke les informations liées aux dates d'un monument historique, comme les dates de construction et de protection.
     - Relation :
        - monument : Lien vers le monument associé.
11. PersonneMonumentHistorique :
     - Représente les personnes associées à un monument historique, comme les auteurs ou les individus liés.
     - Relation :
        - monument : Lien vers le monument associé.
12. TypeMonumentHistorique :
     - Représente le type et la classification d'un monument historique, comme son domaine et sa dénomination.
     - Relation :
        - monument : Lien vers le monument associé.
13. festival_monuments_geopoint :
     - Une table de relation many-to-many reliant les festivals et les monuments historiques, avec des attributs supplémentaires comme la distance et les points de géolocalisation.
14. relation_user_favori :
     - Une table de relation many-to-many pour gérer les favoris des utilisateurs, reliant les utilisateurs aux festivals, monuments ou communes.
"""
# Déclaration des tables de relation
festival_monuments_geopoint = db.Table(
    "festival_monuments_geopoint", db.Model.metadata,
    db.Column('id_monument_historique', db.Integer, db.ForeignKey('lieu_monument_historique.id_monument_historique'), primary_key=True),
    db.Column('id_festival', db.Integer, db.ForeignKey('titre_festival_data_gouv.id_festival'), primary_key=True),
    db.Column('distance', db.Float),
    db.Column('GeoPoint_monument', db.Text(50)),
    db.Column('GeoPoint_festival', db.Text(50))
)

# Table de relation many-to-many pour la gestion des favoris
relation_user_favori = db.Table(
    'relation_user_favori', db.Model.metadata,
    db.Column('id_relation', db.Integer, primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), nullable=False),
    db.Column('id_festival', db.Integer, db.ForeignKey('titre_festival_data_gouv.id_festival'), nullable=True),  # Permet NULL
    db.Column('id_monument_historique', db.Integer, db.ForeignKey('lieu_monument_historique.id_monument_historique'), nullable=True),  # Permet NULL
    db.Column('id_commune', db.Integer, db.ForeignKey('communes.id_commune'), nullable=True)  # Permet NULL
)

class Commune(db.Model):
    __tablename__ = 'communes'

    id_code_insee_commune = db.Column(db.Integer)
    geocodage_latitude_commune = db.Column(db.Float)
    geocodage_longitude_commune = db.Column(db.Float)
    code_commune = db.Column(db.Integer)
    nom_commune = db.Column(db.Text(30), index=True)  # Assurez-vous que c'est du texte
    code_departement = db.Column(db.Integer)
    nom_departement = db.Column(db.Text(30))
    code_region = db.Column(db.Integer)
    nom_region = db.Column(db.Text(30))
    id_commune = db.Column(db.Integer, primary_key=True, unique=True, index=True)

    # Spécifiez explicitement la clé étrangère utilisée
    lieux_festivals = db.relationship(
        "LieuFestival",
        back_populates="commune",
        foreign_keys="LieuFestival.id_commune"
    )
    monuments = db.relationship(
        "MonumentHistorique",
        back_populates="commune",
        foreign_keys="MonumentHistorique.id_commune"
    )

class Festival(db.Model):
    __tablename__ = 'titre_festival_data_gouv'

    id_festival = db.Column(db.Integer, primary_key=True, index=True)
    nom_festival = db.Column(db.Text, index=True)  # Assurez-vous que c'est du texte
    
    contact = db.relationship("ContactFestival", back_populates="festival", uselist=False)
    dates = db.relationship("DateFestival", back_populates="festival", uselist=False)
    lieu = db.relationship("LieuFestival", back_populates="festival", uselist=False)
    type = db.relationship("TypeFestival", back_populates="festival", uselist=False)
    monuments = db.relationship("MonumentHistorique", secondary=festival_monuments_geopoint, back_populates="festivals")

class ContactFestival(db.Model):
    __tablename__ = 'contact_festival'

    id_festival = db.Column(db.Integer, db.ForeignKey('titre_festival_data_gouv.id_festival'), primary_key=True)
    site_internet_festival = db.Column(db.Text(30))
    adresse_mail_festival = db.Column(db.Text(30))
    
    festival = db.relationship("Festival", back_populates="contact")
    
class DateFestival(db.Model):
    __tablename__ = 'date_festival'

    id_festival = db.Column(db.Integer, db.ForeignKey('titre_festival_data_gouv.id_festival'), primary_key=True)
    annee_creation_festival = db.Column(db.Text)
    periode_principale_deroulement_festival = db.Column(db.Text)
    decennie_creation_festival = db.Column(db.Text)

    festival = db.relationship("Festival", back_populates="dates")
    
class LieuFestival(db.Model):
    __tablename__ = 'lieu_festival'
  
    id_festival = db.Column(db.Integer, db.ForeignKey('titre_festival_data_gouv.id_festival'), primary_key=True)
    envergure_territoriale_festival = db.Column(db.Text(50))
    code_insee_commune_festival = db.Column(db.Integer, db.ForeignKey('communes.id_code_insee_commune'))
    adresse_postale_festival = db.Column(db.Text(50))
    complement_adresse_festival = db.Column(db.Text(50))
    geocodage_xy_festival = db.Column(db.Float)
    latitude_festival = db.Column(db.Float)
    longitude_festival = db.Column(db.Float)
    id_commune = db.Column(db.Integer, db.ForeignKey('communes.id_commune'), index=True)
    GeoPoint_festival = db.Column(db.Text(50))
    
    festival = db.relationship("Festival", back_populates="lieu")
    # Spécifiez explicitement la clé étrangère utilisée
    commune = db.relationship(
        "Commune",
        back_populates="lieux_festivals",
        foreign_keys=[id_commune]
    )
    
class TypeFestival(db.Model):
    __tablename__ = 'type_festival'

    id_festival = db.Column(db.Integer, db.ForeignKey('titre_festival_data_gouv.id_festival'), primary_key=True)
    discipline_dominante_festival = db.Column(db.Text(50), index=True)  # Ajout d'index
    sous_categorie_spectacle_vivant = db.Column(db.Text(50))
    sous_categorie_musique = db.Column(db.Text(50))
    sous_categorie_cinema_et_audiovisuel = db.Column(db.Text(50))
    sous_categorie_arts_visuels_et_numeriques = db.Column(db.Text(50))
    sous_categorie_livre_et_litterature = db.Column(db.Text(50))

    
    festival = db.relationship("Festival", back_populates="type")
    
class MonumentHistorique(db.Model):
    __tablename__ = 'lieu_monument_historique'

    id_monument_historique = db.Column(db.Integer, primary_key=True)
    adresse_edifice_forme_index = db.Column(db.Text(50))
    code_insee_edifice_lors_de_protection = db.Column(db.Integer, db.ForeignKey('communes.id_code_insee_commune'))
    titre_editorial_de_la_notice = db.Column(db.Text(50))  # Colonne réelle dans la base de données
    geocodage_xy_monument_historique = db.Column(db.Float(50))
    latitude_monument_historique = db.Column(db.Float)
    longitude_monument_historique = db.Column(db.Float)
    id_commune = db.Column(db.Integer, db.ForeignKey('communes.id_commune'))
    GeoPoint_monument = db.Column(db.Text(50))

    # Alias pour titre_editorial_de_la_notice
    @property
    def nom_monument(self):
        return self.titre_editorial_de_la_notice

    aspects_juridiques = db.relationship("AspectJuridiqueMonumentHistorique", back_populates="monument", uselist=False)
    commune = db.relationship(
        "Commune",
        back_populates="monuments",
        foreign_keys=[id_commune]
    )
    festivals = db.relationship("Festival", secondary=festival_monuments_geopoint, back_populates="monuments")  
    contact = db.relationship("ContactMonumentHistorique", back_populates="monument", uselist=False)   
    dates = db.relationship("DateMonumentHistorique", back_populates="monument", uselist=False) 
    personnes = db.relationship("PersonneMonumentHistorique", back_populates="monument", uselist=False)
    types = db.relationship("TypeMonumentHistorique", back_populates="monument", uselist=False)

class AspectJuridiqueMonumentHistorique(db.Model):
    __tablename__ = 'aspect_juridique_monument_historique'
    
    id_monument_historique = db.Column(db.Integer, db.ForeignKey('lieu_monument_historique.id_monument_historique'), primary_key=True)
    statut_juridique_edifice = db.Column(db.Text)
    precision_sur_statut_edifice = db.Column(db.Text(50))

    
    monument = db.relationship("MonumentHistorique", back_populates="aspects_juridiques")

class ContactMonumentHistorique(db.Model):
    __tablename__ = 'contact_monument_historique'

    id_monument_historique = db.Column(db.Integer, db.ForeignKey('lieu_monument_historique.id_monument_historique'), primary_key=True)
    lien_internet_externe = db.Column(db.Text(50))
    lien_internet_vers_base_archiv_mh = db.Column(db.Text(50))
    lien_internet_vers_base_palissy = db.Column(db.Text(50))
    
    monument = db.relationship("MonumentHistorique", back_populates="contact")

class DateMonumentHistorique(db.Model):
    __tablename__ = 'date_monument_historique'

    datation_edifice = db.Column(db.Text(50))
    date_et_typologie_de_protection = db.Column(db.Text(50))
    historique = db.Column(db.Text(50))
    siecle_campagne_secondaire_de_construction = db.Column(db.Text(50))
    siecle_construction_forme_abregee = db.Column(db.Text(50))
    id_monument_historique = db.Column(db.Integer, db.ForeignKey('lieu_monument_historique.id_monument_historique'), primary_key=True)
    
    monument = db.relationship("MonumentHistorique", back_populates="dates")

class PersonneMonumentHistorique(db.Model):
    __tablename__ = 'personne_monument_historique'

    auteur_edifice = db.Column(db.Text(50))
    personne_liee_a_edifice = db.Column(db.Text(50))
    id_monument_historique = db.Column(db.Integer, db.ForeignKey('lieu_monument_historique.id_monument_historique'), primary_key=True)
    
    monument = db.relationship("MonumentHistorique", back_populates="personnes")

class TypeMonumentHistorique(db.Model):
    __tablename__ = 'type_monument_historique'

    id_monument_historique = db.Column(db.Integer, db.ForeignKey('lieu_monument_historique.id_monument_historique'), primary_key=True)
    destination_actuelle_edifice = db.Column(db.Text(50))
    denomination_edifice = db.Column(db.Text(50))
    domaine_edifice = db.Column(db.Text(50))
    precision_sur_protection_edifice = db.Column(db.Text(50))
    
    monument = db.relationship("MonumentHistorique", back_populates="types")