from testing import case, expect, test


@test("Add function can add properly")
@case(4, 5)
@expect(90.0)
@test("Some sub test")
@case(10, 2)
@expect(12)
def add(a, b):
    return a + b
