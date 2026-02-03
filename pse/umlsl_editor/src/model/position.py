from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def clone(self)-> 'Position':
        return Position(self.x, self.y)