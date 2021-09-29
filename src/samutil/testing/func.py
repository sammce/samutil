from testing import Comparisons, case, expect, test


@test
@case(4,5)
@expect(9)
@case(1, 3)
@expect(4)
@case(1, 100)
@expect(11)
def add(a, b):
    return a + b
