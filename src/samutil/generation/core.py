from secrets import choice
from string import ascii_letters, digits, punctuation

KEY_LENGTH = 84
punctuation = punctuation.replace('"', "").replace("'", "")
ALLOWED_CHARACTERS = ascii_letters + digits + punctuation


def generate_key(
    length: int = KEY_LENGTH, allowed_characters: str = ALLOWED_CHARACTERS
) -> str:
    """
    Generate a key using a given `length` from the set of charcters `allowed_characters`
    """
    key = ""
    for _ in range(length):
        key += choice(allowed_characters)

    assert len(key) == length
    return key
