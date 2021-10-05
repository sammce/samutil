from samutil.testing.decorators import case, expect, test


@test("Adds properly")
@case(10, 4)
@expect(14)
def add(a, b):
    return a + b
