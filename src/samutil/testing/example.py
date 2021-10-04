from samutil.testing import UnitTest


def add(a, b):
    return a + b


add = UnitTest(add, "Adds properly")
add(1, 4).should_equal(5)
