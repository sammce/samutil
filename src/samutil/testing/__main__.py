from time import perf_counter
from typing import Callable, Tuple, Union

from formatting.__main__ import Formatter

# We don't inherit from formatting in order to hide the Formatter methods 
# from the autocomplete, as it may confuse the user using the module.
f = Formatter()

# Api should be
#   test = UnitTest(callback_fn or value)

#   Testing callback:
#       test.with_args(*args, **kwargs).should<_equal, _be_greater ...etc>(performance=False)

#   Testing value:
#       test.should<_equal, _be_greater ...etc>(performance=False)
#

Value = object
TestSubject = Union

def _prepare_value(obj, *args, **kwargs) -> Value:
    if obj._is_callable:
        return obj._val(*args, **kwargs)
    else:
        return obj._val

def _prepare_value_with_performance(obj, *args, **kwargs) -> Tuple[Value, float]:
    if obj._is_callable:
        t1 = perf_counter()
        result = obj._val(*args, **kwargs)
        t2 = perf_counter()

        return result, t2 - t1
    else:
        return obj._val, 0.0
class _Comparisons:
    def __init__(self, val: Value, is_callable: bool, name: str, *args, **kwargs):
        self._val = val
        self._is_callable = is_callable
        self._name = name
        self._args = args
        self._kwargs = kwargs

    def _run(self, operator: str, a: Value, performance: bool):
        time_taken = 0

        if performance:
            result, time_taken = _prepare_value_with_performance(self, *self._args, **self._kwargs)
        else:
            result = _prepare_value(self, *self._args, **self._kwargs)

        passed = self._make_comparison(operator, a)

        values_have_same_type = True

        # Check to see if result has same type as expected value,
        # If it doesn't, try to cast it
        if not isinstance(result, a):
            try:
                result = type(a)(result)
            except ValueError:
                values_have_same_type = False

        return passed, operator, result, a, time_taken, values_have_same_type

    def _make_comparison(self, operator: str, a: Value) -> Value:
        return eval(f"{a} {operator} {self._val}")

    def _negate_operator(self, operator: str):
        """
        Return the negation of `operator`
        """
        # '==' is edge case as it can't be negated by prefixing it with '!'
        if operator.startswith("!"):
            if operator == "!=":
                return "=="
            else:
                return operator.removeprefix("!")
        else:
            if operator == "==":
                return "!="
            else:
                return "!" + operator

    def _parse(self, passed: bool, operator, result: Value, a: object, time_taken: float, same_type: bool):
        time_unit = "seconds"
        if time_taken > 0 and time_taken <= 0.01:
            time_taken = time_taken * 1000 # Convert to milliseconds
            time_unit = "milliseconds"

        if not passed:
            operator = self._negate_operator(operator)
            print(f.error(f"UnitTest({f.bold(self._name)}) - FAILED with:"))
            self._args and print(f.info("    Arguments:", ", ".join(self._args)))
            self._kwargs and print(f.info("    Keyword Arguments:", ", ".join(self._args)))
            (not self._is_callable) and print(f.info("    Value:", self._val))

            # new line
            print()

            print(f.bold(f.error("Received")), operator, f.success(f.bold("Expected")))
            print(f.bold(f.error(result)), operator, f.success(f.bold(self._val)))

            time_taken != 0 and print(f.bold(f.magenta(f"Test took {time_taken} {time_unit}")))
        else:
            print(f.error(f"UnitTest({f.bold(self._name)}) - PASS."))

    def should_equal(self, a: Value, performance: bool = False):
        """
        Test equality between expected and returned values
        """
        self._parse(self._run("==", a, performance))

    def should_be_less_than(self, a: Value, performance: bool = False):
        """
        Test less thanity between expected and returned values
        """
        self._parse(self.run("==", a, performance))



class UnitTest:
    def __init__(self, val_or_callback: TestSubject[Callable, Value]):
        self._val = val_or_callback
        self._is_callable = hasattr(self.val, "__call__")

        if self._val is None:
            raise ValueError("UnitTest was called without any arguments.")
        elif self._is_callable is None:
            raise ValueError(f"An invalid argument '{self.val}' of type '{type(self.val)}' passed to UnitTest")


        if not self._is_callable:
            if not (hasattr(self._val, "__str__") or hasattr(self._val, "__repr__")):
                raise ValueError(f"UnitTest value '{self._val} of type '{type(self._val)}' has no __str__ or __repr__ method")
            self._name = str(self._val)
        else:
            self._name = self._val.__name__

        print(f.bold(f.info("+----------------------------------------+")))
        print(f.bold(f.info("|                 Unit                   |")))
        print(f.bold(f.info("|                Tester                  |")))
        print(f.bold(f.info("+----------------------------------------+")))
        print(f.bold(       "            By: Sam McElligott            "))

    def as_value(self):
        return _Comparisons(self._val, self._is_callable, self._name)

    def with_args(self, *args, **kwargs):
        return _Comparisons(self._val, self._is_callable,self._name, *args, **kwargs)

    def __str__(self):
        return f"UnitTest({self._name})"



