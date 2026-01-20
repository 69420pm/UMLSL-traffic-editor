from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.view_models.traffic_snapshot import TrafficSnapshot
from pse.umlsl_editor.src.query.ast.ast import UnaryNode
from pse.umlsl_editor.src.query.ast.chop_node import VerticalChopNode, HorizontalChopNode
from pse.umlsl_editor.src.query.ast.logic_node import TrueNode
from pse.umlsl_editor.src.query.view import View


class SomewhereNode(UnaryNode):
    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        # we treat <phi> as <phi> = true hchop (true vchp (phi vchop true)) hchp true (infix notation for readability)
        # todo: iterate through all sub-layers directly for performance optimization
        vertical_somewhere_node = VerticalChopNode(
            TrueNode(),
            VerticalChopNode(self._child, TrueNode())
        )
        horizontal_somewhere_node = HorizontalChopNode(
            TrueNode(),
            HorizontalChopNode(vertical_somewhere_node, TrueNode())
        )
        return horizontal_somewhere_node.evaluate(traffic_snapshot, view, variable_car_map)

    def _format(self, child: str) -> str:
        return f"<{child}>"
