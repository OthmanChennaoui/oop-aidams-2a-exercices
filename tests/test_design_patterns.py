import json
import threading

import pytest

import adapter
import builder
import decorator as deco
import factory
import singleton
import strategy
import template_method as tm


# --------------------------------------------------------------- Factory ---
class TestFactory:
    @pytest.mark.parametrize(
        "kind, details, fee",
        [
            ("credit_card", {"card_number": "1234567890123456", "cvv": "123"}, 2.9),
            ("bank_transfer", {"iban": "FR7630006000011234567890189"}, 1.5),
            ("paypal", {"email": "a@b.c"}, 3.7),
        ],
    )
    def test_processors(self, kind, details, fee):
        result = factory.PaymentFactory().get_processor(kind).process(100.0, details)
        assert result["success"] is True
        assert result["method"] == kind
        assert result["fee"] == pytest.approx(fee)
        assert result["amount"] == pytest.approx(100 + fee)

    @pytest.mark.parametrize(
        "kind, details",
        [
            ("credit_card", {"card_number": "123", "cvv": "123"}),
            ("credit_card", {"card_number": "1234567890123456"}),
            ("bank_transfer", {"iban": "FR76"}),
            ("paypal", {"email": "nope"}),
        ],
    )
    def test_invalid_details(self, kind, details):
        assert factory.PaymentFactory().get_processor(kind).process(100.0, details)["success"] is False

    def test_unknown_type(self):
        with pytest.raises(ValueError, match="Unknown payment type"):
            factory.PaymentFactory().get_processor("cheque")

    def test_extension_without_modification(self):
        processor = factory.PaymentFactory().get_processor("apple_pay")
        assert isinstance(processor, factory.PaymentProcessor)

    def test_interface_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            factory.PaymentProcessor()


# --------------------------------------------------------------- Builder ---
class TestBuilder:
    def test_fluent_build(self):
        e = (
            builder.EmployeeBuilder()
            .with_name("John", "Doe")
            .with_email("john.doe@company.com")
            .with_job("Engineering", "Senior Developer", 75000)
            .with_equipment(laptop=True, parking=False)
            .with_access(vpn=True, admin=True)
            .build()
        )
        assert e.full_name == "John Doe"
        assert (e.has_laptop, e.has_parking, e.has_vpn_access, e.has_admin_rights) == (True, False, True, True)
        assert e.contract_type == "permanent"

    def test_developer_preset_always_has_admin(self):
        dev = builder.DeveloperBuilder("John", "Doe", "j@d.com").build()
        assert dev.has_admin_rights and dev.position == "Senior Developer"

    def test_intern_preset(self):
        intern = builder.InternBuilder("Jane", "Smith", "j@s.com", "Marketing", 42).build()
        assert intern.contract_type == "internship" and intern.manager_id == 42
        assert not intern.has_admin_rights

    @pytest.mark.parametrize(
        "steps, message",
        [
            (lambda b: b.with_email("a@b.c").with_job("X", "Y", 1), "Name"),
            (lambda b: b.with_name("A", "B").with_email("bad").with_job("X", "Y", 1), "email"),
            (lambda b: b.with_name("A", "B").with_email("a@b.c"), "Job"),
            (lambda b: b.with_name("A", "B").with_email("a@b.c").with_job("X", "Y", -1), "Salary"),
        ],
    )
    def test_validation(self, steps, message):
        with pytest.raises(ValueError, match=message):
            steps(builder.EmployeeBuilder()).build()

    def test_product_is_immutable(self):
        e = builder.DeveloperBuilder("A", "B", "a@b.c").build()
        with pytest.raises(AttributeError):
            e.salary = 0


