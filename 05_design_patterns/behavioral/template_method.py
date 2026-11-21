"""Template Method - refactoring the ETL pipelines.

Problems found in the legacy code:
  1. Validation is copied 3 times (only the required fields change).
  2. Cleanup and load are copied 3 times, identically.
  3. Adding logging to every pipeline = modifying 3 classes.
  4. If the workflow order changes, it must be changed everywhere (and a step
     can be forgotten in one pipeline).
  5. ~80% of the code of the three classes is duplicated.

Solution:
  - DataPipeline (ABC): run() is the *template method*, it fixes the order
    connect -> extract -> transform -> validate -> load -> cleanup
  - abstract steps: connect, extract, transform (what changes)
  - shared steps: validate, load, cleanup (written only once)
  - optional hooks: before_run / after_run / on_error
"""

from __future__ import annotations

import time
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod


class DataPipeline(ABC):
    name: str = "Generic"
    required_fields: tuple[str, ...] = ()
    io_delay: float = 0.5  # simulated latency; set to 0 in the tests

    def __init__(self, source: str) -> None:
        self.source = source
        self.data: list[dict] | None = None
        self.log: list[str] = []

    # ---------------------------------------------------- template method --
    def run(self) -> str:
        """The skeleton of the algorithm: subclasses do not override it."""
        self.before_run()
        try:
            self.connect()
            self.data = self.extract()
            self._say(f"Extracted {len(self.data)} records")
            self.data = self.transform(self.data)
            self._say("Transformation complete")
            self.validate(self.data)
            self.load(self.data)
        except Exception as exc:
            self.on_error(exc)
            raise
        finally:
            self.cleanup()
        self.after_run()
        return f"{self.name} Pipeline finished"

    # ------------------------------------- steps specific to each source
    @abstractmethod
    def connect(self) -> None: ...

    @abstractmethod
    def extract(self) -> list[dict]: ...

    @abstractmethod
    def transform(self, data: list[dict]) -> list[dict]: ...

    # ---------------------------------------------------- shared steps ----
    def validate(self, data: list[dict]) -> None:
        self._say("Validating data...")
        for record in data:
            if any(f not in record for f in self.required_fields):
                raise ValueError("Invalid record structure")
        self._say("Validation passed")

    def load(self, data: list[dict]) -> None:
        self._say("Loading data to destination...")
        time.sleep(self.io_delay)
        self._say(f"Loaded {len(data)} records successfully")

    def cleanup(self) -> None:
        self._say("Cleaning up resources...")
        self.data = None
        self._say("Cleanup complete")

    # ------------------------------------------------------------ hooks ----
    def before_run(self) -> None:
        """Optional hook."""

    def after_run(self) -> None:
        """Optional hook."""

    def on_error(self, exc: Exception) -> None:
        self._say(f"Pipeline failed: {exc}")

    # ----------------------------------------------------------- helpers --
    def _say(self, message: str) -> None:
        # A single place to add logging to ALL pipelines.
        self.log.append(message)
        print(message)

    def _connect(self, target: str) -> None:
        self._say(f"Connecting to {target}: {self.source}")
        time.sleep(self.io_delay)
        self._say(f"{self.name} connection established")


class CSVPipeline(DataPipeline):
    name = "CSV"
    required_fields = ("id", "name")

    def connect(self) -> None:
        self._connect("CSV file")

    def extract(self) -> list[dict]:
        self._say("Extracting data from CSV...")
        return [{"id": 1, "name": "Alice", "age": 30}, {"id": 2, "name": "Bob", "age": 25}]

    def transform(self, data: list[dict]) -> list[dict]:
        return [{**r, "age": int(r["age"]), "name": r["name"].upper()} for r in data]


class APIPipeline(DataPipeline):
    name = "API"
    required_fields = ("user_id", "username")

    def connect(self) -> None:
        self._connect("API")

    def extract(self) -> list[dict]:
        self._say("Extracting data from API...")
        return [
            {"user_id": 101, "username": "charlie", "score": 85},
            {"user_id": 102, "username": "diana", "score": 92},
        ]

    def transform(self, data: list[dict]) -> list[dict]:
        out = []
        for r in data:
            score = int(r["score"])
            out.append({**r, "score": score, "username": r["username"].lower(), "grade": "A" if score >= 90 else "B"})
        return out


class DatabasePipeline(DataPipeline):
    name = "Database"
    required_fields = ("product_id", "price")

    def connect(self) -> None:
        self._connect("database")

    def extract(self) -> list[dict]:
        self._say("Extracting data from database...")
        return [
            {"product_id": 501, "product_name": "Laptop", "price": 1200},
            {"product_id": 502, "product_name": "Mouse", "price": 25},
        ]

    def transform(self, data: list[dict]) -> list[dict]:
        out = []
        for r in data:
            price = float(r["price"])
            out.append({**r, "price": price, "product_name": r["product_name"].title(), "tax": price * 0.2})
        return out


# Validating the solution: a new XML pipeline, nothing else to change.
class XMLPipeline(DataPipeline):
    name = "XML"
    required_fields = ("order_id", "amount")
    SAMPLE = """<orders>
        <order><order_id>9001</order_id><customer>eve</customer><amount>59.90</amount></order>
        <order><order_id>9002</order_id><customer>frank</customer><amount>120</amount></order>
    </orders>"""

    def connect(self) -> None:
        self._connect("XML file")

    def extract(self) -> list[dict]:
        self._say("Extracting data from XML...")
        root = ET.fromstring(self.SAMPLE)
        return [{child.tag: child.text for child in order} for order in root.iter("order")]

    def transform(self, data: list[dict]) -> list[dict]:
        return [
            {**r, "order_id": int(r["order_id"]), "amount": float(r["amount"]), "customer": r["customer"].capitalize()}
            for r in data
        ]


if __name__ == "__main__":
    for title, pipeline in [
        ("CSV", CSVPipeline("data/users.csv")),
        ("API", APIPipeline("https://api.example.com/users")),
        ("DATABASE", DatabasePipeline("postgresql://localhost/mydb")),
        ("XML (NEW!)", XMLPipeline("data/orders.xml")),
    ]:
        print(f"RUNNING {title} PIPELINE")
        print("=" * 70)
        print(f"\n{pipeline.run()}\n")
