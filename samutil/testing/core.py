from samutil.formatting import Formatter as f

from .comparisons import ComparisonRunner
from .types import TestSubject


class UnitTest:
    def __init__(self, test_subject: TestSubject):
        """
        Instantiate a new UnitTest with a value or callback which is the
        subject of the test.
        """
        self._test_subject = test_subject
        is_callable = callable(self._test_subject)

        if not is_callable:
            if not (
                hasattr(self._test_subject, "__str__")
                or hasattr(self._test_subject, "__repr__")
            ):
                raise ValueError(
                    f"UnitTest value '{self._test_subject} of type '{type(self._test_subject)}' has no __str__ or __repr__ method"
                )
            name = str(self._test_subject)
            self._test_subject = lambda: self._test_subject
        else:
            name = self._test_subject.__name__

        self._test_subject._name = name

    def describe(self, testname: str):
        self._test_subject._name = testname

    def value(self):
        """
        Create a new test case using the value passed to `UnitTest` when it was instantiated.
        """
        print("\n" + f.underline(self._test_subject._name + "\n"))
        return ComparisonRunner(self._test_subject)

    def with_args(self, *args, **kwargs):
        """
        Create a new test case, which calls the callable passed to the `UnitTest` when
        it was instantiated using the the args passed to this method.
        """
        print("\n" + f.underline(self._test_subject._name + "\n"))
        return ComparisonRunner(self._test_subject, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        """
        Create a new test case, which calls the callable passed to the `UnitTest` when
        it was instantiated using the the args passed to this method.
        """
        return self.with_args(*args, **kwargs)

    def string(self):
        """
        Run a test using the return value of the __str__ method defined on the
        test subject.
        """
        print("\n" + f.underline(self._test_subject._name + "\n"))
        return ComparisonRunner(str(self._test_subject))

    def type(self):
        print("\n" + f.underline(self._test_subject._name + "\n"))
        return ComparisonRunner(type(self._test_subject))

    def method(self, methodname: str):
        """
        Run a test on a specific method of the test subject
        """
        method = getattr(self._test_subject, methodname, None)
        if not method:
            raise AttributeError(
                f.error(
                    f"Method '{methodname}' does not exist on object {self._test_subject.__name__}"
                )
            )

        test = UnitTest(method)
        test.describe(self._test_subject._name)
        return test

    def __str__(self):
        return self._test_subject._name
