from dataclasses import dataclass

from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.helper.direction import Direction
from pse.umlsl_editor.src.model.interval import Interval
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment_interval import SegmentInterval
from pse.umlsl_editor.src.model.traffic_value_objects.segments.virtual_lane import VirtualLane
from pse.umlsl_editor.src.model.traffic_value_objects.turn_intent import TurnDirection


@dataclass(frozen=True)
class CarEnvironment:
    car_direction: Direction
    turn_direction: TurnDirection

    path: list[Segment]
    horizon: Interval
    parallel_virtual_lanes: list[list[VirtualLane]]
    path_virtual_lane: VirtualLane

    path_segment_intervals: list[SegmentInterval]
    physical_segment_intervals: list[SegmentInterval]

    reserved: list[SegmentInterval]
    claimed: list[SegmentInterval]

    def print_debug(self, ts: TrafficSnapshotReader, car_name: str):
        print(f"--- debug --- env of {car_name}")
        print("path is ", list(map(lambda seg: ts.get_segment_info(seg.uid), self.path)))

        def format_seg_intervals(segment_intervals: list[SegmentInterval]) -> str:
            return " ".join(
                map(lambda seg: ts.get_segment_info(seg.segment.uid) + " " + str(seg.interval), segment_intervals))

        print("horizon is ", self.horizon)
        print("path seg-intervals is ", format_seg_intervals(self.path_segment_intervals))
        print("physical segment intervals are ", format_seg_intervals(self.physical_segment_intervals))
        print("reserved segment intervals are ", format_seg_intervals(self.reserved))
        print("claimed segment intervals are ", format_seg_intervals(self.claimed))

        for parallel_virtual_lane in self.parallel_virtual_lanes:
            print("parallel virtual lane:")
            for virtual_lane in parallel_virtual_lane:
                print(" > virtual lane is ", format_seg_intervals(virtual_lane.segment_intervals))

    def translate_interval_coordinates(self, virtual_lanes: list[VirtualLane], horizon: Interval,
                                       to_translate: list[SegmentInterval], translate_car: 'Car',
                                       ts: TrafficSnapshotReader) -> dict[Segment, Interval]:
        """"
        Translates the segment of the given interval into the coordinates of the "self" car - w.r.t the virtual_lanes.
        """

        # 1) for each element in to_translate, figure out the corresponding virtual lane that includes that segment -> create a map from to_translate to virtual_lane
        # 2) for each virtual lane, translate the interval into the coordinate system of the "self" car
        # 3) remove those segment intervals that do not intersect with the horizon of the "self" car

        lane_to_segment_intervals: dict[int, dict[Segment, Interval]] = {}
        segments_to_virtual_lane: dict[Segment, int] = {}
        for virtual_lane_index in virtual_lanes:
            for segment_interval in virtual_lane_index.segment_intervals:
                lane_index = virtual_lanes.index(virtual_lane_index)
                segments_to_virtual_lane[segment_interval.segment] = lane_index

        # 2) align intervals of to_translate
        self_dir: Direction = self.car_direction
        turn_dir: TurnDirection = self.turn_direction
        car_dir: Direction = translate_car.environment.car_direction
        swap_alignment = car_dir == self_dir.opposite

        if not swap_alignment and turn_dir != TurnDirection.STRAIGHT:
            # we have to be careful on turns
            swap_alignment = turn_dir == TurnDirection.LEFT and car_dir == Direction.DOWN or turn_dir == TurnDirection.RIGHT and car_dir == Direction.UP

        aligned_to_translate: list[SegmentInterval] = []
        if swap_alignment:
            for translate_segment_interval in to_translate:
                segment = translate_segment_interval.segment
                segment_length = segment.get_size_in_direction(ts)
                interval = translate_segment_interval.interval

                new_start = segment_length - interval.end
                new_end = segment_length - interval.start

                aligned_interval = Interval(new_start, new_end)
                aligned_to_translate.append(SegmentInterval(segment, aligned_interval))
        else:
            aligned_to_translate = to_translate

        for translate_segment_interval in aligned_to_translate:
            lane_index = segments_to_virtual_lane.get(translate_segment_interval.segment)
            if lane_index is not None:
                if lane_to_segment_intervals.get(lane_index) is None:
                    lane_to_segment_intervals[lane_index] = {}

                lane_to_segment_intervals[lane_index][
                    translate_segment_interval.segment] = translate_segment_interval.interval

        translated_segment_intervals: dict[Segment, Interval] = {}
        for lane_index, virtual_lane in enumerate(virtual_lanes):
            segment_intervals_on_lane: dict[Segment, Interval] = lane_to_segment_intervals.get(lane_index)
            if segment_intervals_on_lane is None:
                continue

            offset = 0
            for lane_segment_interval in virtual_lane.segment_intervals:
                lane_segment = lane_segment_interval.segment

                interval = segment_intervals_on_lane.get(lane_segment)
                if interval is not None:
                    interval_on_lane = Interval(interval.start + offset, interval.end + offset)
                    if interval_on_lane.intersects(horizon):
                        translated_segment_intervals[lane_segment] = interval_on_lane

                offset += lane_segment.get_size_in_direction(ts)

        return translated_segment_intervals
