import os
from functools import wraps
from importlib import import_module
from time import perf_counter
from typing import Callable, Tuple, Union

import click
from click.types import Path
from formatting import Formatter

# We don't inherit from formatting in order to hide the Formatter methods 
# from user facing autocomplete, as it may confuse the user using the module.
f = Formatter()

Value = object
TestSubject = Union

def _prepare_value(obj, *args, **kwargs) -> Tuple[Value, float]:
    if callable(obj):
        t1 = perf_counter()
        result = obj(*args, **kwargs)
        t2 = perf_counter()

        return result, t2 - t1
    else:
        return obj, 0.0
class _Comparisons:
    def __init__(self, val: Value, is_callable: bool, name: str, *args, **kwargs):
        self._val = val
        self._is_callable = is_callable
        self._name = name
        self._args = args
        self._kwargs = kwargs

    def _run(self, operator: str, expected: Value):
        time_taken = 0

        result, time_taken = _prepare_value(self._val, *self._args, **self._kwargs)

        passed = self._make_comparison(operator, expected, result)

        values_have_same_type = True

        # Check to see if result has same type as expected value,
        # If it doesn't, try to cast it
        should_be_type = type(expected)
        if not isinstance(result, should_be_type):
            try:
                result = should_be_type(result)
            except ValueError:
                values_have_same_type = False

        return passed, operator, result, expected, time_taken, values_have_same_type

    def _make_comparison(self, operator: str, expected: Value, result: Value) -> Value:
        return eval(f"{expected} {operator} {result}")

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

    def _parse(self, passed: bool, operator, result: Value, expected: object, time_taken: float, same_type: bool):
        time_unit = "seconds"
        if time_taken > 0 and time_taken <= 0.01:
            time_taken = time_taken * 1000 # Convert to milliseconds
            time_unit = "milliseconds"

        if not passed:
            operator = self._negate_operator(operator)
            print(f.error("UnitTest(", f.bold(self._name), ") - FAILED with:"))
            self._args and print(" ",f.underline("Arguments:"), f.bold(", ".join(list(map(str, self._args)))))
            self._kwargs and print(" ",f.underline("Keyword Arguments:"), f.bold(", ".join(list(map(str, self._kwargs)))))

            print()

            print(f.bold(f.error("Received")), operator, f.success(f.bold("Expected")))
            print(f.bold(f.error(result)), operator, f.success(f.bold(expected)))

            time_taken != 0 and print(f.bold(f.magenta(f"Execution time: {time_taken} {time_unit}\n")))
        else:
            print(f.success("UnitTest(", f.bold(self._name), ") - PASS"))
            if not same_type:
                print(f.warning(f"Warning: received and expected values had different types."))
                print(f.warning(f"  Received: type {type(result)} ({result})"))
                print(f.warning(f"  Expected: type {type(expected)} ({expected})"))
            time_taken != 0 and print(f.bold(f.magenta(f"Execution time: {time_taken} {time_unit}\n")))

    def should_equal(self, expected: Value):
        """
        Test equality between expected and returned values
        """
        self._parse(*self._run("==", expected))

    def should_be_less_than(self, expected: Value):
        """
        Test less thanity between expected and returned values
        """
        self._parse(*self._run("==", expected))

class Comparisons:
    @staticmethod
    def to_equal(value: Value) -> Tuple[str, Value]:
        return "_to_equal", value
    @staticmethod
    def to_be_less_than(value: Value) -> Tuple[str, Value]:
        return "_to_be_less_than", value
    @staticmethod
    def to_be_less_or_equal_to(value: Value) -> Tuple[str, Value]:
        return "_to_be_less_or_equal_to", value
    @staticmethod
    def to_be_greater_than(value: Value) -> Tuple[str, Value]:
        return "_to_be_greater_than", value
    @staticmethod
    def to_be_greater_or_equal_to(value: Value) -> Tuple[str, Value]:
        return "_to_be_greater_or_equal_to", value
    @staticmethod
    def to_raise_error(error: Exception) -> Tuple[str, Exception]:
        return "_to_raise_error", error


