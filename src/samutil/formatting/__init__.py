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

    def __add__(self, rhs: str) -> str:
        """
        Defines what to do in the case of a concatenation like ColoredText + "Hello".
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
    """

    # Required to make ANSI codes work on Windows
    if platform == "win32":
        system("color")

    @staticmethod
    def _concat(strings: Iterable[str], code: str = "", sep: str = " ") -> str:
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
                    f"Value '{string}' of type '{type(string)}' doesn't have __str__ or __repr__ method."
                )

            string = str(string)

            if isinstance(string, ColoredText):
                combined_strings += string + sep
            else:
                # This is to ensure that nested formatter calls work as intended
                combined_strings += code + string + sep

        return combined_strings

    @staticmethod
    def info(*strings: str, sep=" ") -> str:
        """
        Return `strings` as 1 Cyan colored string, separated by `sep`
        """
        text = Formatter._concat(strings, ColorCodes.CYAN, sep)
        return ColoredText(ColorCodes.CYAN, text)

    @staticmethod
    def success(*strings: str, sep=" ") -> str:
        """
        Return `strings` as 1 Green colored string, separated by `sep`
        """
        text = Formatter._concat(strings, ColorCodes.GREEN, sep)
        return ColoredText(ColorCodes.GREEN, text)

    @staticmethod
    def warning(*strings: str, sep=" ") -> str:
        """
        Return `strings` as 1 Yellow colored string, separated by `sep`
        """

        text = Formatter._concat(strings, ColorCodes.YELLOW, sep)
        return ColoredText(ColorCodes.YELLOW, text)

    @staticmethod
    def error(*strings: str, sep=" ") -> str:
        """
        Return `strings` as 1 Red colored string, separated by `sep`
        """
        text = Formatter._concat(strings, ColorCodes.RED, sep)
        return ColoredText(ColorCodes.RED, text)

    @staticmethod
    def magenta(*strings: str, sep=" ") -> str:
        """
        Return `strings` as 1 Magenta colored string, separated by `sep`
        """
        text = Formatter._concat(strings, ColorCodes.MAGENTA, sep)
        return ColoredText(ColorCodes.MAGENTA, text)

    @staticmethod
    def bold(*strings: str, sep=" ") -> str:
        """
        Return `strings` as 1 Bold string, separated by `sep`
        """
        text = Formatter._concat(strings, ColorCodes.BOLD, sep)
        return ColoredText(ColorCodes.BOLD, text)

    @staticmethod
    def underline(*strings: str, sep=" ") -> str:
        """
        Return `strings` as 1 Underlined string, separated by `sep`
        """
        text = Formatter._concat(strings, ColorCodes.UNDERLINE, sep)
        return ColoredText(ColorCodes.UNDERLINE, text)
