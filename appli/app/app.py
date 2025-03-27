from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.config import Config

app = Flask(__name__, template_folder="templates", static_folder='statics')
app.config.from_object(Config)

# Créez les instances avant les importations
db = SQLAlchemy(app)
login = LoginManager(app)

# Définissez les configurations de login si nécessaire
login.login_view = 'login'  # assurez-vous que cette route existe

# Importez les routes APRÈS avoir créé db et login
from .routes import favoris, generales, users