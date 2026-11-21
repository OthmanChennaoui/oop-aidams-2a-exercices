"""OOP Problems - Operator Overloading.

Énoncé : https://gist.github.com/bdallard/b2f2c910e3a9b564a30c86991c97b4fc
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import total_ordering


# --------------------------------------------------------------------------
# Problem 1 - Nombre complexe : + et -
# --------------------------------------------------------------------------
class Complex:
    def __init__(self, real: float, imag: float = 0.0) -> None:
        self.real = real
        self.imag = imag

    def __add__(self, other: Complex) -> Complex:
        return Complex(self.real + other.real, self.imag + other.imag)

    def __sub__(self, other: Complex) -> Complex:
        return Complex(self.real - other.real, self.imag - other.imag)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Complex):
            return NotImplemented
        return self.real == other.real and self.imag == other.imag

    def __repr__(self) -> str:
        return f"Complex({self.real}, {self.imag})"

    def __str__(self) -> str:
        sign = "+" if self.imag >= 0 else "-"
        return f"{self.real} {sign} {abs(self.imag)}i"


# --------------------------------------------------------------------------
# Problem 2 - Person : > selon l'âge
# --------------------------------------------------------------------------
class Person:
    def __init__(self, name: str, age: int, gender: str) -> None:
        self.name = name
        self.age = age
        self.gender = gender

    def __gt__(self, other: Person) -> bool:
        return self.age > other.age

    def __repr__(self) -> str:
        return f"Person({self.name!r}, {self.age}, {self.gender!r})"


# --------------------------------------------------------------------------
# Problem 4 - Vector : * = produit scalaire
# (le gist n'a pas de Problem 3)
# --------------------------------------------------------------------------
class Vector:
    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z

    def __mul__(self, other: Vector) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def __repr__(self) -> str:
        return f"Vector({self.x}, {self.y}, {self.z})"


# --------------------------------------------------------------------------
# Problem 5 - Circle : tous les opérateurs de comparaison selon le rayon
# (écrits à la main pour l'exercice ; functools.total_ordering ferait pareil)
# --------------------------------------------------------------------------
class Circle:
    def __init__(self, radius: float) -> None:
        if radius < 0:
            raise ValueError("radius must be >= 0")
        self.radius = radius

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Circle):
            return NotImplemented
        return self.radius == other.radius

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Circle):
            return NotImplemented
        return self.radius != other.radius

    def __lt__(self, other: Circle) -> bool:
        return self.radius < other.radius

    def __le__(self, other: Circle) -> bool:
        return self.radius <= other.radius

    def __gt__(self, other: Circle) -> bool:
        return self.radius > other.radius

    def __ge__(self, other: Circle) -> bool:
        return self.radius >= other.radius

    def __hash__(self) -> int:
        return hash(self.radius)

    def __repr__(self) -> str:
        return f"Circle({self.radius})"


# --------------------------------------------------------------------------
# Problem 6 - Point 2D comparé par distance euclidienne à l'origine
# --------------------------------------------------------------------------
@total_ordering
class Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    @property
    def distance(self) -> float:
        """sqrt(x² + y²)"""
        return math.hypot(self.x, self.y)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return math.isclose(self.distance, other.distance)

    def __lt__(self, other: Point) -> bool:
        return self.distance < other.distance and not self == other

    def __hash__(self) -> int:
        return hash(round(self.distance, 9))

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"


# --------------------------------------------------------------------------
# Problem 7 - Multiplication de matrices
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Matrix:
    rows: tuple[tuple[float, ...], ...]

    def __init__(self, rows: list[list[float]]) -> None:
        if not rows or any(len(r) != len(rows[0]) for r in rows):
            raise ValueError("a matrix needs non-empty rows of equal length")
        object.__setattr__(self, "rows", tuple(tuple(r) for r in rows))

    @property
    def shape(self) -> tuple[int, int]:
        return len(self.rows), len(self.rows[0])

    def __mul__(self, other: Matrix) -> Matrix:
        n, m = self.shape
        m2, p = other.shape
        if m != m2:
            raise ValueError(f"cannot multiply {self.shape} by {other.shape}")
        cols = list(zip(*other.rows))
        return Matrix(
            [[sum(a * b for a, b in zip(row, col)) for col in cols] for row in self.rows]
        )

    def __str__(self) -> str:
        return "\n".join(" ".join(f"{v:g}" for v in row) for row in self.rows)


if __name__ == "__main__":
    print("Complex :", Complex(1, 2) + Complex(3, -5), "|", Complex(1, 2) - Complex(3, -5))
    alice, bob = Person("Alice", 30, "F"), Person("Bob", 25, "M")
    print("alice > bob :", alice > bob)
    print("dot product :", Vector(1, 2, 3) * Vector(4, 5, 6))
    print("Circle(2) <= Circle(3) :", Circle(2) <= Circle(3))
    print("Point(3,4) == Point(0,5) :", Point(3, 4) == Point(0, 5))
    print("Matrix product :")
    print(Matrix([[1, 2], [3, 4]]) * Matrix([[5, 6], [7, 8]]))
