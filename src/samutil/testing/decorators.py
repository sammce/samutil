import inspect
from typing import Callable

from samutil.formatting import Formatter as f

from .comparisons import BaseComparison, EqualTo
from .core import UnitTest
from .utils import make_lazy_run_test


def expect(*args):
    """
    Specify the expected value that should be returned by the test case.
    Must always be used directly underneath a `@case`.
    """
    if len(args) != 1:
        raise ValueError(
            f.error(
                "@expect only takes 1 argument, the value returned by one of the Comparisons methods, or a literal"
            )
        )

    def deco(func: Callable) -> Callable:
        func._is_class = inspect.isclass(func)
        comparison = args[0]
        if not hasattr(func, "_tests"):
            func._tests = [[]]

        if not isinstance(comparison, BaseComparison):
            comparison = EqualTo(comparison)

        index = 0
        if hasattr(func, "_test_index"):
            index = func._test_index

        try:
            func._tests[index].append(comparison)
        except IndexError:
            func._tests.append([comparison])

        return func

    return deco


def case(*args, **kwargs) -> Callable:
    """
    Decorator which wraps a function and automatically creates a test case with it.
    """

    def deco(func: Callable) -> Callable:
        if not hasattr(func, "_tests"):
            raise ValueError(
                f.error(f"@case called on '{func.__name__}' without @expect underneath")
            )

        index = 0
        if hasattr(func, "_test_index"):
            index = func._test_index

        comparison = func._tests[index][-1]
        del func._tests[index][-1]
        func._tests[index].append(
            make_lazy_run_test(*args, comparison=comparison, **kwargs)
        )
        return func

    return deco


def test(*args):
    """
    Create a new test suite for a function which can be run using `samutil test <file_with_function_declaration>`
    """
    if len(args) > 1:
        raise ValueError(
            f.error(
                f"@test accepts 1 argument: `name` which is the name of the unit test. Got {len(args)} arguments: {', '.join(args)}"
            )
        )

    def deco(func: Callable):
        try:
            name = args[0]
        except IndexError:
            name = func.__name__

        if hasattr(func, "_is_class") and func._is_class:
            raise TypeError(
                f.error(
                    "@test can't be used on a class. For testing classes, use @testmethod"
                )
            )

        test = UnitTest(func)
        test.describe(name)

        # Used for grouping like tests together
        if not hasattr(func, "_test_index"):
            func._test_index = 1
        else:
            func._test_index += 1

        # Used for grouping callbacks that run tests
        this_suite = 0
        if hasattr(func, "_run_tests"):
            this_suite = len(func._run_tests)
        else:
            func._run_tests = []

        if not hasattr(func, "_tests"):
            raise ValueError(
                f.error(
                    f"@test called on '{func.__name__}' without any @case statements underneath"
                )
            )

        def run_tests(fn):
            for case in fn._tests[this_suite][::-1]:
                case(test)()

        func._run_tests.append(run_tests)

        return func

    return deco


def testmethod(*args):
    """
    Create a new test suite for a class method which can be run using `samutil test <file_with_class_declaration>`
    """
    arg_len = len(args)
    if arg_len > 2:
        raise ValueError(
            f.error(
                f"@testmethod accepts 2 arguments: 'methodname' and 'testname'. Got {len(args)} arguments: {', '.join(args)}"
            )
        )
    elif arg_len == 0:
        raise ValueError(
            f.error(
                "@testmethod must be called without arguments. The first argument must be the name of the method."
            )
        )

    def deco(func: Callable):
        methodname = args[0]

        if arg_len == 2:
            testname = args[1]
        else:
            testname = func.__name__

        if hasattr(func, "_is_class") and func._is_class:
            method = getattr(func, methodname)
            method.__dict__.update(func.__dict__)
            method._parent = func
            test = UnitTest(method, testname)

        this_suite = 0

        if not hasattr(func, "_test_index"):
            func._test_index = 1
        else:
            func._test_index += 1

        has_tests = hasattr(func, "_run_tests")

        if has_tests:
            this_suite = len(func._run_tests)

        if not hasattr(func, "_tests"):
            raise ValueError(
                f.error(
                    f"@test called on '{func.__name__}' without any @case statements underneath"
                )
            )

        def run_tests(fn):
            print("\n" + f.underline(testname + "\n"))

            for case in fn._tests[this_suite][::-1]:
                case(test)()

        if not has_tests:
            func._run_tests = [run_tests]
        else:
            func._run_tests.append(run_tests)

        return func

    return deco
