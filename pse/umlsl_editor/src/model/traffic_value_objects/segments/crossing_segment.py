from dataclasses import dataclass

<<<<<<<< HEAD:pse/umlsl_editor/src/model/value_objects/segments/crossing_segment.py
<<<<<<<< HEAD:pse/umlsl_editor/src/core/value_objects/segments/crossing_segment.py
from pse.umlsl_editor.src.core.value_objects.lane import Lane
from pse.umlsl_editor.src.core.value_objects.position import Position
from pse.umlsl_editor.src.core.value_objects.segments.segment import Segment
========
from pse.umlsl_editor.src.model.value_objects.lane import Lane
from pse.umlsl_editor.src.model.value_objects.position import Position
from pse.umlsl_editor.src.model.value_objects.segments.segment import Segment
>>>>>>>> 83e486a70109dc9a73cb47ad2fbf2eaa9e93b535:pse/umlsl_editor/src/model/value_objects/segments/crossing_segment.py
========
from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane
from pse.umlsl_editor.src.model.traffic_value_objects.position import Position
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment
>>>>>>>> f5aa8be893b6cdb275c41e175b4b8127d5c941ae:pse/umlsl_editor/src/model/traffic_value_objects/segments/crossing_segment.py


@dataclass(frozen=True)
class CrossingSegment(Segment):
    lane_horizontal: Lane
    lane_vertical: Lane
    is_lane_segment = False

    def get_position(self) -> Position:
        """Return position of the top left corner of the crossing segment.
        It gets calculated from the position of the two lanes."""
        raise NotImplementedError()