# ------------------------------------------------------------- Singleton ---
class TestSingleton:
    def test_same_instance_loaded_once(self, fresh_config):
        assert singleton.ConfigManager.get_instance() is fresh_config
        singleton.start_application()
        singleton.connect_database()
        singleton.send_email("u@test.com", "Hi")
        singleton.process_payment(10)
        assert fresh_config.load_count == 1

    def test_nested_get(self, fresh_config):
        assert fresh_config.get("database.host") == "localhost"
        assert fresh_config.get("app.debug") is True
        assert fresh_config.get("database.port") == 5432
        assert fresh_config.get("nope.nothing", default=None) is None
        with pytest.raises(KeyError):
            fresh_config.get("nope")

    def test_shared_state(self, fresh_config):
        fresh_config.set("database.host", "db.prod")
        assert "db.prod" in singleton.connect_database()

    def test_direct_instantiation_forbidden(self, fresh_config):
        with pytest.raises(RuntimeError):
            singleton.ConfigManager()

    def test_thread_safe(self, tmp_path):
        path = tmp_path / "c.json"
        path.write_text(json.dumps({"a": 1}))
        singleton.ConfigManager.reset()
        seen = []
        threads = [
            threading.Thread(target=lambda: seen.append(singleton.ConfigManager.get_instance(path)))
            for _ in range(20)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len({id(x) for x in seen}) == 1
        singleton.ConfigManager.reset()


# --------------------------------------------------------------- Adapter ---
class TestAdapter:
    def test_adapter_returns_json_with_types(self):
        gen = adapter.LegacyReportAdapter(adapter.LegacyReportGenerator())
        data = {"total_sales": 150000, "orders": 1234, "avg_order": 121.55}
        assert json.loads(gen.generate(data)) == data

    def test_adapter_implements_interface(self):
        assert isinstance(adapter.LegacyReportAdapter(adapter.LegacyReportGenerator()), adapter.ReportGeneratorInterface)

    def test_dashboard_integration(self, capsys):
        gen = adapter.LegacyReportAdapter(adapter.LegacyReportGenerator())
        adapter.show_report(gen, adapter.AnalyticsDashboard(), {"low_stock": 45})
        assert "low_stock: 45" in capsys.readouterr().out


# ------------------------------------------------------------- Decorator ---
class TestDecorator:
    def test_base(self):
        assert deco.BaseOrder(100).get_cost() == 100

    def test_full_stack_matches_legacy(self):
        order = deco.BaseOrder(100.0)
        order = deco.ExpressShippingDecorator(order)
        order = deco.InsuranceDecorator(order)
        order = deco.GiftWrapDecorator(order)
        order = deco.DiscountDecorator(order, percent=15)
        order = deco.PremiumMemberDecorator(order)
        # même résultat que le code legacy : (100+15+5+5) * 0.85 * 0.90
        assert order.get_cost() == pytest.approx(95.625)
        lines = order.get_description().splitlines()
        assert lines[0].startswith("Base price") and lines[-1].startswith("Premium member")
        assert len(lines) == 6

    def test_order_of_decorators_matters(self):
        a = deco.DiscountDecorator(deco.ExpressShippingDecorator(deco.BaseOrder(100)), percent=10)
        b = deco.ExpressShippingDecorator(deco.DiscountDecorator(deco.BaseOrder(100), percent=10))
        assert a.get_cost() == pytest.approx(103.5)
        assert b.get_cost() == pytest.approx(105.0)

    def test_insurance_on_base_price_only(self):
        order = deco.InsuranceDecorator(deco.ExpressShippingDecorator(deco.BaseOrder(100)))
        assert order.get_cost() == pytest.approx(120)

    def test_invalid_discount(self):
        with pytest.raises(ValueError):
            deco.DiscountDecorator(deco.BaseOrder(10), percent=120)


# -------------------------------------------------------------- Strategy ---
class TestStrategy:
    def test_csv(self, report_data):
        gen = strategy.ReportGenerator(report_data, strategy.CSVFormatStrategy())
        assert gen.generate_report() == "name,value\nSales Q1,15000\nSales Q2,18000\n"

    def test_json(self, report_data):
        gen = strategy.ReportGenerator(report_data, strategy.JSONFormatStrategy())
        assert json.loads(gen.generate_report()) == report_data

    def test_switch_at_runtime(self, report_data):
        gen = strategy.ReportGenerator(report_data)
        gen.set_strategy(strategy.PDFFormatStrategy())
        assert gen.generate_report().startswith("PDF REPORT")
        gen.set_strategy(strategy.ExcelFormatStrategy())
        assert gen.generate_report().startswith("EXCEL REPORT")

    def test_html_added_without_modification(self, report_data):
        gen = strategy.ReportGenerator(report_data, strategy.HTMLFormatStrategy())
        assert "<td>Sales Q1</td><td>15000</td>" in gen.generate_report()

    def test_save_uses_strategy_extension(self, report_data, tmp_path):
        gen = strategy.ReportGenerator(report_data, strategy.CSVFormatStrategy())
        path = gen.save_report(tmp_path / "sales_report")
        assert path.name == "sales_report.csv"
        assert path.read_text().startswith("name,value")

    def test_no_strategy(self, report_data):
        with pytest.raises(ValueError):
            strategy.ReportGenerator(report_data).generate_report()


# -------------------------------------------------------- Template Method ---
class TestTemplateMethod:
    @pytest.mark.parametrize(
        "cls, name",
        [(tm.CSVPipeline, "CSV"), (tm.APIPipeline, "API"), (tm.DatabasePipeline, "Database"), (tm.XMLPipeline, "XML")],
    )
    def test_pipelines_run(self, cls, name):
        p = cls("src")
        assert p.run() == f"{name} Pipeline finished"
        assert p.data is None  # cleanup effectué
        steps = [line for line in p.log if line.startswith(("Connecting", "Validating", "Loading", "Cleaning"))]
        assert [s.split()[0] for s in steps] == ["Connecting", "Validating", "Loading", "Cleaning"]

    def test_transform_results(self):
        p = tm.APIPipeline("src")
        data = p.transform(p.extract())
        assert [r["grade"] for r in data] == ["B", "A"]
        x = tm.XMLPipeline("src")
        assert x.transform(x.extract())[0] == {"order_id": 9001, "customer": "Eve", "amount": 59.9}

    def test_validation_failure_still_cleans_up(self):
        class BrokenPipeline(tm.CSVPipeline):
            def extract(self):
                return [{"id": 1}]  # pas de "name"

            def transform(self, data):
                return data

        p = BrokenPipeline("src")
        with pytest.raises(ValueError, match="Invalid record structure"):
            p.run()
        assert p.data is None
        assert any("Pipeline failed" in line for line in p.log)

    def test_hooks_are_called(self):
        calls = []

        class Hooked(tm.CSVPipeline):
            def before_run(self):
                calls.append("before")

            def after_run(self):
                calls.append("after")

        Hooked("src").run()
        assert calls == ["before", "after"]

    def test_abstract_base(self):
        with pytest.raises(TypeError):
            tm.DataPipeline("src")
