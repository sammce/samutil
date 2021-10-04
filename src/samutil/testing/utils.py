import os
from importlib import import_module
from time import perf_counter
from types import FunctionType, ModuleType
from typing import Callable, Tuple

import click
from click.types import Path
from samutil.formatting import Formatter as f

from .types import TestSubject, Value


def call_if_callable(obj: object, *args, **kwargs) -> Tuple[Value, float]:
    """
    Take an object and any amout of args, and call the object with the args
    if it can be called, with performance metrics.
    """
    if callable(obj):
        if getattr(obj, "_is_class", False) and (not isinstance(obj, FunctionType)):
            response = obj(obj._parent(), *args, **kwargs)
        else:
            response = obj(*args, **kwargs)
        return response
    else:
        return obj, 0


def output_case_args(test_subject: TestSubject, *args, **kwargs):
    """
    Take a test subject and all of the test's arguments and output it nicely.
    """
    formatted_kwargs = [f"{k}={v}" for (k, v) in kwargs.items()]
    args = tuple(map(str, args))
    formatted_args = ", ".join([*args, *formatted_kwargs])
    formatted_output = f.bold(test_subject.__name__ + "(" + formatted_args + ")")
    print(f.info("  RUNS", f.bold(formatted_output), "\b:"))


def lazy_run_test(test, *args, comparison, **kwargs) -> Callable:
    case = test.with_args(*args, **kwargs)

    return lambda: case.should(comparison)


def make_lazy_run_test(*args, comparison, **kwargs):
    return lambda test: lazy_run_test(test, *args, comparison=comparison, **kwargs)


def import_file(filename: str) -> ModuleType:
    """
    Import the contents of a file and return it as a module
    """
    filename = filename.replace(".py", "")
    split_path = os.path.split(filename)

    if split_path[0] == ".":
        non_test_module = import_module(split_path[1])
    else:

        if filename.startswith("./"):
            filename = filename[2:]
        filename = filename.replace("/", ".")

        non_test_module = import_module(filename)

    return non_test_module


def module_funcs(module: ModuleType):
    for func in module.__dict__.items():
        yield func


def test_file(filename: str):
    """
    Dynamically import a python file and check for functions declared with @case and @test
    """

    module = import_file(filename)
    for func in module_funcs(module):
        # func is a tuple in the form ('func_name', actual_func)
        func = func[1]
        if callable(func) and hasattr(func, "_run_tests"):
            print(f.bold("\nFile:", filename))
            for test in func._run_tests[::-1]:
                test(func)

    del module


def test_test_file(filename: str):
    with open(filename) as f:
        code = compile(f.read(), filename, "exec")
        exec(code, globals(), locals())


def test_dir(dir: Path):
    dirname = click.format_filename(dir)
    for file in os.listdir(dirname):
        filename = os.path.join(dirname, file)

        if os.path.isdir(filename):
            test_dir(filename)
        elif os.path.isfile(filename):
            if filename.endswith(".py"):
                if filename.endswith(".test.py"):
                    test_test_file(filename)
                else:
                    test_file(filename)
