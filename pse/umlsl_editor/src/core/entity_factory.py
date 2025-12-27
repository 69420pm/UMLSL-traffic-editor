from pse.umlsl_editor.src.core.dataclasses.car import Car
from pse.umlsl_editor.src.core.dataclasses.params import CarParams, RoadParams
from pse.umlsl_editor.src.core.dataclasses.road import Road


class EntityFactory:
    """Creates car and road objects to store in the traffic snapshot."""

    @staticmethod
    def create_car(**car_params: CarParams) -> Car:
        """
        Create a Car instance.

        Required parameters must be provided. Optional parameters will use
        the Car class defaults if not specified (i.e., if not provided).

        Args:
            **car_params: Car creation parameters. See CarParams TypedDict for all available parameters.
                         Required: name, assigned_road, lane_index, lane_direction
                         Optional: color, position_on_lane, transition, velocity, length, next_turn

        Returns:
            A new Car instance validated by Car.__post_init__.

        Raises:
            CarValidationError: If validation fails in Car.__post_init__.
        """
        # Filter out None values to let Car defaults take effect
        filtered_params = {k: v for k, v in car_params.items() if v is not None}
        return Car(**filtered_params)

    @staticmethod
    def create_road(**road_params: RoadParams) -> Road:
        """Create a Road instance.

        Args:
            **road_params: Road creation parameters. See RoadParams TypedDict for all available parameters.
                          Required: name, orientation, position
                          Optional: forward_lanes, backward_lanes

        Returns:
            A new Road instance validated by Road.__post_init__.

        Raises:
            RoadValidationError: If validation fails in Road.__post_init__.
        """
        # Filter out None values to let Road defaults take effect
        filtered_params = {k: v for k, v in road_params.items() if v is not None}
        return Road(**filtered_params)
