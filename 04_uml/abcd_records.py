"""Exo 2 - ABCD Records : implémentation du diagramme de classes (Task 2.2).

Scénario demandé : un membre Royal commande 2 CDs (un indisponible) et paie par chèque.
"""

from __future__ import annotations

import itertools
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from enum import Enum


# ---------------------------------------------------------------- Members ---
class Member(ABC):
    def __init__(self, member_id: int, name: str, address: str) -> None:
        self.member_id = member_id
        self.name = name
        self.address = address

    @abstractmethod
    def discount_rate(self) -> float: ...

    @abstractmethod
    def can_order_unavailable(self) -> bool: ...


class RoyalMember(Member):
    def discount_rate(self) -> float:
        return 0.10

    def can_order_unavailable(self) -> bool:
        return True


class RegularMember(Member):
    def discount_rate(self) -> float:
        return 0.0

    def can_order_unavailable(self) -> bool:
        return False


@dataclass
class NonMember:
    name: str
    address: str


@dataclass
class MembershipApplication:
    applicant: NonMember
    sent_on: date = field(default_factory=date.today)


# ------------------------------------------------------------------ Items ---
class Item(ABC):
    def __init__(self, ref: str, title: str, artist: str, price: float, stock: int) -> None:
        self.ref = ref
        self.title = title
        self.artist = artist
        self.price = price
        self.stock = stock

    def is_available(self, quantity: int = 1) -> bool:
        return self.stock >= quantity

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.title!r}, stock={self.stock})"


class CD(Item):
    def __init__(self, ref: str, title: str, artist: str, price: float, stock: int, tracks: int = 10) -> None:
        super().__init__(ref, title, artist, price, stock)
        self.tracks = tracks


class Tape(Item):
    def __init__(self, ref: str, title: str, artist: str, price: float, stock: int, duration_min: int = 60) -> None:
        super().__init__(ref, title, artist, price, stock)
        self.duration_min = duration_min


# ----------------------------------------------------------------- Orders ---
class OrderStatus(Enum):
    NEW = "new"
    PROCESSED = "processed"
    PARTIALLY_SHIPPED = "partially_shipped"
    PAID = "paid"


@dataclass
class OrderLine:
    item: Item
    quantity: int
    backordered: bool = False

    def line_total(self) -> float:
        return self.item.price * self.quantity


@dataclass
class Invoice:
    order_id: int
    amount: float

    def print(self) -> str:
        return f"INVOICE order #{self.order_id} - amount due: {self.amount:.2f}€"


@dataclass
class ShippingList:
    lines: list[OrderLine]

    def print(self) -> str:
        return "SHIPPING LIST\n" + "\n".join(f"  {l.quantity} x {l.item.title}" for l in self.lines)


class Order:
    _ids = itertools.count(1)

    def __init__(self, member: Member) -> None:
        self.order_id = next(Order._ids)
        self.member = member
        self.order_date = date.today()
        self.lines: list[OrderLine] = []
        self.status = OrderStatus.NEW
        self.invoice: Invoice | None = None
        self.shipping_list: ShippingList | None = None
        self.payment: Payment | None = None

    def add_item(self, item: Item, quantity: int = 1) -> None:
        self.lines.append(OrderLine(item, quantity))

    def subtotal(self) -> float:
        return sum(line.line_total() for line in self.lines)

    def total(self) -> float:
        return round(self.subtotal() * (1 - self.member.discount_rate()), 2)


# --------------------------------------------------------------- Payments ---
class Payment(ABC):
    def __init__(self, amount: float) -> None:
        self.amount = amount
        self.paid_on = date.today()

    @abstractmethod
    def process(self) -> str: ...


class Cash(Payment):
    def process(self) -> str:
        return f"Cash {self.amount:.2f}€ collected"


class Check(Payment):
    def __init__(self, amount: float, check_number: str) -> None:
        super().__init__(amount)
        self.check_number = check_number

    def process(self) -> str:
        return f"Check #{self.check_number} of {self.amount:.2f}€ deposited"


class BankDraft(Payment):
    def __init__(self, amount: float, bank_name: str) -> None:
        super().__init__(amount)
        self.bank_name = bank_name

    def process(self) -> str:
        return f"Bank draft from {self.bank_name} of {self.amount:.2f}€ verified"


# ------------------------------------------------------------------ Staff ---
class DailyRecords:
    def __init__(self) -> None:
        self.orders: list[Order] = []

    def save(self, order: Order) -> None:
        self.orders.append(order)


class OrderProcessingClerk:
    def __init__(self, records: DailyRecords) -> None:
        self.records = records

    @staticmethod
    def verify_membership(person: object) -> bool:
        return isinstance(person, Member)

    def handle_request(self, person: Member | NonMember) -> MembershipApplication | None:
        """Non-membres : on leur envoie un formulaire d'adhésion."""
        if self.verify_membership(person):
            return None
        assert isinstance(person, NonMember)
        return MembershipApplication(person)

    def process_order(self, order: Order) -> Order:
        shippable: list[OrderLine] = []
        kept: list[OrderLine] = []
        for line in order.lines:
            if line.item.is_available(line.quantity):
                line.item.stock -= line.quantity
                shippable.append(line)
                kept.append(line)
            elif order.member.can_order_unavailable():
                line.backordered = True  # sera commandé auprès du fournisseur
                kept.append(line)
            # sinon (membre Regular) : la ligne est refusée
        order.lines = kept
        order.invoice = Invoice(order.order_id, order.total())
        order.shipping_list = ShippingList(shippable)
        order.status = (
            OrderStatus.PARTIALLY_SHIPPED if any(l.backordered for l in kept) else OrderStatus.PROCESSED
        )
        self.records.save(order)
        return order


class CollectionDeptClerk:
    @staticmethod
    def collect(order: Order, payment: Payment) -> str:
        if order.invoice is None:
            raise ValueError("order must be processed first")
        if payment.amount != order.invoice.amount:
            raise ValueError("payment amount does not match the invoice")
        receipt = payment.process()
        order.payment = payment
        order.status = OrderStatus.PAID
        return receipt


if __name__ == "__main__":
    records = DailyRecords()
    clerk = OrderProcessingClerk(records)

    print(clerk.handle_request(NonMember("Bob", "Lille")))

    alice = RoyalMember(42, "Alice", "Paris")
    cd1 = CD("CD-001", "Kind of Blue", "Miles Davis", 15.0, stock=5)
    cd2 = CD("CD-002", "Abbey Road", "The Beatles", 15.0, stock=0)

    order = Order(alice)
    order.add_item(cd1)
    order.add_item(cd2)
    clerk.process_order(order)

    print(order.status, order.lines)
    print(order.invoice.print())
    print(order.shipping_list.print())
    print(CollectionDeptClerk.collect(order, Check(order.total(), "000123")))
    print(order.status)
