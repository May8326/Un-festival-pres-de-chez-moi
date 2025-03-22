
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, TextAreaField, PasswordField, SubmitField
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
#tentative de formulaire multifacette pr trouver un festival
class Recherche(FlaskForm):
    nom = StringField("Nom du festival", validators=[Optional(), Length(min=2, max =50)])
    #potentiellement transformer les selectfield qui suivent en radiofield selon comment ça se présente au final
    periode = SelectField('Période', choices=[('avant','Avant-Saison (1 Janvier-20 Juin)')('saison','Saison (21 Juin-5 Septembre)')('apres','Après-saison (6 septembre - 31 décembre)')] validators=[DataRequired()])
    discipline = SelectField('Discipline', choices =[('arts_visu','Arts visuels, arts numériques'),("cinema","Cinémna et audiovisuel"), ("livres","Livres et littérature"),("musique","Musique"),("spectacle_vivant","Spectacle vivant"),("autre","Autres")], validators=[Optional()])
    lieu = StringField('Lieu', validators=[Optional()])
    #réfléchir avant de faire les lieux