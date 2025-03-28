from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, TextAreaField, PasswordField, SubmitField, FloatField
from wtforms.validators import DataRequired, Length, Email, Optional

class RechercheFestivalMonument(FlaskForm):
    nom = StringField("Nom", validators=[DataRequired(), Length(min=2, max=100)])
    type = SelectField('Type', choices=[('festival', 'Festival'), ('monument', 'Monument')])
    submit = SubmitField('Rechercher')

class AjoutFavori(FlaskForm):
    nom = StringField("Nom", validators=[DataRequired(), Length(min=2, max=100)])
    type = SelectField('Type', choices=[('festival', 'Festival'), ('monument', 'Monument')])
    submit = SubmitField('Ajouter aux favoris')

class ModificationFavori(FlaskForm):
    ancien_nom = StringField("Ancien Nom", validators=[DataRequired(), Length(min=2, max=100)])
    nouveau_nom = StringField("Nouveau Nom", validators=[DataRequired(), Length(min=2, max=100)])
    type = SelectField('Type', choices=[('festival', 'Festival'), ('monument', 'Monument')])
    submit = SubmitField('Modifier le favori')

class SuppressionFavori(FlaskForm):
    nom = StringField("Nom", validators=[DataRequired(), Length(min=2, max=100)])
    type = SelectField('Type', choices=[('festival', 'Festival'), ('monument', 'Monument')])
    submit = SubmitField('Supprimer des favoris')

class AjoutUtilisateur(FlaskForm):
    prenom = StringField("Prénom", validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Ajouter l\'utilisateur')

class ModificationUtilisateur(FlaskForm):
    prenom = StringField("Prénom", validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField("Email", validators=[Optional(), Email()])
    password = PasswordField("Mot de passe", validators=[Optional(), Length(min=6)])
    submit = SubmitField('Modifier l\'utilisateur')
class SuppressionUtilisateur(FlaskForm):
    prenom = StringField("Prénom", validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField("Mot de passe", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Supprimer l\'utilisateur')

class Connexion(FlaskForm):
    prenom = StringField("Prénom", validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField("Mot de passe", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Se connecter')
#tentative de formulaire multifacette pr trouver un festival

"""
class Recherche(FlaskForm):
    nom = StringField("Nom du festival", validators=[Optional(), Length(min=2, max =50)])
    #potentiellement transformer les selectfield qui suivent en radiofield selon comment ça se présente au final
    periode = SelectField("Période", choices=[('avant','Avant-Saison (1 Janvier-20 Juin)'),('saison','Saison (21 Juin-5 Septembre)'),('apres','Après-saison (6 septembre - 31 décembre)')], validators=[DataRequired(), Length(min=5)])
    discipline = SelectField('Discipline', choices =[('arts_visu','Arts visuels, arts numériques'),("cinema","Cinéma, audiovisuel"), ("livres","Livre, Littérature"),("musique","Musique"),("spectacle_vivant","Spectacle vivant"),("autre","Autres"), ("tout", Tout")], validators=[Optional()])
    lieu = StringField('Lieu', validators=[Optional()])
    if lieu:
        dist=FloatField('Distance maximum', validators=[DataRequired()])
"""

# correction proposée par Copilot
class Recherche(FlaskForm):
    nom = StringField("Nom du festival", validators=[Optional(), Length(min=2, max=50)])
    periode = SelectMultipleField("Période", choices=[
        ('avant', 'Avant-Saison (1 Janvier-20 Juin)'),
        ('saison', 'Saison (21 Juin-5 Septembre)'),
        ('apres', 'Après-saison (6 septembre - 31 décembre)')
    ], validators=[Optional()])
    discipline = SelectMultipleField('Discipline', choices=[
        ('arts_visu', 'Arts visuels, arts numériques'),
        ("cinema", "Cinéma, audiovisuel"),
        ("livre", "Livre, littérature"),
        ("musique", "Musique"),
        ("spectacle_vivant", "Spectacle vivant"),
        ("autre", "Autres")
    ], validators=[Optional()])
    lieu = StringField('Lieu', validators=[Optional()])
    dist = FloatField('Distance maximum', validators=[Optional()])