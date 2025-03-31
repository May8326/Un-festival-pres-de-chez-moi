from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from app.config import Config
import jinja2
import logging


# Pour désactiver complètement les logs, décommentez cette ligne:
# logging.getLogger().setLevel(logging.CRITICAL)

# Initialisation de l'application Flask
app = Flask(__name__, template_folder="templates", static_folder='statics', static_url_path='/static')
app.config.from_object(Config)

# Initialisation des extensions
csrf = CSRFProtect(app)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'

# Configuration de Jinja pour gérer les erreurs de variables indéfinies
app.jinja_env.undefined = jinja2.StrictUndefined

# Importation des routes et blueprints
from .routes import favoris, generales, users, item, errors

# Enregistrement du blueprint d'erreurs
from .routes.errors import error_bp
app.register_blueprint(error_bp)

# Importation des modèles
from app.models import *