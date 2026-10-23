from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from identity.services import create_family
from investments.models import InvestmentTransaction
from investments.services import record_contribution, record_withdrawal

User = get_user_model()


@pytest.mark.django_db
def test_contribution_and_withdrawal_change_position_as_patrimony():
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")

    position = record_contribution(
        user,
        family,
        "Tesouro Selic",
        Decimal("2.00"),
        Decimal("100.00"),
        transaction_date=date(2026, 1, 10),
    )
    withdrawal = record_withdrawal(
        user,
        family,
        position,
        Decimal("0.50"),
        Decimal("30.00"),
        transaction_date=date(2026, 2, 10),
    )

    position.refresh_from_db()
    assert position.quantity == Decimal("1.50")
    assert withdrawal.kind == InvestmentTransaction.Kind.WITHDRAWAL
    assert InvestmentTransaction.objects.filter(position=position).count() == 2
