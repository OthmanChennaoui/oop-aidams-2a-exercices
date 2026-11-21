"""OOP Problems - Inheritance.

Énoncé : https://gist.github.com/bdallard/b2f2c910e3a9b564a30c86991c97b4fc
"""

from __future__ import annotations


# --------------------------------------------------------------------------
# Problem 1 - Vehicle / Car / Bicycle
# --------------------------------------------------------------------------
class Vehicle:
    def drive(self) -> str:
        return "Driving a vehicle"


class Car(Vehicle):
    def drive(self) -> str:
        return "Driving a car"


class Bicycle(Vehicle):
    def drive(self) -> str:
        return "Riding a bicycle"


# --------------------------------------------------------------------------
# Problem 2 - Person / Student / Employee
# --------------------------------------------------------------------------
class Person:
    def __init__(self, name: str, age: int, address: str) -> None:
        self.name = name
        self.age = age
        self.address = address

    def introduce(self) -> str:
        return f"Hi, I'm {self.name}, {self.age} years old, living in {self.address}."


class Student(Person):
    def __init__(self, name: str, age: int, address: str, field_of_study: str) -> None:
        super().__init__(name, age, address)
        self.field_of_study = field_of_study

    def introduce(self) -> str:
        return f"{super().introduce()} I study {self.field_of_study}."


class Employee(Person):
    def __init__(self, name: str, age: int, address: str, company: str) -> None:
        super().__init__(name, age, address)
        self.company = company

    def introduce(self) -> str:
        return f"{super().introduce()} I work at {self.company}."


# --------------------------------------------------------------------------
# Problem 3 - BankAccount / SavingsAccount
# --------------------------------------------------------------------------
class BankAccount:
    def __init__(self, account_number: str, balance: float = 0.0) -> None:
        if balance < 0:
            raise ValueError("initial balance cannot be negative")
        self.account_number = account_number
        self._balance = balance  # "protected" : on passe par les méthodes

    @property
    def balance(self) -> float:
        return self._balance

    def deposit(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("deposit amount must be positive")
        self._balance += amount
        return self._balance

    def withdraw(self, amount: float) -> bool:
        """Retire `amount`. Renvoie False (sans rien modifier) si le solde est insuffisant."""
        if amount <= 0:
            raise ValueError("withdraw amount must be positive")
        if amount > self._balance:
            return False
        self._balance -= amount
        return True

    def transfer(self, destination: BankAccount, amount: float) -> bool:
        """Transfère vers `destination`. False si solde insuffisant, True sinon."""
        if not self.withdraw(amount):
            return False
        destination.deposit(amount)
        return True

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.account_number!r}, balance={self._balance:.2f})"


class SavingsAccount(BankAccount):
    def __init__(self, account_number: str, balance: float = 0.0, interest_rate: float = 0.03) -> None:
        super().__init__(account_number, balance)
        if interest_rate < 0:
            raise ValueError("interest rate cannot be negative")
        self.interest_rate = interest_rate

    def add_interest(self) -> float:
        """Crédite les intérêts et renvoie leur montant."""
        interest = self._balance * self.interest_rate
        self._balance += interest
        return interest

    def check_balance(self) -> float:
        return self._balance


if __name__ == "__main__":
    for v in (Vehicle(), Car(), Bicycle()):  # polymorphisme
        print(v.drive())

    for p in (
        Person("Othman", 20, "Paris"),
        Student("Lina", 21, "Lyon", "Data Science"),
        Employee("Sam", 35, "Nantes", "Airbus"),
    ):
        print(p.introduce())

    checking = BankAccount("FR-001", 500)
    savings = SavingsAccount("FR-002", 1000, interest_rate=0.05)
    print("transfer 200 :", checking.transfer(savings, 200))
    print("transfer 9999 :", checking.transfer(savings, 9999))
    print("interest :", savings.add_interest(), "->", savings.check_balance())
