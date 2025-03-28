class Pagination:
    def __init__(self, items, page, per_page, total):
        # Initialisation de la classe Pagination avec les éléments, la page actuelle,
        # le nombre d'éléments par page et le total d'éléments.
        self.items = items
        self.page = page
        self.per_page = per_page
        self.total = total

    @property
    def has_prev(self):
        # Vérifie s'il existe une page précédente.
        return self.page > 1

    @property
    def has_next(self):
        # Vérifie s'il existe une page suivante.
        return self.page * self.per_page < self.total

    @property
    def prev_num(self):
        # Retourne le numéro de la page précédente si elle existe, sinon None.
        return self.page - 1 if self.has_prev else None

    @property
    def next_num(self):
        # Retourne le numéro de la page suivante si elle existe, sinon None.
        return self.page + 1 if self.has_next else None

    def iter_pages(self, left_edge=2, left_current=3, right_current=3, right_edge=2):
        """
        Génère les numéros de pages à afficher dans la pagination.
        - `left_edge` : Nombre de pages à afficher au début.
        - `left_current` : Nombre de pages à afficher avant la page actuelle.
        - `right_current` : Nombre de pages à afficher après la page actuelle.
        - `right_edge` : Nombre de pages à afficher à la fin.
        """
        last = 0  # Dernier numéro de page affiché
        # Parcourt toutes les pages possibles
        for num in range(1, (self.total // self.per_page) + 2):
            # Vérifie si le numéro de page doit être affiché :
            # - Si le numéro est dans les premières pages (left_edge)
            # - Si le numéro est proche de la page actuelle (left_current et right_current)
            # - Si le numéro est dans les dernières pages (right_edge)
            if (
                num <= left_edge or
                (self.page - left_current <= num <= self.page + right_current) or
                num > (self.total // self.per_page) + 1 - right_edge
            ):
                # Si une coupure est détectée (pages non consécutives), ajoute "..."
                if last + 1 != num:
                    yield None  # Ajoute "..." pour indiquer une coupure
                # Retourne le numéro de page
                yield num
                last = num  # Met à jour le dernier numéro affiché
