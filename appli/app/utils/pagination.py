class Pagination:
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
        """
        Génère les numéros de pages à afficher dans la pagination.
        - `left_edge` : Nombre de pages à afficher au début.
        - `left_current` : Nombre de pages à afficher avant la page actuelle.
        - `right_current` : Nombre de pages à afficher après la page actuelle.
        - `right_edge` : Nombre de pages à afficher à la fin.
        """
        last = 0
        for num in range(1, (self.total // self.per_page) + 2):
            if (
                num <= left_edge or
                (self.page - left_current <= num <= self.page + right_current) or
                num > (self.total // self.per_page) + 1 - right_edge
            ):
                if last + 1 != num:
                    yield None  # Ajoute "..." pour indiquer une coupure
                yield num
                last = num
