"""Fonctions utilitaires pour transformer des données."""

def clean_arg(arg):
    """
    Nettoie un argument de requête.
    
    :param arg: Chaîne de caractères à nettoyer
    :return: Chaîne nettoyée ou None si vide
    """
    if arg is None:
        return None
    cleaned = arg.strip()
    return cleaned if cleaned else None

def to_bool(val):
    """
    Convertit une valeur en booléen.
    
    :param val: Valeur à convertir (string, int, bool...)
    :return: True si valeur est 'true', 'yes', 'y', '1', sinon False
    """
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() in ('true', 'yes', 'y', '1')
    return bool(val)