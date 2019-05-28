''' Taken from https://github.com/ropod-project/ropod_common
'''

import uuid


def generate_uuid():
    """
    Returns a string containing a random uuid
    """
    return str(uuid.uuid4())
