# 05 - Design patterns in practice

Exercises:
[creational](https://courses.dallard.tech/sys_design/creational_pattern/) ·
[structural](https://courses.dallard.tech/sys_design/structural_pattern/) ·
[behavioral](https://courses.dallard.tech/sys_design/behavioral_pattern/)

Each file's docstring lists the *problems found* in the legacy code, then
the refactored solution follows. The UML diagrams the exercises ask for
before coding are below.

| Pattern | File | Exercise |
|---|---|---|
| Factory Method | [`creational/factory.py`](creational/factory.py) | payment system |
| Builder | [`creational/builder.py`](creational/builder.py) | HR onboarding |
| Singleton | [`creational/singleton.py`](creational/singleton.py) | configuration manager |
| Adapter | [`structural/adapter.py`](structural/adapter.py) | XML → JSON reports |
| Decorator | [`structural/decorator.py`](structural/decorator.py) | order pricing |
| Strategy | [`behavioral/strategy.py`](behavioral/strategy.py) | multi-format reports (+ HTML) |
| Template Method | [`behavioral/template_method.py`](behavioral/template_method.py) | ETL pipelines (+ XML) |

```bash
python 05_design_patterns/creational/factory.py   # etc.
pytest tests/test_design_patterns.py
```

## Factory Method

```mermaid
classDiagram
    class PaymentProcessor {
        <<abstract>>
        +validate(details)* bool
        +compute_fee(amount)* float
        +process(amount, details) dict
    }
    class CreditCardProcessor
    class BankTransferProcessor
    class PayPalProcessor
    class ApplePayProcessor
    class PaymentFactory {
        -dict _processors
        +register(name, cls)$
        +get_processor(payment_type) PaymentProcessor
    }
    PaymentProcessor <|-- CreditCardProcessor
    PaymentProcessor <|-- BankTransferProcessor
    PaymentProcessor <|-- PayPalProcessor
    PaymentProcessor <|-- ApplePayProcessor
    PaymentFactory ..> PaymentProcessor : creates
```

## Builder

```mermaid
classDiagram
    class Employee {
        <<dataclass>>
        +str first_name
        +str last_name
        +str email
        +str department
        +str position
        +float salary
        +bool has_laptop
        +bool has_vpn_access
        +bool has_admin_rights
        +...
    }
    class EmployeeBuilder {
        -dict _fields
        +with_name(first, last) EmployeeBuilder
        +with_email(email) EmployeeBuilder
        +with_job(dept, position, salary) EmployeeBuilder
        +with_equipment(laptop, parking) EmployeeBuilder
        +with_access(vpn, admin) EmployeeBuilder
        +build() Employee
    }
    class DeveloperBuilder
    class InternBuilder
    EmployeeBuilder <|-- DeveloperBuilder
    EmployeeBuilder <|-- InternBuilder
    EmployeeBuilder ..> Employee : build()
```

## Singleton

```mermaid
classDiagram
    class ConfigManager {
        -ConfigManager _instance$
        -Lock _lock$
        -dict _data
        +get_instance()$ ConfigManager
        +get(key) Any
        +set(key, value)
        +reset()$
    }
    ConfigManager --> ConfigManager : _instance
    start_application ..> ConfigManager
    connect_database ..> ConfigManager
    send_email ..> ConfigManager
    process_payment ..> ConfigManager
```

## Adapter

```mermaid
classDiagram
    class ReportGeneratorInterface {
        <<interface>>
        +generate(data)* str
    }
    class LegacyReportAdapter {
        -LegacyReportGenerator _legacy
        +generate(data) str
        -_xml_to_json(xml) str
    }
    class LegacyReportGenerator {
        +generate_report(data) str
    }
    class AnalyticsDashboard {
        +display(json_data)
    }
    ReportGeneratorInterface <|.. LegacyReportAdapter
    LegacyReportAdapter o-- LegacyReportGenerator : wraps
    AnalyticsDashboard ..> ReportGeneratorInterface : JSON
```

## Decorator

```mermaid
classDiagram
    class OrderComponent {
        <<interface>>
        +get_cost()* float
        +get_description()* str
    }
    class BaseOrder {
        +float base_price
    }
    class OrderDecorator {
        #OrderComponent _order
    }
    OrderComponent <|.. BaseOrder
    OrderComponent <|.. OrderDecorator
    OrderDecorator o-- OrderComponent : wraps
    OrderDecorator <|-- ExpressShippingDecorator
    OrderDecorator <|-- InsuranceDecorator
    OrderDecorator <|-- GiftWrapDecorator
    OrderDecorator <|-- DiscountDecorator
    DiscountDecorator <|-- PremiumMemberDecorator
```

Example from the exercise (100 € + express + insurance + gift wrap, -15%, -10% premium):
`(100 + 15 + 5 + 5) × 0.85 × 0.90 ≈ 95.62 €`.

## Strategy

```mermaid
classDiagram
    class ReportFormatStrategy {
        <<interface>>
        +str extension
        +format(data)* str
    }
    class ReportGenerator {
        -ReportFormatStrategy _strategy
        +list data
        +set_strategy(strategy)
        +generate_report() str
        +save_report(filename) Path
    }
    ReportGenerator o-- ReportFormatStrategy
    ReportFormatStrategy <|.. PDFFormatStrategy
    ReportFormatStrategy <|.. ExcelFormatStrategy
    ReportFormatStrategy <|.. CSVFormatStrategy
    ReportFormatStrategy <|.. JSONFormatStrategy
    ReportFormatStrategy <|.. HTMLFormatStrategy
```

> Note: on the course website this exercise is filed under "Template Method",
> but it explicitly asks for a **Strategy** pattern.

## Template Method

```mermaid
classDiagram
    class DataPipeline {
        <<abstract>>
        +str source
        +tuple required_fields
        +run() str
        +connect()*
        +extract()* list
        +transform(data)* list
        +validate(data)
        +load(data)
        +cleanup()
        +before_run()
        +after_run()
        +on_error(exc)
    }
    DataPipeline <|-- CSVPipeline
    DataPipeline <|-- APIPipeline
    DataPipeline <|-- DatabasePipeline
    DataPipeline <|-- XMLPipeline
```

`run()` fixes the order `connect → extract → transform → validate → load → cleanup`;
`cleanup()` runs in a `finally` block, so it can never be skipped, even on errors.
