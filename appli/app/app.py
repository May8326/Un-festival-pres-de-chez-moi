from flask import Flask
from flask_sqlalchemy import SQLAlchemy
<<<<<<< HEAD
from config import Config
=======
from .config import Config
from flask_login import LoginManager
>>>>>>> ab1a85728137f90e8ecaab5ebb78f629f57bf985

app = Flask(__name__, template_folder="templates", static_folder='statics')
app.config.from_object(Config)
db = SQLAlchemy(app)
from .routes import generales