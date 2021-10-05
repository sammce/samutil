from time import perf_counter

from samutil.formatting import Formatter as f
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
    _not = False

    def __init__(self, expected: Value):
        self.expected = expected

    def compare(self, expected: Value, result: Value) -> bool:
        """
        If compare has not been implemented by a child class, raise an error
        """
        raise AttributeError(
            f.error(
                f"Custom comparison implementation '{self.__name__}' must implement a 'compare' method."
            )
        )


class EqualTo(BaseComparison):
    operator = "=="
    negated = "!="

    def compare(self, result, expected):
        return result == expected


def Not(comp: BaseComparison):
    """
    Negate the value that is being expected
    """
    if isinstance(comp, BaseComparison):
        comp._not = True
    else:
        comp = EqualTo(comp)
        comp._not = True
    return comp


class ListEqual(EqualTo):
    def compare(self, result, expected):
        if not isinstance(result, (list, tuple)):
            return False

        for result_val, expected_val in zip(result, expected):
            if result_val != expected_val:
                return False

        return True


class DictEqual(EqualTo):
    def compare(self, result: dict, expected: dict):
        if not isinstance(result, dict):
            return False

        for result_val, expect_val in zip(result.values(), expected.values()):
            if isinstance(result_val, dict):
                if not self.compare(result_val, expect_val):
                    return False
            elif result_val != expect_val:
                return False

        return True


class HasType(BaseComparison):
    operator = "instance of"
    negated = "not instance of"

    def compare(self, result, expected):
        return isinstance(result, type(expected))


class LessThan(BaseComparison):
    operator = "<"
    negated = "!<"

    def compare(self, result, expected):
        return result < expected


class LessThanOrEqualTo(BaseComparison):
    operator = "<="
    negated = "!<="

    def compare(self, result, expected):
        return result <= expected


class GreaterThan(BaseComparison):
    operator = ">"
    negated = "!>"

    def compare(self, result, expected):
        return result > expected


class GreaterThanOrEqualTo(BaseComparison):
    operator = ">="
    negated = "!>="

    def compare(self, result, expected):
        return result >= expected


class ToRaise(BaseComparison):
    operator = "instance of"
    negated = "not instance of"

    def compare(self, result, expected):
        return isinstance(result, expected)


class ComparisonRunner:
    def __init__(self, test_subject: TestSubject, *args, **kwargs):
        self._test_subject = test_subject
        self._args = args
        self._kwargs = kwargs

        output_case_args(test_subject, *args, **kwargs)

    def _run(self, comparison: BaseComparison):
        t1 = perf_counter()

        # Only catch errors if the test is checking for an exception
        if isinstance(comparison, ToRaise):
            try:
                comparison.result = call_if_callable(
                    self._test_subject, *self._args, **self._kwargs
                )
            except Exception as e:
                comparison.result = e
        else:
            comparison.result = call_if_callable(
                self._test_subject, *self._args, **self._kwargs
            )

        t2 = perf_counter()
        comparison.time_taken = t2 - t1

        comparison.passed = comparison.compare(comparison.result, comparison.expected)

        if comparison._not:
            comparison.passed = not comparison.passed
            comparison.operator, comparison.negated = (
                comparison.negated,
                comparison.operator,
            )

        # Check to see if result has same type as expected value,
        # If it doesn't, try to cast it.
        should_be_type = type(comparison.expected)
        if not isinstance(comparison.result, should_be_type):
            comparison.same_type = False

        return comparison

    def _parse(self, comparison: BaseComparison):
        time_unit = "seconds"
        time_taken = comparison.time_taken

        if time_taken > 0 and time_taken <= 0.01:
            time_taken = time_taken * 1000  # Convert to milliseconds
            time_unit = "milliseconds"

            if time_taken <= 0.01:
                time_taken = time_taken * 1000  # Convert to microseconds
                time_unit = "microseconds"

        time_taken = round(time_taken, sigfigs=3)

        if not comparison.passed:
            print(f.error("    - FAIL -"))

            print()

            print(
                f.bold(f.error("    Received")),
                comparison.negated,
                f.success(f.bold("Expected")),
            )
            print(
                f.bold("    " + f.error(comparison.result)),
                comparison.negated,
                f.success(f.bold(comparison.expected)),
            )

            if not comparison.same_type:
                print(
                    f.warning(
                        f"\n    Warning: expected and received values had different types."
                    )
                )
                print(
                    f.success(
                        f"      Expected: {type(comparison.expected).__name__} ({comparison.expected})"
                    )
                )
                print(
                    f.error(
                        f"      Received: {type(comparison.result).__name__} ({comparison.result})"
                    )
                )

            time_taken != 0 and print(
                f.magenta(f"\n  Execution time:", f.bold(time_taken, time_unit)) + "\n"
            )
        else:
            print(f.success("    - PASS -"))
            if not comparison.same_type:
                print(
                    f.warning(
                        f"\n    Warning: expected and received values had different types."
                    )
                )
                print(
                    f.success(
                        f"      Expected: {type(comparison.expected).__name__} ({comparison.expected})"
                    )
                )
                print(
                    f.error(
                        f"      Received: {type(comparison.result).__name__} ({comparison.result})\n"
                    )
                )
            time_taken != 0 and print(
                f.magenta(f"  Execution time:", f.bold(time_taken, time_unit)) + "\n"
            )

    def should_equal(self, expected: Value):
        """
        Result of call should be equal to expected
        """
        self._parse(self._run(EqualTo(expected)))

    def should_be_less_than(self, expected: Value):
        """
        Result of call should be less than expected
        """
        self._parse(self._run(LessThan(expected)))

    def should_be_less_or_equal_to(self, expected: Value):
        """
        Result of call should be less than or equal to expected
        """
        self._parse(self._run(LessThanOrEqualTo(expected)))

    def should_be_greater_than(self, expected: Value):
        """
        Result of call should be greater than to expected
        """
        self._parse(self._run(GreaterThan(expected)))

    def should_be_greater_or_equal_to(self, expected: Value):
        """
        Result of call should be greater than or equal to expected
        """
        self._parse(self._run(GreaterThanOrEqualTo(expected)))

    def should_be(self, comparison: BaseComparison):
        """
        Pass a custom comparison class which extends `BaseComparison` for use in unit test.
        """
        if not isinstance(comparison, BaseComparison):
            raise TypeError(
                f.error(
                    "Argument passed to 'should' method must be a class which extends from BaseComparison, or one of the pre-defined comparison objects."
                )
            )

        self._parse(self._run(comparison))
