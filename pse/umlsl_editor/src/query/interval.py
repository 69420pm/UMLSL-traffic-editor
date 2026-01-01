class Interval:
    def __init__(self, start: float, end: float) -> None:
        if end < start:
            raise ValueError(f"Start must be greater than (or equal to) end but got {start} and {end}")
        else:
            self.start = start
            self.end = end

    def length(self):
        return self.end - self.start

    def subset_of(self, other: "Interval"):
        return self.start >= other.start and self.end <= other.end
