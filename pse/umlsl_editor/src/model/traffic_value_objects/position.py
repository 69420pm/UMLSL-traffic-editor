from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class Position:
    x: float
    y: float

    def __post_init__(self) -> None:
        if not isinstance(self.x, (int, float)):
            raise ValueError("x must be a number")
        if not isinstance(self.y, (int, float)):
            raise ValueError("y must be a number")

