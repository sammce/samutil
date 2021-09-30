from formatting import Formatter as f
from sigfig import round

from .types import TestSubject, Value
from .utils import call_if_callable, output_case_args


class BaseComparison:
    result = None
    time_taken = 0
    same_type = True
    passed = False
    operator = "?"
    negated = "?"

    def __init__(self, expected: Value):
        self.expected = expected
        
    def compare(self, expected: Value, result: Value) -> bool:
        """
        If compare has not been implemented on a child class, raise an error
        """
        raise AttributeError(f.error(f"Custom comparison implementation '{self.__name__}' must implement a 'compare' method."))
        
class ShouldEqual(BaseComparison):
    operator = "=="
    negated = "!="

    def compare(self, expected, result):
        return expected == result

class ShouldBeLessThan(BaseComparison):
    operator = "<"
    negated = "!<"

    def compare(self, expected, result):
        return expected < result

class ComparisonRunner:
    def __init__(self, test_subject: TestSubject, *args, **kwargs):
        self._test_subject = test_subject
        self._args = args
        self._kwargs = kwargs

        output_case_args(test_subject, *args, **kwargs)

    def _run(self, comparison: BaseComparison):
        comparison.result, comparison.time_taken = call_if_callable(self._test_subject, *self._args, **self._kwargs)
        comparison.passed = comparison.compare(comparison.expected, comparison.result)

        # Check to see if result has same type as expected value,
        # If it doesn't, try to cast it
        should_be_type = type(comparison.expected)
        if not isinstance(comparison.result, should_be_type):
            comparison.same_type = False

        return comparison

    def _parse(self, comparison: BaseComparison):
        time_unit = "seconds"
        time_taken = comparison.time_taken

        if time_taken > 0 and time_taken <= 0.01:
            if time_taken <= 0.001:
                time_taken = time_taken * 1000 * 1000 # Convert to microseconds
                time_unit = "microseconds"
            else:
                time_taken = time_taken * 1000 # Convert to milliseconds
                time_unit = "milliseconds"

        time_taken = round(time_taken, sigfigs=3)

        if not comparison.passed:
            print(f.error("    - FAIL -"))

            print()

            print(f.bold(f.error("    Received")), comparison.negated, f.success(f.bold("Expected")))
            print(f.bold("    " + f.error(comparison.result)), comparison.negated, f.success(f.bold(comparison.expected)))

            if not comparison.same_type:
                print(f.warning(f"\n    Warning: expected and received values had different types."))
                print(f.success(f"      Expected: {type(comparison.expected).__name__} ({comparison.expected})"))
                print(f.error(f"      Received: {type(comparison.result).__name__} ({comparison.result})"))

            time_taken != 0 and print(f.magenta(f"\n  Execution time:", f.bold(time_taken, time_unit)))
        else:
            print(f.success("    - PASS -"))
            if not comparison.same_type:
                print(f.warning(f"\n    Warning: expected and received values had different types."))
                print(f.success(f"      Expected: {type(comparison.expected).__name__} ({comparison.expected})"))
                print(f.error(f"      Received: {type(comparison.result).__name__} ({comparison.result})\n"))
            time_taken != 0 and print(f.magenta(f"  Execution time:", f.bold(time_taken, time_unit)))

    def should_equal(self, expected: Value):
        """
        Test equality between expected and returned values
        """
        self._parse(self._run(ShouldEqual(expected)))

    def should_be_less_than(self, expected: Value):
        """
        Test less thanity between expected and returned values
        """
        self._parse(self._run())

    def should(self, comparison: BaseComparison):
        """
        Pass a custom comparison class which extends `BaseComparison` for use in unit test.
        """
        if not isinstance(comparison, BaseComparison):
            raise TypeError(f.error("Argument passed to 'should' method must be a class which extends from BaseComparison, or one of the pre-defined comparison objects."))

        self._parse(self._run(comparison))
