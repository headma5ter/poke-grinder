class Route:
    def __init__(self, name: str):
        self._name = name
        self._hyperlink = f"https:\\{name}"

    @property
    def name(self) -> str:
        return self._name
