# 03 - OOP Problems

Exercise: <https://gist.github.com/bdallard/b2f2c910e3a9b564a30c86991c97b4fc> (slide 67)

| File | Content |
|---|---|
| [`operator_overloading.py`](operator_overloading.py) | `Complex` (+, -), `Person` (>), `Vector` (* = dot product), `Circle` (all 6 comparisons), `Point` (compared by distance from the origin), `Matrix` (matrix product) |
| [`inheritance.py`](inheritance.py) | `Vehicle`/`Car`/`Bicycle`, `Person`/`Student`/`Employee`, `BankAccount`/`SavingsAccount` (with `transfer`) |

The gist has no *Problem 3* in the Operator Overloading part (it jumps from 2 to 4).

```bash
python 03_oop/operator_overloading.py
python 03_oop/inheritance.py
pytest tests/test_oop.py
```

## Key takeaways

- Python operators call *dunder methods*: `a + b` → `a.__add__(b)`,
  `a > b` → `a.__gt__(b)`, `a * b` → `a.__mul__(b)`.
- Return `NotImplemented` (not `False`) from `__eq__` when the other object
  has the wrong type: Python then tries the reflected operation.
- Defining `__eq__` makes the class unhashable: redefine `__hash__` to use it
  in a `set` or as a `dict` key.
- `@functools.total_ordering` generates `<=`, `>`, `>=` from `__eq__` + `__lt__`
  (used for `Point`, written by hand for `Circle`).
- `super().__init__(...)` reuses the parent constructor; `super().introduce()`
  extends a method instead of copying it.
