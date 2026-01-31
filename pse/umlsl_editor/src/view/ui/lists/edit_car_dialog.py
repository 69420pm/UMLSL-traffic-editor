from xxlimited_35 import Null

from PySide6.QtWidgets import QDialog

from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.traffic_value_objects.turn_intent import TurnDirection
from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_car_dialog import Ui_Edit_Car_Dialog

class EditCarDialog(QDialog, Ui_Edit_Car_Dialog):
    def __init__(self,car:Car, parent=None,):
        super().__init__(parent)
        self.setupUi(self)

        self.t_name.setText(car.name)
        self.t_color.setText(car.color)
        self.s_length.setValue(car.length)
        self.s_speed.setValue(car.speed)
        self.s_acceleration.setValue(car.acceleration)

        self.d_road.addItem("aösdlkjföaskjdfölaksjdöfkajsdölkfjasöldkfjaölsdkjfölasdkjf")
        self.d_lane.addItem("öaksdjfölkajsdfasdf")
        self.s_position.setValue(car.position_on_lane)
        self.s_transition.setValue(car.transition)

        directions = [direction.value for direction in TurnDirection]
        car_drives_straight = car.next_turn is None or car.next_turn.direction == TurnDirection.STRAIGHT
        self.d_direction.clear()
        self.d_direction.addItems(directions)
        self.d_direction.setCurrentText(TurnDirection.STRAIGHT.value if car_drives_straight else car.next_turn.direction.value)

        if car_drives_straight :
            self.d_road_turn.hide()
            self.l_road_turn.hide()
            self.d_lane_turn.hide()
            self.l_lane_turn.hide()
        else:
            self.d_road_turn.show()
            #fill
            self.d_lane_turn.show()
            #fill