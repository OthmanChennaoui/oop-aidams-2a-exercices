"""Factory Method - refactoring du système de paiement.

Problème du code legacy : un seul `process_payment` avec une chaîne if/elif.
Ajouter un moyen de paiement oblige à modifier cette fonction (violation de
l'Open/Closed Principle) et tout est testé d'un bloc.

Solution :
  - PaymentProcessor (ABC) : le contrat validate() / process()
  - une classe concrète par moyen de paiement
  - PaymentFactory : un dictionnaire str -> classe, extensible via register()
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class PaymentProcessor(ABC):
    """Interface commune à tous les processeurs de paiement."""

    method: str = ""
    error_message: str = "Invalid payment details"

    @abstractmethod
    def validate(self, details: dict) -> bool: ...

    @abstractmethod
    def compute_fee(self, amount: float) -> float: ...

    def process(self, amount: float, details: dict) -> dict:
        # Squelette commun : valider, calculer les frais, renvoyer le résultat.
        if not self.validate(details):
            return {"success": False, "error": self.error_message}
        fee = self.compute_fee(amount)
        return {"success": True, "method": self.method, "amount": amount + fee, "fee": fee}


class CreditCardProcessor(PaymentProcessor):
    method = "credit_card"
    error_message = "Invalid card details"
    FEE_RATE = 0.029  # 2.9 %

    def validate(self, details: dict) -> bool:
        card_number = details.get("card_number") or ""
        cvv = details.get("cvv") or ""
        return len(card_number) == 16 and len(cvv) == 3

    def compute_fee(self, amount: float) -> float:
        return amount * self.FEE_RATE


class BankTransferProcessor(PaymentProcessor):
    method = "bank_transfer"
    error_message = "Invalid IBAN"
    FLAT_FEE = 1.50

    def validate(self, details: dict) -> bool:
        return len(details.get("iban") or "") >= 15

    def compute_fee(self, amount: float) -> float:
        return self.FLAT_FEE


class PayPalProcessor(PaymentProcessor):
    method = "paypal"
    error_message = "Invalid PayPal email"

    def validate(self, details: dict) -> bool:
        return "@" in (details.get("email") or "")

    def compute_fee(self, amount: float) -> float:
        return amount * 0.034 + 0.30  # 3.4 % + 0.30 €


class PaymentFactory:
    """Associe un nom de moyen de paiement à sa classe — sans if/elif."""

    _processors: dict[str, type[PaymentProcessor]] = {
        "credit_card": CreditCardProcessor,
        "bank_transfer": BankTransferProcessor,
        "paypal": PayPalProcessor,
    }

    @classmethod
    def register(cls, name: str, processor: type[PaymentProcessor]) -> None:
        """Ajouter Apple Pay, Crypto... sans toucher au code existant."""
        cls._processors[name] = processor

    def get_processor(self, payment_type: str) -> PaymentProcessor:
        try:
            return self._processors[payment_type]()
        except KeyError:
            raise ValueError(f"Unknown payment type: {payment_type}") from None


# Exemple d'extension : un nouveau moyen de paiement, zéro modification ailleurs.
class ApplePayProcessor(PaymentProcessor):
    method = "apple_pay"
    error_message = "Invalid Apple Pay token"

    def validate(self, details: dict) -> bool:
        return bool(details.get("token"))

    def compute_fee(self, amount: float) -> float:
        return amount * 0.015


PaymentFactory.register("apple_pay", ApplePayProcessor)


if __name__ == "__main__":
    factory = PaymentFactory()

    processor = factory.get_processor("credit_card")
    print(processor.process(100.0, {"card_number": "1234567890123456", "cvv": "123"}))

    processor = factory.get_processor("bank_transfer")
    print(processor.process(100.0, {"iban": "FR7630006000011234567890189", "bic": "BNPAFRPP"}))

    print(factory.get_processor("paypal").process(100.0, {"email": "me@example.com"}))
    print(factory.get_processor("apple_pay").process(100.0, {"token": "tok_abc"}))