class UnitTest:
    def __init__(self, val_or_callback: TestSubject[Callable, Value]):
        """
        Instantiate a new UnitTest with a value or callback which is the 
        subject of the test.
        """
        self._val = val_or_callback
        self._is_callable = callable(self._val)

        if self._val is None:
            raise ValueError("UnitTest was called without any arguments.")
        elif self._is_callable is None:
            raise ValueError(f"An invalid argument '{self._val}' of type '{type(self._val)}' passed to UnitTest")


        if not self._is_callable:
            if not (hasattr(self._val, "__str__") or hasattr(self._val, "__repr__")):
                raise ValueError(f"UnitTest value '{self._val} of type '{type(self._val)}' has no __str__ or __repr__ method")
            self._name = str(self._val)
            self.name = self._name
        else:
            self._name = self._val.__name__
            self.name = self._name

        print(f.bold(f.info("+----------------------------------------+")))
        print(f.bold(f.info("|                 Unit                   |")))
        print(f.bold(f.info("|                Tester                  |")))
        print(f.bold(f.info("+----------------------------------------+")))
        print(f.bold(       "            By: Sam McElligott            \n"))

    def as_value(self):
        """
        Create a new test case using the value passed to `UnitTest` when it was instantiated.
        """
        return _Comparisons(self._val, self._is_callable, self._name)

    def with_args(self, *args, **kwargs):
        """
        Create a new test case, which calls the callable passed to the `UnitTest` when
        it was instantiated using the the args passed to this method.
        """
        return _Comparisons(self._val, self._is_callable,self._name, *args, **kwargs)

    def describe(self, name: str) -> None:
        """
        Set the name of the test for the output UI
        """
        self._name = name

    def __str__(self):
        return self._name
def _lazy_run_test(test: UnitTest, *args, comparison: Tuple[str, Union[Value, Exception]], **kwargs) -> Callable:

    case = test.with_args(*args, **kwargs)
    code, value = comparison

    if code == "_to_equal":
        return lambda: case.should_equal(value)
    elif code == "_to_be_less_than":
        return lambda: case.should_be_less_than(value)
    elif code == "_to_be_less_or_equal_to":
        pass
    elif code == "_to_be_greater_than":
        pass
    elif code == "_to_be_greater_or_equal_to":
        pass
    elif code == "_to_raise_error":
        pass

    raise ValueError("Invalid comparison passed as should argument to @test decorator.")

def _make_lazy_run_test(*args, comparison: Tuple[str, Union[Value, Exception]], **kwargs):
    return lambda test: _lazy_run_test(test, *args, comparison=comparison, **kwargs)

def expect(*args):
    """
    Specify the expected value that should be returned by the test case.
    Must always be used directly underneath a `@case`.
    """
    if len(args) != 1:
        raise ValueError(f.error("@expect only takes 1 argument, the value returned by one of the Comparisons methods, or a literal"))
    comparison = args[0]
    def deco(func: Callable) -> Callable:
        if not hasattr(func, "_tests"):
            func._tests = []

        local_comparison = comparison

        if not isinstance(local_comparison, tuple):
            local_comparison = Comparisons.to_equal(local_comparison)

        if not len(local_comparison) == 2:
            test_number = len(func._tests) + 1            
            raise ValueError(f.error(f"Invalid 'comparison' parameter in @expect call on", "'" + f.bold(func.__name__), f"\b()' (case {test_number}, bottom up). It should be a constant or the return value from a 'Comparisons' method"))

        func._tests.append(
            local_comparison
        )
        return func
    return deco

def case(*args, **kwargs) -> Callable:
    """
    Decorator which wraps a function and automatically creates a test case with it.
    """
    def deco(func: Callable) -> Callable:
        if not hasattr(func, "_tests"):
            raise ValueError(f"@case called on function {func.__name__} without an @expect call")

        comparison = func._tests[-1]
        func._tests[-1] = _make_lazy_run_test(*args, comparison=comparison, **kwargs)
        return func
    return deco

def test(func: Callable):
    """
    Create a new test suite for a function which can be run using `samutil test <file_with_function_declaration>`
    """

    test = UnitTest(0)

    test._val = func
    test._name = func.__name__

    def run_tests(self):
        for case in self._tests:
            f.bold("RUNS", self.__name__)
            case(test)()

    if not hasattr(func, "_tests"):
        raise ValueError(f"@test decorator on function '{func.__name__}' used without any @case decorators underneath")

    func._run_tests = run_tests
    return func

def _test_non_test_file(filename: str):
    """
    Dynamically import a python file and check for functions declared with @case and @test
    """
    filename = filename.replace(".py", "")
    split_path = os.path.split(filename)

    if len(split_path) < 2:
        non_test_module = import_module(".func", ".")
    else:
        root, file = split_path[:-1], split_path[-1]
        root = "." + ".".join(root)
        file = "." + file
        
        non_test_module = import_module(file, root)

    for item in non_test_module.__dict__.items():
        item = item[1]
        if callable(item) and hasattr(item, "_run_tests"):
            item._run_tests(item)

    del non_test_module

def _test_file(file: Path):
    """
    Execute a python script from a path to a file if it ends in .test.py
    """
    filename = click.format_filename(file)
    with open(filename) as f:
        code = compile(f.read(), filename, 'exec')
        exec(code, globals(), locals())

def _test_dir(dir: Path):
    dirname = click.format_filename(dir)
    for file in os.listdir(dirname):
        filename = os.path.join(dirname, file)

        if os.path.isdir(filename):
            _test_dir(filename)
        elif os.path.isfile(filename):
            if filename.endswith(".test.py"):
                _test_file(filename)
            elif filename.endswith(".py"):
                _test_non_test_file(filename)
