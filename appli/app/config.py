import dotenv
import os
from .utils.transformations import to_bool

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv.load_dotenv(os.path.join(BASE_DIR, '.env'))

class Config():
    DEBUG = to_bool(os.environ.get("DEBUG"))
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_ECHO = os.environ.get("SQLALCHEMY_ECHO")
    RESULTATS_PER_PAGE = int(os.environ.get("RESULTATS_PER_PAGE"))
    SECRET_KEY = os.environ.get("SECRET_KEY")  # Utilisé pour les sessions et CSRF
    WTF_CSRF_ENABLED = to_bool(os.environ.get("WTF_CSRF_ENABLED"))
    WTF_CSRF_SECRET_KEY = os.environ.get("WTF_CSRF_SECRET_KEY", os.environ.get("SECRET_KEY"))  # Fallback sur SECRET_KEY
