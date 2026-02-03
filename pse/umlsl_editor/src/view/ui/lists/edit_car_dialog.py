from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDialog

if TYPE_CHECKING:
    from pse.umlsl_editor.src.controllers import ApplicationController
from pse.umlsl_editor.src.model.entities.car import Car, CarParams
from pse.umlsl_editor.src.model.traffic_value_objects.turn_intent import TurnDirection
from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_car_dialog import Ui_Edit_Car_Dialog


class EditCarDialog(QDialog, Ui_Edit_Car_Dialog):
    def __init__(self, car: Car | None, application_controller: "ApplicationController", parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.car = car
        self.isEdit = car is not None

        self.application_controller = application_controller

        self.road_dict = application_controller.data_controller.get_all_roads()
        self.roads_list = list(self.road_dict.values())

        if not self.isEdit:
            if self.road_dict is None or len(self.road_dict) == 0:
                raise RuntimeError("No roads available to assign default lane to the new car.")
            first_road = self.roads_list[0]
            default_lane = first_road.forward_lanes[0] if len(first_road.forward_lanes) > 0 else \
                first_road.backward_lanes[0]
            car_params = CarParams(
                name="",
                color="#eb34d8",
                length=1,
                speed=0.0,
                acceleration=0.0,
                position_on_lane=0.0,
                transition=0.0,
                next_turn=None,
                lane=default_lane
            )
            self.car = Car.from_params(car_params)

        self.t_name.setText(self.car.name)
        self.t_color.setText(self.car.color)
        self.s_length.setValue(self.car.length)
        self.s_speed.setValue(self.car.speed)
        self.s_acceleration.setValue(self.car.acceleration)

        current_road = self.road_dict[self.car.lane.road_uid]
        current_road_index = self.roads_list.index(current_road)

        self.d_road.addItems([road.name for road in self.road_dict.values()])
        self.d_road.setCurrentIndex(current_road_index)

        self.d_lane.addItems(
            [f"Lane {i}" for i in range(-current_road.number_of_backward_lanes, current_road.number_of_forward_lanes)])
        self.d_lane.setCurrentIndex(self.car.lane.lane_index + current_road.number_of_backward_lanes)

        self.s_position.setValue(self.car.position_on_lane)
        self.s_transition.setValue(self.car.transition)

        directions = [direction.value for direction in TurnDirection]
        car_drives_straight = self.car.next_turn is None or self.car.next_turn.direction == TurnDirection.STRAIGHT
        self.d_direction.clear()
        self.d_direction.addItems(directions)
        self.d_direction.setCurrentText(
            TurnDirection.STRAIGHT.value if car_drives_straight else self.car.next_turn.direction.value)

        if car_drives_straight:
            self.d_road_turn.hide()
            self.l_road_turn.hide()
            self.d_lane_turn.hide()
            self.l_lane_turn.hide()
        else:
            self.d_road_turn.show()
            # fill
            self.d_lane_turn.show()
            # fill

        self.b_save.clicked.connect(self.save_and_close)

    def save_and_close(self) -> None:
        name = self.t_name.text()
        color = self.t_color.text()
        length = self.s_length.value()
        speed = self.s_speed.value()
        acceleration = self.s_acceleration.value()
        position_on_lane = self.s_position.value()
        transition = self.s_transition.value()

        road = self.roads_list[self.d_road.currentIndex()]
        lane_index = self.d_lane.currentIndex() - road.number_of_backward_lanes

        if self.isEdit:
            self.application_controller.command_controller.edit_car(
                car=self.car,
                car_name=name,
                color=color,
                length=length,
                speed=speed,
                acceleration=acceleration,
                position_on_lane=position_on_lane,
                transition=transition,
                road_uid=road.uid,
                lane_index=lane_index,
                next_turn=None,

            )
        else:
            self.application_controller.command_controller.add_car(
                name=name,
                color=color,
                length=length,
                speed=speed,
                acceleration=acceleration,
                position_on_lane=position_on_lane,
                transition=transition,
                assigned_road=road,
                lane_index=lane_index,
                next_turn=None,
            )
        self.accept()
