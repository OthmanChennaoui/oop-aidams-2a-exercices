import pytest

import inheritance as inh
from operator_overloading import Circle, Complex, Matrix, Person, Point, Vector


# ------------------------------------------------- operator overloading ---
def test_complex_add_sub():
    assert Complex(1, 2) + Complex(3, 4) == Complex(4, 6)
    assert Complex(1, 2) - Complex(3, 4) == Complex(-2, -2)
    assert str(Complex(1, -2)) == "1 - 2i"


def test_person_gt_by_age():
    old, young = Person("A", 40, "F"), Person("B", 20, "M")
    assert old > young
    assert not young > old
    assert not Person("C", 20, "F") > young


def test_vector_dot_product():
    assert Vector(1, 2, 3) * Vector(4, 5, 6) == 32
    assert Vector(1, 0, 0) * Vector(0, 1, 0) == 0


def test_circle_all_comparisons():
    small, big = Circle(1), Circle(2)
    assert small < big and small <= big and big > small and big >= small
    assert small != big and Circle(1) == small and Circle(1) <= small
    assert len({Circle(1), Circle(1.0), Circle(2)}) == 2
    with pytest.raises(ValueError):
        Circle(-1)


def test_point_compared_by_distance():
    assert Point(3, 4) == Point(0, 5) == Point(-5, 0)
    assert Point(1, 1) < Point(3, 4)
    assert Point(3, 4) >= Point(0, 5)
    assert not Point(3, 4) < Point(0, 5)
    assert Point(3, 4).distance == 5


def test_matrix_multiplication():
    result = Matrix([[1, 2], [3, 4]]) * Matrix([[5, 6], [7, 8]])
    assert result == Matrix([[19, 22], [43, 50]])
    assert (Matrix([[1, 2, 3]]) * Matrix([[1], [2], [3]])).rows == ((14,),)
    with pytest.raises(ValueError):
        Matrix([[1, 2]]) * Matrix([[1, 2]])
    with pytest.raises(ValueError):
        Matrix([[1, 2], [3]])


# ---------------------------------------------------------- inheritance ---
def test_vehicle_polymorphism():
    assert [v.drive() for v in (inh.Vehicle(), inh.Car(), inh.Bicycle())] == [
        "Driving a vehicle",
        "Driving a car",
        "Riding a bicycle",
    ]


def test_person_student_employee():
    s = inh.Student("Lina", 21, "Lyon", "Data Science")
    e = inh.Employee("Sam", 35, "Nantes", "Airbus")
    assert isinstance(s, inh.Person) and isinstance(e, inh.Person)
    assert s.introduce().startswith("Hi, I'm Lina") and "Data Science" in s.introduce()
    assert "Airbus" in e.introduce()


def test_bank_account_deposit_withdraw():
    acc = inh.BankAccount("A", 100)
    assert acc.deposit(50) == 150
    assert acc.withdraw(30) is True and acc.balance == 120
    assert acc.withdraw(1000) is False and acc.balance == 120
    with pytest.raises(ValueError):
        acc.deposit(-5)


def test_transfer():
    src, dst = inh.BankAccount("A", 100), inh.SavingsAccount("B", 0)
    assert src.transfer(dst, 60) is True
    assert (src.balance, dst.check_balance()) == (40, 60)
    assert src.transfer(dst, 41) is False
    assert (src.balance, dst.check_balance()) == (40, 60)


def test_savings_interest():
    s = inh.SavingsAccount("S", 1000, interest_rate=0.05)
    assert s.add_interest() == pytest.approx(50)
    assert s.check_balance() == pytest.approx(1050)
