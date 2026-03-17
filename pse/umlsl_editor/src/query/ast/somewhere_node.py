from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel
from pse.umlsl_editor.src.query.ast.ast import UnaryNode
from pse.umlsl_editor.src.query.ast.chop_node import VerticalChopNode, HorizontalChopNode
from pse.umlsl_editor.src.query.ast.logic_node import TrueNode
from pse.umlsl_editor.src.query.view import View


class SomewhereNode(UnaryNode):
    def evaluate(self, traffic_snapshot: TrafficSnapshotModel, view: View, variable_car_map: dict[str, Car]) -> bool:
        # we treat <phi> as "true hchop (true vchop (phi vchop true)) hchop true"
        somewhere_node = VerticalChopNode.create_nested_vchop(
            [
                TrueNode(),
                HorizontalChopNode.create_nested_hchop([TrueNode(), self._child, TrueNode()]),
                TrueNode()
            ]
        )
        return somewhere_node.evaluate(traffic_snapshot, view, variable_car_map)

    def to_latex(self) -> str:
        # we do not need to encapsulate anything in parentheses, it is already clear because of <...>
        return self._format(self._child.to_latex())

    def _format(self, child: str) -> str:
        return f"\\langle {child}\\rangle"
