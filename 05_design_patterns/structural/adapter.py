"""Adapter - brancher le générateur de rapports XML legacy sur le dashboard JSON.

Problèmes du code legacy :
  - interfaces incompatibles : le legacy renvoie du XML, le dashboard attend du JSON
  - logique de conversion répétée dans chaque fonction (et en trichant : on
    re-sérialise les données d'origine au lieu de convertir la sortie XML)
  - LegacyReportGenerator est une lib externe : on ne peut pas la modifier
  - couplage fort entre logique métier et conversion de format

Solution : LegacyReportAdapter implémente ReportGeneratorInterface, enveloppe
le legacy et convertit *réellement* son XML en JSON.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod


# --------------------------------------------- code existant (intouchable) --
class LegacyReportGenerator:
    def generate_report(self, data: dict) -> str:
        """Returns XML format - old system"""
        xml = "<report>\n"
        for key, value in data.items():
            xml += f"  <{key}>{value}</{key}>\n"
        xml += "</report>"
        return xml


class AnalyticsDashboard:
    def display(self, json_data: str) -> str:
        data = json.loads(json_data)
        lines = ["=== Analytics Dashboard ==="] + [f"  {k}: {v}" for k, v in data.items()]
        output = "\n".join(lines)
        print(output)
        return output


# ------------------------------------------------------------- Adapter -----
class ReportGeneratorInterface(ABC):
    """L'interface attendue par le nouveau code : renvoie du JSON."""

    @abstractmethod
    def generate(self, data: dict) -> str: ...


class LegacyReportAdapter(ReportGeneratorInterface):
    def __init__(self, legacy: LegacyReportGenerator) -> None:
        self._legacy = legacy  # composition : on enveloppe, on n'hérite pas

    def generate(self, data: dict) -> str:
        xml_report = self._legacy.generate_report(data)
        return self._xml_to_json(xml_report)

    @staticmethod
    def _xml_to_json(xml_report: str) -> str:
        root = ET.fromstring(xml_report)
        return json.dumps({child.tag: LegacyReportAdapter._parse_value(child.text) for child in root})

    @staticmethod
    def _parse_value(text: str | None) -> int | float | str | None:
        """Le XML perd les types : on retrouve int / float quand c'est possible."""
        if text is None:
            return None
        for cast in (int, float):
            try:
                return cast(text)
            except ValueError:
                pass
        return text


# --------------------------------------- code métier, désormais découplé ---
def show_report(generator: ReportGeneratorInterface, dashboard: AnalyticsDashboard, data: dict) -> str:
    return dashboard.display(generator.generate(data))


if __name__ == "__main__":
    report_generator = LegacyReportAdapter(LegacyReportGenerator())
    dashboard = AnalyticsDashboard()

    show_report(report_generator, dashboard, {"total_sales": 150000, "orders": 1234, "avg_order": 121.55})
    show_report(report_generator, dashboard, {"total_items": 5000, "low_stock": 45, "out_of_stock": 12})
