"""Exo 1 - Hospital Management System: implementation of Task 3.

The matching diagrams are in hospital_uml.md.
"""

from __future__ import annotations

import hashlib
import itertools
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


def _now() -> datetime:
    return datetime.now()


# ------------------------------------------------------------------ Users ---
class User(ABC):
    _ids = itertools.count(1)

    def __init__(self, name: str, password: str) -> None:
        self.id = next(User._ids)
        self.name = name
        self._password_hash = self._hash(password)
        self.logged_in = False

    @staticmethod
    def _hash(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, password: str) -> bool:
        self.logged_in = self._hash(password) == self._password_hash
        return self.logged_in

    def logout(self) -> None:
        self.logged_in = False

    def __repr__(self) -> str:
        return f"{type(self).__name__}(id={self.id}, name={self.name!r})"


class Patient(User):
    def __init__(self, name: str, password: str) -> None:
        super().__init__(name, password)
        self.problems: list[HealthProblem] = []

    def post_problem(self, description: str) -> HealthProblem:
        problem = HealthProblem(patient=self, description=description)
        self.problems.append(problem)
        return problem

    def past_prescriptions(self) -> list[Prescription]:
        return [p for problem in self.problems for p in problem.prescriptions]

    def pay(self, prescription: Prescription, method: PaymentMethod) -> Payment:
        if prescription.paid:
            raise ValueError("prescription already paid")
        receipt = method.pay(prescription.fee)
        prescription.paid = True
        return Payment(prescription=prescription, method=method, receipt=receipt)


class Doctor(User):
    def __init__(self, name: str, password: str, specialty: str) -> None:
        super().__init__(name, password)
        self.specialty = specialty
        self.balance = 0.0

    def provide_prescription(self, problem: HealthProblem, content: str, fee: float) -> Prescription:
        if problem.doctor is not self:
            raise PermissionError("this problem is not assigned to you")
        prescription = Prescription(content=content, fee=fee, doctor=self)
        problem.prescriptions.append(prescription)
        problem.touch()
        return prescription

    def receive_payment(self, amount: float) -> None:
        self.balance += amount


class Organizer(User):
    """Coordinates the workflow and also acts as administrator."""

    def __init__(self, name: str, password: str) -> None:
        super().__init__(name, password)
        self.members: dict[int, User] = {}

    def register_member(self, user: User) -> User:
        self.members[user.id] = user
        return user

    def assign(self, problem: HealthProblem, doctor: Doctor) -> None:
        problem.doctor = doctor
        problem.set_status(ProblemStatus.IN_REVIEW)

    def deliver(self, problem: HealthProblem) -> Prescription:
        if not problem.prescriptions:
            raise ValueError("no prescription to deliver yet")
        problem.set_status(ProblemStatus.RESOLVED)
        return problem.prescriptions[-1]

    def forward_payment(self, payment: Payment) -> None:
        if payment.forwarded:
            raise ValueError("payment already forwarded")
        payment.prescription.doctor.receive_payment(payment.amount)
        payment.forwarded = True


# ----------------------------------------------------------------- Domain ---
class ProblemStatus(Enum):
    PENDING = "pending"
    IN_REVIEW = "in-review"
    RESOLVED = "resolved"


@dataclass
class Prescription:
    content: str
    fee: float
    doctor: Doctor
    issued_at: datetime = field(default_factory=_now)
    paid: bool = False


@dataclass
class HealthProblem:
    patient: Patient
    description: str
    status: ProblemStatus = ProblemStatus.PENDING
    doctor: Doctor | None = None
    prescriptions: list[Prescription] = field(default_factory=list)
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)

    def touch(self) -> None:
        self.updated_at = _now()

    def set_status(self, status: ProblemStatus) -> None:
        self.status = status
        self.touch()


# -------------------------------------------- Payment (Strategy pattern) ---
class PaymentMethod(ABC):
    @abstractmethod
    def pay(self, amount: float) -> str:
        """Collect `amount` and return a receipt."""


class CheckPayment(PaymentMethod):
    def __init__(self, check_number: str) -> None:
        self.check_number = check_number

    def pay(self, amount: float) -> str:
        return f"Check #{self.check_number} of {amount:.2f}€ received"


class CashPayment(PaymentMethod):
    def pay(self, amount: float) -> str:
        return f"Cash payment of {amount:.2f}€ received"


class CreditCardPayment(PaymentMethod):
    def __init__(self, card_number: str) -> None:
        if len(card_number) != 16 or not card_number.isdigit():
            raise ValueError("invalid card number")
        self.card_number = card_number

    def pay(self, amount: float) -> str:
        return f"Card ****{self.card_number[-4:]} charged {amount:.2f}€"


@dataclass
class Payment:
    prescription: Prescription
    method: PaymentMethod
    receipt: str
    paid_at: datetime = field(default_factory=_now)
    forwarded: bool = False

    @property
    def amount(self) -> float:
        return self.prescription.fee


if __name__ == "__main__":
    admin = Organizer("Admin", "admin")
    patient = admin.register_member(Patient("Alice", "pwd"))
    doctor = admin.register_member(Doctor("Dr House", "vicodin", "Diagnostics"))
    assert isinstance(patient, Patient) and isinstance(doctor, Doctor)

    patient.login("pwd")
    problem = patient.post_problem("Headache for 3 days")
    print(problem.status)
    admin.assign(problem, doctor)
    print(problem.status)
    doctor.provide_prescription(problem, "Paracetamol 1g x3/day", fee=25)
    prescription = admin.deliver(problem)
    print(problem.status, "->", prescription.content)

    payment = patient.pay(prescription, CreditCardPayment("1234567812345678"))
    print(payment.receipt)
    admin.forward_payment(payment)
    print(f"{doctor.name} balance: {doctor.balance}€")
