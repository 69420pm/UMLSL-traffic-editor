from abc import ABC, abstractmethod
from typing import TypeVar, Generic

ReturnValue = TypeVar('ReturnValue')

class Command(ABC, Generic[ReturnValue]):
    """Interface for commands that can be executed in the UMLSL editor."""
    @abstractmethod
    def execute(self) -> ReturnValue:
        pass