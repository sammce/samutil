from time import perf_counter
from typing import Callable

from .formatting import Formatter


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
            raise TypeError(
                "Arguments cannot be passed to non callable value", self._val)

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
            raise TypeError(
                "Argument 'callback' passed to compare() must be a method of UnitTester, such as UnitTester.equals")

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
        arguments = ", ".join(list(map(lambda val: self.bold(
            val).__repr__(), (args + [f"{key}={kwargs[key]}" for key in kwargs]))))

        # If the expected value is an exception, compare their names, as comparing them directly is always falsey
        if hasattr(val, "__call__") and isinstance(val(), Exception):
            val = type(val()).__name__
            result = type(result).__name__

        # To go to a new line
        print()

        # Perform the comparison and display the results
        if comparison(result, val):
            print(self.success(self.bold(name + "(" + arguments + ")"), "call", keyword,
                  f"an acceptable {'value' if keyword == 'returned' else 'exception' } of", self.bold(str(val))))
            print(str(result) + self.bold(comparison_operand) + str(val))
        else:
            print(self.error(self.bold(name, + "(" + arguments + ")"), "call", keyword, self.bold(str(result)),
                  "when it should have", keyword + self.bold((comparison_operand if comparison_operand != ' = ' else ' ') + str(val))))
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
            print(self.warning(
                "Performance measure can't be used on non callable object", self._info["name"]), "\n")
            return

        timing = "seconds"
        if self._info["exec_time"] < 0.0001:
            self._info["exec_time"] = self._info["exec_time"] * 1000
            timing = "milliseconds"
        print(
            f"{self.bold(self.info(str(self._info['name'])))} execution took {self.bold(self.info(str(self._info['exec_time'])))} {timing}"
        )
        print()
