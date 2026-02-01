from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDialog

from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane

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
        self.application_controller = application_controller

        if self.car is None:
            roads = application_controller.data_controller.get_all_roads()
            if roads is None or len(roads) == 0:
                raise RuntimeError("No roads available to assign default lane to the new car.")
            default_lane = Lane(road_uid=roads[0].car_uid, lane_index=0)
            car_params = CarParams(
                name="C",
                color="#eb34d8",
                length=1.5,
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

        self.d_road.addItem("aösdlkjföaskjdfölaksjdöfkajsdölkfjasöldkfjaölsdkjfölasdkjf")
        self.d_lane.addItem("öaksdjfölkajsdfasdf")
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
        """Saves the car data and closes the dialog."""
        self.application_controller.command_controller.add_car(
            name=self.t_name.text(),
            color=self.t_color.text(),
            length=self.s_length.value(),
            speed=self.s_speed.value(),
            acceleration=self.s_acceleration.value(),
            position_on_lane=self.s_position.value(),
            transition=self.s_transition.value(),
            lane=self.car.lane
        )
        self.accept()
