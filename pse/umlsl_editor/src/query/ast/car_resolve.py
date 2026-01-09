from abc import ABC, abstractmethod

from pse.umlsl_editor.src.model.entities.car import Car


class CarResolve(ABC):
    @abstractmethod
    def resolve(self, variables: dict[str, Car]) -> Car:
        pass


class ConstantCarResolve(CarResolve):
    def __init__(self, car: Car):
        self.car = car

    def resolve(self, variables: dict[str, Car]) -> Car:
        return self.car


class VariableCarResolve(CarResolve):
    def __init__(self, car_variable: str):
        self.car_variable = car_variable

    def resolve(self, variables: dict[str, Car]) -> Car:
        return variables[self.car_variable]
