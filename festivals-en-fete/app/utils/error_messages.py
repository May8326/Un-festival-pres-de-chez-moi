"""Module pour la traduction des messages d'erreur en français."""

# Messages d'erreur HTTP
HTTP_ERRORS = {
    400: "Requête incorrecte. Veuillez vérifier les informations saisies.",
    401: "Authentification requise. Veuillez vous connecter pour accéder à cette page.",
    403: "Accès interdit. Vous n'avez pas les droits suffisants pour accéder à cette page.",
    404: "Page non trouvée. L'adresse demandée n'existe pas sur ce site.",
    405: "Méthode non autorisée pour cette requête.",
    408: "Délai d'attente dépassé. Veuillez réessayer ultérieurement.",
    500: "Erreur interne du serveur. Nos équipes ont été informées du problème.",
    503: "Service temporairement indisponible. Veuillez réessayer plus tard."
}

# Messages d'erreur pour les formulaires WTForms
FORM_ERRORS = {
    "required": "Ce champ est obligatoire.",
    "email": "Veuillez saisir une adresse email valide.",
    "length": "La longueur doit être comprise entre {min} et {max} caractères.",
    "equal_to": "Les champs ne correspondent pas.",
    "invalid_choice": "Choix invalide, veuillez sélectionner une option de la liste.",
    "invalid_date": "Format de date invalide.",
    "invalid_url": "Veuillez saisir une URL valide.",
    "password_too_weak": "Le mot de passe est trop faible. Il doit contenir au moins 8 caractères, avec des lettres majuscules, minuscules et des chiffres."
}

# Messages d'erreur système
SYSTEM_ERRORS = {
    "database_error": "Erreur de base de données. Veuillez réessayer ultérieurement.",
    "connection_error": "Erreur de connexion. Veuillez vérifier votre connexion internet.",
    "timeout_error": "Délai d'attente dépassé. Veuillez réessayer plus tard.",
    "internal_error": "Une erreur interne s'est produite. Nos équipes ont été notifiées."
}
