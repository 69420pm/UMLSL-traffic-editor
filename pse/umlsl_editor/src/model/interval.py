class Interval:
    def __init__(self, start: float, end: float) -> None:
        if start > end:
            raise ValueError(f"End must be greater than or equal to start but got start={start} and end={end}")
        else:
            self.start = start
            self.end = end

    def length(self):
        return self.end - self.start

    def subset_of(self, other: "Interval"):
        return self.start >= other.start and self.end <= other.end

    def union(self, other: "Interval"):
        return Interval(min(self.start, other.start), max(self.end, other.end))
