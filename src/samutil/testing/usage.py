from testing import case, expect, test


@test("Doesn't return a ridiculous value")
@case(4, 5)
@expect(90.0)

@test("Returns correct value for simple sum")
@case(10, 2)
@expect(12)
@case(5, 50)
@expect(55)
def add(a, b):
    return a + b
