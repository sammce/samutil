from samutil.testing import UnitTest


def add(a, b):
    return a + b

t = UnitTest(add)
t.describe("Adds properly")
t(10, 4).should_equal(14)
