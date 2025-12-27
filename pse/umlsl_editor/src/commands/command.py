from abc import ABC, abstractmethod
from typing import TypeVar, Generic

ReturnValue = TypeVar('ReturnValue')

"""Interface for commands that can be executed in the UMLSL editor."""
class Command(ABC, Generic[ReturnValue]):
    @abstractmethod
    def execute(self) -> ReturnValue:
        raise NotImplementedError("Subclasses must implement this method")