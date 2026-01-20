from abc import ABC, abstractmethod

from pse.umlsl_editor.src.model.entities.car import Car


class CarResolve(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def resolve(self, variable_car_map: dict[str, Car]) -> Car:
        pass


class ConstantCarResolve(CarResolve):
    def __init__(self, car: Car):
        super().__init__(car.name)
        self._car = car

    def resolve(self, variable_car_map: dict[str, Car]) -> Car:
        return self._car


class VariableCarResolve(CarResolve):
    def __init__(self, car_variable: str):
        super().__init__(car_variable)
        self._car_variable = car_variable

    def resolve(self, variable_car_map: dict[str, Car]) -> Car:
        return variable_car_map[self._car_variable]
