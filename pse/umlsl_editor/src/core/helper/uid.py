"""
UID Manager - Centralized unique identifier generation using UUID1.

This class provides a singleton manager for generating consistent,
time-ordered unique identifiers across your application.
"""

import uuid


class UIDManager:
    """
    Singleton manager for generating UUID1-based unique identifiers.
    """

    # _instance: Optional['UIDManager'] = None

    # def __new__(cls):
    #     """Ensure only one instance of UIDManager exists."""
    #     if cls._instance is None:
    #         cls._instance = super().__new__(cls)
    #         cls._instance._initialized = False
    #     return cls._instance

    # def __init__(self):
    #     """Initialize the UID manager (only runs once due to singleton pattern)."""
    #     if self._initialized:
    #         return

    #     self._initialized = True

    def generate_str(self) -> str:
        """
        Generate a new UUID1 as a string.

        Returns:
            str: A new UUID1 in standard string format (with dashes)
        """
        return str(uuid.uuid1())
