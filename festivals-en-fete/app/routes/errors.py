"""Module de gestion des erreurs pour l'application."""

from flask import render_template, Blueprint
from flask_wtf.csrf import CSRFError
import jinja2
from ..utils.error_messages import HTTP_ERRORS, SYSTEM_ERRORS, FORM_ERRORS
from flask_wtf import FlaskForm
import logging
from functools import wraps

# Création d'un blueprint pour les erreurs
error_bp = Blueprint('errors', __name__)

# Configuration des messages d'erreur pour WTForms
FlaskForm.Meta.error_messages = {
    'csrf_token_missing': FORM_ERRORS.get('required', 'Ce champ est obligatoire.'),
    'csrf_token_expired': 'Le formulaire a expiré. Veuillez soumettre à nouveau.',
    'csrf_token_invalid': 'Problème de sécurité détecté. Veuillez réessayer.'
}

# Gestionnaires d'erreurs HTTP standards
@error_bp.app_errorhandler(404)
def page_not_found(e):
    """Gestion de l'erreur 404 (page non trouvée)."""
    return render_template('errors/error.html', 
                           code=404, 
                           message=HTTP_ERRORS[404]), 404

@error_bp.app_errorhandler(500)
def internal_server_error(e):
    """Gestion de l'erreur 500 (erreur interne du serveur)."""
    return render_template('errors/error.html', 
                           code=500, 
                           message=HTTP_ERRORS[500]), 500

@error_bp.app_errorhandler(403)
def forbidden(e):
    """Gestion de l'erreur 403 (accès interdit)."""
    return render_template('errors/error.html', 
                           code=403, 
                           message=HTTP_ERRORS[403]), 403

@error_bp.app_errorhandler(400)
def bad_request(e):
    """Gestion de l'erreur 400 (requête incorrecte)."""
    return render_template('errors/error.html', 
                           code=400, 
                           message=HTTP_ERRORS[400]), 400

# Gestion des erreurs CSRF
@error_bp.app_errorhandler(CSRFError)
def handle_csrf_error(e):
    """Gestion des erreurs CSRF."""
    return render_template('errors/error.html',
                           code=400,
                           message="Erreur de sécurité : jeton CSRF invalide. Veuillez réessayer."), 400

# Gestion des erreurs de template Jinja
@error_bp.app_errorhandler(jinja2.exceptions.TemplateError)
def handle_jinja_error(e):
    """Gestion des erreurs de template Jinja."""
    return render_template('errors/error.html',
                           code=500,
                           message="Erreur de template : problème d'affichage de la page. Nos équipes ont été informées."), 500

@error_bp.app_errorhandler(jinja2.exceptions.TemplateNotFound)
def handle_template_not_found(e):
    """Gestion des erreurs de template non trouvé."""
    return render_template('errors/error.html',
                           code=404,
                           message="Template non trouvé : la page demandée n'existe pas."), 404

# Décorateur pour enregistrer les erreurs
def log_exception(f):
    @wraps(f)
    def decorated_function(e):
        # Enregistrer l'erreur dans le journal
        logging.exception(f"Exception non gérée: {str(e)}")
        return f(e)
    return decorated_function

# Mettre à jour le gestionnaire d'exception global avec le décorateur
@error_bp.app_errorhandler(Exception)
@log_exception
def handle_unhandled_exception(e):
    """Gestion générique pour toutes les exceptions non traitées spécifiquement."""
    return render_template('errors/error.html',
                           code=500,
                           message=SYSTEM_ERRORS.get("internal_error", "Une erreur interne s'est produite.")), 500
