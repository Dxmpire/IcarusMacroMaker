class Macro:
    def __init__(self, name):
        self.name = name
        self.enabled = True
        self.steps = []
        self.conditions = []

        # ⭐ NEW: Category support
        # Default category if none assigned
        self.category = "Uncategorized"

    def __repr__(self):
        return f"<Macro {self.name}>"
