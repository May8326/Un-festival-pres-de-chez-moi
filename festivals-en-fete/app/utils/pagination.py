class Pagination:
    """
    Une classe utilitaire pour gérer la pagination des éléments.

    Attributs :
        items (list) : La liste des éléments à paginer.
        page (int) : Le numéro de la page actuelle (index basé sur 1).
        per_page (int) : Le nombre d'éléments par page.
        total (int) : Le nombre total d'éléments.

    Propriétés :
        has_prev (bool) : Indique s'il existe une page précédente.
        has_next (bool) : Indique s'il existe une page suivante.
        prev_num (int ou None) : Le numéro de la page précédente, ou None s'il n'y a pas de page précédente.
        next_num (int ou None) : Le numéro de la page suivante, ou None s'il n'y a pas de page suivante.

    Méthodes :
        iter_pages(left_edge=2, left_current=3, right_current=3, right_edge=2):
            Génère un itérateur de numéros de pages pour l'affichage de la pagination.
            Inclut des ellipses (None) là où il y a des écarts dans la plage de pages.

            Arguments :
                left_edge (int) : Nombre de pages à afficher au début de la plage.
                left_current (int) : Nombre de pages à afficher à gauche de la page actuelle.
                right_current (int) : Nombre de pages à afficher à droite de la page actuelle.
                right_edge (int) : Nombre de pages à afficher à la fin de la plage.

            Génère :
                int ou None : Numéros de pages ou None.
    """
    def __init__(self, items, page, per_page, total):
        self.items = items
        self.page = page
        self.per_page = per_page
        self.total = total

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page * self.per_page < self.total

    @property
    def prev_num(self):
        return self.page - 1 if self.has_prev else None

    @property
    def next_num(self):
        return self.page + 1 if self.has_next else None

    def iter_pages(self, left_edge=2, left_current=3, right_current=3, right_edge=2):
        last = 0
        for num in range(1, (self.total // self.per_page) + 2):
            if (
                num <= left_edge or
                (self.page - left_current <= num <= self.page + right_current) or
                num > (self.total // self.per_page) + 1 - right_edge
            ):
                if last + 1 != num:
                    yield None
                yield num
                last = num

def args_to_dict(request_args):
    """
    Convertit les arguments de requête en dictionnaire pour les transmettre dans les liens de pagination.
    """
    return {key: value for key, value in request_args.items() if value}