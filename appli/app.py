from flask import Flask
from flask_sqlalchemy import SQLALCHEMY
from .config import Config

app = Flask(__name__, template_folder="templates", static_folder='statics')
app.config.from_object(Config)