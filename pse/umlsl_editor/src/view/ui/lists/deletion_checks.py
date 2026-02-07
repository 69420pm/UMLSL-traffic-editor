"""
Shared deletion checks for cars and roads.

These helpers centralize deletion validation logic so UI components
can reuse the same rules.
"""

from typing import TYPE_CHECKING, Iterable, Optional

from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.entities.road import Road

if TYPE_CHECKING:
    from pse.umlsl_editor.src.controllers import ApplicationController


def get_car_deletion_block_reason(
    application_controller: "ApplicationController",
    car: Car,
) -> Optional[str]:
    """
    Returns a human-readable reason if the car cannot be deleted.
    Otherwise returns None.
    """
    queries = application_controller.command_controller.umlsl_queries_model.get_queries().values()
    related_queries = [query.latex for query in queries if query.assigned_car_uid == car.uid]

    if related_queries:
        related_text = _format_bulleted_list(related_queries)
        return (
            f"Cannot delete car '{car.name}' because the following queries reference it "
            f"as ego cars:\n{related_text}"
        )

    return None


def get_road_deletion_block_reason(
    application_controller: "ApplicationController",
    road: Road,
) -> Optional[str]:
    """
    Returns a human-readable reason if the road cannot be deleted.
    Otherwise returns None.
    """
    cars = application_controller.data_controller.get_all_cars().values()
    cars_on_road = [car.name for car in cars if car.lane.road_uid == road.uid]

    if cars_on_road:
        cars_text = _format_bulleted_list(cars_on_road)
        return (
            f"Cannot delete road '{road.name}' because the following cars are on it:\n{cars_text}"
        )

    return None


def _format_bulleted_list(items: Iterable[str]) -> str:
    return "\n".join(items)
