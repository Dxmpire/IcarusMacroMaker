class Profile:
    def __init__(self, name: str):
        self.name = name
        self.macros = []  # list of Macro instances

    def __repr__(self):
        return f"<Profile {self.name} ({len(self.macros)} macros)>"
