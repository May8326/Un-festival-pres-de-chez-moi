from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, TextAreaField, PasswordField, SubmitField, FloatField
from wtforms.validators import DataRequired, Length, Email, Optional

class RechercheFestivalMonument(FlaskForm):
    nom = StringField("Nom", validators=[DataRequired(), Length(min=2, max=100)])
    type = SelectField('Type', choices=[('festival', 'Festival'), ('monument', 'Monument')])
    submit = SubmitField('Rechercher')

class AjoutFavori(FlaskForm):
    nom = StringField("Nom", validators=[DataRequired(), Length(min=2, max=100)])
    type = SelectField('Type', choices=[('festival', 'Festival'), ('monument', 'Monument'), ('commune', 'Commune')])
    submit = SubmitField('Ajouter aux favoris')

class ModificationFavori(FlaskForm):
    ancien_nom = StringField("Ancien Nom", validators=[DataRequired(), Length(min=2, max=100)])
    nouveau_nom = StringField("Nouveau Nom", validators=[DataRequired(), Length(min=2, max=100)])
    type = SelectField('Type', choices=[('festival', 'Festival'), ('monument', 'Monument')])
    submit = SubmitField('Modifier le favori')

class SuppressionFavori(FlaskForm):
    nom = StringField("Nom", validators=[DataRequired(), Length(min=2, max=100)])
    type = SelectField('Type', choices=[('festival', 'Festival'), ('monument', 'Monument'), ('commune', 'Commune')])
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

class Recherche(FlaskForm):
    nom = StringField("Nom du festival", validators=[Optional(), Length(min=2, max=50)])
    periode = SelectField("Période", choices=[
        ('Avant-Saison (1 Janvier - 20 Juin)', 'Avant-Saison (1 Janvier-20 Juin)'),
        ('Saison (21 Juin - 5 Septembre)', 'Saison (21 Juin-5 Septembre)'),
        ('Après-saison (6 septembre - 31 décembre)', 'Après-saison (6 septembre - 31 décembre)'),
        ('',''),
    ], validators=[Optional()])
    discipline = SelectField('Discipline', choices=[
        ('Arts visuels, arts numériques', 'Arts visuels, arts numériques'),
        ("Cinéma, audiovisuel", "Cinéma, audiovisuel"),
        ("Livre, littérature", "Livre, littérature"),
        ("Musique", "Musique"),
        ("Spectacle vivant", "Spectacle vivant"),
        ("Autre", "Pluridisciplinaire"),
        ('',''),
    ], validators=[Optional()])
    lieu = StringField('Lieu', validators=[Optional()])
    dist = FloatField('Distance maximum', validators=[Optional()])
