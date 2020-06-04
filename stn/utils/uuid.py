import uuid


def generate_uuid():
    """
    Returns a string containing a random uuid
    """
    return uuid.uuid4()


def from_str(uuid_str):
    """
     Converts a uuid string to an uuid instance
    """
    return uuid.UUID(uuid_str)
