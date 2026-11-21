"""Template Method - refactoring des pipelines ETL.

Problèmes identifiés dans le code legacy :
  1. La validation est recopiée 3 fois (seuls les champs requis changent).
  2. Le cleanup et le load sont recopiés 3 fois à l'identique.
  3. Ajouter du logging à tous les pipelines = modifier 3 classes.
  4. Si l'ordre du workflow change, il faut le changer partout (et on peut
     oublier une étape dans un pipeline).
  5. ~80 % du code des trois classes est dupliqué.

Solution :
  - DataPipeline (ABC) : run() est la *template method*, elle fixe l'ordre
    connect -> extract -> transform -> validate -> load -> cleanup
  - étapes abstraites : connect, extract, transform (ce qui change)
  - étapes communes : validate, load, cleanup (écrites une seule fois)
  - hooks optionnels : before_run / after_run / on_error
"""

from __future__ import annotations

import time
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod


class DataPipeline(ABC):
    name: str = "Generic"
    required_fields: tuple[str, ...] = ()
    io_delay: float = 0.5  # simulation de latence ; mis à 0 dans les tests

    def __init__(self, source: str) -> None:
        self.source = source
        self.data: list[dict] | None = None
        self.log: list[str] = []

    # ---------------------------------------------------- template method --
    def run(self) -> str:
        """Le squelette de l'algorithme : les sous-classes ne le redéfinissent pas."""
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

    # ---------------------------------------- étapes propres à chaque source
    @abstractmethod
    def connect(self) -> None: ...

    @abstractmethod
    def extract(self) -> list[dict]: ...

    @abstractmethod
    def transform(self, data: list[dict]) -> list[dict]: ...

    # ------------------------------------------------- étapes communes ----
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
        """Hook optionnel."""

    def after_run(self) -> None:
        """Hook optionnel."""

    def on_error(self, exc: Exception) -> None:
        self._say(f"Pipeline failed: {exc}")

    # ----------------------------------------------------------- helpers --
    def _say(self, message: str) -> None:
        # Un seul endroit pour ajouter du logging à TOUS les pipelines.
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


# Validation de la solution : nouveau pipeline XML, rien d'autre à modifier.
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
