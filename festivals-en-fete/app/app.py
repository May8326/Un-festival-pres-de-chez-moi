from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect, CSRFError
from app.config import Config

# Utiliser 'static' comme endpoint et 'statics' comme dossier réel
app = Flask(__name__, template_folder="templates", static_folder='statics', static_url_path='/static')
app.config.from_object(Config)

# Initialisez CSRFProtect
csrf = CSRFProtect(app)

db = SQLAlchemy(app)
login = LoginManager(app)

# Définissez les configurations de login si nécessaire
login.login_view = 'login' 

# Importez les routes APRÈS avoir créé db et login
from .routes import favoris, generales, users, errors, item 

# Importez TOUS les modèles
from app.models import *