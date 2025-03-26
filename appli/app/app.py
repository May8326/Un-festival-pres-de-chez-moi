from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
from flask_login import LoginManager
<<<<<<< HEAD

=======
>>>>>>> Mathieu

app = Flask(__name__, template_folder="templates", static_folder='statics')
app.config.from_object(Config)
db = SQLAlchemy(app)
from .routes import generales