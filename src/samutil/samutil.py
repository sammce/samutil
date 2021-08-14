from os import system
from sys import platform
from typing import Callable, Iterable, Type, Union
from time import perf_counter

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
        system('color')

    class ColorCodes:
        CYAN = '\033[96m'
        WHITE = '\033[97m'
        MAGENTA = '\033[95m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        # Returns terminal color to normal
        END = '\033[0m'

    class ColoredText(ColorCodes):
        def __init__(self, code: str, val: str):
            self.code = code
            self.val = val

        def __add__(self, rhs: str) -> str:
            """
            Defines what to do in the case of a concatenation like ColoredText + "Hello".

            :param rhs: The object on the right hand side of the '+' operand.

            :returns The result of concatenating the 2 objects.
            """
            if isinstance(rhs, str):
                return self.code + self.val + self.END + rhs
            elif isinstance(rhs, self):
                return self.code + self.val + self.END + rhs.code + rhs.val
            else:
                raise TypeError(f"Operand '+' is not supported between types {type(self)} and {type(rhs)}.")
       
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


    def _concat(self, strings: Iterable[str], code: str = "", sep: str = " ") -> str:
        """
        Helper function for concatenating multiple arguments passed 
        to any Formatter methods properly.
        """
        if len(strings) == 1:
            sep = ""

        combined_strings = ""
        for string in strings:

            if isinstance(string, self.ColoredText):
                combined_strings += (string + sep)
            else:
                # This is to ensure that nested formatter calls work as intended
                combined_strings += (code + string + sep)

        return combined_strings
    
    def info(self, *strings: str) -> str:
        """
        Make passed text cyan in color.

        :param Text (str): The text to be colored.
        
        :returns Cyan colored string.
        """
        text = self._concat(strings, self.ColorCodes.CYAN)
        return self.ColoredText(self.ColorCodes.CYAN, text)

    def success(self, *strings: str) -> str:
        """
        Make passed text green in color.

        :param text (str): The text to be made green.
        
        :returns Green colored string.
        """
        text = self._concat(strings, self.ColorCodes.GREEN)
        return self.ColoredText(self.ColorCodes.GREEN, text)

    def warning(self, *strings: str) -> str:
        """
        Make passed text yellow in color.

        :param text (str): The text to be colored.
        
        :returns Yellow colored string.
        """

        text = self._concat(strings, self.ColorCodes.YELLOW)
        return self.ColoredText(self.ColorCodes.YELLOW, text)

    def error(self, *strings: str) -> str:
        """
        Make passed text red in color.

        :param text (str): The text to be colored.
        
        :returns Red colored string.
        """
        text = self._concat(strings, self.ColorCodes.RED)
        return self.ColoredText(self.ColorCodes.RED, text)

    def bold(self, *strings: str) -> str:
        """
        Make passed text bold.

        :param text (str): The text to be made bold.
        
        :returns A bold string.
        """
        text = self._concat(strings, self.ColorCodes.BOLD)
        return self.ColoredText(self.ColorCodes.BOLD, text)

    def underline(self, *strings: str) -> str:
        """
        Make passed text underlined.

        :param text (str): The text to be underlined.
        
        :returns An underlined string.
        """
        text = self._concat(strings, self.ColorCodes.UNDERLINE)
        return self.ColoredText(self.ColorCodes.UNDERLINE, text)

class UnitTester():

    def __init__(self, val: object):
        """
        Setup a unit tester for a value or callable

        :param val The value or callable that is being tested
        """
        self._val = val
        self._is_callable = hasattr(val, "__call__")
    
    def arguments(self, *args, **kwargs):
        if not self._is_callable:
            raise TypeError("Arguments cannot be passed to non callable value", self._val)

        time1 = perf_counter()
        try:
            result = self._val(*args, **kwargs)
        except Exception as e:
            result = e
        
        exec_time = perf_counter() - time1

        if hasattr(self._val, "__name__"):
            name = self._val.__name__
        else:
            name = self._val
        
        return _Compare({
            "result": result, 
            "exec_time": exec_time, 
            "name": name, 
            "is_callable": self._is_callable,
            "args": args,
            "kwargs": kwargs
        }, parent=type(self))

    def equals(self):
        return [lambda a, b: a == b, " = ", " != ", "returned"]

    def greater_than(self):
        return [lambda a, b: a > b, " > ", " !> ", "returned"]

    def greater_or_equal(self):
        return [lambda a, b: a >= b, " >= ", " !>= ", "returned"]

    def less_than(self):
        return [lambda a, b: a < b, " < ", " !< ", "returned"]

    def less_or_equal(self):
        return [lambda a, b: a <= b, " <= ", " !<= ", "returned"]

    def raises(self):
        return [lambda a, b: a == b, " = ", " != ", "raised"]

