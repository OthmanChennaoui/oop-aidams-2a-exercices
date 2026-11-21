import pytest

import abcd_records as abcd
import hospital as h


# ------------------------------------------------------------- hospital ---
@pytest.fixture
def clinic():
    admin = h.Organizer("Admin", "admin")
    patient = admin.register_member(h.Patient("Alice", "pwd"))
    doctor = admin.register_member(h.Doctor("Dr House", "x", "Diagnostics"))
    return admin, patient, doctor


def test_login_logout(clinic):
    _, patient, _ = clinic
    assert patient.login("wrong") is False
    assert patient.login("pwd") is True
    patient.logout()
    assert patient.logged_in is False


def test_full_consultation_and_payment(clinic):
    admin, patient, doctor = clinic
    problem = patient.post_problem("Headache")
    assert problem.status is h.ProblemStatus.PENDING

    admin.assign(problem, doctor)
    assert problem.status is h.ProblemStatus.IN_REVIEW

    doctor.provide_prescription(problem, "Rest", fee=30)
    prescription = admin.deliver(problem)
    assert problem.status is h.ProblemStatus.RESOLVED
    assert patient.past_prescriptions() == [prescription]

    payment = patient.pay(prescription, h.CheckPayment("42"))
    admin.forward_payment(payment)
    assert doctor.balance == 30

    with pytest.raises(ValueError):
        patient.pay(prescription, h.CashPayment())
    with pytest.raises(ValueError):
        admin.forward_payment(payment)


def test_unassigned_doctor_cannot_prescribe(clinic):
    _, patient, doctor = clinic
    problem = patient.post_problem("Cough")
    with pytest.raises(PermissionError):
        doctor.provide_prescription(problem, "Syrup", fee=10)


@pytest.mark.parametrize(
    "method", [h.CashPayment(), h.CheckPayment("1"), h.CreditCardPayment("1234567812345678")]
)
def test_payment_methods_are_polymorphic(method):
    assert "10.00€" in method.pay(10)


def test_invalid_card_rejected():
    with pytest.raises(ValueError):
        h.CreditCardPayment("123")


# --------------------------------------------------------- ABCD records ---
@pytest.fixture
def shop():
    records = abcd.DailyRecords()
    return records, abcd.OrderProcessingClerk(records)


def _two_cds():
    return (
        abcd.CD("1", "Kind of Blue", "Miles Davis", 15.0, stock=5),
        abcd.CD("2", "Abbey Road", "The Beatles", 15.0, stock=0),
    )


def test_non_member_receives_application(shop):
    _, clerk = shop
    application = clerk.handle_request(abcd.NonMember("Bob", "Lille"))
    assert isinstance(application, abcd.MembershipApplication)
    assert clerk.handle_request(abcd.RegularMember(1, "Al", "Paris")) is None


def test_royal_member_scenario(shop):
    records, clerk = shop
    cd1, cd2 = _two_cds()
    order = abcd.Order(abcd.RoyalMember(42, "Alice", "Paris"))
    order.add_item(cd1)
    order.add_item(cd2)

    clerk.process_order(order)

    assert order.status is abcd.OrderStatus.PARTIALLY_SHIPPED
    assert [l.backordered for l in order.lines] == [False, True]
    assert cd1.stock == 4
    assert order.total() == 27.0  # 30 EUR - 10%
    assert [l.item for l in order.shipping_list.lines] == [cd1]
    assert records.orders == [order]

    receipt = abcd.CollectionDeptClerk.collect(order, abcd.Check(27.0, "000123"))
    assert "000123" in receipt and order.status is abcd.OrderStatus.PAID


def test_regular_member_cannot_order_unavailable(shop):
    _, clerk = shop
    cd1, cd2 = _two_cds()
    order = abcd.Order(abcd.RegularMember(7, "Bob", "Lyon"))
    order.add_item(cd1)
    order.add_item(cd2)

    clerk.process_order(order)

    assert [l.item for l in order.lines] == [cd1]
    assert order.total() == 15.0
    assert order.status is abcd.OrderStatus.PROCESSED


def test_payment_must_match_invoice(shop):
    _, clerk = shop
    cd1, _ = _two_cds()
    order = abcd.Order(abcd.RegularMember(7, "Bob", "Lyon"))
    order.add_item(cd1)
    with pytest.raises(ValueError):
        abcd.CollectionDeptClerk.collect(order, abcd.Cash(15.0))  # not processed yet
    clerk.process_order(order)
    with pytest.raises(ValueError):
        abcd.CollectionDeptClerk.collect(order, abcd.BankDraft(1.0, "BNP"))
