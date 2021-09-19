from os import system
from sys import platform
from typing import Iterable


class ColorCodes:
    """
    A class representation of the color codes used by `samutil.Formatter`
    """

    CYAN = "\033[96m"
    WHITE = "\033[97m"
    MAGENTA = "\033[95m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    # Returns terminal color to normal
    END = "\033[0m"


class ColoredText(ColorCodes):
    def __init__(self, code: str, val: str):
        self.code = code
        self.val = val

    def __add__(self, rhs) -> str:
        """
        Defines what to do in the case of a concatenation like ColoredText + "Hello".

        :param rhs: The object on the right hand side of the '+' operand.

        :returns The result of concatenating the 2 objects.
        """
        if isinstance(rhs, str):
            return self.code + self.val + self.END + rhs
        elif isinstance(rhs, ColoredText):
            return self.code + self.val + self.END + rhs.code + rhs.val
        else:
            raise TypeError(
                f"Operand '+' is not supported between types {type(self)} and {type(rhs)}."
            )

    def __radd__(self, lhs: str) -> str:
        """
        Defines what to do in the case of a concatenation like "Hello" + ColoredText.

        :param lhs: The object on the left hand side of the + operand.

        :returns The result of concatenating the 2 objects.
        """
        if isinstance(lhs, str):
            return lhs + f"{self.code}{self.val}{self.END}"

    def __repr__(self) -> str:
        """
        Format the ColoredText object into a string
        """
        return f"{self.code}{self.val}"

    def __str__(self) -> str:
        """
        Format the ColoredText object into a string
        """
        return f"{self.code}{self.val}{self.END}"


class Formatter:
    """
    Class with methods for changing the color of text.

    Methods:
        info -> Cyan colored text.
        success -> Green colored text.
        warning -> Yellow colored text.
        error -> Yellow colored text.
        bold -> Yellow colored text.
        underline -> Yellow colored text.
    """

    # Required to make ANSI codes work on Windows
    if platform == "win32":
        system("color")

    def _concat(self, strings: Iterable[str], code: str = "", sep: str = " ") -> str:
        """
        Helper function for concatenating multiple arguments passed
        to any Formatter methods properly.
        """
        if len(strings) == 1:
            sep = ""

        combined_strings = ""
        for string in strings:
            if not (hasattr(string, "__str__") or hasattr(string, "__repr__")):
                raise TypeError(
                    f"Value {string} of type: {type(string)} doesn't have a __str__ or __repr__ implementation."
                )

            if isinstance(string, ColoredText):
                combined_strings += string + sep
            else:
                # This is to ensure that nested formatter calls work as intended
                combined_strings += code + string + sep

        return combined_strings

    def info(self, *strings: str) -> str:
        """
        Make passed text cyan in color.

        :param Text (str): The text to be colored.

        :returns Cyan colored string.
        """
        text = self._concat(strings, ColorCodes.CYAN)
        return ColoredText(ColorCodes.CYAN, text)

    def success(self, *strings: str) -> str:
        """
        Make passed text green in color.

        :param text (str): The text to be made green.

        :returns Green colored string.
        """
        text = self._concat(strings, ColorCodes.GREEN)
        return ColoredText(ColorCodes.GREEN, text)

    def warning(self, *strings: str) -> str:
        """
        Make passed text yellow in color.

        :param text (str): The text to be colored.

        :returns Yellow colored string.
        """

        text = self._concat(strings, ColorCodes.YELLOW)
        return ColoredText(ColorCodes.YELLOW, text)

    def error(self, *strings: str) -> str:
        """
        Make passed text red in color.

        :param text (str): The text to be colored.

        :returns Red colored string.
        """
        text = self._concat(strings, ColorCodes.RED)
        return ColoredText(ColorCodes.RED, text)

    def bold(self, *strings: str) -> str:
        """
        Make passed text bold.

        :param text (str): The text to be made bold.

        :returns A bold string.
        """
        text = self._concat(strings, ColorCodes.BOLD)
        return ColoredText(ColorCodes.BOLD, text)

    def underline(self, *strings: str) -> str:
        """
        Make passed text underlined.

        :param text (str): The text to be underlined.

        :returns An underlined string.
        """
        text = self._concat(strings, ColorCodes.UNDERLINE)
        return ColoredText(ColorCodes.UNDERLINE, text)
