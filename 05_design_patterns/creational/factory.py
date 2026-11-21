"""Factory Method - refactoring the payment system.

Problem with the legacy code: a single `process_payment` with an if/elif chain.
Adding a payment method means modifying that function (violates the
Open/Closed Principle) and everything can only be tested as one block.

Solution:
  - PaymentProcessor (ABC): the validate() / process() contract
  - one concrete class per payment method
  - PaymentFactory: a str -> class dictionary, extensible through register()
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class PaymentProcessor(ABC):
    """Common interface for every payment processor."""

    method: str = ""
    error_message: str = "Invalid payment details"

    @abstractmethod
    def validate(self, details: dict) -> bool: ...

    @abstractmethod
    def compute_fee(self, amount: float) -> float: ...

    def process(self, amount: float, details: dict) -> dict:
        # Shared skeleton: validate, compute the fee, return the result.
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
    """Maps a payment method name to its class - no if/elif."""

    _processors: dict[str, type[PaymentProcessor]] = {
        "credit_card": CreditCardProcessor,
        "bank_transfer": BankTransferProcessor,
        "paypal": PayPalProcessor,
    }

    @classmethod
    def register(cls, name: str, processor: type[PaymentProcessor]) -> None:
        """Add Apple Pay, Crypto... without touching the existing code."""
        cls._processors[name] = processor

    def get_processor(self, payment_type: str) -> PaymentProcessor:
        try:
            return self._processors[payment_type]()
        except KeyError:
            raise ValueError(f"Unknown payment type: {payment_type}") from None


# Extension example: a new payment method, zero changes anywhere else.
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
