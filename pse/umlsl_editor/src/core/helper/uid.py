import uuid


def uid(self) -> str:
    """
    Generate a new UUID1 as a string.

    Returns:
        str: A new UUID1 in standard string format (with dashes)
    """
    return str(uuid.uuid1())
