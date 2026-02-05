from networkx.algorithms.planarity import Interval

class Interval:
    def __init__(self, start: float, end: float) -> None:
        if start > end:
            raise ValueError(f"End must be greater than or equal to start but got start={start} and end={end}")
        else:
            self.start = start
            self.end = end

    def length(self):
        return self.end - self.start

    def subset_of(self, intervals: list['Interval']):
        for interval in intervals:
            if interval.start <= self.start and self.end <= interval.end:
                return True
        return False

    @staticmethod
    def union(interval: list['Interval']) -> list[Interval]:
        """"
        Returns the union of a list of intervals (that may overlap).
        """

        sorted_intervals = sorted(interval, key=lambda x: x.start)
        merged = []

        current_start = sorted_intervals[0].start
        current_end = sorted_intervals[0].end

        for i in range(1, len(sorted_intervals)):
            next_interval = sorted_intervals[i]

            if next_interval.start <= current_end:
                # Intervals overlap
                current_end = max(current_end, next_interval.end)
            else:
                # Intervals do not overlap, create a new one
                merged.append(Interval(current_start, current_end))

                current_start = next_interval.start
                current_end = next_interval.end

        merged.append(Interval(current_start, current_end))
        return merged
