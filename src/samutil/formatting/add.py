from samutil.testing.decorators import case, expect, test


@test
@case(1, 4)
@expect(4)
def add(a, b):
    return a + b

