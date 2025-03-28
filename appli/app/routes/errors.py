from flask import render_template
from flask_wtf.csrf import CSRFError
from app.app import app

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    """
    Gestionnaire d'erreurs pour les erreurs CSRF.
    Rendu d'une page d'erreur personnalisée.
    """
    return render_template("errors/csrf_error.html", reason=e.description), 400
