"""Adapter - plugging the legacy XML report generator into the JSON dashboard.

Problems with the legacy code:
  - incompatible interfaces: the legacy system returns XML, the dashboard expects JSON
  - conversion logic repeated in every function (and cheating: it re-serialises
    the original data instead of converting the XML output)
  - LegacyReportGenerator is an external library: it cannot be modified
  - tight coupling between business logic and format conversion

Solution: LegacyReportAdapter implements ReportGeneratorInterface, wraps the
legacy generator and *really* converts its XML into JSON.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod


# ---------------------------------------- existing code (cannot change) --
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
    """The interface expected by the new code: returns JSON."""

    @abstractmethod
    def generate(self, data: dict) -> str: ...


class LegacyReportAdapter(ReportGeneratorInterface):
    def __init__(self, legacy: LegacyReportGenerator) -> None:
        self._legacy = legacy  # composition: we wrap, we don't inherit

    def generate(self, data: dict) -> str:
        xml_report = self._legacy.generate_report(data)
        return self._xml_to_json(xml_report)

    @staticmethod
    def _xml_to_json(xml_report: str) -> str:
        root = ET.fromstring(xml_report)
        return json.dumps({child.tag: LegacyReportAdapter._parse_value(child.text) for child in root})

    @staticmethod
    def _parse_value(text: str | None) -> int | float | str | None:
        """XML loses the types: recover int / float when possible."""
        if text is None:
            return None
        for cast in (int, float):
            try:
                return cast(text)
            except ValueError:
                pass
        return text


# ------------------------------------ business code, now decoupled ---
def show_report(generator: ReportGeneratorInterface, dashboard: AnalyticsDashboard, data: dict) -> str:
    return dashboard.display(generator.generate(data))


if __name__ == "__main__":
    report_generator = LegacyReportAdapter(LegacyReportGenerator())
    dashboard = AnalyticsDashboard()

    show_report(report_generator, dashboard, {"total_sales": 150000, "orders": 1234, "avg_order": 121.55})
    show_report(report_generator, dashboard, {"total_items": 5000, "low_stock": 45, "out_of_stock": 12})
