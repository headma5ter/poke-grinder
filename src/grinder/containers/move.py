class Move:
    def __init__(self, name):
        self._name = name
        self._power = 0  # placeholder
        self._accuracy = 0  # placeholder
        self._max_pp = 0  # placeholder

    def expected_power(self) -> float:
        return self._power * (self._accuracy / 100)
