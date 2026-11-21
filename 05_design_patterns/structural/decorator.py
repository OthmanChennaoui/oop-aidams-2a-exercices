"""Decorator - refactoring du calcul de prix des commandes.

Problèmes du code legacy :
  - explosion de flags booléens : chaque option = un paramètre de plus
  - une seule méthode fait tout (viole le Single Responsibility Principle)
  - ajouter une option = modifier calculate_total (viole Open/Closed)
  - la logique d'une option (ex. assurance) n'est pas réutilisable
  - l'ordre des opérations est implicite (remise avant ou après livraison ?)

Solution : chaque option est un décorateur qui enveloppe un OrderComponent,
ajoute son coût / sa description et délègue le reste à l'objet enveloppé.
L'ordre d'application est explicite : c'est l'ordre d'empilement.
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
    """Décorateur de base : délègue tout à la commande enveloppée."""

    def __init__(self, order: OrderComponent) -> None:
        self._order = order  # protected, comme conseillé dans le cours

    def get_cost(self) -> float:
        return self._order.get_cost()

    def get_description(self) -> str:
        return self._order.get_description()

    @property
    def base_price(self) -> float:
        """Remonte jusqu'à la BaseOrder (l'assurance se calcule sur le prix de base)."""
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
    """Remise en % sur le total *accumulé jusqu'ici*."""

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
    """Un membre premium, c'est une remise de 10 % : on réutilise DiscountDecorator."""

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
