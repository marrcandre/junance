from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from cards.models import Card, Invoice
from identity.services import create_family

User = get_user_model()


@pytest.mark.django_db
def test_card_and_invoice_belong_to_family():
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    card = Card.objects.create(family=family, name="Cartão", last_four="1234")
    invoice = Invoice.objects.create(
        family=family,
        card=card,
        competence_date="2026-01-01",
        due_date="2026-02-05",
    )

    assert invoice.card == card
    assert invoice.total_open == Decimal("0.00")
