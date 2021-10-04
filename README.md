# samutil
A set of Python utility modules to help develop and maintain quality software.

# Installation
## Using Pip
```bash
  $ pip install samutil
```
## Manual
```bash
  $ git clone https://github.com/sammce/samutil
  $ cd samutil
  $ python setup.py install
```
# Usage

## Testing
### **CLI**
```bash
$ samutil test [...files]
```

### **Quick Links**
- [How do I write tests?](#the-first-api)
- [What does the output look like?](#output)
- [How do I run test files?](#running-tests)
- [What API should I use?](#what-api-should-i-use)
- [What comparisons are available?](#comparisons)
- [How do I write my own comparisons?](#writing-custom-comparisons)
- [How do I test class methods?](#testing-classes)

### Why I made this module
I made this module to solve a paricularly niche problem I had. I am also a React developer, so I am well versed in writing [jest](https://jestjs.io) tests, which this module aims to replicate. Another reason is to provide a more verbose output than the built in Python package [unittest](https://docs.python.org/3/library/unittest.html)

The testing module provides 2 simple APIs for unit testing functions and class methods.

### The first API
```python
# add.py, where the function is defined
from samutil.testing.decorators import test, case, expect
from samutil.testing.comparisons import LessThan

@test("Adds 2 integers correctly")
@case(1, 6)
@expect(7)
@case(10, b=4)
@expect(14)

@test("Doesn't return a crazy value")
@case(10, 20)
@expect(LessThan(1000))
def add(a, b):
  return a + b
```
### The second:
```python
# add.test.py, an explicit testing file

# Note: 'add' can be anything, any file ending in .test.py is executed but it is best practice for test files to share the name of whatever they are testing

from samutil.testing import UnitTest
from samutil.testing.comparisons import LessThan
# Import the test subject
from .add import add

test = UnitTest(add)

test.describe("Adds 2 integers correctly")
test(1, 6).should_equal(7)
test(10, b=4).should_equal(14)

test = UnitTest(add)
test.describe("Doesn't return a crazy value")

test(10, 20).should_be_less_than(100)
# Or, if you want to manually set a comparison
test(10, 20).should_be(LessThan(100))
```

### **Output**
Both result in the following output after running `samutil test`:

<img width="317" alt="Screenshot 2021-10-01 at 18 00 20" src="https://user-images.githubusercontent.com/78268167/135659400-1075ec25-d54f-4f9a-8e7a-71af176f2cf8.png">

### **Running tests**
The `test` command by itself recursively runs all tests in all sub directories with respect to the directory in which the command was executed.

Consider the following file system:
```
root
│   add.py
│   add.test.py  
│
└── foomodule
    │   bar.py
    │   bar.test.py
```

If the `test` command were to be executed without any arguments in `root`, `add.test.py` and `bar.test.py` would be executed automatically. For any other `.py` file, its top level definitions are programatically imported, and only run if a `@test` or `@testmethod` call is detected on it (i.e. it has the attributes which are set by the decorators).

Another way of calling the `test` command includes passing specific files as arguments. With the file structure above in mind, the command `test ./foomodule/bar.py add.test.py` would execute `add.test.py`, and import the definitions of `./foomodule/bar.py` and run any that are decorated with `@test` or `@testmethod`.

If a file has tests written with both the first and second API, only one will run. Which one depends on the name of the file, as outlined above.

---
### **What API should I use?**

The 2 APIs are identical under the hood. The first API is simply syntactic sugar for the second, but may become unmanageable if more rigorous tests are needed. 

**IMPORTANT:** For applications where performance is vital, I strongly recommend the second API. This is because the decorators work by setting attributes on the test subject, and this comes with a small overhead.

Following from that, there are some attributes which will be overwritten on the test subject. These attributes are:
- _tests
- _run_index
- _run_tests
- _is_class
- _parent

This is more so a problem on classes rather than functions, as functions rarely have custom attributes. I have tried to make the names fairly verbose so as not to cause too much hassle.

### **Comparisons**
I have provided several pre-defined comparisons, which are:
| Name | Description |
|-----------|-----------|
| **EqualTo** | Checks if `result == expected`. If a literal is passed to `@expect`, the comparison is set to `EqualTo` by default |
| **LessThan** | Checks if `result < expected` |
| **LessThanOrEqualTo** | Checks if `result <= expected` |
| **GreaterThan** | Checks if `result > expected` |
| **GreaterThanOrEqualTo** | Checks if `result >= expected` |
| **HasType** | Checks if `result` is an instance of `expected` |
| **Raises** | Checks if `result` is an exception, and an instance of `expected` |
| **ListEqual** | Checks if `result` is a list, and has exactly the same order and values as `expected` |
| **DictEqual** | Checks if `result` is a dict, and has exactly the same order and key value pairs as `expected` |
| **Not** | Wraps a comparison and negates the result. Examples: `@expect(Not(10))` or `@expect(Not(LessThan(11)))`. The amount of use cases for this is probably slim, but it's there if you need it. |

### Writing custom comparisons
If for any reason you need more functionality than what I have offered, you can write your own comparisons. The `EqualTo` comparison source code looks like this:
```python
# Your custom comparison must extend BaseComparison
from samutil.testing.comparisons import BaseComparison

class EqualTo(BaseComparison):
    # These properties are used in the test output
    operator = "=="
    negated = "!="

    def compare(self, result, expected) -> bool:
        return result == expected
```
Or alternatively, you can inherit from an existing comparison if your comparison is just a flavour of it. For example, take a look at the `ListEqual` source code:
```python
from samutil.testing.comparisons import EqualTo

class ListEqual(EqualTo):
    def compare(self, result, expected):
        if not isinstance(result, (list, tuple)): return False

        for result_val, expected_val in zip(result, expected):
            if result_val != expected_val: return False

        return True
```

When you call a comparison, the value passed during instantiation is the expected value. For instance, in the statement `EqualTo(9)`, the `compare` method would receive the following arguments:
- The value returned by the function call (`result`)
- 9 (`expected`)

### **Testing classes**
The current implementation of class based testing is to test each method separately.
Consider the following tests:
```python
# class.py
from samutil.testing import case, expect, testmethod

@testmethod("add", "Adds properly")
@case(2, 4)
@expect(6)

@testmethod("sub", "Subtracts properly")
@case(10, 4)
@expect(30.5) # Purposefully wrong
class ClassToBeTested:
  def add(a, b):
    return a + b

  @staticmethod
  def sub(a, b):
    return a - b
```
A separate decorator is used for testing class methods, as a method cannot be detected by the current file importing implementation (i.e. the decorator calls have to be at the top level)

The test-file API implementation of the above would look like this:

```python
# classname.test.py
from samutil.testing import UnitTest
from .classname import ClassToBeTested

test = UnitTest(ClassToBeTested)

test.describe("Adds properly")
test.method("add")(2, 4).should_equal(6)

test.describe("Subtracts properly")
test.method("sub")(10, 4).should_equal(30.5)
```

Both test suites would result in the following output:

<img width="520" alt="Screenshot 2021-10-01 at 22 40 17" src="https://user-images.githubusercontent.com/78268167/135689156-04b70434-36b9-4c48-9d7b-787b953413c4.png">


**NOTE:** The execution time measurement is accurate to about ~1 or 2 percent due to overhead around test subject call.


