from typing import Callable

from formatting import Formatter as f

from .comparisons import BaseComparison, ShouldEqual
from .core import UnitTest
from .utils import make_lazy_run_test


def expect(*args):
    """
    Specify the expected value that should be returned by the test case.
    Must always be used directly underneath a `@case`.
    """
    if len(args) != 1:
        raise ValueError(f.error("@expect only takes 1 argument, the value returned by one of the Comparisons methods, or a literal"))

    def deco(func: Callable) -> Callable:
        comparison = args[0]
        if not hasattr(func, "_tests"):
            func._tests = []

        if not isinstance(comparison, BaseComparison):
            comparison = ShouldEqual(comparison)

        func._tests.append([comparison])
        return func
    return deco

def case(*args, **kwargs) -> Callable:
    """
    Decorator which wraps a function and automatically creates a test case with it.
    """
    def deco(func: Callable) -> Callable:
        if not hasattr(func, "_tests"):
            raise ValueError(f"@case called on function {func.__name__} without an @expect call")

        comparison = func._tests[-1][-1]
        func._tests[-1][-1] = make_lazy_run_test(*args, comparison=comparison, **kwargs)
        return func
    return deco

def test(*args):
    """
    Create a new test suite for a function which can be run using `samutil test <file_with_function_declaration>`
    """ 
    if len(args) > 1:
        raise ValueError(f.error(f"@test accepts 1 argument: `name` which is the name of the unit test. Got {len(args)} arguments"))
    
    def deco(func: Callable):
        try:
            name = args[0]
        except IndexError:
            name = func.__name__

        test = UnitTest(func, name)
        this_suite = 0

        has_tests = hasattr(func, "_run_tests")

        if has_tests:
            this_suite = len(func._run_tests)

        def run_tests(fn):
            print("\n" + f.underline(name + "\n"))
            
            for case in fn._tests[this_suite]:
                case(test)()

        if not hasattr(func, "_tests"):
            raise ValueError(f"@test decorator on function '{func.__name__}' used without any @case decorators underneath")

        if not has_tests:
            func._run_tests = [run_tests]
        else:
            func._run_tests.append(run_tests)

        return func
    
    return deco
