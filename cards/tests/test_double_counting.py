from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from cards.models import Card, Invoice, Purchase
from cards.services import record_card_purchase, settle_invoice
from identity.services import create_family
from ledger.models import Category, Expense
from ledger.services import create_account, create_category

User = get_user_model()


@pytest.mark.django_db
def test_invoice_payment_settles_obligation_without_creating_second_expense():
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    account = create_account(family, "Conta corrente")
    category = create_category(family, "Mercado", kind=Category.Kind.EXPENSE)
    card = Card.objects.create(family=family, name="Cartão", last_four="4321")
    purchase = record_card_purchase(
        user,
        family,
        card,
        category,
        Decimal("100.00"),
        purchase_date=date(2026, 1, 10),
    )
    invoice = purchase.installments.get().invoice

    payment = settle_invoice(user, invoice, account, Decimal("100.00"), paid_at=date(2026, 2, 5))

    invoice.refresh_from_db()
    assert payment.amount == Decimal("100.00")
    assert invoice.status == Invoice.Status.PAID
    assert Purchase.objects.filter(family=family).count() == 1
    assert Expense.objects.filter(family=family).count() == 0
