from time import sleep

from testing import UnitTest


class ClassToBeTested:
  def add(a, b):
    return a + b

  @staticmethod
  def sub(a, b):
    return a - b

test = UnitTest(ClassToBeTested)

test.describe("Adds properly")
test.method("add").with_args(2, 4).should_equal(6)

test.describe("Subtracts properly")
test.method("sub").with_args(10, 4).should_equal(30.5)
