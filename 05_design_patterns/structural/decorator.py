"""Decorator - refactoring the order pricing system.

Problems with the legacy code:
  - boolean flag explosion: every option = one more parameter
  - a single method does everything (violates the Single Responsibility Principle)
  - adding an option = modifying calculate_total (violates Open/Closed)
  - the logic of an option (e.g. insurance) cannot be reused
  - the order of operations is implicit (discount before or after shipping?)

Solution: each option is a decorator that wraps an OrderComponent, adds its
own cost / description and delegates the rest to the wrapped object.
The order of application is explicit: it is the stacking order.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class OrderComponent(ABC):
    @abstractmethod
    def get_cost(self) -> float: ...

    @abstractmethod
    def get_description(self) -> str: ...


class BaseOrder(OrderComponent):
    def __init__(self, base_price: float) -> None:
        if base_price < 0:
            raise ValueError("base price cannot be negative")
        self.base_price = base_price

    def get_cost(self) -> float:
        return self.base_price

    def get_description(self) -> str:
        return f"Base price: {self.base_price:.2f}€"


class OrderDecorator(OrderComponent):
    """Base decorator: delegates everything to the wrapped order."""

    def __init__(self, order: OrderComponent) -> None:
        self._order = order  # protected, as recommended in the course

    def get_cost(self) -> float:
        return self._order.get_cost()

    def get_description(self) -> str:
        return self._order.get_description()

    @property
    def base_price(self) -> float:
        """Walk down to the BaseOrder (insurance is computed on the base price)."""
        return self._order.base_price  # type: ignore[attr-defined]


class ExpressShippingDecorator(OrderDecorator):
    COST = 15.00

    def get_cost(self) -> float:
        return super().get_cost() + self.COST

    def get_description(self) -> str:
        return f"{super().get_description()}\nExpress shipping: +{self.COST:.2f}€"


class InsuranceDecorator(OrderDecorator):
    RATE = 0.05

    def _insurance(self) -> float:
        return self.base_price * self.RATE

    def get_cost(self) -> float:
        return super().get_cost() + self._insurance()

    def get_description(self) -> str:
        return f"{super().get_description()}\nInsurance (5%): +{self._insurance():.2f}€"


class GiftWrapDecorator(OrderDecorator):
    COST = 5.00

    def get_cost(self) -> float:
        return super().get_cost() + self.COST

    def get_description(self) -> str:
        return f"{super().get_description()}\nGift wrap: +{self.COST:.2f}€"


class DiscountDecorator(OrderDecorator):
    """Percentage discount on the total *accumulated so far*."""

    def __init__(self, order: OrderComponent, percent: float) -> None:
        super().__init__(order)
        if not 0 <= percent <= 100:
            raise ValueError("percent must be between 0 and 100")
        self.percent = percent

    def _discount(self) -> float:
        return super().get_cost() * self.percent / 100

    def get_cost(self) -> float:
        return super().get_cost() - self._discount()

    def get_description(self) -> str:
        return f"{super().get_description()}\nDiscount ({self.percent:g}%): -{self._discount():.2f}€"


class PremiumMemberDecorator(DiscountDecorator):
    """A premium member is a 10% discount: we reuse DiscountDecorator."""

    def __init__(self, order: OrderComponent) -> None:
        super().__init__(order, percent=10)

    def get_description(self) -> str:
        return f"{OrderDecorator.get_description(self)}\nPremium member (10%): -{self._discount():.2f}€"


if __name__ == "__main__":
    simple = BaseOrder(100.00)
    print(simple.get_description())
    print(f"TOTAL: {simple.get_cost():.2f}€")

    print("\n---\n")

    order: OrderComponent = BaseOrder(100.00)
    order = ExpressShippingDecorator(order)
    order = InsuranceDecorator(order)
    order = GiftWrapDecorator(order)
    order = DiscountDecorator(order, percent=15)
    order = PremiumMemberDecorator(order)

    print(order.get_description())
    print(f"Total: {order.get_cost():.2f}€")
