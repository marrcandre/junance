from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from cards.models import Card
from cards.services import record_card_purchase
from identity.services import create_family
from imports.services import confirm_import, preview_import, receive_file
from ledger.models import Category
from ledger.services import create_account, create_category, record_expense
from planning.queries import monthly_summary

User = get_user_model()


@pytest.mark.django_db
def test_primary_financial_journey_keeps_domains_separate():
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    account = create_account(family, "Conta corrente")
    category = create_category(family, "Mercado", kind=Category.Kind.EXPENSE)
    record_expense(
        user,
        family,
        account,
        category,
        Decimal("40.00"),
        transaction_date=date(2026, 1, 5),
        competence_date=date(2026, 1, 1),
    )

    card = Card.objects.create(family=family, name="Cartão", last_four="1234")
    record_card_purchase(
        user,
        family,
        card,
        category,
        Decimal("100.00"),
        purchase_date=date(2026, 1, 10),
    )

    batch = receive_file(
        user,
        family,
        "journey.csv",
        b"external_id,date,amount,description\njourney-1,2026-01-20,-12.50,Importado anonimo\n",
    )
    preview_import(user, batch)
    confirm_import(user, batch)

    summary = monthly_summary(family, date(2026, 1, 1))
    assert summary["expense"] == Decimal("40.00")
    assert batch.status == "confirmed"
    assert family.card_purchases.count() == 1
