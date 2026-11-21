# 05 - Design patterns in practice

Énoncés :
[creational](https://courses.dallard.tech/sys_design/creational_pattern/) ·
[structural](https://courses.dallard.tech/sys_design/structural_pattern/) ·
[behavioral](https://courses.dallard.tech/sys_design/behavioral_pattern/)

Chaque fichier contient en docstring les *problèmes identifiés* dans le code
legacy, puis la solution refactorée. Les diagrammes UML demandés avant de
coder sont ci-dessous.

| Pattern | Fichier | Exercice |
|---|---|---|
| Factory Method | [`creational/factory.py`](creational/factory.py) | système de paiement |
| Builder | [`creational/builder.py`](creational/builder.py) | onboarding RH |
| Singleton | [`creational/singleton.py`](creational/singleton.py) | gestionnaire de config |
| Adapter | [`structural/adapter.py`](structural/adapter.py) | rapports XML → JSON |
| Decorator | [`structural/decorator.py`](structural/decorator.py) | prix des commandes |
| Strategy | [`behavioral/strategy.py`](behavioral/strategy.py) | rapports multi-formats (+ HTML) |
| Template Method | [`behavioral/template_method.py`](behavioral/template_method.py) | pipelines ETL (+ XML) |

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
    PaymentFactory ..> PaymentProcessor : crée
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
    LegacyReportAdapter o-- LegacyReportGenerator : enveloppe
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
    OrderDecorator o-- OrderComponent : enveloppe
    OrderDecorator <|-- ExpressShippingDecorator
    OrderDecorator <|-- InsuranceDecorator
    OrderDecorator <|-- GiftWrapDecorator
    OrderDecorator <|-- DiscountDecorator
    DiscountDecorator <|-- PremiumMemberDecorator
```

Exemple du sujet (100 € + express + assurance + emballage, -15 %, -10 % premium) :
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

> Remarque : l'énoncé est rangé sous « Template Method » sur le site mais
> demande explicitement un **Strategy** pour cet exercice.

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

`run()` fixe l'ordre `connect → extract → transform → validate → load → cleanup` ;
`cleanup()` est dans un `finally` donc impossible à sauter, même en cas d'erreur.
