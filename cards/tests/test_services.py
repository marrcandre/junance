from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from cards.models import Installment
from cards.services import record_card_purchase
from identity.services import create_family
from ledger.models import Category
from ledger.services import create_category

User = get_user_model()


@pytest.mark.django_db
def test_installment_purchase_preserves_purchase_invoice_links():
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    category = create_category(family, "Viagem", kind=Category.Kind.EXPENSE)
    from cards.models import Card

    card = Card.objects.create(family=family, name="Cartão principal", last_four="1234")

    purchase = record_card_purchase(
        user,
        family,
        card,
        category,
        Decimal("300.00"),
        purchase_date=date(2026, 1, 10),
        installments=3,
        description="Passagens",
    )

    installments = list(purchase.installments.select_related("invoice"))
    assert len(installments) == 3
    assert sum((item.amount for item in installments), Decimal("0.00")) == Decimal("300.00")
    assert [item.invoice.competence_date for item in installments] == [
        date(2026, 1, 1),
        date(2026, 2, 1),
        date(2026, 3, 1),
    ]
    assert all(item.status == Installment.Status.OPEN for item in installments)
