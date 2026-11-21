"""Strategy - refactoring du générateur de rapports multi-formats.

Problèmes identifiés dans le code legacy :
  1. Ajouter un format (XML, Markdown...) = modifier generate_report ET
     save_report : violation de l'Open/Closed Principle.
  2. Deux chaînes if/elif parallèles qui doivent rester synchronisées
     (le format et son extension de fichier).
  3. Impossible de tester un format isolément : tout est dans une méthode.
  4. Le format est un simple str passé à chaque appel : aucune vérification,
     "Unknown format" renvoyé silencieusement.
  5. Duplication : la boucle sur les données et l'écriture du fichier sont
     répétées pour chaque format.

Solution :
  - ReportFormatStrategy (interface) : format() + extension
  - une stratégie concrète par format
  - ReportGenerator (contexte) : set_strategy() pour changer à l'exécution
"""

from __future__ import annotations

import html
import json
from abc import ABC, abstractmethod
from pathlib import Path


class ReportFormatStrategy(ABC):
    extension: str = ""

    @abstractmethod
    def format(self, data: list[dict]) -> str: ...


class PDFFormatStrategy(ReportFormatStrategy):
    extension = ".pdf"

    def format(self, data: list[dict]) -> str:
        rows = "".join(f"| {item['name']:20} | {item['value']:10} |\n" for item in data)
        return f"PDF REPORT\n{'=' * 50}\n{rows}{'=' * 50}\nEnd of PDF Report"


class ExcelFormatStrategy(ReportFormatStrategy):
    extension = ".xlsx"

    def format(self, data: list[dict]) -> str:
        rows = "".join(f"{item['name']}\t{item['value']}\n" for item in data)
        return f"EXCEL REPORT\n{'-' * 50}\nName\tValue\n{rows}{'-' * 50}\n"


class CSVFormatStrategy(ReportFormatStrategy):
    extension = ".csv"

    def format(self, data: list[dict]) -> str:
        return "name,value\n" + "".join(f"{item['name']},{item['value']}\n" for item in data)


class JSONFormatStrategy(ReportFormatStrategy):
    extension = ".json"

    def format(self, data: list[dict]) -> str:
        return json.dumps(data, indent=2)


# Test final de l'exo : nouveau format SANS modifier les classes existantes.
class HTMLFormatStrategy(ReportFormatStrategy):
    extension = ".html"

    def format(self, data: list[dict]) -> str:
        rows = "\n".join(
            f"    <tr><td>{html.escape(str(item['name']))}</td><td>{item['value']}</td></tr>" for item in data
        )
        return (
            "<table>\n    <tr><th>Name</th><th>Value</th></tr>\n"
            f"{rows}\n</table>"
        )


class ReportGenerator:
    """Le contexte : il ne connaît que l'interface ReportFormatStrategy."""

    def __init__(self, data: list[dict], strategy: ReportFormatStrategy | None = None) -> None:
        self.data = data
        self._strategy = strategy

    def set_strategy(self, strategy: ReportFormatStrategy) -> None:
        self._strategy = strategy

    def generate_report(self) -> str:
        if self._strategy is None:
            raise ValueError("No format strategy set")
        return self._strategy.format(self.data)

    def save_report(self, filename: str | Path) -> Path:
        content = self.generate_report()
        path = Path(filename).with_suffix(self._strategy.extension)  # type: ignore[union-attr]
        path.write_text(content, encoding="utf-8")
        return path


if __name__ == "__main__":
    data = [
        {"name": "Sales Q1", "value": 15000},
        {"name": "Sales Q2", "value": 18000},
        {"name": "Sales Q3", "value": 22000},
        {"name": "Sales Q4", "value": 25000},
    ]
    generator = ReportGenerator(data)

    for title, strategy in [
        ("PDF", PDFFormatStrategy()),
        ("CSV", CSVFormatStrategy()),
        ("JSON", JSONFormatStrategy()),
        ("HTML (NEW!)", HTMLFormatStrategy()),
    ]:
        print(f"=== {title} FORMAT ===")
        generator.set_strategy(strategy)
        print(generator.generate_report())
        print("\n" + "=" * 60 + "\n")