class _Compare:

    def __init__(self, info: dict, parent: object):
        self._info = info
        self._parent = parent

    def compare(self, callback: Callable):
        """
        Take in a function, which must be a method of UnitTester, and inject it into the _info dict.

        :param callback: A function which must be a method of UnitTester

        :raises TypeError: If callback is not a method of UnitTester
        """

        # Raise an error if callback isn't a function, isn't a method of UnitTester and isn't the 'arguments' method
        if not (hasattr(callback, "__self__") and isinstance(callback.__self__, self._parent) and callback.__name__ != "arguments"):
            raise TypeError("Argument 'callback' passed to compare() must be a method of UnitTester, such as UnitTester.equals")

        # Destructure the return value of callback and inject it into _info
        self._info["comparison"], self._info["comparison_operand"], self._info["failed_operand"], self._info["keyword"] = callback()
        return _Expects(self._info)

class _Expects(Formatter):

    def __init__(self, info: dict):
        self._info = info

    def expect(self, val: object, ):
        """
        Take in an object and compare it against the returned result of the object being tested.
        Print out success / error messages depending on the result.

        :param val: The value expected to be returned from the object being tested.

        :returns A Details class, with a method called "performance()" which displays
        how long the object took to run, if the test object is callable
        """
        result = self._info["result"]
        name = self._info["name"]
        keyword = self._info["keyword"]
        comparison = self._info["comparison"]
        comparison_operand = self._info["comparison_operand"]
        failed_operand = self._info["failed_operand"]
        kwargs = self._info["kwargs"]
        args = list(map(lambda x: str(x), list(self._info["args"])))

        # For each arg and kwarg, make it bold and put a separating comma ',' between them
        arguments = ", ".join(list(map(lambda val: self.bold(val).__repr__(), (args + [f"{key}={kwargs[key]}" for key in kwargs]))))

        # If the expected value is an exception, compare their names, as comparing them directly is always falsey
        if hasattr(val, "__call__") and isinstance(val(), Exception):
            val = type(val()).__name__
            result = type(result).__name__

        # To go to a new line
        print()

        # Perform the comparison and display the results
        if comparison(result, val):
            print(self.success(self.bold(name + "(" + arguments + ")"), "call", keyword, f"an acceptable {'value' if keyword == 'returned' else 'exception' } of", self.bold(str(val))))
            print(str(result) + self.bold(comparison_operand) + str(val))
        else:
            print(self.error(self.bold(name, + "(" + arguments + ")"), "call", keyword, self.bold(str(result)), "when it should have", keyword + self.bold((comparison_operand if comparison_operand != ' = ' else ' ')+ str(val))))
            print(str(result) + self.bold(self.error(failed_operand)) + str(val))

        return _Details(self._info)

class _Details(Formatter):
    def __init__(self, info: dict):
        self._info = info

    def performance(self):
        """
        Displays how long the callable being tested took to run, if it is callable.
        If it is not, it displays a usage warning.
        """
        if not self._info["is_callable"]:
            print(self.warning("Performance measure can't be used on non callable object", self._info["name"]), "\n")
            return

        timing = "seconds"
        if self._info["exec_time"] < 0.0001:
            self._info["exec_time"] = self._info["exec_time"] * 1000
            timing = "milliseconds"
        print(
            f"{self.bold(self.info(str(self._info['name'])))} execution took {self.bold(self.info(str(self._info['exec_time'])))} {timing}"
        )
        print()

if __name__ == "__main__":
    def add(a, b):
        return (a / b)

    ut = UnitTester(add)
    # ut.arguments(10, 5).compare(ut.equals).expect(5).performance()

    ut.arguments(10, 5).compare(ut.equals).expect(10).performance()

