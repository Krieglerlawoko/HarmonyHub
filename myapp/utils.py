import os
import binascii

def generate_token(length=16):
    """
    Generate a random token of the specified length.

    Args:
        length (int): The length of the token in bytes.

    Returns:
        str: The generated token as a hexadecimal string.
    """
    random_bytes = os.urandom(length)
    token = binascii.hexlify(random_bytes).decode()
    return token
