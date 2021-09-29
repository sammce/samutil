from formatting.__main__ import Formatter

formatter = Formatter()

from secrets import choice
from string import ascii_letters, digits, punctuation

KEY_LENGTH = 84
punctuation = punctuation.replace('"', "'")
ALLOWED_CHARACTERS = ascii_letters + digits + punctuation


def generate_key(
    length: int = KEY_LENGTH, allowed_characters: str = ALLOWED_CHARACTERS
) -> str:
    key = ""
    for _ in range(length):
        key += choice(allowed_characters)

    assert len(key) == length
    return key


if __name__ == "__main__":
    import sys

    for index, arg in enumerate(sys.argv):
        cli_length = KEY_LENGTH
        cli_amount = 1
        cli_out = False

        if arg == "--length":
            try:
                cli_length = sys.argv[index + 1]
            except IndexError:
                raise ValueError("No length given.")

        elif arg == "--amount":
            try:
                cli_amount = sys.argv[index + 1]
            except IndexError:
                raise ValueError("No amount given.")

        elif arg == "--out":
            try:
                cli_out = sys.argv[index + 1]
            except IndexError:
                raise ValueError("No output file given")

    tokens = []
    for _ in range(cli_amount):
        tokens.append(generate_key(cli_length))

    if cli_out:
        with open(cli_out, "w+") as f:
            f.write("\n\n".join(tokens))
            f.close()
            print(formatter.success("Wrote tokens to", formatter.bold(cli_out)))
    else:
        print("\n".join(tokens))
