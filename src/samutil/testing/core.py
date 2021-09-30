from formatting import Formatter as f

from .comparisons import ComparisonRunner
from .types import TestSubject


class UnitTest:
    def __init__(self, test_subject: TestSubject, name: str = ""):
        """
        Instantiate a new UnitTest with a value or callback which is the 
        subject of the test.
        """
        
        self._test_subject = test_subject
        is_callable = callable(self._test_subject)

        if self._test_subject is None:
            raise ValueError("UnitTest was called without a 'value_or_callable' argument.")

        elif is_callable is None:
            raise ValueError(f"An invalid argument '{self._test_subject}' of type '{type(self._test_subject)}' passed to UnitTest")

        if not is_callable:
            if not (hasattr(self._test_subject, "__str__") or hasattr(self._test_subject, "__repr__")):
                raise ValueError(f"UnitTest value '{self._test_subject} of type '{type(self._test_subject)}' has no __str__ or __repr__ method")
            name = str(self._test_subject)
            self._test_subject = lambda: self._test_subject

        if not name:
            name = self._test_subject.__name__

        self._test_subject._name = name

        
    def as_value(self):
        """
        Create a new test case using the value passed to `UnitTest` when it was instantiated.
        """
        return ComparisonRunner(self._test_subject)

    def with_args(self, *args, **kwargs):
        """
        Create a new test case, which calls the callable passed to the `UnitTest` when
        it was instantiated using the the args passed to this method.
        """
        return ComparisonRunner(self._test_subject, *args, **kwargs)

    def as_string(self):
        """
        Run a test using the return value of the __str__ method defined on the 
        test subject.
        """
        return ComparisonRunner(str(self._test_subject))

    def __str__(self):
        return self._test_subject._name

